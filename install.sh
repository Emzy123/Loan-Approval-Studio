#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PIP_OPTS=(--default-timeout=600 --retries 15)

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip "${PIP_OPTS[@]}"

# Smallest / fewest deps first so partial installs survive timeouts
packages=(joblib numpy scipy scikit-learn pandas matplotlib)
for pkg in "${packages[@]}"; do
  echo "==> Installing ${pkg}..."
  python -m pip install "${PIP_OPTS[@]}" "${pkg}"
done

echo ""
echo "Done. Run:"
echo "  python train.py"
echo "  python predict.py"
