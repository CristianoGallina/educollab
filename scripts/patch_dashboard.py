import os

with open('frontend/src/pages/Dashboard.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

if 'TrilhaReforco' not in c:
    c = c.replace("import TutorChat from '../components/chat/TutorChat';", "import TutorChat from '../components/chat/TutorChat';\nimport TrilhaReforco from '../components/chat/TrilhaReforco';")

if 'trilhaAberta' not in c:
    c = c.replace('const [tutorAberto, setTutorAberto] = useState(false);', 'const [tutorAberto, setTutorAberto] = useState(false);\n  const [trilhaAberta, setTrilhaAberta] = useState(false);')

# We'll just regex replace the onClick handler of the target card.
import re
# The card has `<Target size={24} />` inside it, and we want to change its onClick.
# Let's find "Trilha de Refor"
idx = c.find('Trilha de Refor')
if idx != -1:
    # Find the nearest onClick backwards from idx
    onClick_idx = c.rfind('onClick={() => navegarPara(', 0, idx)
    if onClick_idx != -1:
        # Replace navigating to exercicios with setTrilhaAberta(true)
        # But wait, it might be the Avaliacoes card!
        # The Avalanche card is earlier. 
        # Let's just be explicit:
        c = re.sub(r'onClick=\{\(\) => navegarPara\(\'exercicios\'\)\}([^<]*?)className=\"bg-white([^<]*?)<Target', r'onClick={() => setTrilhaAberta(true)}\1className="bg-white\2<Target', c)

if '<TrilhaReforco ' not in c:
    c = c.replace('</Layout>', '  <TrilhaReforco isOpen={trilhaAberta} onClose={() => setTrilhaAberta(false)} />\n    </Layout>')

with open('frontend/src/pages/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(c)

print('Dashboard patched')
