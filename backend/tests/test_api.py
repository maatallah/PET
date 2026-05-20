import os

import pytest


@pytest.mark.anyio
async def test_create_workspace(client):
    response = await client.post(
        "/workspaces",
        json={"name": "Test WS", "description": "smoke test"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test WS"
    assert data["description"] == "smoke test"
    assert "id" in data
    return data["id"]


@pytest.mark.anyio
async def test_list_workspaces(client):
    await client.post("/workspaces", json={"name": "WS 1"})
    await client.post("/workspaces", json={"name": "WS 2"})
    response = await client.get("/workspaces")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.anyio
async def test_get_workspace(client):
    created = await client.post("/workspaces", json={"name": "Get Test"})
    ws_id = created.json()["id"]
    response = await client.get(f"/workspaces/{ws_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Test"


@pytest.mark.anyio
async def test_update_workspace(client):
    created = await client.post("/workspaces", json={"name": "Old Name"})
    ws_id = created.json()["id"]
    response = await client.patch(f"/workspaces/{ws_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.anyio
async def test_delete_workspace(client):
    created = await client.post("/workspaces", json={"name": "Delete Me"})
    ws_id = created.json()["id"]
    response = await client.delete(f"/workspaces/{ws_id}")
    assert response.status_code == 204
    response = await client.get(f"/workspaces/{ws_id}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_full_hierarchy(client):
    ws = (await client.post("/workspaces", json={"name": "Root"})).json()
    proj = (
        await client.post(
            f"/workspaces/{ws['id']}/projects",
            json={"name": "My Project", "description": "test project"},
        )
    ).json()
    assert proj["workspace_id"] == ws["id"]

    sess = (
        await client.post(
            f"/projects/{proj['id']}/sessions",
            json={"name": "Session 1"},
        )
    ).json()
    assert sess["project_id"] == proj["id"]

    prompt = (
        await client.post(
            f"/sessions/{sess['id']}/prompts",
            json={
                "name": "My Prompt",
                "system_prompt": "You are helpful",
                "user_prompt": "Explain {topic}",
                "variables": [{"name": "topic", "type": "string"}],
                "prompt_pattern": "persona",
            },
        )
    ).json()
    assert prompt["session_id"] == sess["id"]
    assert prompt["version"] == 1
    assert prompt["prompt_pattern"] == "persona"

    listed = await client.get(f"/workspaces/{ws['id']}/projects")
    assert len(listed.json()) == 1


@pytest.mark.anyio
async def test_404(client):
    response = await client.get("/workspaces/nonexistent")
    assert response.status_code == 404
    response = await client.get("/projects/nonexistent", params={"workspace_id": "x"})
    assert response.status_code == 404


@pytest.mark.anyio
async def test_execute_prompt_dry_run(client):
    ws = (await client.post("/workspaces", json={"name": "Exec WS"})).json()
    proj = (
        await client.post(f"/workspaces/{ws['id']}/projects", json={"name": "Exec Proj"})
    ).json()
    sess = (
        await client.post(f"/projects/{proj['id']}/sessions", json={"name": "Exec Sess"})
    ).json()

    prompt = (
        await client.post(
            f"/sessions/{sess['id']}/prompts",
            json={
                "name": "Exec Prompt",
                "system_prompt": "You are an expert on {topic}",
                "user_prompt": "Tell me about {topic} in {style} style",
                "variables": [
                    {"name": "topic", "type": "string"},
                    {"name": "style", "type": "string"},
                ],
                "prompt_pattern": "persona",
            },
        )
    ).json()

    response = await client.post(
        f"/sessions/{sess['id']}/prompts/{prompt['id']}/execute",
        json={
            "variables": {"topic": "Python", "style": "beginner"},
            "dry_run": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["prompt_id"] == prompt["id"]
    assert data["resolved_prompt"] != ""
    assert "Python" in data["resolved_prompt"]
    assert "beginner" in data["resolved_prompt"]
    assert data["tokens_input"] is not None
    assert data["tokens_input"] > 0
    assert data["cost_estimate"] is not None
    assert data["cost_estimate"] > 0
    assert data["model_response"] is None
    assert data["tokens_output"] is None
    assert sorted(data["detected_variables"]) == ["style", "topic"]
    assert data["unsubstituted_variables"] == []


@pytest.mark.anyio
async def test_execute_prompt_no_variables(client):
    ws = (await client.post("/workspaces", json={"name": "Exec2 WS"})).json()
    proj = (
        await client.post(f"/workspaces/{ws['id']}/projects", json={"name": "Exec2 Proj"})
    ).json()
    sess = (
        await client.post(f"/projects/{proj['id']}/sessions", json={"name": "Exec2 Sess"})
    ).json()
    prompt = (
        await client.post(
            f"/sessions/{sess['id']}/prompts",
            json={
                "name": "No Var Prompt",
                "system_prompt": "You are helpful.",
                "user_prompt": "Hello world",
            },
        )
    ).json()

    response = await client.post(
        f"/sessions/{sess['id']}/prompts/{prompt['id']}/execute",
        json={"dry_run": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tokens_input"] is not None
    assert data["detected_variables"] == []
    assert data["unsubstituted_variables"] == []


@pytest.mark.anyio
async def test_file_upload_and_download(client):
    ws = (await client.post("/workspaces", json={"name": "File WS"})).json()
    proj = (
        await client.post(f"/workspaces/{ws['id']}/projects", json={"name": "File Proj"})
    ).json()
    sess = (
        await client.post(f"/projects/{proj['id']}/sessions", json={"name": "File Sess"})
    ).json()
    sid = sess["id"]

    # Upload
    content = b"Hello, this is a test file!"
    response = await client.post(
        f"/sessions/{sid}/files",
        files={"upload": ("test.txt", content, "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["original_name"] == "test.txt"
    assert data["mime_type"] == "text/plain"
    assert data["size_bytes"] == len(content)
    assert data["session_id"] == sid
    file_id = data["id"]

    # List
    list_resp = await client.get(f"/sessions/{sid}/files")
    assert list_resp.status_code == 200
    files = list_resp.json()
    assert len(files) == 1
    assert files[0]["id"] == file_id

    # Get
    get_resp = await client.get(f"/sessions/{sid}/files/{file_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["filename"] == "test.txt"

    # Download
    dl_resp = await client.get(f"/sessions/{sid}/files/{file_id}/download")
    assert dl_resp.status_code == 200
    assert dl_resp.content == content
    assert dl_resp.headers["content-type"].startswith("text/plain")

    # Delete
    del_resp = await client.delete(f"/sessions/{sid}/files/{file_id}")
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/sessions/{sid}/files/{file_id}")
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_file_upload_binary(client):
    ws = (await client.post("/workspaces", json={"name": "FileBin WS"})).json()
    proj = (
        await client.post(f"/workspaces/{ws['id']}/projects", json={"name": "FileBin Proj"})
    ).json()
    sess = (
        await client.post(f"/projects/{proj['id']}/sessions", json={"name": "FileBin Sess"})
    ).json()

    content = b"\x89PNG\r\n\x1a\n" + os.urandom(100)
    response = await client.post(
        f"/sessions/{sess['id']}/files",
        files={"upload": ("image.png", content, "image/png")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["mime_type"] == "image/png"
    assert data["size_bytes"] == len(content)

    # Download binary content back
    dl_resp = await client.get(f"/sessions/{sess['id']}/files/{data['id']}/download")
    assert dl_resp.content == content


@pytest.mark.anyio
async def test_file_404(client):
    response = await client.get("/sessions/nonexistent/files/badid")
    assert response.status_code == 404
    response = await client.get("/sessions/nonexistent/files/badid/download")
    assert response.status_code == 404
