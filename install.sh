#!/usr/bin/env bash
# Instala o actualiza el skill primeros-pasos en el repositorio de la carpeta actual.
#
#   curl -fsSL https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.sh | bash
#
# PRIMEROS_PASOS_ORIGEN=<carpeta> instala desde una copia local (lo usan las pruebas).
set -euo pipefail

REPO="davidortiz-ops/espacio-trabajo-claude"
RAMA="${PRIMEROS_PASOS_RAMA:-main}"
DESTINO_REL=".claude/skills/primeros-pasos"

aviso() { printf '%s\n' "$*"; }
falla() { printf 'No se pudo instalar: %s\n' "$*" >&2; exit 1; }

DESTINO_REPO="$(pwd -P)"
if [ "$DESTINO_REPO" = "$(cd "$HOME" && pwd -P)" ]; then
  falla "estás en tu carpeta personal. Entra primero a la carpeta del repositorio donde vas a trabajar (cd ruta/a/tu-repositorio) y vuelve a ejecutar el comando."
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ -n "${PRIMEROS_PASOS_ORIGEN:-}" ]; then
  [ -f "$PRIMEROS_PASOS_ORIGEN/skill/SKILL.md" ] || falla "$PRIMEROS_PASOS_ORIGEN no contiene skill/SKILL.md."
  cp -R "$PRIMEROS_PASOS_ORIGEN/skill" "$TMP/skill"
else
  command -v curl >/dev/null 2>&1 || falla "hace falta curl."
  command -v tar >/dev/null 2>&1 || falla "hace falta tar."
  aviso "Descargando primeros-pasos…"
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$RAMA" | tar -xz -C "$TMP" \
    || falla "no se pudo descargar de GitHub. Revisa tu conexión."
  mv "$TMP"/*/skill "$TMP/skill" 2>/dev/null || falla "la descarga no trae la carpeta skill/."
fi
find "$TMP/skill" -name '__pycache__' -type d -prune -exec rm -rf {} +

mkdir -p "$DESTINO_REPO/.claude/skills"
if [ -d "$DESTINO_REPO/$DESTINO_REL" ]; then
  ACCION="actualizado"
  rm -rf "$DESTINO_REPO/$DESTINO_REL.anterior"
  mv "$DESTINO_REPO/$DESTINO_REL" "$DESTINO_REPO/$DESTINO_REL.anterior"
  mv "$TMP/skill" "$DESTINO_REPO/$DESTINO_REL"
  rm -rf "$DESTINO_REPO/$DESTINO_REL.anterior"
else
  ACCION="instalado"
  mv "$TMP/skill" "$DESTINO_REPO/$DESTINO_REL"
fi

aviso ""
aviso "Listo: primeros-pasos quedó $ACCION en $DESTINO_REPO/$DESTINO_REL"

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  aviso ""
  aviso "Ojo: falta Python 3.10 o superior. Instálalo desde https://www.python.org/downloads/ antes de empezar."
fi
if [ ! -d "$DESTINO_REPO/.git" ]; then
  aviso "Ojo: esta carpeta no es un repositorio git. Funciona igual, pero te conviene versionarla (git init)."
fi

aviso ""
aviso "Siguiente paso: abre Claude Code en esta carpeta y escribe «empezar»."
