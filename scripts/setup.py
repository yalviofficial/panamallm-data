#!/usr/bin/env python3
import os


dirs = ['raw/gov', 'raw/docs', 'raw/corp', 'interim', 'processed', 'meta']
for d in dirs:
    os.makedirs(d, exist_ok=True)
    with open(f'{d}/README.md', 'w') as f:
        f.write(f'# {d}\nCarpeta para {d.split("/")[-1]}\n')
print("\u2713 Estructura de carpetas creada")
