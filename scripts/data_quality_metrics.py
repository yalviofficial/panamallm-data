#!/usr/bin/env python3
"""Métricas de calidad para los datos de PanamaLLM"""
import json
import yaml
from pathlib import Path
from collections import Counter
from typing import Dict, List
import pandas as pd
from datetime import datetime

class DataQualityAnalyzer:
    def __init__(self):
        self.metrics = {
            'total_documents': 0,
            'total_tokens': 0,
            'total_characters': 0,
            'unique_sources': set(),
            'coverage_by_category': Counter(),
            'license_distribution': Counter(),
            'file_format_distribution': Counter(),
            'year_distribution': Counter(),
            'quality_scores': [],
            'missing_metadata': []
        }
    
    def analyze_processed_data(self):
        """Analiza datos procesados en formato JSONL"""
        processed_path = Path("processed")
        
        for jsonl_file in processed_path.glob("*.jsonl"):
            print(f"📄 Analizando: {jsonl_file.name}")
            
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        self.analyze_document(data)
                    except json.JSONDecodeError as e:
                        print(f"  ✗ Error en línea {line_num}: {e}")
    
    def analyze_document(self, doc: Dict):
        """Analiza un documento individual"""
        self.metrics['total_documents'] += 1
        
        # Análisis de texto
        text = doc.get('text', '') or doc.get('output', '') or doc.get('response', '')
        if text:
            tokens = text.split()
            self.metrics['total_tokens'] += len(tokens)
            self.metrics['total_characters'] += len(text)
        
        # Fuente
        source = doc.get('source', 'unknown')
        self.metrics['unique_sources'].add(source)
        
        # Categoría/Tipo
        doc_type = doc.get('type', 'unknown')
        self.metrics['coverage_by_category'][doc_type] += 1
        
        # Calidad del documento
        quality_score = self.calculate_quality_score(doc)
        self.metrics['quality_scores'].append(quality_score)
    
    def calculate_quality_score(self, doc: Dict) -> float:
        """Calcula un score de calidad para el documento (0-1)"""
        score = 0.0
        checks = 0
        
        # Tiene texto significativo
        text = doc.get('text', '') or doc.get('output', '')
        if text and len(text) > 100:
            score += 1
        checks += 1
        
        # Tiene fuente identificada
        if doc.get('source') and doc.get('source') != 'unknown':
            score += 1
        checks += 1
        
        # Tiene tipo/categoría
        if doc.get('type') and doc.get('type') != 'unknown':
            score += 1
        checks += 1
        
        # Tiene metadata adicional
        if any(key in doc for key in ['year', 'date', 'metadata']):
            score += 1
        checks += 1
        
        return score / checks if checks > 0 else 0
    
    def analyze_contrib_datasets(self):
        """Analiza datasets contribuidos"""
        contrib_path = Path("contrib/datasets")
        
        for dataset_dir in contrib_path.iterdir():
            if dataset_dir.is_dir():
                # Buscar source.yaml
                source_yaml = dataset_dir / "source.yaml"
                if source_yaml.exists():
                    with open(source_yaml, 'r', encoding='utf-8') as f:
                        meta = yaml.safe_load(f)
                        self.analyze_dataset_metadata(meta, dataset_dir.name)
    
    def analyze_dataset_metadata(self, meta: Dict, dataset_name: str):
        """Analiza metadata de un dataset"""
        # Distribución de licencias
        license_type = meta.get('license', 'unknown')
        self.metrics['license_distribution'][license_type] += 1
        
        # Verificar campos requeridos
        required_fields = ['name', 'url', 'license', 'owner']
        missing = [field for field in required_fields if field not in meta]
        
        if missing:
            self.metrics['missing_metadata'].append({
                'dataset': dataset_name,
                'missing_fields': missing
            })
    
    def analyze_raw_data(self):
        """Analiza datos crudos"""
        raw_path = Path("raw")
        
        for file_path in raw_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                suffix = file_path.suffix.lower()
                self.metrics['file_format_distribution'][suffix] += 1
    
    def generate_report(self) -> Dict:
        """Genera reporte completo de métricas"""
        # Calcular estadísticas
        avg_tokens = (self.metrics['total_tokens'] / 
                     self.metrics['total_documents'] 
                     if self.metrics['total_documents'] > 0 else 0)
        
        avg_quality = (sum(self.metrics['quality_scores']) / 
                      len(self.metrics['quality_scores']) 
                      if self.metrics['quality_scores'] else 0)
        
        report = {
            'summary': {
                'total_documents': self.metrics['total_documents'],
                'total_tokens': self.metrics['total_tokens'],
                'total_characters': self.metrics['total_characters'],
                'unique_sources': len(self.metrics['unique_sources']),
                'average_tokens_per_doc': round(avg_tokens, 2),
                'average_quality_score': round(avg_quality, 3)
            },
            'distributions': {
                'categories': dict(self.metrics['coverage_by_category']),
                'licenses': dict(self.metrics['license_distribution']),
                'file_formats': dict(self.metrics['file_format_distribution'])
            },
            'quality': {
                'average_score': round(avg_quality, 3),
                'documents_above_0.8': sum(1 for s in self.metrics['quality_scores'] if s > 0.8),
                'documents_below_0.5': sum(1 for s in self.metrics['quality_scores'] if s < 0.5)
            },
            'issues': {
                'datasets_with_missing_metadata': self.metrics['missing_metadata']
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Imprime el reporte de forma legible"""
        print("\n" + "="*60)
        print("📊 REPORTE DE CALIDAD - PanamaLLM Dataset")
        print("="*60)
        
        print("\n📈 RESUMEN GENERAL:")
        for key, value in report['summary'].items():
            print(f"  • {key.replace('_', ' ').title()}: {value:,}")
        
        print("\n📊 DISTRIBUCIONES:")
        for dist_name, dist_data in report['distributions'].items():
            print(f"\n  {dist_name.upper()}:")
            for item, count in sorted(dist_data.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {item}: {count}")
        
        print("\n⭐ CALIDAD:")
        for key, value in report['quality'].items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        if report['issues']['datasets_with_missing_metadata']:
            print("\n⚠️ PROBLEMAS DETECTADOS:")
            for issue in report['issues']['datasets_with_missing_metadata']:
                print(f"  • {issue['dataset']}: Faltan {', '.join(issue['missing_fields'])}")
        
        print("\n" + "="*60)

def main():
    """Función principal"""
    analyzer = DataQualityAnalyzer()
    
    print("🔍 Iniciando análisis de calidad de datos...")
    
    # Analizar diferentes fuentes
    analyzer.analyze_raw_data()
    analyzer.analyze_contrib_datasets()
    analyzer.analyze_processed_data()
    
    # Generar y mostrar reporte
    report = analyzer.generate_report()
    analyzer.print_report(report)
    
    # Guardar reporte en JSON
    report_file = Path("meta/quality_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Reporte guardado en: {report_file}")

if __name__ == "__main__":
    main()
