"""
Pack a clean source ZIP for Hirebox submission (< 50MB).
  cd nana-agent && npm run pack:submit
"""

from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path

SKIP_DIR_NAMES = {
    "node_modules",
    ".venv",
    "dist",
    "__pycache__",
    ".git",
    ".cursor",
    "submit",
}
SKIP_FILE_NAMES = {".env", ".DS_Store"}
SKIP_SUFFIXES = {".pyc", ".log"}


def skip_path(path: Path, base: Path) -> bool:
    rel = path.relative_to(base)
    if any(part in SKIP_DIR_NAMES for part in rel.parts):
        return True
    if path.name in SKIP_FILE_NAMES:
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    if path.name.startswith(".env.") and path.name != ".env.example":
        return True
    return False


def add_tree(zf: zipfile.ZipFile, folder: Path, arc_prefix: str) -> int:
    if not folder.is_dir():
        return 0
    n = 0
    for path in folder.rglob("*"):
        if not path.is_file() or skip_path(path, folder):
            continue
        arcname = f"{arc_prefix}/{path.relative_to(folder).as_posix()}"
        zf.write(path, arcname)
        n += 1
    return n


def main() -> None:
    app_root = Path(__file__).resolve().parents[1]
    repo_root = app_root.parent
    out_dir = repo_root / "submit"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_path = out_dir / f"nana-teochew-agent_submit_{stamp}.zip"

    count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        root_readme = repo_root / "README.md"
        if root_readme.is_file():
            zf.write(root_readme, "README.md")
            count += 1
        count += add_tree(zf, app_root, "nana-agent")
        count += add_tree(zf, repo_root / "docs", "docs")
        count += add_tree(zf, repo_root / "data", "data")

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"OK: {zip_path}")
    print(f"files={count}, size={size_mb:.2f} MB")
    if size_mb >= 50:
        print("WARNING: ZIP exceeds Hirebox 50MB limit")


if __name__ == "__main__":
    main()
