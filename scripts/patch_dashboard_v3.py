import os

with open('frontend/src/pages/Dashboard.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

# Just find the exact index of `Trilha de Refor`
idx = c.find('Trilha de Refor')

# Now find the last `onClick={() => navegarPara('exercicios')}` before this index
if idx != -1:
    click_idx = c.rfind("onClick={() => navegarPara('exercicios')}", 0, idx)
    if click_idx != -1:
        # replace just that occurrence
        before = c[:click_idx]
        after = c[click_idx + len("onClick={() => navegarPara('exercicios')} போலீசார்") - 10:] # math is hard, let's just do:
        
        # better approach:
        # we know the block is precisely lines 638-645.
        
        # Let's just find and replace using a very small target near the card.
        part1 = "onClick={() => navegarPara('exercicios')}\n          className=\"bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all space-y-3\"\n        >\n          <div className=\"p-3 bg-emerald-50 text-emerald-600 w-fit rounded-xl font-bold\">\n            <Target size={24} />\n          </div>\n          <h4 className=\"text-lg font-bold text-slate-800\">Trilha de Refor"
        part2 = "onClick={() => setTrilhaAberta(true)}\n          className=\"bg-white p-6 rounded-2xl border border-emerald-200 shadow-sm hover:border-emerald-400 cursor-pointer transition-all space-y-3\"\n        >\n          <div className=\"p-3 bg-emerald-50 text-emerald-600 w-fit rounded-xl font-bold\">\n            <Target size={24} />\n          </div>\n          <h4 className=\"text-lg font-bold text-slate-800\">Trilha de Refor"
        c = c.replace(part1, part2)

with open('frontend/src/pages/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(c)

print('Patched successfully v3')
