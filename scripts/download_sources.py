#!/usr/bin/env python3
"""Descarga fuentes públicas de Panamá"""
import time
import json
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm


class PanamaDataDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PanamaLLM/1.0 (contacto@panamallm.ai)'
        })
        self.delay = 1  # segundos entre peticiones

    def download_file(self, url: str, output_path: Path) -> bool:
        """Descarga un archivo mostrando progreso"""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            return True
        except Exception as e:
            print(f"Error descargando {url}: {e}")
            return False

    def download_gaceta_oficial(self, limit: int = 10):
        """Descarga Gacetas Oficiales recientes"""
        print("Descargando Gacetas Oficiales...")
        base_url = "https://www.gacetaoficial.gob.pa"
        output_dir = Path("raw/gov/gaceta")
        output_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = output_dir / "metadata.json"
        metadata = []
        try:
            print("La Gaceta Oficial requiere un scraper específico")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error accediendo a Gaceta Oficial: {e}")

    def download_datos_abiertos(self):
        """Descarga datasets del portal de Datos Abiertos"""
        print("Descargando datasets del portal de Datos Abiertos...")
        base_url = "https://www.datosabiertos.gob.pa"
        output_dir = Path("raw/gov/datos_abiertos")
        output_dir.mkdir(parents=True, exist_ok=True)
        datasets = [
            {
                'name': 'estadisticas_educacion',
                'url': f'{base_url}/dataset/example1.csv',
                'description': 'Estadísticas de educación'
            },
            {
                'name': 'datos_salud_publica',
                'url': f'{base_url}/dataset/example2.csv',
                'description': 'Datos de salud pública'
            }
        ]
        for dataset in datasets:
            output_file = output_dir / f"{dataset['name']}.csv"
            if output_file.exists():
                print(f"Ya existe: {output_file.name}")
                continue
            print(f"Descargando: {dataset['description']}")
            print(f"URL real necesario para: {dataset['name']}")
            time.sleep(self.delay)

    def download_acp_documents(self):
        """Descarga documentos públicos del Canal de Panamá"""
        print("Descargando documentos de la ACP...")
        output_dir = Path("raw/corp/acp")
        output_dir.mkdir(parents=True, exist_ok=True)
        documents = [
            {
                'name': 'informe_anual_2023',
                'url': 'https://pancanal.com/informes/2023.pdf',
                'type': 'informe'
            }
        ]
        for doc in documents:
            output_file = output_dir / f"{doc['name']}.pdf"
            if output_file.exists():
                print(f"Ya existe: {output_file.name}")
                continue
            print(f"Descargando: {doc['name']}")
            print(f"Verificar URL real para: {doc['name']}")
            time.sleep(self.delay)

    def download_sample_data(self):
        """Crea datos de ejemplo para desarrollo"""
        print("Creando datos de ejemplo...")
        sample_dir = Path("raw/docs/samples")
        sample_dir.mkdir(parents=True, exist_ok=True)
        sample_data = {
            "title": "Muestra de Documento Panameño",
            "content": (
                "Este es un documento de ejemplo para el desarrollo de PanamaLLM. "
                "Incluye información sobre la historia de Panamá, su cultura "
                "y el Canal de Panamá."
            ),
            "metadata": {
                "source": "Generado para desarrollo",
                "license": "CC0",
                "date": "2024-01-01"
            }
        }
        sample_file = sample_dir / "sample_document.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        print(f"Creado archivo de ejemplo: {sample_file}")


def main():
    print("PanamaLLM Data Downloader")
    print("=" * 40)
    downloader = PanamaDataDownloader()
    downloader.download_sample_data()
    # Descomentar cuando haya URLs reales:
    # downloader.download_gaceta_oficial(limit=5)
    # downloader.download_datos_abiertos()
    # downloader.download_acp_documents()
    print("Descarga completada")


if __name__ == "__main__":
    main()
