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

# ---- Programas para trabajar: Python, Node.js y Playwright
tiene_python() {
  for c in python3 python; do
    command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null && return 0
  done
  return 1
}
tiene_node() {
  command -v node >/dev/null 2>&1 || return 1
  [ "$(node --version 2>/dev/null | sed -E 's/^v([0-9]+).*/\1/')" -ge 18 ] 2>/dev/null
}
tiene_playwright() { command -v playwright >/dev/null 2>&1; }

GESTOR=""
case "$(uname -s)" in
  Darwin) command -v brew >/dev/null 2>&1 && GESTOR="brew" ;;
  *) if command -v apt-get >/dev/null 2>&1; then GESTOR="apt"; elif command -v dnf >/dev/null 2>&1; then GESTOR="dnf"; fi ;;
esac

orden() {  # orden de instalación de un programa con el gestor de este sistema
  case "$1:$GESTOR" in
    python:brew) echo "brew install python@3.12" ;;
    python:apt) echo "sudo apt-get install -y python3" ;;
    python:dnf) echo "sudo dnf install -y python3" ;;
    node:brew) echo "brew install node" ;;
    node:apt) echo "sudo apt-get install -y nodejs npm" ;;
    node:dnf) echo "sudo dnf install -y nodejs npm" ;;
    playwright:*) echo "npm install -g playwright && npx playwright install chromium" ;;
  esac
}
descarga() {
  case "$1" in
    python) echo "https://www.python.org/downloads/" ;;
    node) echo "https://nodejs.org/" ;;
    playwright) echo "https://playwright.dev/docs/intro" ;;
  esac
}

INTERACTIVO=0
if [ -z "${PRIMEROS_PASOS_SIN_PROGRAMAS:-}" ] && { : </dev/tty; } 2>/dev/null; then INTERACTIVO=1; fi

preguntar() {  # devuelve 0 si la persona acepta
  [ "$INTERACTIVO" = 1 ] || return 1
  printf '%s [S/n] ' "$1" > /dev/tty
  read -r r < /dev/tty || return 1
  case "$r" in n|N|no|NO|No) return 1 ;; *) return 0 ;; esac
}

aviso ""
aviso "Programas para trabajar:"
PENDIENTES=""
for p in python node playwright; do
  if "tiene_$p"; then
    aviso "  OK     $p"
    continue
  fi
  aviso "  FALTA  $p"
  cmd="$(orden "$p")"
  if [ "$p" = "playwright" ] && ! tiene_node; then cmd=""; fi
  if [ -n "$cmd" ] && preguntar "  ¿Instalo $p ahora? Se ejecutará: $cmd"; then
    if sh -c "$cmd" && "tiene_$p"; then
      aviso "  OK     $p instalado"
      continue
    fi
    aviso "  No se pudo instalar $p."
  fi
  PENDIENTES="$PENDIENTES $p"
done
if [ -n "$PENDIENTES" ]; then
  aviso ""
  aviso "Quedan por instalar:"
  for p in $PENDIENTES; do
    cmd="$(orden "$p")"
    aviso "  $p: ${cmd:-descárgalo de $(descarga "$p")}"
  done
  [ "$(uname -s)" = "Darwin" ] && [ -z "$GESTOR" ] && aviso "  (Con Homebrew, https://brew.sh, se instalan con un solo comando.)"
fi

if [ ! -d "$DESTINO_REPO/.git" ]; then
  aviso "Ojo: esta carpeta no es un repositorio git. Funciona igual, pero te conviene versionarla (git init)."
fi

aviso ""
aviso "Siguiente paso: abre Claude Code en esta carpeta y escribe «empezar»."
