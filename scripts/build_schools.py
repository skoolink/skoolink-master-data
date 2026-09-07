#!/usr/bin/env python3
"""
build_schools.py

Alternatif Python untuk build-schools.sh. Membaca semua entry Sveltia CMS
collection "schools" di schools/<slug>/index.yaml, lalu:
  1. Menggabungkan semua entry jadi satu file dist/schools.json (JSON array)
  2. Menyalin logo tiap sekolah ke dist/logo/<code>.webp

Dependency: PyYAML (pip install pyyaml). Python 3 sudah tersedia di
runner ubuntu-latest, tinggal `pip install pyyaml` di step workflow.

Asumsi sama seperti versi shell:
  - schools/<slug>/index.yaml berisi field: name, code, domain_name, logo
  - field `logo` berisi nama file relatif terhadap folder entry
    (karena media_folder/public_folder: "."), sudah berformat .webp
    (hasil transformasi media_libraries Sveltia CMS).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "Error: modul 'yaml' (PyYAML) tidak ditemukan. Install dengan: "
        "pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(1)

SCHOOLS_DIR = Path("schools")
DIST_DIR = Path("dist")
LOGO_DIR = DIST_DIR / "logo"


def resolve_logo_path(entry_dir: Path, logo_value: str) -> Path | None:
    """Coba beberapa kemungkinan lokasi file logo."""
    candidates = [
        entry_dir / logo_value,
        entry_dir / Path(logo_value).name,
        Path(logo_value),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    if not SCHOOLS_DIR.is_dir():
        print(f"Error: folder '{SCHOOLS_DIR}' tidak ditemukan", file=sys.stderr)
        return 1

    LOGO_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    count = 0

    for entry_dir in sorted(SCHOOLS_DIR.iterdir()):
        if not entry_dir.is_dir():
            continue

        yaml_file = entry_dir / "index.yaml"
        if not yaml_file.is_file():
            yaml_file = entry_dir / "index.yml"
        if not yaml_file.is_file():
            print(f"Skip: tidak ada index.yaml di {entry_dir}", file=sys.stderr)
            continue

        with yaml_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        code = str(data.get("code") or "").strip()
        domain_name = str(data.get("domain_name") or "").strip()
        if not code:
            print(f"Skip: field 'code' kosong di {yaml_file}", file=sys.stderr)
            continue

        logo_value = data.get("logo")
        logo_dest_rel = f"logo/{code}.webp"
        domain_url = f"http://{domain_name}/"

        if logo_value:
            src_logo = resolve_logo_path(entry_dir, str(logo_value))
            if src_logo is not None:
                shutil.copyfile(src_logo, LOGO_DIR / f"{code}.webp")
            else:
                print(
                    f"Warning: file logo '{logo_value}' tidak ditemukan "
                    f"untuk code={code} (dir: {entry_dir})",
                    file=sys.stderr,
                )
                logo_dest_rel = None
        else:
            logo_dest_rel = None

        entries.append(
            {
                "name": data.get("name"),
                "code": code,
                "domain": domain_url,
                "domain_name": data.get("domain_name"),
                "logo": logo_dest_rel,
            }
        )
        count += 1

    entries.sort(key=lambda e: e["code"])

    json_content = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    (DIST_DIR / "schools.json").write_text(json_content, encoding="utf-8")

    print(f"OK: {count} sekolah diproses -> {DIST_DIR / 'schools.json'}")
    print(f"Logo disalin ke: {LOGO_DIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
