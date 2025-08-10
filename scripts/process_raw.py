#!/usr/bin/env python3
"""Pipeline para procesar raw → interim"""
import json
from pathlib import Path
import pandas as pd

def process_raw_files():
    """Procesa archivos raw básico"""
    raw_path = Path("raw")
    interim_path = Path("interim")
    interim_path.mkdir(parents=True, exist_ok=True)
    
    print("📄 Procesando archivos raw...")
    
    # Por ahora solo contar archivos
    file_count = 0
    for file_path in raw_path.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            file_count += 1
    
    print(f"✓ Encontrados {file_count} archivos")
    
    # Crear un archivo dummy para que DVC funcione
    dummy_data = pd.DataFrame([{ "status": "ready", "files": file_count }])
    dummy_data.to_parquet(interim_path / "status.parquet")

if __name__ == "__main__":
    process_raw_files()
