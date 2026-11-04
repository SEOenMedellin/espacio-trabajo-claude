#!/usr/bin/env python3
"""Utilidades compartidas por los scripts de primeros-pasos.

Encuentra la raíz del espacio de trabajo, lee `espacio.json` (la configuración
que deja el montaje), resuelve las rutas de cada rol y da formato a fechas y
nombres. Ningún otro script decide dónde vive algo: todos preguntan aquí.

Solo biblioteca estándar. Python 3.10+.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True  # no dejar __pycache__ dentro del skill instalado

AQUI = Path(__file__).resolve().parent
SKILL = AQUI.parent
PLANTILLAS = SKILL / "plantillas"       # lo que montar.py renderiza
CONVENCIONES = SKILL / "convenciones"   # se copian a DOCS en cada espacio
CONFIG = "espacio.json"
ESTADO = ".espacio"                  # derivados: grafo, sesiones, respaldos
DOCS = "docs/espacio-de-trabajo"     # convenciones copiadas al repositorio
VERSION = "1.5.1"
MARCA_INICIO = "<!-- primeros-pasos:inicio -->"
MARCA_FIN = "<!-- primeros-pasos:fin -->"
MESES = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
# Límites contra silos profundos: Windows corta en 260 caracteres de ruta
# completa (MAX_PATH) y macOS en 255 por nombre. Se deja margen para la carpeta
# donde viva el repositorio y para herramientas que agregan sufijos.
MAX_NIVELES = 6        # segmentos de una ruta relativa a la raíz (archivo incluido)
MAX_RUTA = 150         # caracteres de la ruta relativa
MAX_NOMBRE = 60        # caracteres de un nombre de archivo o carpeta
MAX_ABSOLUTA = 240     # caracteres de la ruta absoluta (aviso)
ROLES = ("contexto", "entregables", "investigacion", "memoria_global",
         "memoria_proyecto", "bitacora_peticiones")
TIPOS_MEMORIA = ("restriccion", "solucion", "decision", "proceso", "dato", "preferencia")


def utf8() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def encontrar_raiz(dada: str | None = None) -> Path:
    """--raiz > $CLAUDE_PROJECT_DIR > carpeta donde está instalado el skill
    (la que eligió la persona, esté donde esté) > subir desde el cwd buscando
    espacio.json, .git o .claude (sin llegar a la carpeta personal) > cwd."""
    if dada:
        return Path(dada).expanduser().resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    casa = Path.home().resolve()
    # .claude/skills/primeros-pasos, o .claude/espacio si el skill se retiró
    if SKILL.parent.name in ("skills", ".claude") and ".claude" in (SKILL.parent.name, SKILL.parent.parent.name):
        instalada = SKILL.parent.parent.parent if SKILL.parent.name == "skills" else SKILL.parent.parent
        if instalada != casa:
            return instalada
    cwd = Path.cwd().resolve()
    for d in (cwd, *cwd.parents):
        if (d / CONFIG).is_file():
            return d
    for d in (cwd, *cwd.parents):
        if d == casa:
            break
        if (d / ".git").exists() or (d / ".claude").is_dir():
            return d
    return cwd


def leer_config(raiz: Path) -> dict | None:
    p = raiz / CONFIG
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return None


def proyectos(cfg: dict) -> list[str]:
    if cfg.get("arquitectura", {}).get("modo") == "multiproyecto":
        return list(cfg.get("proyectos", {}).get("lista", []))
    return []


def resolver(cfg: dict, proyecto: str | None = None) -> dict:
    """Rutas de cada rol, relativas a la raíz y con `<proyecto>` sustituido.
    Si hay un solo proyecto y no se dio ninguno, se usa ese."""
    lista = proyectos(cfg)
    if proyecto is None and len(lista) == 1:
        proyecto = lista[0]
    res = {}
    for rol, valor in cfg.get("rutas", {}).items():
        if not valor:
            continue
        if "<proyecto>" in valor and proyecto:
            valor = valor.replace("<proyecto>", proyecto)
        res[rol] = valor
    return res


def programa_disponible(comprobar: str) -> bool:
    """¿Está en el PATH el ejecutable con el que empieza `comprobar`?"""
    partes = (comprobar or "").split()
    return bool(partes) and shutil.which(partes[0]) is not None


def base_dir(ruta: str) -> str:
    """'entregables/<DD-mmm-YYYY>/' -> 'entregables'. Corta en el primer marcador."""
    return ruta.split("<", 1)[0].rstrip("/\\") or "."


def hoy(fecha: dt.date | None = None) -> str:
    d = fecha or dt.date.today()
    return f"{d.day:02d}-{MESES[d.month - 1]}-{d.year}"


# Carpeta de una tarea dentro de los entregables: <id>-<DD-mmm-YYYY>, p. ej. P-012-27-oct-2026
TAREA = re.compile(r"^(P-\d{3,}|[a-z][a-z0-9]*(?:-[a-z0-9]+)*?)-\d{2}-(" + "|".join(MESES) + r")-\d{4}$")
RELACIONES = ("requiere", "resuelve", "deriva_en", "relacionado")


def activo() -> bool:
    """¿El skill está activo? (desactivado o eliminado, sus herramientas siguen funcionando)."""
    return (SKILL / "SKILL.md").is_file()


def legado(cfg: dict) -> bool:
    """Espacios anteriores a 1.4: entregables por fecha (<DD-mmm-YYYY>/<categoria>/<archivo>)."""
    return "<DD-mmm-YYYY>" in cfg.get("rutas", {}).get("entregables", "")


def carpeta_tarea(cfg: dict, proyecto: str | None, categoria: str, id_: str, fecha: str) -> str:
    """Ruta relativa de la carpeta de una tarea: <entregables><categoria>/<id>-<fecha>/."""
    base = base_dir(resolver(cfg, proyecto)["entregables"])
    pre = "" if base == "." else base + "/"
    if legado(cfg):
        return f"{pre}{fecha}/{categoria}/{id_}"
    return f"{pre}{categoria}/{id_}-{fecha}"


def a_fecha(texto: str) -> dt.date | None:
    """'27-oct-2026' -> date, o None si no tiene ese formato."""
    m = re.match(r"^(\d{2})-([a-z]{3})-(\d{4})$", (texto or "").strip())
    if not m or m.group(2) not in MESES:
        return None
    try:
        return dt.date(int(m.group(3)), MESES.index(m.group(2)) + 1, int(m.group(1)))
    except ValueError:
        return None


def duracion(minutos: int | float) -> str:
    """95 -> '1 h 35 min'."""
    m = int(round(minutos))
    h, r = divmod(abs(m), 60)
    signo = "-" if m < 0 else ""
    if not h:
        return f"{signo}{r} min"
    return f"{signo}{h} h" + (f" {r} min" if r else "")


def atajos(cfg: dict) -> list[dict]:
    """Un atajo (skill invocable como /<slug>) por cada tarea habitual del perfil."""
    res, vistos = [], set()
    for t in cfg.get("perfil", {}).get("tareas", []):
        t = t if isinstance(t, dict) else {"tarea": str(t)}
        nombre = str(t.get("tarea", "")).strip()
        if not nombre or t.get("skill"):  # la cubre un skill que ya existía: no se crea atajo
            continue
        s = slug(nombre, largo=40)
        if s == "primeros-pasos":
            s = "tarea-primeros-pasos"
        if s in vistos:
            continue
        vistos.add(s)
        res.append({"slug": s, "tarea": nombre, "entrega": t.get("entrega") or "",
                    "frecuencia": t.get("frecuencia") or "", "ruta": f".claude/skills/{s}/SKILL.md"})
    return res


def sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def slug(texto: str, largo: int = MAX_NOMBRE - 8) -> str:
    """kebab-case sin acentos, cortado en un guion para no pasar `largo`
    (deja espacio para la extensión y un sufijo -2)."""
    t = re.sub(r"[^a-z0-9]+", "-", sin_acentos(texto).lower()).strip("-")
    if len(t) > largo:
        t = t[:largo].rsplit("-", 1)[0] or t[:largo]
    return t.strip("-") or "proyecto"


def problema_longitud(raiz: Path, rel: str) -> str:
    """'' si la ruta es segura en Windows y macOS; si no, el motivo."""
    partes = [p for p in rel.split("/") if p]
    if len(partes) > MAX_NIVELES:
        return f"ruta demasiado profunda ({len(partes)} niveles; máximo {MAX_NIVELES})"
    if len(rel) > MAX_RUTA:
        return f"ruta demasiado larga ({len(rel)} caracteres; máximo {MAX_RUTA})"
    largo = next((p for p in partes if len(p) > MAX_NOMBRE), None)
    if largo:
        return f"nombre demasiado largo ({len(largo)} caracteres; máximo {MAX_NOMBRE}): {largo[:30]}…"
    if len(str(raiz / rel)) > MAX_ABSOLUTA:
        return (f"la ruta completa pasa de {MAX_ABSOLUTA} caracteres y puede fallar en Windows: "
                "acorta nombres o mueve el repositorio a una carpeta más corta")
    return ""


def escribir(p: Path, texto: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)


_PYTHON_CACHE: dict[tuple[str, ...], bool] = {}


def _python_sirve(cmd: list[str]) -> bool:
    """Está en el PATH, no es el acceso directo de la Microsoft Store
    (WindowsApps\\python.exe, que abre la tienda o, desde Git Bash, falla con
    «Permission denied») y es Python 3.10 o superior (en Mac, /usr/bin/python3
    puede ser 3.9)."""
    clave = tuple(cmd)
    if clave not in _PYTHON_CACHE:
        ruta = shutil.which(cmd[0])
        ok = bool(ruta) and "windowsapps" not in ruta.lower()
        if ok:
            try:
                ok = subprocess.run([ruta, *cmd[1:], "-c", "import sys; sys.exit(sys.version_info < (3, 10))"],
                                    capture_output=True, timeout=15).returncode == 0
            except (OSError, subprocess.SubprocessError):
                ok = False
        _PYTHON_CACHE[clave] = ok
    return _PYTHON_CACHE[clave]


def _candidatos_python() -> list[list[str]]:
    # Windows: «python» es el nombre habitual y «py» el lanzador oficial.
    # Mac y Linux: «python3»; «python» puede no existir o ser Python 2.
    if os.name == "nt":
        return [["python"], ["python3"], ["py", "-3"]]
    return [["python3"], ["python"]]


def python_hook() -> tuple[str, list[str]]:
    """Programa y argumentos previos para lanzar Python desde un hook, sin consola."""
    for cmd in _candidatos_python():
        if _python_sirve(cmd):
            return cmd[0], cmd[1:]
    # Ningún Python adecuado en el PATH: el que está corriendo este script, en esta máquina.
    return Path(sys.executable).as_posix(), []


def python_cmd() -> str:
    """Intérprete para los comandos que se escriben en la documentación del espacio."""
    exe, previos = python_hook()
    return " ".join([f'"{exe}"' if " " in exe else exe, *previos])


# Hooks del espacio: evento -> (script, timeout, matcher)
HOOKS = {
    "SessionStart": ("inicio.py", 30, None),
    "Stop": ("cierre_check.py", 15, None),
    "PreToolUse": ("orden_check.py", 15, "Write|Bash|PowerShell"),
    "UserPromptSubmit": ("activar.py", 10, None),
}


def hook(raiz: Path, script: str, timeout: int) -> dict:
    """Hook en formato exec («command» + «args»). Claude Code reemplaza
    ${CLAUDE_PROJECT_DIR} por la carpeta del proyecto de quien lo usa y lanza
    Python directamente, sin Git Bash ni PowerShell de por medio: no depende del
    sistema, de la consola, de espacios en la ruta ni de dónde esté la carpeta."""
    try:
        ruta = "${CLAUDE_PROJECT_DIR}/" + SKILL.relative_to(raiz).as_posix()
    except ValueError:
        ruta = SKILL.as_posix()  # skill fuera del proyecto: su ruta en esta máquina
    exe, previos = python_hook()
    return {"type": "command", "command": exe, "args": [*previos, f"{ruta}/scripts/{script}"],
            "timeout": timeout}


def es_hook_propio(h: dict, script: str) -> bool:
    """Hook de este skill, en formato viejo o nuevo, instalado o retirado a .claude/espacio."""
    texto = " ".join([str(h.get("command", ""))] + [str(a) for a in h.get("args") or []]).replace("\\", "/")
    return f"/scripts/{script}" in texto and any(
        m in texto for m in ("primeros-pasos/", ".claude/espacio/", SKILL.as_posix()))


def reparar_hooks(raiz: Path, agregar: set[str]) -> tuple[dict, list[str]] | None:
    """Lee .claude/settings.json, pasa todos los hooks de este skill al formato
    vigente y agrega los de `agregar` que falten. Lo demás se conserva tal cual.
    Devuelve (settings, cambios), o None si el JSON está dañado."""
    p = raiz / ".claude" / "settings.json"
    try:
        actual = json.loads(p.read_text(encoding="utf-8") or "{}") if p.is_file() else {}
    except ValueError:
        return None
    cambios = []
    hk = actual.setdefault("hooks", {})
    for evento, (script, timeout, matcher) in HOOKS.items():
        nuevo = hook(raiz, script, timeout)
        hallado = False
        for g in hk.get(evento, []):
            for i, h in enumerate(g.get("hooks", [])):
                if es_hook_propio(h, script):
                    hallado = True
                    if h != nuevo:
                        g["hooks"][i] = nuevo
                        cambios.append(f"{evento}:{script} (reparado)")
        if not hallado and script in agregar:
            grupo = {"matcher": matcher, "hooks": [nuevo]} if matcher else {"hooks": [nuevo]}
            hk.setdefault(evento, []).append(grupo)
            cambios.append(f"{evento}:{script}")
    return actual, cambios


def _sesion_ruta(raiz: Path, sid: str) -> Path:
    return raiz / ESTADO / "sesiones" / f"{re.sub(r'[^A-Za-z0-9_-]', '', sid) or 'sin-id'}.json"


def sesion_leer(raiz: Path, sid: str) -> dict:
    try:
        return json.loads(_sesion_ruta(raiz, sid).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def sesion_guardar(raiz: Path, sid: str, datos: dict) -> None:
    try:
        escribir(_sesion_ruta(raiz, sid), json.dumps(datos))
    except OSError:
        pass


def skill_rel(raiz: Path) -> str:
    """Ruta del skill para los hooks: relativa a la raíz si vive dentro, absoluta si no."""
    try:
        return SKILL.relative_to(raiz).as_posix()
    except ValueError:
        return SKILL.as_posix()
