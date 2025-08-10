#!/usr/bin/env python3
"""Crea el dataset final para entrenamiento"""
import json
import random
from pathlib import Path
import pandas as pd
from tqdm import tqdm

def create_instruction_dataset():
    """Crea dataset en formato instrucción"""
    processed_path = Path("processed")
    processed_path.mkdir(parents=True, exist_ok=True)
    
    # Por ahora, usar los ejemplos de eval como base
    evals_path = Path("contrib/evals")
    all_data = []
    
    for jsonl_file in evals_path.glob("*.jsonl"):
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                all_data.append(data)
    
    # Guardar
    output_file = processed_path / "panama_dataset_v1.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in all_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✓ Dataset creado: {len(all_data)} ejemplos")

if __name__ == "__main__":
    create_instruction_dataset()
