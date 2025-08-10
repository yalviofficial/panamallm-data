#!/usr/bin/env python3
"""Pipeline para procesar raw → interim"""
import os
import json
import re
from pathlib import Path
from typing import Dict, List
import pandas as pd
from tqdm import tqdm
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import requests

def clean_text(text: str) -> str:
    """Limpia y normaliza texto"""
    # Eliminar caracteres extraños
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    text = text.strip()
    return text

def extract_metadata_from_filename(filename: str) -> Dict:
    """Extrae metadata del nombre del archivo"""
    metadata = {
        'original_filename': filename,
        'year': None,
        'type': 'unknown'
    }
    
    # Buscar año (formato YYYY)
    year_match = re.search(r'(19|20)\d{2}', filename)
    if year_match:
        metadata['year'] = int(year_match.group())
    
    # Detectar tipo por keywords
    filename_lower = filename.lower()
    if 'gaceta' in filename_lower:
        metadata['type'] = 'gaceta_oficial'
    elif 'ley' in filename_lower or 'decreto' in filename_lower:
        metadata['type'] = 'legislacion'
    elif 'resolucion' in filename_lower:
        metadata['type'] = 'resolucion'
    
    return metadata

def process_pdf_file(pdf_path: Path) -> Dict:
    """Procesa un archivo PDF"""
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                full_text += f"\n--- Página {page_num} ---\n"
                full_text += page_text
        
        cleaned_text = clean_text(full_text)
        metadata = extract_metadata_from_filename(pdf_path.name)
        
        return {
            'text': cleaned_text,
            'source': pdf_path.name,
            'format': 'pdf',
            'pages': len(reader.pages),
            **metadata
        }
    except Exception as e:
        print(f"Error procesando PDF {pdf_path}: {e}")
        return None

def process_html_file(html_path: Path) -> Dict:
    """Procesa un archivo HTML"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Eliminar scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        cleaned_text = clean_text(text)
        metadata = extract_metadata_from_filename(html_path.name)
        
        return {
            'text': cleaned_text,
            'source': html_path.name,
            'format': 'html',
            **metadata
        }
    except Exception as e:
        print(f"Error procesando HTML {html_path}: {e}")
        return None

def process_csv_file(csv_path: Path) -> List[Dict]:
    """Procesa un archivo CSV"""
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        records = []
        
        for idx, row in df.iterrows():
            # Concatenar todas las columnas como texto
            text_parts = []
            for col in df.columns:
                if pd.notna(row[col]):
                    text_parts.append(f"{col}: {row[col]}")
            
            text = " | ".join(text_parts)
            cleaned_text = clean_text(text)
            
            if cleaned_text:
                metadata = extract_metadata_from_filename(csv_path.name)
                records.append({
                    'text': cleaned_text,
                    'source': csv_path.name,
                    'format': 'csv',
                    'row_index': idx,
                    **metadata
                })
        
        return records
    except Exception as e:
        print(f"Error procesando CSV {csv_path}: {e}")
        return []

def process_directory(input_dir: Path, output_dir: Path):
    """Procesa todos los archivos en un directorio"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_records = []
    
    # Procesar PDFs
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"Procesando {len(pdf_files)} archivos PDF...")
    for pdf_path in tqdm(pdf_files):
        result = process_pdf_file(pdf_path)
        if result:
            all_records.append(result)
    
    # Procesar HTMLs
    html_files = list(input_dir.glob("*.html")) + list(input_dir.glob("*.htm"))
    print(f"Procesando {len(html_files)} archivos HTML...")
    for html_path in tqdm(html_files):
        result = process_html_file(html_path)
        if result:
            all_records.append(result)
    
    # Procesar CSVs
    csv_files = list(input_dir.glob("*.csv"))
    print(f"Procesando {len(csv_files)} archivos CSV...")
    for csv_path in tqdm(csv_files):
        results = process_csv_file(csv_path)
        all_records.extend(results)
    
    # Guardar como parquet
    if all_records:
        df = pd.DataFrame(all_records)
        output_file = output_dir / f"{input_dir.name}_processed.parquet"
        df.to_parquet(output_file, engine='pyarrow')
        print(f"Guardado: {output_file} ({len(all_records)} registros)")
    
    return all_records

def main():
    """Pipeline principal"""
    print("Iniciando procesamiento de datos raw...")
    
    raw_dirs = {
        'gov': Path('raw/gov'),
        'docs': Path('raw/docs'),
        'corp': Path('raw/corp')
    }
    
    total_processed = 0
    
    for category, raw_path in raw_dirs.items():
        if raw_path.exists() and any(raw_path.iterdir()):
            print(f"\nProcesando categoría: {category}")
            interim_path = Path('interim') / category
            records = process_directory(raw_path, interim_path)
            total_processed += len(records)
        else:
            print(f"Directorio vacío o no existe: {raw_path}")
    
    print(f"\nProcesamiento completado: {total_processed} documentos procesados")

if __name__ == "__main__":
    main()
