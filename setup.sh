#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Clone TEMP2 if not already present
if [ ! -d "${SCRIPT_DIR}/TEMP2" ]; then
    echo "Cloning TEMP2..."
    git clone https://github.com/weng-lab/TEMP2.git "${SCRIPT_DIR}/TEMP2"
fi

# Replace TEMP2/bin/TEMP2 with a symlink to the root entry script
target="${SCRIPT_DIR}/TEMP2/bin/TEMP2"
if [ -e "$target" ] || [ -L "$target" ]; then
    unlink "$target"
fi
ln -s "${SCRIPT_DIR}/TEMP2/TEMP2" "$target"

echo "Setup complete."
echo "Run the pipeline with:"
echo "  bash ${SCRIPT_DIR}/denovo_te_calling.sub -s SAMPLE -l FQ1 -r FQ2 -i BAM -g REFERENCE -a ANNOTATION"
