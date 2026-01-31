#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="./police"

URLS=(
  "https://policie.gov.cz/soubor/data-web-12-2025-rar.aspx"
  "https://policie.gov.cz/soubor/data-web-2024-rar.aspx"
  "https://policie.gov.cz/soubor/data-na-web-2023-rar.aspx"
)

mkdir -p "$BASE_DIR"

for url in "${URLS[@]}"; do
  echo "Processing: $url"

  if [[ $url =~ (20[0-9]{2}) ]]; then
    year="${BASH_REMATCH[1]}"
  else
    echo "ERROR: Could not determine year from URL: $url"
    continue
  fi

  target_dir="$BASE_DIR/$year"
  mkdir -p "$target_dir"

  # Use a meaningful filename
  filename=$(basename "$url" | sed 's/\.aspx$/.rar/')
  output_path="$target_dir/$filename"

  echo "Saving to $output_path"
  curl -L --fail --retry 3 -o "$output_path" "$url"

  unrar x -o+ "$output_path" "$target_dir"
  rm -f "$output_path"

done

echo "All downloads completed."