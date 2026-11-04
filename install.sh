#!/usr/bin/env bash
# Instala o actualiza el skill Primer Paso (primeros-pasos) en la carpeta actual, sea cual sea su ruta.
#
#   curl -fsSL https://raw.githubusercontent.com/SEOenMedellin/espacio-trabajo-claude/main/install.sh | bash
#
# PRIMEROS_PASOS_ORIGEN=<carpeta> instala desde una copia local (lo usan las pruebas).
set -euo pipefail

REPO="SEOenMedellin/espacio-trabajo-claude"
RAMA="${PRIMEROS_PASOS_RAMA:-main}"
DESTINO_REL=".claude/skills/primeros-pasos"

aviso() { printf '%s\n' "$*"; }
falla() {
  echo "No se pudo instalar: $*" >&2
  echo "Si no sabes cómo seguir, copia este mensaje y envíaselo a quien te compartió el enlace." >&2
  exit 1
}

# Con «curl … | bash» la entrada es el propio script: las preguntas se leen de /dev/tty.
INTERACTIVO=0
if [ -z "${PRIMEROS_PASOS_SIN_PROGRAMAS:-}" ] && { : </dev/tty; } 2>/dev/null; then INTERACTIVO=1; fi

no_sirve() {  # la carpeta personal o la raíz del disco no son una carpeta de trabajo
  [ "$1" = "$(cd "$HOME" && pwd -P)" ] || [ "$1" = "/" ]
}

DESTINO_REPO="$(pwd -P)"
if no_sirve "$DESTINO_REPO"; then
  [ "$INTERACTIVO" = 1 ] || falla "estás en tu carpeta personal. Entra primero a la carpeta donde vas a trabajar y vuelve a ejecutar el comando."
  aviso "Estás en tu carpeta personal, no en una carpeta de trabajo."
  printf '%s' "Escribe la ruta de la carpeta donde vas a trabajar (o arrástrala aquí desde el Finder) y presiona Enter: " > /dev/tty
  IFS= read -r ruta < /dev/tty || falla "no se recibió ninguna carpeta."
  # Al arrastrar, Terminal pone una barra antes de cada espacio y un espacio al final.
  ruta="$(printf '%s' "$ruta" | sed -e 's/[[:space:]]*$//' -e 's/^[[:space:]]*//' -e "s/^['\"]//" -e "s/['\"]\$//" -e 's/\\\(.\)/\1/g')"
  case "$ruta" in "~"|"~/"*) ruta="$HOME${ruta#?}" ;; esac
  [ -n "$ruta" ] || falla "no se recibió ninguna carpeta."
  if [ ! -d "$ruta" ]; then
    printf '%s [S/n] ' "La carpeta $ruta no existe. ¿La creo?" > /dev/tty
    read -r r < /dev/tty || r=n
    case "$r" in n|N|no|NO|No) falla "la carpeta $ruta no existe." ;; esac
    mkdir -p "$ruta" || falla "no se pudo crear $ruta."
  fi
  DESTINO_REPO="$(cd "$ruta" && pwd -P)" || falla "no se pudo entrar a $ruta."
  if no_sirve "$DESTINO_REPO"; then falla "esa es tu carpeta personal: elige o crea una carpeta para tu trabajo."; fi
  cd "$DESTINO_REPO"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ -n "${PRIMEROS_PASOS_ORIGEN:-}" ]; then
  [ -f "$PRIMEROS_PASOS_ORIGEN/skill/SKILL.md" ] || falla "$PRIMEROS_PASOS_ORIGEN no contiene skill/SKILL.md."
  cp -R "$PRIMEROS_PASOS_ORIGEN/skill" "$TMP/skill"
