import os

with open('frontend/src/components/FerramentasIA.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'const [quantidadeQuestoes, setQuantidadeQuestoes] = useState(4);', 
    'const [quantidadeQuestoes, setQuantidadeQuestoes] = useState(4);\n  const [nivelQuiz, setNivelQuiz] = useState(\'Básico\');'
)

content = content.replace("nivel: 'Básico',", "nivel: nivelQuiz,")
content = content.replace('grid-cols-1 md:grid-cols-3 gap-4', 'grid-cols-1 md:grid-cols-4 gap-4')

search_block = '''                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Tema da Aula</label>'''

replace_block = '''                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Nível</label>
                  <select
                    value={nivelQuiz}
                    onChange={(e) => setNivelQuiz(e.target.value)}
                    className="w-full border p-2.5 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  >
                    <option value="Fácil">Fácil</option>
                    <option value="Básico">Básico</option>
                    <option value="Médio">Médio</option>
                    <option value="Difícil">Difícil</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Tema da Aula</label>'''

content = content.replace(search_block, replace_block)

with open('frontend/src/components/FerramentasIA.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("done frontend")
