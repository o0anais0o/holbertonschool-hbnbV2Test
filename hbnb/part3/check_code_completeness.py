import os

def is_code_complete(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines()]
        # Ignore empty lines and comments
        code_lines = [l for l in lines if l and not l.startswith('#')]
        return len(code_lines) >= 3

project_dir = 'app'  # ou 'hbnb' selon ton arborescence

for root, dirs, files in os.walk(project_dir):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            if not is_code_complete(path):
                print(f"⚠️  Fichier incomplet ou vide : {path}")
