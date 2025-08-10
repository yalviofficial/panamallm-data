#!/usr/bin/env python3
import json, sys, glob, yaml
from jsonschema import validate, ValidationError
from langdetect import detect

PANAMA_TERMS = ['vaina', 'chévere', 'plena', 'pelaos', 'juega vivo']

def validate_panama_spanish(text):
    """Valida que el texto tenga elementos del español panameño"""
    has_panama_terms = any(term in text.lower() for term in PANAMA_TERMS)
    return has_panama_terms

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
    print(f"{meta}: faltan campos {missing}")
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
          if not validate_panama_spanish(txt):
            print(f"! {p}:{i}: falta jerga panameña")
      except (json.JSONDecodeError, ValidationError) as e:
        print(f"{p}:{i}: {e}")
        errors += 1

if errors:
  print(f"\nFALLÓ validación: {errors} problema(s)")
  sys.exit(1)
else:
  print("Validaciones OK")
