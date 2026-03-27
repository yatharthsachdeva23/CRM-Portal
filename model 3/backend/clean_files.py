import os

def clean_file(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove non-ascii characters
    clean_content = "".join([c for c in content if ord(c) < 128])
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    print(f"Cleaned {path}")

clean_file(r"c:\Desktop\Antigravity Projects\India_Innovates\model 3\backend\app\main.py")
clean_file(r"c:\Desktop\Antigravity Projects\India_Innovates\model 3\backend\app\services\ai_service.py")
clean_file(r"c:\Desktop\Antigravity Projects\India_Innovates\model 3\backend\seed_data.py")
