#!/usr/bin/env python3
import os


dirs = ['raw/gov', 'raw/docs', 'raw/corp', 'interim', 'processed', 'meta']
for d in dirs:
    os.makedirs(d, exist_ok=True)
    open(f'{d}/.gitkeep', 'a').close()
print("\u2713 Estructura de carpetas creada")
