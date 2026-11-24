#!/usr/bin/env bash
# Prepare only the project-owned inference environment; never start devices.
set -euo pipefail
DP_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
DP_VERIFY_ONLY=false
DP_ALLOW_CPU=()
for dp_argument in "$@"; do
  case "$dp_argument" in
    --verify-only) DP_VERIFY_ONLY=true ;;
    --allow-cpu) DP_ALLOW_CPU=(--allow-cpu) ;;
    -h|--help) printf 'Usage: bash scripts/prepare_environment.sh [--verify-only] [--allow-cpu]\n'; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$dp_argument" >&2; exit 2 ;;
  esac
done
DP_CONDA="${CONDA_EXE:-$(command -v conda || true)}"
if [[ -z "$DP_CONDA" ]]; then
  printf 'Set CONDA_EXE to the Conda executable or place conda on PATH.\n' >&2
  exit 2
fi
DP_BASE="$("$DP_CONDA" info --base)"
DP_PREFIX="$DP_ROOT/.envs/inference"
DP_REPORTS="$DP_ROOT/runs/validation/environment"
mkdir -p "$DP_REPORTS" "$DP_ROOT/.cache/conda_pkgs" "$DP_ROOT/.cache/pip" "$DP_ROOT/.cache/tmp" "$DP_ROOT/.runtime"
export CONDA_PKGS_DIRS="$DP_ROOT/.cache/conda_pkgs"
export CONDA_ENVS_PATH="$DP_ROOT/.envs"
export CONDA_AUTO_UPDATE_CONDA=false
export CONDA_ALWAYS_COPY=true
export CONDARC="$DP_ROOT/.runtime/condarc"
printf 'auto_activate_base: false\nauto_update_conda: false\n' > "$CONDARC"
export PIP_CACHE_DIR="$DP_ROOT/.cache/pip"
export PIP_CONFIG_FILE=/dev/null
export PIP_USER=false
export PIP_NO_INPUT=1
export TMPDIR="$DP_ROOT/.cache/tmp"
export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH PIP_TARGET PIP_PREFIX PIP_ROOT
if [[ ! -f "$DP_REPORTS/protected_before.json" ]]; then
  /usr/bin/python3 "$DP_ROOT/scripts/check_environment.py" baseline --conda-base "$DP_BASE"
fi
if [[ "$DP_VERIFY_ONLY" != true ]]; then
  if [[ ! -e "$DP_PREFIX" ]]; then
    "$DP_CONDA" env create --prefix "$DP_PREFIX" --file "$DP_ROOT/environment.yml" --dry-run --json > "$DP_REPORTS/solve_plan.json"
    "$DP_CONDA" env create --prefix "$DP_PREFIX" --file "$DP_ROOT/environment.yml" --yes 2>&1 | tee "$DP_REPORTS/install.log"
  elif [[ ! -f "$DP_PREFIX/conda-meta/history" ]]; then
    printf 'Invalid existing environment prefix; inspect before retrying.\n' >&2
    exit 3
  fi
  "$DP_PREFIX/bin/python" -m pip install --no-deps --no-build-isolation --editable "$DP_ROOT" 2>&1 | tee "$DP_REPORTS/adapter_install.log"
fi
"$DP_PREFIX/bin/python" -m pip check | tee "$DP_REPORTS/pip_check.txt"
"$DP_PREFIX/bin/python" "$DP_ROOT/scripts/check_environment.py" verify --conda-base "$DP_BASE" "${DP_ALLOW_CPU[@]}" > "$DP_REPORTS/verification_output.json"
"$DP_CONDA" list --prefix "$DP_PREFIX" --explicit > "$DP_REPORTS/conda-explicit.txt"
"$DP_PREFIX/bin/python" -m pip freeze > "$DP_REPORTS/pip-freeze.txt"
printf 'Inference environment checked. No weights were loaded and no devices were opened.\n'
