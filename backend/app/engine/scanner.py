INJECTION_PATTERNS: list[dict] = [
    {"name": "ignore instructions", "severity": "high", "patterns": [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directions|prompts|commands)",
        r"forget\s+(all\s+)?(previous|prior|above)\s+(instructions|directions|prompts|commands)",
        r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|directions|prompts|commands)",
    ]},
    {"name": "role hijack", "severity": "high", "patterns": [
        r"(you\s+are\s+(now|free|not\s+bound|released))",
        r"act\s+as\s+(if\s+you\s+are|though\s+you\s+are)",
        r"from\s+(now\s+on|this\s+point\s+forward)\s+you\s+are",
    ]},
    {"name": "DAN / jailbreak", "severity": "high", "patterns": [
        r"\bDAN\b",
        r"do\s+anything\s+now",
        r"jail\s*(?:break|broke)",
        r"no\s+(?:restrictions|limits|boundaries|rules|filter)",
        r"unfiltered|uncensored|ungoverned",
    ]},
    {"name": "system prompt leak", "severity": "medium", "patterns": [
        r"(repeat|output|print|display|show)\s+(the\s+)?(above|system|initial|first)\s+(prompt|instructions|message)",
        r"what\s+(is|was|were)\s+(the\s+)?(system|initial|first)\s+(prompt|instructions|message)",
        r"leak\s+(the\s+)?(system|prompt|instructions)",
        r"output\s+(your\s+)?(system|initial)\s+prompt",
    ]},
    {"name": "token smuggling", "severity": "medium", "patterns": [
        r"rot13|base64|hex\s+encode|caesar\s+cipher",
        r"decode\s+(this|the\s+following)",
        r"convert\s+(to|from)\s+(base64|hex|rot13)",
    ]},
    {"name": "role reversal", "severity": "medium", "patterns": [
        r"you\s+are\s+(the\s+)?(user|human|assistant)\s+(now|and)",
        r"(i|the\s+user)\s+(am|is)\s+(the\s+)?(ai|assistant|bot)",
        r"reverse\s+(our\s+)?roles",
    ]},
    {"name": "payload splitting", "severity": "low", "patterns": [
        r"ignore\s+the\s+above.*(?:and|then).*instead",
        r"first\s+(half|part).*second\s+(half|part)",
    ]},
]


def scan_prompt(text: str) -> list[dict]:
    import re

    findings: list[dict] = []
    text_lower = text.lower()

    for group in INJECTION_PATTERNS:
        for pattern in group["patterns"]:
            matches = re.findall(pattern, text_lower)
            if matches:
                findings.append({
                    "type": group["name"],
                    "severity": group["severity"],
                    "match": matches[0] if isinstance(matches[0], str) else matches[0][0],
                })
                break

    return findings
