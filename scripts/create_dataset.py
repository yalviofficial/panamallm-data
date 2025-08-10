#!/usr/bin/env python3
"""Crea el dataset final para entrenamiento del modelo"""
import json
import random
from pathlib import Path
from typing import List, Dict
import pandas as pd
from tqdm import tqdm

def load_interim_data() -> List[Dict]:
    """Carga todos los datos intermedios"""
    all_data = []
    interim_path = Path("interim")
    
    for parquet_file in interim_path.rglob("*.parquet"):
        try:
            df = pd.read_parquet(parquet_file)
            records = df.to_dict('records')
            all_data.extend(records)
            print(f"✓ Cargado: {parquet_file.name} ({len(records)} registros)")
        except Exception as e:
            print(f"✗ Error cargando {parquet_file}: {e}")
    
    return all_data

def create_instruction_dataset(data: List[Dict]) -> List[Dict]:
    """Convierte datos raw en formato instrucción para fine-tuning"""
    instruction_data = []
    
    for item in tqdm(data, desc="Creando dataset de instrucciones"):
        text = item.get('text', '').strip()
        if not text:
            continue
        
        # Dividir texto largo en chunks
        chunks = [text[i:i+2000] for i in range(0, len(text), 1500)]
        
        for chunk in chunks:
            # Formato para fine-tuning estilo Alpaca
            instruction_item = {
                "instruction": "Resume el siguiente texto oficial de Panamá:",
                "input": chunk[:1000],
                "output": chunk[1000:1500] if len(chunk) > 1000 else chunk,
                "source": item.get('source', 'unknown'),
                "type": item.get('type', 'document')
            }
            instruction_data.append(instruction_item)
    
    return instruction_data

def create_qa_pairs() -> List[Dict]:
    """Crea pares pregunta-respuesta del conocimiento base"""
    qa_pairs = []
    
    # Cargar evaluaciones existentes
    evals_path = Path("contrib/evals")
    for jsonl_file in evals_path.glob("*.jsonl"):
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    qa = json.loads(line)
                    qa_pairs.append({
                        "instruction": qa.get("prompt", ""),
                        "input": "",
                        "output": qa.get("response", ""),
                        "source": qa.get("source", ""),
                        "type": "qa"
                    })
                except:
                    continue
    
    return qa_pairs

def split_dataset(data: List[Dict], train_ratio: float = 0.8, val_ratio: float = 0.1):
    """Divide el dataset en train/val/test"""
    random.shuffle(data)
    
    total = len(data)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)
    
    splits = {
        'train': data[:train_size],
        'validation': data[train_size:train_size + val_size],
        'test': data[train_size + val_size:]
    }
    
    return splits

def save_datasets(splits: Dict[str, List[Dict]]):
    """Guarda los datasets en formato JSONL"""
    processed_path = Path("processed")
    processed_path.mkdir(parents=True, exist_ok=True)
    
    for split_name, data in splits.items():
        output_file = processed_path / f"panama_{split_name}.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"✓ Guardado: {output_file.name} ({len(data)} ejemplos)")
    
    # Crear versión completa
    all_data = []
    for data in splits.values():
        all_data.extend(data)
    
    full_file = processed_path / "panama_full_dataset.jsonl"
    with open(full_file, 'w', encoding='utf-8') as f:
        for item in all_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✓ Dataset completo: {full_file.name} ({len(all_data)} ejemplos)")

def main():
    print("🚀 Creando dataset PanamaLLM...")
    
    # Cargar datos intermedios
    interim_data = load_interim_data()
    
    # Crear dataset de instrucciones
    instruction_data = create_instruction_dataset(interim_data)
    
    # Agregar QA pairs
    qa_data = create_qa_pairs()
    
    # Combinar todos los datos
    all_data = instruction_data + qa_data
    print(f"📊 Total de ejemplos: {len(all_data)}")
    
    # Dividir en train/val/test
    splits = split_dataset(all_data)
    
    # Guardar datasets
    save_datasets(splits)
    
    print("✅ Dataset creado exitosamente!")

if __name__ == "__main__":
    main()
