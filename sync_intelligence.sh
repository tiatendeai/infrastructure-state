#!/bin/bash
# Script de Ativação Manual do Terreno (Bypass CLI)
# Este script executa a lógica interna do Graphify que o CLI está escondendo.

GRAPHIFY_PYTHON=$(python3 -c "import sys; print(sys.executable)")

echo "🧠 J.A.R.V.I.S.: Iniciando Síntese do Terreno..."

$GRAPHIFY_PYTHON -c "
import json, os
from pathlib import Path
from graphify.detect import detect
from graphify.extract import extract
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.export import to_json, to_obsidian, to_canvas

# 1. Configuração de Caminhos (Mapeamento Global)
print('📡 Iniciando Varredura Global de /dev/...')
root_path = '/Users/diego/dev/'
obsidian_dir = Path('/Users/diego/Documents/Obsidian Vault/Graphify')

# Padrões de exclusão - IMPORTANTÍSSIMO PARA PERFORMANCE
ignore_dirs = {
    'node_modules', '.git', 'venv', '.venv', 'dist', 'build', 
    '.cache', '.next', '__pycache__', '.obsidian', 'bower_components',
    'target', 'bin', 'obj'
}

# 2. Coleta Ultra-Rápida (Poda de árvore na origem)
print('📂 Coletando arquivos (Modo Turbo - Ignorando Ruido)...')
files = []
for root, dirs, filenames in os.walk(root_path):
    # Poda os diretórios para que o os.walk nem entre neles
    dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
    
    for f in filenames:
        # A biblioteca exige objetos Path, não apenas strings
        if f.endswith(('.js', '.ts', '.py', '.go', '.java', '.c', '.cpp', '.rs', '.md')):
            files.append(Path(root) / f)

print(f'📂 Coletados {len(files)} arquivos relevantes de código.')

# Garante que as pastas de saída existam
os.makedirs('graphify-out', exist_ok=True)
os.makedirs(obsidian_dir, exist_ok=True)

# 3. Execução da Inteligência
print('📂 Extraindo estrutura (AST)...')
extraction = extract(files)

print('🕸️ Construindo rede neural...')
G = build_from_json(extraction)
communities = cluster(G)
cohesion = score_all(G, communities)

# 4. Exportar para Obsidian
print('🎨 Injetando no Obsidian...')
to_obsidian(G, communities, obsidian_dir, cohesion=cohesion)
to_canvas(G, communities, obsidian_dir / 'graph.canvas')
to_json(G, communities, 'graphify-out/graph.json')

print('✅ Terreno Mapeado com Sucesso!')
"
