import os

with open('frontend/src/pages/Dashboard.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, l in enumerate(lines):
    if "onClick={() => navegarPara('exercicios')}" in l and "<Target" in "".join(lines[i:i+8]):
        new_lines.append(l.replace("onClick={() => navegarPara('exercicios')}", "onClick={() => setTrilhaAberta(true)}"))
    else:
        new_lines.append(l)

with open('frontend/src/pages/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
