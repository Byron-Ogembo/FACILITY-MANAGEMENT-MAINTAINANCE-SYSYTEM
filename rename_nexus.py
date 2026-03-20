import os

directory = r"c:\Users\Jungle\Desktop\byron22"

for root, dirs, files in os.walk(directory):
    if any(ignore in os.path.normpath(root).split(os.sep) for ignore in ['.git', '__pycache__', 'instance', '.venv', '.gemini']):
        continue
    for file in files:
        if file.endswith(('.html', '.py', '.js', '.json', '.md', '.txt', '.sql')):
            filepath = os.path.join(root, file)
            if file == 'rename_nexus.py': continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                changed = False
                if 'Nexus CMMS' in content:
                    content = content.replace('Nexus CMMS', 'TINDI CMMS')
                    changed = True
                if 'Nexus' in content:
                    content = content.replace('Nexus', 'TINDI')
                    changed = True
                if 'nexus' in content:
                    content = content.replace('nexus', 'tindi')
                    changed = True
                
                # Also fix the space in index.html
                if '"> TINDI CMMS<' in content:
                    content = content.replace('"> TINDI CMMS<', '">TINDI CMMS<')
                    changed = True

                if changed:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {filepath}")
            except Exception as e:
                pass
