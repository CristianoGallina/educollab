import os

with open('backend/app/services.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'JSON {"resposta": "sua resposta em markdown aqui"}',
    'JSON {{"resposta": "sua resposta em markdown aqui"}}'
)

with open('backend/app/services.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
