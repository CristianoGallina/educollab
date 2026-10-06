import re

with open('frontend/src/components/MinhasTurmas.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add cadastrarProfessor function
cad_prof_func = '''
  const cadastrarProfessor = async (turmaId) => {
    const emailProfessor = prompt("Digite o e-mail do professor para adicioná-lo a esta turma:");
    if (!emailProfessor) return;
    setLoading(true);
    setMensagem('');
    setErro('');
    try {
      const response = await apiFetch(`${API_BASE}/professor/turma/${turmaId}/professores`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'professor' },
        body: JSON.stringify({ email: emailProfessor }),
      });
      const data = await response.json();
      if (!response.ok) {
        setErro(data.detail || 'Não foi possível adicionar o professor.');
        return;
      }
      setMensagem(data.mensagem || 'Professor adicionado à turma.');
      await carregarTurmas();
    } catch (error) {
      console.error('Erro ao adicionar professor:', error);
      setErro('Falha de conexão.');
    } finally {
      setLoading(false);
    }
  };
'''

if 'const cadastrarProfessor = async' not in content:
    content = content.replace('const cadastrarAluno = async', cad_prof_func + '\n  const cadastrarAluno = async')

# Add button
btn_code = '''<button type="button" onClick={() => cadastrarProfessor(turma.id)} disabled={loading} className="md:col-span-2 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2.5 rounded-lg text-sm font-medium disabled:opacity-60 transition-colors">
                        <Users size={16} />
                        Adicionar Professor
                      </button>'''

if 'cadastrarProfessor(turma.id)' not in content:
    content = content.replace(
        '<button type="button" onClick={() => cadastrarAluno(turma.id)}',
        btn_code + '\n                      <button type="button" onClick={() => cadastrarAluno(turma.id)}'
    )

with open('frontend/src/components/MinhasTurmas.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("MinhasTurmas atualizado.")
