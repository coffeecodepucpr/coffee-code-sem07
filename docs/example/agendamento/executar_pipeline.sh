#!/usr/bin/env bash
# Executa o pipeline de coleta. Feito para ser chamado pelo cron.
# Ajuste PROJETO e PYTHON para os caminhos do SEU computador (sempre absolutos).
set -u

PROJETO="${PROJETO:-$(cd "$(dirname "$0")/../pipeline" && pwd)}"
PYTHON="${PYTHON:-$PROJETO/.venv/bin/python}"
LOG="$PROJETO/logs/cron.log"

mkdir -p "$PROJETO/logs"
cd "$PROJETO" || exit 2

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') inicio"
  "$PYTHON" -m coleta "$@"
  codigo=$?
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') fim (codigo $codigo)"
} >> "$LOG" 2>&1

exit "$codigo"
