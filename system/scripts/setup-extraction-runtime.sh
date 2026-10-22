#!/usr/bin/env bash
# Install the SHA256-locked Poppler provider used to replay extraction recipes.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
runtime_dir="${1:-${script_dir}/../../.cache/extraction-runtime}"
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  printf '%s\n' 'This extraction provider requires Linux x86_64.' >&2
  exit 2
fi
mkdir -p "${runtime_dir}/bootstrap"
runtime_dir="$(cd "${runtime_dir}" && pwd)"
bootstrap="${runtime_dir}/bootstrap/micromamba"
curl --fail --location --silent --show-error --retry 3 \
  https://github.com/mamba-org/micromamba-releases/releases/download/2.9.0-0/micromamba-linux-64 \
  --output "${bootstrap}.download"
printf '%s  %s\n' \
  366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3 \
  "${bootstrap}.download" | sha256sum --check
mv "${bootstrap}.download" "${bootstrap}"
chmod +x "${bootstrap}"
MAMBA_ROOT_PREFIX="${runtime_dir}/packages" "${bootstrap}" create --yes \
  --prefix "${runtime_dir}/env" \
  --file "${script_dir}/../runtime/poppler-linux-64.lock"
version="$("${runtime_dir}/env/bin/pdftoppm" -v 2>&1)"
if [[ "${version%%$'\n'*}" != 'pdftoppm version 26.05.0' ]]; then
  printf '%s\n' 'Installed extraction provider has the wrong Poppler version.' >&2
  exit 1
fi
printf 'Extraction tools: %s\n' "${runtime_dir}/env/bin"
