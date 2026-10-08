import os

with open('frontend/src/pages/Dashboard.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Import
if 'TrilhaReforco' not in c:
    c = c.replace("import React, { useEffect, useState } from 'react';", "import React, { useEffect, useState } from 'react';\nimport TrilhaReforco from '../components/chat/TrilhaReforco';")

# 2. State
if 'trilhaAberta' not in c:
    c = c.replace('export default function Dashboard({ papel = \'professor\', navegarPara }) {', 'export default function Dashboard({ papel = \'professor\', navegarPara }) {\n  const [trilhaAberta, setTrilhaAberta] = useState(false);')

# 3. onClick
import re
# We look for the card with "Trilha de Refor"
c = re.sub(
    r"onClick=\{\(\) => navegarPara\('exercicios'\)\}\s*(className=\"bg-white[^>]+>\s*<div className=\"p-3 bg-emerald-50[^>]+>\s*<Target[^>]+>\s*</div>\s*<h4[^>]+>Trilha de Refor)",
    r"onClick={() => setTrilhaAberta(true)}\n          \1",
    c
)

# 4. Render
if '<TrilhaReforco' not in c:
    # replace the very last `</div>\n  );`
    idx = c.rfind('</div>\n  );')
    if idx != -1:
        c = c[:idx] + '  <TrilhaReforco isOpen={trilhaAberta} onClose={() => setTrilhaAberta(false)} />\n    ' + c[idx:]

with open('frontend/src/pages/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(c)

print('Patched successfully!')
