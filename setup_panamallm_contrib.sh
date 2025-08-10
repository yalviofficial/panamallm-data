#!/usr/bin/env bash
# PanamaLLM – Bootstrap de repositorio de datos con flujos de contribución
# Uso:
#   1) Guardar como setup_panamallm_contrib.sh
#   2) chmod +x setup_panamallm_contrib.sh
#   3) ./setup_panamallm_contrib.sh
# Requiere: git, python3. Opcional: gh (GitHub CLI), dvc
# Compatible con bash 3.x (macOS) – evita ${var^^}

set -euo pipefail

ask() { local prompt="$1" default="${2:-}"; read -r -p "$prompt" resp || true; echo "${resp:-$default}"; }

have() { command -v "$1" >/dev/null 2>&1; }

ORG=$(ask "GitHub Organization (default: PanamaLLM): " "PanamaLLM")
REPO=$(ask "Nombre del repo (default: panamallm-data): " "panamallm-data")
CREATE_REMOTE=$(ask "¿Crear repo en GitHub con gh? [Y/n]: " "Y")
PRIVATE_CHOICE=$(ask "¿Privado? [y/N]: " "N")
INIT_DVC=$(ask "¿Inicializar DVC si está disponible? [Y/n]: " "Y")

# PRIVATE_FLAG compatible con bash 3.x
case "$PRIVATE_CHOICE" in
  Y|y) PRIVATE_FLAG="--private" ;;
  *)   PRIVATE_FLAG="--public" ;;
esac

ROOT_DIR="$REPO"
mkdir -p "$ROOT_DIR"
cd "$ROOT_DIR"

echo "==> Inicializando git"
git init -q

echo "==> Creando estructura de carpetas"
mkdir -p raw/{gov,docs,corp} interim processed meta scripts contrib/datasets contrib/evals .github/ISSUE_TEMPLATE .github/workflows

# .gitignore
cat > .gitignore << 'EOF'
.DS_Store
.venv/
__pycache__/
*.pyc
*.ipynb_checkpoints/
# DVC
/.dvc/tmp/
/.dvc/cache/
EOF

# README
cat > README.md << 'EOF'
# PanamaLLM Data

Repositorio de **datos** y **contribuciones** para entrenar PanamaLLM.

- `raw/` fuentes originales (PDF/CSV/HTML)
- `interim/` datos limpios intermedios (parquet)
- `processed/` datasets finales en JSONL para entrenamiento
- `contrib/` aportes de la comunidad (datasets/ evals/)
- `scripts/` validaciones y pipelines

Consulta `CONTRIBUTING.md` para aportar.
EOF

# DATASET_CARD plantilla
cat > DATASET_CARD.md << 'EOF'
# Ficha del Dataset (Plantilla)

**Nombre:** 
**Descripción:** 
**Origen/Fuente:** 
**URL:** 
**Licencia:** (CC-BY, CC0, Open Government, Permiso, etc.)
**PII:** (sí/no + método de desidentificación)
**Cobertura temporal:** 
**Campos/Esquema:** 
**Uso previsto:** Entrenamiento/Validación/RAG
**Riesgos y limitaciones:** 
EOF

# CONTRIBUTING
cat > CONTRIBUTING.md << 'EOF'
# Cómo contribuir a PanamaLLM Data

Gracias por aportar. Hay 3 formas principales:

1. **Datasets**: crea una carpeta en `contrib/datasets/<slug>` con:
   - `source.yaml` (metadatos y licencia)
   - `samples/` (muestras pequeñas en `.jsonl` si aplica)
2. **Evaluaciones**: añade un archivo `contrib/evals/<tema>.jsonl` con pares *pregunta-respuesta* y cita de fuente.
3. **Código**: mejoras a scripts o validaciones.

## Paso a paso (PR)
- Haz *fork*, crea una rama y añade tus archivos.
- Asegúrate de que **no** incluyes PII ni material sin licencia.
- Ejecuta `python scripts/validate_contrib.py` y corrige errores.
- Abre un Pull Request usando la plantilla.

## Esquema JSONL para ejemplos instruct
Cada línea un objeto:
```json
{"id":"id-unico","prompt":"Pregunta…","response":"Respuesta…","source":"Fuente","license":"open","split":"train"}
```

## Licencias aceptadas
- CC0, CC-BY, Open Government/Data, Permiso por escrito del titular.

## Código de conducta
Cumple el `CODE_OF_CONDUCT.md`. Respeto y colaboración.
EOF

# CODE_OF_CONDUCT
cat > CODE_OF_CONDUCT.md << 'EOF'
# Código de Conducta

Participa con respeto. No se tolera conducta abusiva. Los mantenedores pueden tomar medidas ante incumplimientos.
EOF

# PR template
cat > PULL_REQUEST_TEMPLATE.md << 'EOF'
### Tipo de contribución
- [ ] Dataset
- [ ] Evals
- [ ] Código

### Checklist
- [ ] Licencia confirmada en `source.yaml`
- [ ] Sin PII o con desidentificación documentada
- [ ] Archivos en rutas `contrib/…` y/o `scripts/`
- [ ] `python scripts/validate_contrib.py` sin errores

### Notas
EOF

