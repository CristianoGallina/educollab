import { API_BASE, apiFetch } from '../api';
import React, { useEffect, useState } from 'react';
import { Plus, LogIn, UserPlus, BookOpen, Users } from 'lucide-react';


const turmaVazia = { nome: '', ano: '', codigo: '' };
const alunoVazio = { nome: '', email: '' };

export default function MinhasTurmas({ papel, onAcessarTurma }) {
  const [turmas, setTurmas] = useState([]);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [formTurma, setFormTurma] = useState(turmaVazia);
  const [disciplinasNovaTurma, setDisciplinasNovaTurma] = useState([]);
  const [disciplinaDigitada, setDisciplinaDigitada] = useState('');
  const [alunoPorTurma, setAlunoPorTurma] = useState({});
  const [disciplinaPorTurma, setDisciplinaPorTurma] = useState({});
  const [codigoTurmaAluno, setCodigoTurmaAluno] = useState('');
  const [nomeAlunoDigitado, setNomeAlunoDigitado] = useState('');
  const [loading, setLoading] = useState(false);
  const [mensagem, setMensagem] = useState('');
  const [erro, setErro] = useState('');

  const usuarioStorage = JSON.parse(localStorage.getItem('usuario') || '{}');
  const emailAlunoAtual = usuarioStorage.email;

  const carregarTurmas = async () => {
    try {
      if (papel === 'aluno') {
        const response = await apiFetch(`${API_BASE}/aluno/turmas?email_aluno=${emailAlunoAtual}`, {
          headers: { 'x-tipo-usuario': 'aluno' },
        });
        const data = await response.json();
        const lista = Array.isArray(data?.turmas) ? data.turmas : [];
        setTurmas(lista);
      } else {
        const response = await apiFetch(`${API_BASE}/professor/dashboard`, {
          headers: { 'x-tipo-usuario': 'professor' },
        });
        const data = await response.json();
        const lista = Array.isArray(data?.turmas) ? data.turmas : [];
        setTurmas(lista);
      }
    } catch (error) {
      console.error('Erro ao carregar turmas:', error);
      setTurmas([]);
    }
  };

  useEffect(() => {
    carregarTurmas();
  }, [papel]);

  const entrarComCodigo = async () => {
    if (!codigoTurmaAluno.trim()) {
      setErro('Por favor, informe o código da turma.');
      return;
    }

    setLoading(true);
    setErro('');
    setMensagem('');
    try {
      const response = await apiFetch(`${API_BASE}/aluno/entrar-turma`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'aluno',
        },
        body: JSON.stringify({
          codigo: codigoTurmaAluno.trim().toUpperCase(),
          email_aluno: emailAlunoAtual,
          nome_aluno: nomeAlunoDigitado.trim() || 'Estudante Demo',
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        setErro(data.detail || 'Não foi possível entrar na turma com este código.');
        return;
      }

      setMensagem(data.mensagem || 'Você ingressou na turma com sucesso!');
      setCodigoTurmaAluno('');
      setNomeAlunoDigitado('');
      setMostrarFormulario(false);
      await carregarTurmas();
    } catch (error) {
      console.error('Erro ao entrar na turma com código:', error);
      setErro('Erro de conexão ao tentar ingressar na turma.');
    } finally {
      setLoading(false);
    }
  };

  const adicionarDisciplinaNaLista = (nome, listaAtual, setLista) => {
    const valor = String(nome || '').trim();
    if (!valor) return;
    const jaExiste = listaAtual.some((item) => item.toLowerCase() === valor.toLowerCase());
    if (jaExiste) return;
    setLista([...listaAtual, valor]);
  };

  const criarTurma = async () => {
    if (!formTurma.nome.trim()) return;

    setLoading(true);
    setErro('');
    try {
      const response = await apiFetch(`${API_BASE}/professor/criar-turma`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'professor',
        },
        body: JSON.stringify({
          nome: formTurma.nome,
          ano: formTurma.ano || 'Ensino Fundamental',
          codigo: formTurma.codigo || `${formTurma.nome.slice(0, 3).toUpperCase()}${Math.floor(Math.random() * 90 + 10)}`,
          cor: 'bg-violet-500',
          disciplinas: disciplinasNovaTurma,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        setErro(data.detail || 'Não foi possível criar a turma.');
        return;
      }

      setMensagem(data.mensagem || 'Turma criada com sucesso.');
      setFormTurma(turmaVazia);
      setDisciplinasNovaTurma([]);
      setDisciplinaDigitada('');
      setMostrarFormulario(false);
      await carregarTurmas();
    } catch (error) {
      console.error('Erro ao criar turma:', error);
      setErro('Não foi possível criar a turma.');
    } finally {
      setLoading(false);
    }
  };

  
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

  const cadastrarAluno = async (turmaId) => {
    const aluno = alunoPorTurma[turmaId] || alunoVazio;
    if (!aluno.nome.trim() || !aluno.email.trim()) {
      setErro('Informe nome e e-mail do aluno.');
      return;
    }

    setLoading(true);
    setErro('');
    try {
      const response = await apiFetch(`${API_BASE}/professor/alunos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'professor',
        },
        body: JSON.stringify({
          nome: aluno.nome,
          email: aluno.email,
          turma_id: Number(turmaId),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setErro(data.detail || 'Não foi possível cadastrar o aluno.');
        return;
      }
      const msg = data.senha_provisoria ? `${data.mensagem || 'Sucesso.'} Senha provisória: ${data.senha_provisoria}` : data.mensagem;
      setMensagem(msg || 'Aluno cadastrado na turma.');
      setAlunoPorTurma((atual) => ({ ...atual, [turmaId]: alunoVazio }));
      await carregarTurmas();
    } catch (error) {
      console.error('Erro ao cadastrar aluno:', error);
      setErro('Não foi possível cadastrar o aluno.');
    } finally {
      setLoading(false);
    }
  };

  const cadastrarDisciplina = async (turmaId) => {
    const nome = String(disciplinaPorTurma[turmaId] || '').trim();
    if (!nome) {
      setErro('Informe o nome da disciplina.');
      return;
    }

    setLoading(true);
    setErro('');
    try {
      const response = await apiFetch(`${API_BASE}/professor/turma/${turmaId}/disciplinas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'professor',
        },
        body: JSON.stringify({ nome }),
      });
      const data = await response.json();
      if (!response.ok) {
        setErro(data.detail || 'Não foi possível adicionar a disciplina.');
        return;
      }
      setMensagem(data.mensagem || 'Disciplina adicionada à turma.');
      setDisciplinaPorTurma((atual) => ({ ...atual, [turmaId]: '' }));
      await carregarTurmas();
    } catch (error) {
      console.error('Erro ao cadastrar disciplina:', error);
      setErro('Não foi possível adicionar a disciplina.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-slate-800">
            {papel === 'administrador' ? 'Turmas da Rede' : 'Minhas Turmas'}
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            {papel === 'aluno'
              ? 'Acesse os exercícios e acompanhe as atividades preparadas para suas turmas.'
              : papel === 'administrador'
              ? 'Visão institucional de todas as turmas cadastradas na rede escolar.'
              : 'Cada turma pode ter várias disciplinas. Cadastre alunos ou compartilhe o código da turma.'}
          </p>
        </div>
        {papel !== 'administrador' && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              setMostrarFormulario((valor) => !valor);
            }}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium transition-colors shadow-sm cursor-pointer"
          >
            {papel === 'professor' ? <Plus size={18} /> : <LogIn size={18} />}
            <span>{papel === 'professor' ? 'Criar Turma' : 'Entrar com Código'}</span>
          </button>
        )}
      </div>

      {mensagem && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl p-4 font-medium">{mensagem}</div>
      )}
      {erro && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-xl p-4 font-medium">{String(erro)}</div>
      )}

      {/* Formulário para o Aluno entrar com código */}
      {papel === 'aluno' && mostrarFormulario && (
        <div className="bg-white p-6 rounded-2xl border border-blue-200 shadow-md space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-lg font-bold text-slate-800">Entrar em uma Turma com Código</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Digite o código da turma fornecido pelo seu professor (ex: DISC7A ou 7A2026).
              </p>
            </div>
            <button
              type="button"
              onClick={() => setMostrarFormulario(false)}
              className="text-slate-400 hover:text-slate-600 text-xs font-semibold px-2 py-1 rounded-lg hover:bg-slate-100 transition-colors"
            >
              ✕ Fechar
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Código da Turma <span className="text-red-500">*</span>
              </label>
              <input
                value={codigoTurmaAluno}
                onChange={(e) => setCodigoTurmaAluno(e.target.value.toUpperCase())}
                className="w-full border border-slate-300 rounded-xl p-3 text-base font-mono font-bold uppercase tracking-wider text-blue-700 outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50 focus:bg-white"
                placeholder="Ex.: DISC7A"
                maxLength={12}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Seu Nome de Aluno</label>
              <input
                value={nomeAlunoDigitado}
                onChange={(e) => setNomeAlunoDigitado(e.target.value)}
                className="w-full border border-slate-300 rounded-xl p-3 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex.: Cristiano Santos"
              />
            </div>
          </div>

          <div className="flex items-center space-x-3 pt-2">
            <button
              type="button"
              onClick={entrarComCodigo}
              disabled={loading || !codigoTurmaAluno.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2.5 rounded-xl text-sm transition-colors disabled:opacity-50 cursor-pointer shadow-sm"
            >
              {loading ? 'Entrando na turma...' : 'Ingressar na Turma'}
            </button>
            <button
              type="button"
              onClick={() => setMostrarFormulario(false)}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold px-4 py-2.5 rounded-xl text-sm transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {papel === 'professor' && mostrarFormulario && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nome da turma</label>
            <input value={formTurma.nome} onChange={(e) => setFormTurma({ ...formTurma, nome: e.target.value })} className="w-full border rounded-lg p-3 outline-none focus:ring-1 focus:ring-blue-500" placeholder="Ex.: 7º Ano A" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Ano / Série</label>
            <input value={formTurma.ano} onChange={(e) => setFormTurma({ ...formTurma, ano: e.target.value })} className="w-full border rounded-lg p-3 outline-none focus:ring-1 focus:ring-blue-500" placeholder="Ex.: 7º Ano" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Código</label>
            <input value={formTurma.codigo} onChange={(e) => setFormTurma({ ...formTurma, codigo: e.target.value })} className="w-full border rounded-lg p-3 outline-none focus:ring-1 focus:ring-blue-500" placeholder="Ex.: 7A2026" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Disciplinas da turma</label>
            <div className="flex gap-2">
              <input
                value={disciplinaDigitada}
                onChange={(e) => setDisciplinaDigitada(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    adicionarDisciplinaNaLista(disciplinaDigitada, disciplinasNovaTurma, setDisciplinasNovaTurma);
                    setDisciplinaDigitada('');
                  }
                }}
                className="flex-1 border rounded-lg p-3 outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="Ex.: Matemática"
              />
              <button
                type="button"
                onClick={() => {
                  adicionarDisciplinaNaLista(disciplinaDigitada, disciplinasNovaTurma, setDisciplinasNovaTurma);
                  setDisciplinaDigitada('');
                }}
                className="bg-slate-100 text-slate-800 px-4 py-2 rounded-lg font-medium"
              >
                Adicionar
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-3">
              {disciplinasNovaTurma.map((disciplina) => (
                <button
                  key={disciplina}
                  type="button"
                  onClick={() => setDisciplinasNovaTurma((atual) => atual.filter((item) => item !== disciplina))}
                  className="text-xs bg-violet-100 text-violet-800 px-3 py-1 rounded-full"
                >
                  {disciplina} ×
                </button>
              ))}
            </div>
          </div>
          <button
            type="button"
            onClick={criarTurma}
            disabled={loading}
            className="bg-slate-900 text-white font-semibold px-6 py-3 rounded-lg disabled:opacity-60"
          >
            {loading ? 'Salvando...' : 'Salvar turma'}
          </button>
        </div>
      )}

      {turmas.length === 0 && (
        <div className="bg-white p-12 text-center rounded-2xl border border-dashed border-slate-300 space-y-3 mt-6">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto">
            <LogIn size={24} />
          </div>
          <h4 className="text-base font-bold text-slate-800">
            {papel === 'aluno' ? 'Você ainda não está em nenhuma turma' : 'Nenhuma turma cadastrada'}
          </h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            {papel === 'aluno'
              ? 'Solicite o código da turma com o seu professor e clique em "Entrar com Código" acima para ingressar!'
              : 'Clique em "Criar Turma" para cadastrar a primeira turma da escola.'}
          </p>
          {papel === 'aluno' && (
            <button
              type="button"
              onClick={() => setMostrarFormulario(true)}
              className="mt-2 bg-blue-600 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-sm hover:bg-blue-700 transition-colors cursor-pointer"
            >
              Digitar Código da Turma
            </button>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 auto-rows-fr gap-6 mt-6">
        {turmas.map((turma) => {
          const alunoForm = alunoPorTurma[turma.id] || alunoVazio;
          return (
            <div key={turma.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col h-full">
              <div className={`h-24 ${turma.cor} p-6 flex items-end`}>
                <h3 className="text-xl font-bold text-white">{turma.nome}</h3>
              </div>
              <div className="p-6 space-y-5 flex-1 flex flex-col">
                <div className="flex justify-between items-center gap-3">
                  <p className="text-slate-600">{turma.ano}</p>
                  <span className="text-xs font-mono bg-slate-100 text-slate-600 px-3 py-1 rounded-full border border-slate-200">
                    Código: {turma.codigo}
                  </span>
                </div>

                <div>
                  <p className="text-sm font-semibold text-slate-700 mb-2">Disciplinas</p>
                  <div className="flex flex-wrap gap-2">
                    {(turma.disciplinas || []).length > 0 ? (
                      turma.disciplinas.map((disciplina) => (
                        <span key={disciplina.id} className="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-100">
                          {disciplina.nome}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-slate-500">Nenhuma disciplina cadastrada.</span>
                    )}
                  </div>
                  {papel === 'professor' && (
                    <div className="flex gap-2 mt-3">
                      <input
                        value={disciplinaPorTurma[turma.id] || ''}
                        onChange={(e) => setDisciplinaPorTurma((atual) => ({ ...atual, [turma.id]: e.target.value }))}
                        className="flex-1 border rounded-lg p-2.5 text-sm outline-none focus:ring-1 focus:ring-blue-500"
                        placeholder="Nova disciplina"
                      />
                      <button type="button" onClick={() => cadastrarDisciplina(turma.id)} disabled={loading} className="flex items-center gap-1 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium disabled:opacity-60">
                        <BookOpen size={16} />
                        Incluir
                      </button>
                    </div>
                  )}
                </div>

                <div className="flex-1 flex flex-col">
                  <p className="text-sm font-semibold text-slate-700 mb-2">
                    {papel === 'aluno' ? 'Colegas da turma' : 'Alunos da turma'} ({(turma.alunos || []).length})
                  </p>
                  <div className="relative flex-1 min-h-[8rem]">
                    <div className="absolute inset-0 space-y-2 overflow-y-auto">
                      {(turma.alunos || []).length > 0 ? (
                        turma.alunos.map((aluno) => (
                          <div key={aluno.id} className="text-sm text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                            {aluno.nome} <span className="text-slate-400">· {aluno.email}</span>
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-slate-500">Nenhum aluno cadastrado nesta turma.</p>
                      )}
                    </div>
                  </div>
                  {papel === 'professor' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-3">
                      <input
                        value={alunoForm.nome}
                        onChange={(e) => setAlunoPorTurma((atual) => ({ ...atual, [turma.id]: { ...alunoForm, nome: e.target.value } }))}
                        className="border rounded-lg p-2.5 text-sm outline-none focus:ring-1 focus:ring-blue-500"
                        placeholder="Nome do aluno"
                      />
                      <input
                        value={alunoForm.email}
                        onChange={(e) => setAlunoPorTurma((atual) => ({ ...atual, [turma.id]: { ...alunoForm, email: e.target.value } }))}
                        className="border rounded-lg p-2.5 text-sm outline-none focus:ring-1 focus:ring-blue-500"
                        placeholder="E-mail do aluno"
                      />
                      <button type="button" onClick={() => cadastrarProfessor(turma.id)} disabled={loading} className="md:col-span-2 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2.5 rounded-lg text-sm font-medium disabled:opacity-60 transition-colors">
                        <Users size={16} />
                        Adicionar Professor
                      </button>
                      <button type="button" onClick={() => cadastrarAluno(turma.id)} disabled={loading} className="md:col-span-2 flex items-center justify-center gap-2 bg-emerald-600 text-white px-3 py-2.5 rounded-lg text-sm font-medium disabled:opacity-60">
                        <UserPlus size={16} />
                        Cadastrar aluno na turma
                      </button>
                    </div>
                  )}
                </div>

                <button
                  type="button"
                  onClick={() => onAcessarTurma?.(turma.id, turma.nome)}
                  className="mt-auto w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 px-4 rounded-xl text-xs flex items-center justify-center space-x-1.5 transition-colors cursor-pointer"
                >
                  <span>{papel === 'aluno' ? 'Acessar Exercícios da Turma' : papel === 'professor' ? 'Acessar Copiloto Pedagógico' : 'Ver Detalhes da Turma'}</span>
                  <span>→</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
