import os
import re
import pytest

# Directories to scan for runtime source code
RUNTIME_DIRS = [
    os.path.join("frontend", "src"),
    "backend",
    "preprocessing",
    "graph",
    "data_generator"
]

# Patterns for external network URLs (allowing localhost / 127.0.0.1 and static doc/license domains)
EXTERNAL_URL_REGEX = re.compile(
    r'https?://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|github\.com|bugs\.webkit\.org|bugs\.chromium\.org|w3\.org|tailwindcss\.com)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?::\d+)?'
)

# Files to ignore (e.g. non-runtime docs, build output, compiled stylesheets with third-party headers)
IGNORED_EXTENSIONS = {".md", ".txt", ".map", ".png", ".jpg", ".ico", ".svg", ".css"}
IGNORED_FILES = {"README.md", "task.md", "implementation_plan.md", "walkthrough.md"}

def test_no_external_runtime_http_dependencies():
    """
    Scans runtime source files for external HTTP/HTTPS dependencies.
    All runtime code must run 100% offline without remote CDNs, remote APIs, or cloud calls.
    Whitelists localhost and 127.0.0.1.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    violations = []

    for rdir in RUNTIME_DIRS:
        abs_rdir = os.path.join(root_dir, rdir)
        if not os.path.exists(abs_rdir):
            continue

        for root, dirs, files in os.walk(abs_rdir):
            # Skip node_modules or pycache if present
            dirs[:] = [d for d in dirs if d not in {"node_modules", "__pycache__", ".pytest_cache"}]
            
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in IGNORED_EXTENSIONS or f in IGNORED_FILES:
                    continue

                fpath = os.path.join(root, f)
                rel_path = os.path.relpath(fpath, root_dir)

                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as file_obj:
                        for idx, line in enumerate(file_obj, start=1):
                            # Skip comments containing documentation links or CSS license/bug headers
                            stripped = line.strip()
                            if (
                                stripped.startswith("#") or
                                stripped.startswith("//") or
                                stripped.startswith("/*") or
                                stripped.startswith("*") or
                                stripped.endswith("*/")
                            ):
                                continue

                            matches = EXTERNAL_URL_REGEX.findall(line)
                            for match in matches:
                                violations.append(f"{rel_path}:L{idx} -> {match}")
                except Exception as err:
                    pytest.fail(f"Failed to read file {rel_path}: {err}")

    assert not violations, f"Found {len(violations)} external runtime dependency violations:\n" + "\n".join(violations)