else
  command -v curl >/dev/null 2>&1 || falla "hace falta curl."
  command -v tar >/dev/null 2>&1 || falla "hace falta tar."
  aviso "Descargando Primer Paso…"
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$RAMA" | tar -xz -C "$TMP" \
    || falla "no se pudo descargar de GitHub. Revisa tu conexión."
  mv "$TMP"/*/skill "$TMP/skill" 2>/dev/null || falla "la descarga no trae la carpeta skill/."
fi
find "$TMP/skill" -name '__pycache__' -type d -prune -exec rm -rf {} +

mkdir -p "$DESTINO_REPO/.claude/skills"
if [ -d "$DESTINO_REPO/$DESTINO_REL" ]; then
  ACCION="actualizado"
  rm -rf "$DESTINO_REPO/$DESTINO_REL.anterior" 2>/dev/null || true
  mv "$DESTINO_REPO/$DESTINO_REL" "$DESTINO_REPO/$DESTINO_REL.anterior"     || falla "no se pudo reemplazar la versión anterior. Revisa los permisos de la carpeta .claude y vuelve a ejecutar el comando."
  mv "$TMP/skill" "$DESTINO_REPO/$DESTINO_REL"
  rm -rf "$DESTINO_REPO/$DESTINO_REL.anterior" 2>/dev/null || true
else
  ACCION="instalado"
  mv "$TMP/skill" "$DESTINO_REPO/$DESTINO_REL"
fi

aviso ""
aviso "Listo: Primer Paso quedó $ACCION en tu carpeta $DESTINO_REPO"

# ---- Programas para trabajar: Git, Python, Node.js y Playwright
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
# En Mac, /usr/bin/git existe aunque Git no esté instalado: hay que ejecutarlo.
tiene_git() { command -v git >/dev/null 2>&1 && git --version >/dev/null 2>&1; }
# npm -g necesita sudo cuando su carpeta global no es de la persona (Node del instalador oficial).
npm_global() {
  pre="$(npm prefix -g 2>/dev/null || echo /usr/local)"
  if [ -w "$pre/lib/node_modules" ] || { [ ! -e "$pre/lib/node_modules" ] && [ -w "$pre/lib" ]; }; then
    echo "npm install -g playwright"
  else
    echo "sudo npm install -g playwright"
  fi
}

GESTOR=""
case "$(uname -s)" in
  Darwin) command -v brew >/dev/null 2>&1 && GESTOR="brew" ;;
  *) if command -v apt-get >/dev/null 2>&1; then GESTOR="apt"; elif command -v dnf >/dev/null 2>&1; then GESTOR="dnf"; fi ;;
esac

orden() {  # orden de instalación de un programa con el gestor de este sistema
  case "$1:$GESTOR" in
    git:brew) echo "brew install git" ;;
    git:apt) echo "sudo apt-get install -y git" ;;
    git:dnf) echo "sudo dnf install -y git" ;;
    git:) if [ "$(uname -s)" = "Darwin" ]; then echo "xcode-select --install"; fi ;;
    python:brew) echo "brew install python@3.12" ;;
    python:apt) echo "sudo apt-get install -y python3" ;;
    python:dnf) echo "sudo dnf install -y python3" ;;
    node:brew) echo "brew install node" ;;
    node:apt) echo "sudo apt-get install -y nodejs npm" ;;
    node:dnf) echo "sudo dnf install -y nodejs npm" ;;
    playwright:*) echo "$(npm_global); npx playwright install chromium" ;;
  esac
}
descarga() {
  case "$1" in
    git) echo "https://git-scm.com/downloads" ;;
    python) echo "https://www.python.org/downloads/" ;;
    node) echo "https://nodejs.org/" ;;
    playwright) echo "https://playwright.dev/docs/intro" ;;
  esac
}

preguntar() {  # devuelve 0 si la persona acepta
  [ "$INTERACTIVO" = 1 ] || return 1
  printf '%s [S/n] ' "$1" > /dev/tty
  read -r r < /dev/tty || return 1
  case "$r" in n|N|no|NO|No) return 1 ;; *) return 0 ;; esac
}

titulo() { case "$1" in git) echo "Git" ;; python) echo "Python" ;; node) echo "Node.js" ;; playwright) echo "Playwright" ;; esac; }
para_que() {
  case "$1" in
    git) echo "guarda el historial de tus archivos" ;;
    python) echo "hace funcionar tu espacio de trabajo" ;;
    node) echo "lo necesitan algunas herramientas" ;;
    playwright) echo "permite a Claude revisar páginas web" ;;
  esac
}

aviso ""
aviso "Programas para trabajar (revisando que tengas lo necesario):"
PENDIENTES=""
for p in git python node playwright; do
  if "tiene_$p"; then
    aviso "  [listo]  $(titulo "$p")"
    continue
  fi
  aviso "  [falta]  $(titulo "$p"), $(para_que "$p")"
  cmd="$(orden "$p")"
  if [ "$p" = "playwright" ] && ! tiene_node; then cmd=""; fi
  if [ -n "$cmd" ] && preguntar "           ¿Lo instalo ahora? Escribe S y presiona Enter (o N para dejarlo para después)"; then
    aviso "           Instalando… puede tardar unos minutos. Si te pide una contraseña, es la de tu computador (no se ve mientras la escribes)."
    if [ "$cmd" = "xcode-select --install" ]; then
      xcode-select --install >/dev/null 2>&1 || true
      aviso "           Se abrió una ventana de Apple: acepta, espera a que termine y vuelve a pegar este mismo comando."
    elif sh -c "$cmd" </dev/tty >/dev/null 2>&1 && "tiene_$p"; then
      aviso "  [listo]  $(titulo "$p")"
      continue
    fi
  fi
  PENDIENTES="$PENDIENTES, $(titulo "$p")"
done
PENDIENTES="${PENDIENTES#, }"

# ---- Que «empezar», «iniciar» o «configurar» activen el skill
# (también repara los ajustes de una instalación anterior)
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"
    break
  fi
done
aviso ""
if [ -z "$PY" ]; then
  aviso "Falta un paso: Python no quedó instalado y sin él tu espacio no puede prepararse."
  aviso "Instálalo desde https://www.python.org/downloads/ (el botón amarillo «Download Python»),"
  aviso "cierra esta ventana, ábrela de nuevo y vuelve a pegar el mismo comando de instalación."
  exit 0
fi
if ! "$PY" "$DESTINO_REPO/$DESTINO_REL/scripts/activar.py" --registrar --raiz "$DESTINO_REPO" >/dev/null 2>&1; then
  aviso "Casi listo: no pude activar la palabra «empezar», pero puedes escribir /primeros-pasos en Claude."
fi
if [ -n "$PENDIENTES" ]; then
  aviso "Quedó pendiente: $PENDIENTES. No te preocupes: Claude te ayuda a instalarlo cuando escribas «empezar»."
  aviso ""
fi
aviso "Siguiente paso: copia estas dos líneas, pégalas aquí y presiona Enter:"
aviso "  cd \"$DESTINO_REPO\""
aviso "  claude"
aviso "Cuando Claude se abra, escribe empezar y presiona Enter. Claude te guía desde ahí."
