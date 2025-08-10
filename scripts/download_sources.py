#!/usr/bin/env python3
"""Descarga fuentes públicas"""
import json
from pathlib import Path

def download_sample_data():
    """Crea datos de ejemplo para desarrollo"""
    docs_path = Path("raw/docs")
    docs_path.mkdir(parents=True, exist_ok=True)
    
    sample = {
        "title": "Documento de Ejemplo",
        "content": "Información sobre Panamá para desarrollo",
        "source": "Generado",
        "license": "CC0"
    }
    
    output = docs_path / "sample.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Creado: {output}")

if __name__ == "__main__":
    download_sample_data()
