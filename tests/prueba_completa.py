"""Prueba de punta a punta de primeros-pasos.

Monta dos espacios en una carpeta temporal (un proyecto con código previo, y
varios proyectos) y recorre: validación de respuestas, montaje, idempotencia,
memoria, bitácora, grafo, hooks (inicio, cierre, orden), límites de ruta,
reorganización y ampliación.

    python tests/prueba_completa.py          # salida completa
    python tests/prueba_completa.py -q       # solo el resultado

Sale con código 1 si algo falla. Solo biblioteca estándar, Python 3.10+.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

SKILL = Path(__file__).resolve().parents[1] / "skill"
BASE = Path(tempfile.mkdtemp(prefix="pp-"))
SILENCIO = "-q" in sys.argv
fallos = []


def log(texto):
    if not SILENCIO:
        print(texto)


def run(repo, args, stdin=None, esperado=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    r = subprocess.run([sys.executable, str(repo / ".claude/skills/primeros-pasos/scripts" / args[0]), *args[1:]],
                       cwd=repo, input=stdin, capture_output=True, text=True, encoding="utf-8", env=env)
    log(f"\n$ {' '.join(args)}  → {r.returncode}")
    log((r.stdout + r.stderr).strip()[:2500])
    if esperado is not None and r.returncode != esperado:
        fallos.append(f"{args} devolvió {r.returncode}, esperaba {esperado}")
    return r


def repo(nombre):
    d = BASE / nombre
    shutil.copytree(SKILL, d / ".claude/skills/primeros-pasos", ignore=shutil.ignore_patterns("__pycache__"))
    return d


def write(repo_, ruta):
    return run(repo_, ["orden_check.py"], stdin=json.dumps({"tool_name": "Write", "tool_input": {
        "file_path": str(repo_ / ruta), "content": "x"}}), esperado=0).stdout


# ---------- Repo A: un proyecto, análisis de datos, con código previo
A = repo("a")
(A / "src").mkdir()
(A / "src/main.py").write_text("print(1)\n")
(A / "README.md").write_text("# Repo previo\n")
(A / ".claude/settings.json").write_text(json.dumps({"hooks": {"PostToolUse": [{"matcher": "*", "hooks": [
    {"type": "command", "command": "telemetria emit"}]}]}}))
resp = {
    "idioma": "es", "trato": "Directo y sin tecnicismos.", "git": False,
    "perfil": {"cargo": "Analista de operaciones", "area": "Operaciones", "proyecto": "Tablero logístico",
               "objetivo": "Indicadores semanales de cumplimiento de entregas.", "destinatarios": "Gerencia",
               "conocimientos": ["OTIF y lead time", "Power Query"],
               "tareas": [{"tarea": "Actualizar el tablero semanal", "frecuencia": "semanal", "entrega": "tablero"}],
               "herramientas": ["Excel", "ERP"]},
    "arquitectura": {"tipo": "analisis-de-datos", "modo": "unico", "por_que": "Exportes del ERP a indicadores.",
                     "carpetas": [{"ruta": "datos/crudos/", "para": "Exportes originales"},
                                  {"ruta": "datos/procesados/", "para": "Datos limpios"},
                                  {"ruta": "analisis/", "para": "Consultas y scripts"}]},
    "rutas": {"contexto": "contexto/", "entregables": "reportes/<DD-mmm-YYYY>/", "investigacion": "investigacion/",
              "memoria_global": "memoria/", "bitacora_peticiones": "bitacora-peticiones.md"},
    "credenciales": [{"variable": "ERP_USUARIO", "para": "Usuario de solo lectura"}],
}
(A / "respuestas-espacio.json").write_text(json.dumps(resp, ensure_ascii=False), encoding="utf-8")
run(A, ["verificar.py"], esperado=2)
malo = dict(resp, credenciales=[{"variable": "erp", "valor": "x"}])
(A / "malo.json").write_text(json.dumps(malo), encoding="utf-8")
run(A, ["montar.py", "--respuestas", "malo.json", "--dry-run"], esperado=2)
profundo = json.loads(json.dumps(resp))
profundo["arquitectura"]["carpetas"].append({"ruta": "a/b/c/d/e/", "para": "demasiado profundo"})
(A / "malo.json").write_text(json.dumps(profundo), encoding="utf-8")
run(A, ["montar.py", "--respuestas", "malo.json", "--dry-run"], esperado=2)
(A / "malo.json").unlink()
run(A, ["montar.py", "--respuestas", "respuestas-espacio.json", "--dry-run"], esperado=0)
run(A, ["montar.py", "--respuestas", "respuestas-espacio.json"], esperado=0)
if (A / "respuestas-espacio.json").exists():
    fallos.append("montar no borró respuestas-espacio.json")
if (A / "BITACORA.md").exists():
    fallos.append("el montaje creó BITACORA.md: lo del sistema no se registra")
run(A, ["verificar.py"], esperado=0)
r = run(A, ["montar.py"], esperado=0)
if "creado" in r.stdout.replace("ya existía", ""):
    fallos.append("montar no es idempotente")
st = json.loads((A / ".claude/settings.json").read_text())
if "telemetria" not in json.dumps(st) or "orden_check" not in json.dumps(st):
    fallos.append("settings no conservó la telemetría o no agregó hooks")
cfg = json.loads((A / "espacio.json").read_text(encoding="utf-8"))
if sorted(cfg["arquitectura"]["preexistentes"]) != ["README.md", "src"]:
    fallos.append(f"preexistentes inesperados: {cfg['arquitectura']['preexistentes']}")

# memoria + bitácora + grafo
(A / "memoria/otif-se-calcula-por-pedido.md").write_text(
    "---\nid: otif-se-calcula-por-pedido\ntitulo: El OTIF se calcula por pedido, no por línea\ntipo: decision\n"
    "ambito: global\nfecha: 27-oct-2026\ntags: [otif, indicadores]\nrelacionado: []\n---\nCuerpo.\n",
    encoding="utf-8")
run(A, ["memoria.py", "--rebuild"], esperado=0)
r = run(A, ["bitacora.py", "--siguiente"], esperado=0)
if r.stdout.strip() != "P-001":
    fallos.append(f"bitacora --siguiente dio {r.stdout.strip()!r}, esperaba P-001")
b = A / "bitacora-peticiones.md"
t = b.read_text(encoding="utf-8").replace("## Entradas\n", "## Entradas\n\n### P-001 — Tablero semanal de OTIF\n"
    "<!-- fecha: 27-oct-2026 | skills: | memoria: otif-se-calcula-por-pedido | archivos: reportes/x.md | "
    "proceso: tablero-semanal | estado: parcial -->\n\n**Petición:** actualizar tablero OTIF.\n\n"
    "**Cómo se resolvió:** con el exporte.\n\n**Conocimiento adyacente:** el ERP corta a medianoche UTC.\n\n")
b.write_text(t, encoding="utf-8")
run(A, ["bitacora.py", "--tabla"], esperado=0)
run(A, ["bitacora.py"], esperado=0)
run(A, ["grafo.py", "--actualizar"], esperado=0)
r = run(A, ["grafo.py", "--plan", "actualizar el tablero de OTIF de esta semana"], esperado=0)
if "otif-se-calcula-por-pedido" not in r.stdout or "Tablero semanal de OTIF" not in r.stdout:
    fallos.append("el plan no encontró la memoria o la petición previa")
r = run(A, ["grafo.py", "--plan", "redactar un contrato de arrendamiento"], esperado=0)
if "Sin antecedentes" not in r.stdout:
    fallos.append("el plan no marcó 'sin antecedentes'")

# hooks de inicio y cierre
r = run(A, ["inicio.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
for parte in ("Última sesión de trabajo", "P-001", "Skills disponibles", "otif-se-calcula-por-pedido"):
    if parte not in r.stdout:
        fallos.append(f"inicio.py no muestra {parte!r}")
run(A, ["cierre_check.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
(A / "reportes/27-oct-2026/informes").mkdir(parents=True)
(A / "reportes/27-oct-2026/informes/semana.md").write_text("x")
r = run(A, ["cierre_check.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
if '"block"' not in r.stdout:
    fallos.append("cierre_check no bloqueó con cambios sin bitácora")
r = run(A, ["cierre_check.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
if r.stdout.strip():
    fallos.append("cierre_check avisó dos veces")

# hook de orden: escrituras y movimientos
largo = "x" * 70
for ruta, debe in [("informe.md", "deny"), ("reportes/informe.md", "deny"), ("cosas/a.md", "deny"),
                   ("analisis/Mi Consulta.sql", "deny"), ("analisis/a/b/c/d/e/f.sql", "deny"),
                   (f"reportes/27-oct-2026/informes/{largo}.md", "deny"),
                   ("reportes/27-oct-2026/informes/b.md", ""), ("memoria/nuevo-nodo.md", ""),
                   ("contexto/Brief Cliente.pdf", ""), ("src/nuevo.py", ""),
                   (".claude/skills/x/SKILL.md", ""), ("README.md", "")]:
    salida = write(A, ruta)
    if (debe and debe not in salida) or (not debe and "deny" in salida):
        fallos.append(f"orden_check Write {ruta[:50]}: esperaba {debe or 'permitir'}, salió {salida[:80]!r}")
for cmd, debe in [("mv a.md b.md", "ask"), ("git mv x y", "ask"), ("Move-Item a b", "ask"),
                  ("python .claude/skills/primeros-pasos/scripts/ordenar.py --aplicar --solo x", "ask"),
                  ("ls -la", ""), ("python ordenar.py", "")]:
    s = run(A, ["orden_check.py"], stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})).stdout
    if (debe and debe not in s) or (not debe and s.strip()):
        fallos.append(f"orden_check Bash {cmd!r}: esperaba {debe or 'nada'}, salió {s[:80]!r}")

# desorden y reorganización
(A / "Informe Final.md").write_text("# Informe de cumplimiento\n", encoding="utf-8")
(A / "export ventas.csv").write_text("a,b\n1,2\n")
(A / "brief del cliente.md").write_text("Brief: alcance del tablero\n", encoding="utf-8")
(A / "reportes/suelto.md").write_text("x")
(A / "datos/crudos/copia.csv").write_text("a,b\n1,2\n")
run(A, ["ordenar.py", "--resumen"], esperado=1)
run(A, ["ordenar.py"], esperado=1)
run(A, ["ordenar.py", "--aplicar", "--solo", "Informe Final.md,export ventas.csv"], esperado=0)
if (A / "Informe Final.md").exists() or not (A / "brief del cliente.md").exists():
    fallos.append("--solo no respetó la selección")
if not (A / "reportes/27-oct-2026/informes/informe-final.md").exists() and not list(
        (A / "reportes").glob("*/informes/informe-final.md")):
    fallos.append("el informe no quedó en reportes/<fecha>/informes/")
run(A, ["ordenar.py"])

# ---------- Repo B: multiproyecto, entregables a clientes
B = repo("b")
respB = {
    "git": True,
    "perfil": {"cargo": "Consultor", "proyecto": "Cartera de clientes", "objetivo": "Diagnósticos y propuestas",
               "tareas": ["Diagnóstico mensual"], "conocimientos": [], "herramientas": []},
    "arquitectura": {"tipo": "entregables-a-clientes", "modo": "multiproyecto", "por_que": "Un cliente por carpeta.",
                     "carpetas": [{"ruta": "proyectos/<proyecto>/historial/", "para": "Datos de cada corrida"},
                                  {"ruta": "plantillas/", "para": "Formatos base"}]},
    "proyectos": {"base": "proyectos", "lista": ["cliente-a", "cliente-b"]},
    "rutas": {"contexto": "proyectos/<proyecto>/contexto/", "entregables": "proyectos/<proyecto>/<DD-mmm-YYYY>/",
              "investigacion": "investigacion/", "memoria_global": "memoria/",
              "memoria_proyecto": "proyectos/<proyecto>/memoria/",
              "bitacora_peticiones": "proyectos/<proyecto>/bitacora-peticiones.md"},
}
(B / "respuestas-espacio.json").write_text(json.dumps(respB, ensure_ascii=False), encoding="utf-8")
run(B, ["montar.py", "--respuestas", "respuestas-espacio.json"], esperado=0)
run(B, ["verificar.py"], esperado=0)
run(B, ["bitacora.py"], esperado=2)
run(B, ["bitacora.py", "--proyecto", "cliente-a", "--siguiente"], esperado=0)
run(B, ["grafo.py", "--plan", "diagnóstico", "--proyecto", "cliente-b"], esperado=0)
for ruta, debe in [("proyectos/cliente-c/x.md", "deny"), ("proyectos/cliente-a/raro/x.md", "deny"),
                   ("proyectos/cliente-a/27-oct-2026/informes/x.md", ""),
                   ("proyectos/cliente-a/historial/datos.json", ""), ("plantillas/acta.md", "")]:
    salida = write(B, ruta)
    if (debe and debe not in salida) or (not debe and "deny" in salida):
        fallos.append(f"B orden_check {ruta}: esperaba {debe or 'permitir'}, salió {salida[:80]!r}")
# ampliar: un proyecto nuevo se suma, no reemplaza
(B / "respuestas-espacio.json").write_text(
    json.dumps(dict(respB, proyectos={"base": "proyectos", "lista": ["cliente-c"]})), encoding="utf-8")
run(B, ["montar.py", "--respuestas", "respuestas-espacio.json", "--actualizar"], esperado=0)
cfgB = json.loads((B / "espacio.json").read_text(encoding="utf-8"))
if cfgB["proyectos"]["lista"] != ["cliente-a", "cliente-b", "cliente-c"]:
    fallos.append(f"ampliar no sumó proyectos: {cfgB['proyectos']['lista']}")
if not (B / "proyectos/cliente-c/bitacora-peticiones.md").is_file():
    fallos.append("ampliar no creó la bitácora del proyecto nuevo")

shutil.rmtree(BASE, ignore_errors=True)
print("\n=== FALLOS ===\n" + ("\n".join(fallos) or "ninguno"))
sys.exit(1 if fallos else 0)
