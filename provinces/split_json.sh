#!/bin/bash

if [ -z "$1" ]; then
  echo "Penggunaan: $0 <nama_file.json>"
  exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File '$INPUT_FILE' tidak ditemukan!"
  exit 1
fi

FILENAME_ONLY=$(basename "$INPUT_FILE")
PROVINCE="${FILENAME_ONLY%.*}"
LEVEL=$(jq '.meta.administrative_area_level' "$INPUT_FILE")

jq -c '.data[]' "$INPUT_FILE" | while read -r item; do
  CODE=$(echo "$item" | jq -r '.code')

  # Membuat JSON sementara lalu dikonversi ke YAML menggunakan Python
  echo "$item" | jq \
    --arg prov "$PROVINCE" \
    --argjson lvl "$LEVEL" \
    '{code: .code, name: .name, administrative_area_level: $lvl}' |
    python3 -c 'import sys, json, yaml; print(yaml.dump(json.load(sys.stdin), sort_keys=False, allow_unicode=True))' \
      >"${CODE}.yml"
done
