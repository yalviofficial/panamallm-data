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