# Issue Form – Aportar datos
cat > .github/ISSUE_TEMPLATE/dataset.yml << 'EOF'
name: "Aportar datos"
description: Sube una fuente con licencia clara para PanamaLLM
labels: ["dataset","help wanted"]
body:
  - type: input
    id: fuente
    attributes:
      label: "Fuente/URL oficial"
      placeholder: "https://…"
    validations:
      required: true
  - type: dropdown
    id: licencia
    attributes:
      label: Licencia
      options: ["CC-BY","CC0","Open Government","Permiso escrito adjunto"]
    validations:
      required: true
  - type: textarea
    id: descripcion
    attributes:
      label: "Descripción y utilidad"
      placeholder: "Qué contiene y por qué sirve"
  - type: textarea
    id: cita
    attributes:
      label: "Cómo citar"
      placeholder: "Autor/Institución, año, enlace"
  - type: textarea
    id: adjuntos
    attributes:
      label: "Archivos o enlaces a ZIP/CSV/PDF"
EOF

# GitHub Actions – Validación
cat > .github/workflows/validate.yml << 'EOF'
name: validate
on:
  pull_request:
    branches: [ main ]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install -r scripts/requirements.txt
      - run: python scripts/validate_contrib.py
EOF

# Requisitos para los scripts
cat > scripts/requirements.txt << 'EOF'
jsonschema
pyyaml
langdetect
pandas
EOF

# Script de validación básico
cat > scripts/validate_contrib.py << 'PY'
#!/usr/bin/env python3
import json, sys, glob, yaml
from jsonschema import validate, ValidationError
from langdetect import detect

DATASET_SCHEMA = {
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "prompt": {"type": "string"},
    "response": {"type": "string"},
    "source": {"type": "string"},
    "license": {"type": "string"},
    "split": {"type": "string"}
  },
  "required": ["id","prompt","response","source","license"]
}

errors = 0

# Validar metadatos YAML
for meta in glob.glob("contrib/datasets/*/source.yaml"):
  with open(meta, 'r', encoding='utf-8') as f:
    y = yaml.safe_load(f)
  required = ["name","url","license","owner"]
  missing = [k for k in required if k not in (y or {})]
  if missing:
    print(f"✗ {meta}: faltan campos {missing}")
    errors += 1

# Validar JSONL de samples y evals
paths = glob.glob("contrib/datasets/*/samples/*.jsonl") + glob.glob("contrib/evals/*.jsonl")
for p in paths:
  with open(p, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
      try:
        obj = json.loads(line)
        validate(instance=obj, schema=DATASET_SCHEMA)
        # idioma básico
        txt = (obj.get("prompt","") + " " + obj.get("response",""))[:400]
        if txt.strip():
          try:
            lang = detect(txt)
            if lang != 'es':
              print(f"! {p}:{i}: idioma detectado {lang} (esperado 'es')")
          except Exception:
            pass
      except (json.JSONDecodeError, ValidationError) as e:
        print(f"✗ {p}:{i}: {e}")
        errors += 1

if errors:
  print(f"\nFALLÓ validación: {errors} problema(s)")
  sys.exit(1)
else:
  print("✓ Validaciones OK")
PY
chmod +x scripts/validate_contrib.py

# CODEOWNERS opcional
cat > .github/CODEOWNERS << 'EOF'
# Revisores por defecto
* @daivearevalo
# Puedes añadir equipos, por ejemplo:
# contrib/datasets/ @PanamaLLM/data-team
EOF

# Plantilla de metadatos de fuente
cat > contrib/datasets/README.md << 'EOF'
Crea aquí carpetas por fuente: `contrib/datasets/<slug>`

Ejemplo de `source.yaml`:
```yaml
name: "Gaceta Oficial 2024"
url: "https://…"
license: "Open Government"
owner: "República de Panamá"
update_freq: "mensual"
fields: ["articulos","resoluciones"]
pii: false
notes: "Solo textos públicos."
```
EOF

# Archivo de ejemplo para probar validación
mkdir -p contrib/evals
cat > contrib/evals/panamaqa_demo.jsonl << 'EOF'
{"id":"demo-1","prompt":"¿Cuál es la capital de Panamá?","response":"La ciudad de Panamá.","source":"Conocimiento general","license":"CC0","split":"test"}
EOF

# Git inicial

git add -A
git commit -m "init: estructura de contribuciones, issue form y validaciones" >/dev/null
# Asegura rama principal 'main' para que el workflow aplique
git branch -M main

echo "==> Repo local creado en $(pwd)"

# DVC (si disponible y solicitado) – compatible con bash 3.x
if have dvc && { [ "$INIT_DVC" = "Y" ] || [ "$INIT_DVC" = "y" ]; }; then
  echo "==> Inicializando DVC"
  dvc init -q
  git add .dvc .dvcignore
  git commit -m "chore: init dvc" >/dev/null
else
  echo "(info) DVC no inicializado. Instala con: brew install dvc  # o pipx install dvc"
fi

# Crear repo remoto con gh (si disponible)
if have gh && ! { [ "$CREATE_REMOTE" = "N" ] || [ "$CREATE_REMOTE" = "n" ]; }; then
  echo "==> Creando repo remoto $ORG/$REPO en GitHub"
  gh repo create "$ORG/$REPO" $PRIVATE_FLAG --source=. --remote=origin --push
  echo "✓ Listo: https://github.com/$ORG/$REPO"
else
  echo "(info) Saltando creación remota. Puedes ejecutar después:
   gh repo create $ORG/$REPO $PRIVATE_FLAG --source=. --remote=origin --push"
fi

echo "
✔ Proyecto listo. Próximos pasos:
- Edita ISSUE FORMS/CONTRIBUTING según tus reglas.
- (Opcional) Configura un remote de DVC: dvc remote add -d s3 s3://<bucket>/panamallm
- Invita revisores en CODEOWNERS y protege la rama main."

