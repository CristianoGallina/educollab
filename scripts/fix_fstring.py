with open('backend/app/services.py', 'r', encoding='utf-8') as f:
    content = f.read()
import re
content = re.sub(r'JSON \{"\\"resposta\\": \\"\.\.\.\\"\}"\"\"', 'JSON {{ "resposta": "..." }}"""', content)
with open('backend/app/services.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fix applied")
