#!/bin/bash

# Pastikan argumen nama file telah diberikan
if [ -z "$1" ]; then
  echo "Penggunaan: $0 <nama_file.json>"
  exit 1
fi

INPUT_FILE="$1"

# Pastikan file input ada
if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File '$INPUT_FILE' tidak ditemukan!"
  exit 1
fi

# Mengambil nama file tanpa ekstensi untuk dijadikan nilai province (contoh: "73.json" -> "73")
FILENAME_ONLY=$(basename "$INPUT_FILE")
PROVINCE="${FILENAME_ONLY%.*}"

# Mengambil nilai administrative_area_level dari objek meta
LEVEL=$(jq '.meta.administrative_area_level' "$INPUT_FILE")

# Iterasi setiap item di array data dan buat file masing-masing
jq -c '.data[]' "$INPUT_FILE" | while read -r item; do
  # Ambil nilai code untuk nama file output
  CODE=$(echo "$item" | jq -r '.code')
  
  # Susun ulang objek JSON dengan urutan atribut sesuai permintaan
  echo "$item" | jq \
    --arg prov "$PROVINCE" \
    --argjson lvl "$LEVEL" \
    '{code: .code, province: $prov, name: .name, administrative_area_level: $lvl}' > "${CODE}.json"
done
