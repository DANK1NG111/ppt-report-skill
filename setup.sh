#!/bin/sh
set -eu
root=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
explicit_python=''
previous=''
for argument in "$@"; do
    if [ "$previous" = '--python' ]; then explicit_python=$argument; break; fi
    case "$argument" in --python=*) explicit_python=${argument#--python=}; break ;; esac
    previous=$argument
done
if [ -n "$explicit_python" ]; then
    exec "$explicit_python" "$root/scripts/setup.py" "$@"
fi
for py in python3 python; do
    if command -v "$py" >/dev/null 2>&1 && "$py" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
        exec "$py" "$root/scripts/setup.py" "$@"
    fi
done
uvbin=$(command -v uv || true)
if [ -z "$uvbin" ]; then
    mkdir -p "$root/.runtime/bin"
    installer=$(mktemp)
    trap 'rm -f "$installer"' EXIT HUP INT TERM
    curl --fail --location --proto '=https' --tlsv1.2 https://astral.sh/uv/install.sh -o "$installer"
    UV_INSTALL_DIR="$root/.runtime/bin" UV_NO_MODIFY_PATH=1 sh "$installer"
    uvbin="$root/.runtime/bin/uv"
fi
exec "$uvbin" run --no-project --python 3.12 "$root/scripts/setup.py" "$@"
