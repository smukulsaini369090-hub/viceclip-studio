import ast
import pathlib
import re
import sys

root = pathlib.Path("backend")
issues = []
py_files = sorted(root.rglob("*.py"))

for py in py_files:
    src = py.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src, filename=str(py))
    except SyntaxError as e:
        issues.append(f"[SYNTAX] {py}:{e.lineno} -> {e.msg}")
        continue

    has_sys_import = any(
        (isinstance(n, ast.Import) and any(a.name == "sys" for a in n.names))
        or (isinstance(n, ast.ImportFrom) and n.module == "sys")
        for n in ast.walk(tree)
    )
    if re.search(r"\bsys\.", src) and not has_sys_import:
        issues.append(f"[MISSING_IMPORT] {py} uses 'sys.' without importing sys")

    if ("librosa.load" in src or "sf.SoundFile" in src or "sf.read" in src) and "ffmpeg" not in src.lower():
        issues.append(f"[AUDIO_DECODE] {py} calls soundfile/librosa without ffmpeg fallback")

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(f"[BARE_EXCEPT] {py}:{node.lineno} uses bare 'except:'")

print(f"Scanned {len(py_files)} Python files. Found {len(issues)} potential issues:")
for item in issues:
    print(" -", item)