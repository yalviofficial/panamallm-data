#!/usr/bin/env python3
"""Métricas de calidad para los datos"""
import json
from pathlib import Path
from collections import Counter

def calculate_metrics():
    """Calcula métricas básicas"""
    metrics = {
        'total_documents': 0,
        'total_tokens': 0,
        'sources': Counter()
    }
    
    # Analizar processed/
    processed_path = Path("processed")
    if processed_path.exists():
        for jsonl_file in processed_path.glob("*.jsonl"):
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    metrics['total_documents'] += 1
                    text = data.get('response', '')
                    metrics['total_tokens'] += len(text.split())
                    metrics['sources'][data.get('source', 'unknown')] += 1
    
    print("📊 MÉTRICAS DE CALIDAD")
    print(f"Documentos: {metrics['total_documents']}")
    print(f"Tokens: {metrics['total_tokens']}")
    print(f"Fuentes: {len(metrics['sources'])}")
    
    return metrics

if __name__ == "__main__":
    calculate_metrics()
