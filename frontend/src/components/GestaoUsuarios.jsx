import { API_BASE, apiFetch } from '../api';
import React, { useEffect, useState } from 'react';



const opcoesModeloPorProvedor = {
  grok: ['grok-2-latest', 'grok-3-mini'],
  groq: ['openai/gpt-oss-20b', 'qwen/qwen3.8-27b', 'openai/gpt-oss-120b'],
};

const vazioEscola = { nome: '', cidade: '', estado: '', diretor: '', api_key_ia: '', provedor_ia: 'grok', modelo_ia: 'grok-2-latest' };
const vazioProfessor = { nome: '', email: '', disciplina: '', escola_id: '1' };
const vazioAluno = { nome: '', email: '', turma_id: '1' };

export default function GestaoUsuarios({ papel = 'administrador' }) {
  const [escola, setEscola] = useState(vazioEscola);
  const [professor, setProfessor] = useState(vazioProfessor);
  const [aluno, setAluno] = useState(vazioAluno);
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resumo, setResumo] = useState({ total_escolas: 0, total_professores: 0, total_turmas: 0, total_alunos: 0, total_tokens: 0, total_custo: 0 });
  const [escolas, setEscolas] = useState([]);
  const [escolaSelecionada, setEscolaSelecionada] = useState('');
  const [usoEscola, setUsoEscola] = useState(null);

  const carregarResumo = async () => {
    try {
      const response = await apiFetch(`${API_BASE}/admin/resumo`, { headers: { 'x-tipo-usuario': 'administrador' } });
      const data = await response.json();
      setResumo(data);
    } catch (error) {
      console.error('Erro ao carregar resumo:', error);
    }
  };

  const carregarEscolas = async () => {
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas`, { headers: { 'x-tipo-usuario': 'administrador' } });
      const data = await response.json();
      const lista = data.escolas || [];
      setEscolas(lista);
      if (!escolaSelecionada && lista.length > 0) {
        setEscolaSelecionada(String(lista[0].id));
      }
    } catch (error) {
      console.error('Erro ao carregar escolas:', error);
    }
  };

  const carregarUsoEscola = async (id) => {
    if (!id) return;
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas/${id}/uso-ia`, { headers: { 'x-tipo-usuario': 'administrador' } });
      const data = await response.json();
      setUsoEscola(data);
    } catch (error) {
      console.error('Erro ao carregar uso da escola:', error);
    }
  };

  useEffect(() => {
    carregarResumo();
    carregarEscolas();
  }, []);

  useEffect(() => {
    if (escolaSelecionada) {
      carregarUsoEscola(escolaSelecionada);
    }
  }, [escolaSelecionada]);

  const cadastrarEscola = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'administrador' },
        body: JSON.stringify(escola),
      });
      const data = await response.json();
      setResultado({ tipo: 'Escola', mensagem: data.mensagem || 'Escola criada.' });
      setEscola(vazioEscola);
      await carregarResumo();
    } catch (error) {
      console.error('Erro ao criar escola:', error);
    } finally {
      setLoading(false);
    }
  };

  const removerChaveIa = async () => {
    if (!escolaSelecionada) {
      setResultado({ tipo: 'Segurança', mensagem: 'Selecione uma escola antes de remover a chave da IA.' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas/${escolaSelecionada}/configuracao-ia`, {
        method: 'DELETE',
        headers: { 'x-tipo-usuario': 'administrador' },
      });
      const data = await response.json();
      setResultado({ tipo: 'Segurança', mensagem: data.mensagem || 'Chave da IA removida.' });
      setEscola((atual) => ({ ...atual, api_key_ia: '', provedor_ia: 'grok', modelo_ia: 'grok-2-latest' }));
      await carregarResumo();
      await carregarUsoEscola(escolaSelecionada);
    } catch (error) {
      console.error('Erro ao remover chave da IA:', error);
      setResultado({ tipo: 'Segurança', mensagem: 'Não foi possível remover a chave da IA.' });
    } finally {
      setLoading(false);
    }
  };

  const cadastrarProfessor = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/admin/professores`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'administrador' },
        body: JSON.stringify({
          ...professor,
          escola_id: Number(professor.escola_id),
        }),
      });
      const data = await response.json();
      const msg = data.senha_provisoria ? `${data.mensagem || 'Sucesso.'} Senha provisória: ${data.senha_provisoria}` : data.mensagem;
      setResultado({ tipo: 'Sucesso', mensagem: msg });
      setProfessor({ ...vazioProfessor, escola_id: professor.escola_id });
      await carregarResumo();
    } catch (error) {
      console.error('Erro ao criar professor:', error);
    } finally {
      setLoading(false);
    }
  };

  const cadastrarAluno = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/professor/alunos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'professor' },
        body: JSON.stringify({
          ...aluno,
          turma_id: Number(aluno.turma_id),
        }),
      });
      const data = await response.json();
      const msg = data.senha_provisoria ? `${data.mensagem || 'Sucesso.'} Senha provisória: ${data.senha_provisoria}` : data.mensagem;
      setResultado({ tipo: 'Sucesso', mensagem: msg });
      setAluno(vazioAluno);
      await carregarResumo();
    } catch (error) {
      console.error('Erro ao criar aluno:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <h2 className="text-3xl font-bold text-slate-800">Gestão de Usuários e Escala</h2>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p className="text-sm text-slate-500">Escolas</p>
          <p className="text-3xl font-bold text-slate-800">{resumo.total_escolas}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p className="text-sm text-slate-500">Professores</p>
          <p className="text-3xl font-bold text-slate-800">{resumo.total_professores}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p className="text-sm text-slate-500">Turmas</p>
          <p className="text-3xl font-bold text-slate-800">{resumo.total_turmas}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <p className="text-sm text-slate-500">Alunos</p>
          <p className="text-3xl font-bold text-slate-800">{resumo.total_alunos}</p>
        </div>
        <div className="bg-sky-50 border border-sky-200 rounded-xl p-4 shadow-sm">
          <p className="text-sm text-sky-700">Tokens IA</p>
          <p className="text-3xl font-bold text-sky-900">{resumo.total_tokens || 0}</p>
        </div>
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 shadow-sm">
          <p className="text-sm text-emerald-700">Custo IA</p>
          <p className="text-2xl font-bold text-emerald-900">R$ {Number(resumo.total_custo || 0).toFixed(4)}</p>
        </div>
      </div>

      {resultado && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-green-700 font-medium">
          {resultado.tipo}: {resultado.mensagem}
        </div>
      )}

      <div className="bg-slate-900 rounded-2xl p-6 shadow-xl mb-6">
        <div className="flex flex-col md:flex-row md:items-center gap-4 justify-between">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400 font-bold mb-1">Contexto de Operação</p>
            <h3 className="text-2xl font-bold text-white">Selecione a Escola</h3>
            <p className="text-sm text-slate-300 mt-1">Todas as ações abaixo (consumo, cadastro de professores) serão aplicadas a esta escola.</p>
          </div>
          <div className="relative w-full md:w-auto">
            <select
              value={escolaSelecionada}
              onChange={(e) => setEscolaSelecionada(e.target.value)}
              className="appearance-none w-full md:w-[350px] bg-slate-800 border-2 border-slate-700 text-white font-bold rounded-xl px-5 py-4 outline-none focus:border-blue-500 transition-colors shadow-inner"
            >
              <option value="">Selecione uma escola...</option>
              {escolas.map((esc) => (
                <option key={esc.id} value={String(esc.id)}>{esc.nome}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {papel === 'administrador' && (
          <>
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <div className="flex items-center justify-between mb-5">
                  <h3 className="text-xl font-bold text-slate-800">Consumo de IA e Custo Operacional</h3>
                  <span className="bg-sky-100 text-sky-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">Tempo Real</span>
                </div>

                {usoEscola ? (
                  <>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-sky-50 border border-sky-200 rounded-xl p-4">
                        <p className="text-xs font-semibold text-sky-700 uppercase tracking-wider mb-1">Tokens</p>
                        <p className="text-2xl font-bold text-sky-900">{usoEscola.totais?.tokens || 0}</p>
                      </div>
                      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                        <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">Custo</p>
                        <p className="text-2xl font-bold text-emerald-900">R$ {Number(usoEscola.totais?.custo || 0).toFixed(4)}</p>
                      </div>
                      <div className="bg-violet-50 border border-violet-200 rounded-xl p-4">
                        <p className="text-xs font-semibold text-violet-700 uppercase tracking-wider mb-1">Provedor</p>
                        <p className="text-lg font-bold text-violet-900 uppercase truncate">{usoEscola.provedor_ia || 'N/D'}</p>
                      </div>
                      <div className="bg-slate-100 border border-slate-200 rounded-xl p-4">
                        <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Modelo</p>
                        <p className="text-sm font-bold text-slate-900 truncate">{usoEscola.modelo_ia || 'Padrão'}</p>
                      </div>
                    </div>
                    {usoEscola?.logs?.length > 0 && (
                      <div className="overflow-hidden rounded-xl border border-slate-200">
                        <table className="min-w-full divide-y divide-slate-200 text-left">
                          <thead className="bg-slate-50">
                            <tr>
                              <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">Descrição</th>
                              <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">Tokens</th>
                              <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">Custo</th>
                              <th className="px-4 py-3 text-xs font-semibold uppercase text-slate-600">Data</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-200 bg-white">
                            {usoEscola.logs.slice(0, 5).map((log) => (
                              <tr key={log.id} className="hover:bg-slate-50">
                                <td className="px-4 py-3 text-sm text-slate-700">{log.descricao}</td>
                                <td className="px-4 py-3 text-sm text-slate-700">{log.tokens_usados}</td>
                                <td className="px-4 py-3 text-sm text-slate-700">R$ {Number(log.custo || 0).toFixed(4)}</td>
                                <td className="px-4 py-3 text-sm text-slate-700">{new Date(log.created_at).toLocaleString('pt-BR')}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                    Selecione uma escola no topo da página para visualizar o histórico.
                  </div>
                )}
              </div>

              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <h3 className="text-xl font-bold text-slate-800 mb-4">Adicionar Professor à Escola Selecionada</h3>
                {escolaSelecionada ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input value={professor.nome} onChange={(e) => setProfessor({ ...professor, nome: e.target.value })} placeholder="Nome completo" className="w-full border border-slate-300 p-3 rounded-lg focus:border-blue-500 outline-none" />
                    <input value={professor.email} onChange={(e) => setProfessor({ ...professor, email: e.target.value })} placeholder="Email profissional" className="w-full border border-slate-300 p-3 rounded-lg focus:border-blue-500 outline-none" />
                    <input value={professor.disciplina} onChange={(e) => setProfessor({ ...professor, disciplina: e.target.value })} placeholder="Disciplina" className="w-full border border-slate-300 p-3 rounded-lg focus:border-blue-500 outline-none" />
                    <div className="md:col-span-3 flex justify-end">
                      <button type="button" onClick={() => { professor.escola_id = escolaSelecionada; cadastrarProfessor(); }} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold transition-colors shadow-md disabled:opacity-60">
                        Cadastrar Professor
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">Por favor, selecione a escola no contexto acima primeiro.</p>
                )}
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <h3 className="text-lg font-bold text-slate-800 mb-4">Criar Nova Escola</h3>
                <div className="space-y-4">
                  <input value={escola.nome} onChange={(e) => setEscola({ ...escola, nome: e.target.value })} placeholder="Nome da instituição" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-blue-500" />
                  <div className="grid grid-cols-2 gap-3">
                    <input value={escola.cidade} onChange={(e) => setEscola({ ...escola, cidade: e.target.value })} placeholder="Cidade" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-blue-500" />
                    <input value={escola.estado} onChange={(e) => setEscola({ ...escola, estado: e.target.value })} placeholder="Estado" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-blue-500" />
                  </div>
                  <input value={escola.diretor} onChange={(e) => setEscola({ ...escola, diretor: e.target.value })} placeholder="Nome do(a) Diretor(a)" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-blue-500" />
                  
                  <div className="rounded-xl border border-sky-200 bg-sky-50 p-4 space-y-3 mt-4">
                    <p className="text-sm font-bold text-sky-800">Chave de Inteligência Artificial</p>
                    <input type="password" value={escola.api_key_ia} onChange={(e) => setEscola({ ...escola, api_key_ia: e.target.value })} placeholder="Sua API Key" className="w-full border border-sky-200 p-3 rounded-lg outline-none" />
                    <select value={escola.provedor_ia} onChange={(e) => {
                      const prov = e.target.value;
                      setEscola({ ...escola, provedor_ia: prov, modelo_ia: opcoesModeloPorProvedor[prov][0] });
                    }} className="w-full border border-sky-200 p-3 rounded-lg bg-white outline-none">
                      <option value="grok">Grok (xAI)</option>
                      <option value="groq">Groq (Rápido)</option>
                    </select>
                    <select value={escola.modelo_ia} onChange={(e) => setEscola({ ...escola, modelo_ia: e.target.value })} className="w-full border border-sky-200 p-3 rounded-lg bg-white outline-none">
                      {(opcoesModeloPorProvedor[escola.provedor_ia] || opcoesModeloPorProvedor.grok).map((m) => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </select>
                  </div>

                  <button type="button" onClick={cadastrarEscola} disabled={loading} className="w-full bg-slate-900 hover:bg-slate-800 text-white py-3 rounded-xl font-bold transition-colors shadow-md disabled:opacity-60">
                    Cadastrar Instituição
                  </button>
                </div>
              </div>

              {escolaSelecionada && (
                <div className="bg-rose-50 p-6 rounded-2xl border border-rose-200 shadow-sm">
                  <h3 className="text-rose-800 font-bold mb-2">Zona de Perigo</h3>
                  <p className="text-xs text-rose-600 mb-4">Remover a chave de IA paralisará todos os serviços inteligentes da escola selecionada no topo.</p>
                  <button type="button" onClick={removerChaveIa} disabled={loading} className="w-full border border-rose-300 text-rose-700 bg-white hover:bg-rose-100 py-2.5 rounded-xl font-bold transition-colors text-sm disabled:opacity-60">
                    Desativar IA da Escola Atual
                  </button>
                </div>
              )}
            </div>
          </>
        )}

        {papel === 'professor' && (
          <div className="lg:col-span-3 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-xl font-bold text-slate-800">Cadastrar Aluno</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input value={aluno.nome} onChange={(e) => setAluno({ ...aluno, nome: e.target.value })} placeholder="Nome do aluno" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-blue-500" />
              <input value={aluno.email} onChange={(e) => setAluno({ ...aluno, email: e.target.value })} placeholder="Email do aluno" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-blue-500" />
              <input value={aluno.turma_id} onChange={(e) => setAluno({ ...aluno, turma_id: e.target.value })} placeholder="ID da turma" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-blue-500" />
              <div className="md:col-span-3 flex justify-end">
                <button type="button" onClick={cadastrarAluno} disabled={loading} className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-xl font-bold transition-colors shadow-md disabled:opacity-60">
                  Matricular Aluno
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
