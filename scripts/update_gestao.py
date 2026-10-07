import os

new_code = """import React, { useState, useEffect } from 'react';
import { Users, School, Key, FileText, CheckCircle2, AlertCircle, Trash2, PlusCircle, Settings } from 'lucide-react';
import { API_BASE, apiFetch } from '../../api';

const opcoesModeloPorProvedor = {
  'grok': ['grok-2-latest', 'grok-3-mini'],
  'groq': ['openai/gpt-oss-20b', 'qwen/qwen3.8-27b', 'openai/gpt-oss-120b']
};

const vazioEscola = { nome: '', cidade: '', estado: '', diretor: '', api_key_ia: '', provedor_ia: 'grok', modelo_ia: 'grok-2-latest' };
const vazioProfessor = { nome: '', email: '', disciplina: '', escola_id: '1' };
const vazioAluno = { nome: '', email: '', turma_id: '1' };

export default function GestaoUsuarios({ papel = 'administrador' }) {
  const [abaAdmin, setAbaAdmin] = useState('cadastradas');
  const [escola, setEscola] = useState(vazioEscola);
  const [professor, setProfessor] = useState(vazioProfessor);
  const [aluno, setAluno] = useState(vazioAluno);
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);

  const [resumo, setResumo] = useState({ total_escolas: 0, total_professores: 0, total_turmas: 0, total_alunos: 0, total_tokens: 0, total_custo: 0 });
  const [escolas, setEscolas] = useState([]);
  const [escolaSelecionada, setEscolaSelecionada] = useState('');
  const [usoEscola, setUsoEscola] = useState(null);
  
  const [configIaAtual, setConfigIaAtual] = useState({ api_key_ia: '', provedor_ia: 'groq', modelo_ia: 'openai/gpt-oss-20b' });

  useEffect(() => {
    if (papel === 'administrador') {
      carregarResumo();
      carregarEscolas();
    }
  }, [papel]);

  useEffect(() => {
    if (escolaSelecionada) {
      carregarUsoEscola(escolaSelecionada);
    } else {
      setUsoEscola(null);
    }
  }, [escolaSelecionada]);

  const carregarResumo = async () => {
    try {
      const response = await apiFetch(`${API_BASE}/admin/resumo`, { headers: { 'x-tipo-usuario': 'administrador' } });
      const data = await response.json();
      setResumo(data);
    } catch (e) { console.error(e); }
  };

  const carregarEscolas = async () => {
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas`, { headers: { 'x-tipo-usuario': 'administrador' } });
      const data = await response.json();
      const lista = data.escolas || [];
      setEscolas(lista);
      if (lista.length > 0 && !escolaSelecionada) {
        setEscolaSelecionada(lista[0].id.toString());
      }
    } catch (e) { console.error(e); }
  };

  const carregarUsoEscola = async (id) => {
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas/${id}/uso-ia`, { headers: { 'x-tipo-usuario': 'administrador' } });
      const data = await response.json();
      setUsoEscola(data);
    } catch (e) { console.error(e); }
  };

  const cadastrarEscola = async () => {
    setLoading(true);
    setResultado(null);
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'administrador' },
        body: JSON.stringify({
          nome: escola.nome, cidade: escola.cidade, estado: escola.estado, diretor: escola.diretor,
          config_ia: escola.api_key_ia ? { api_key_ia: escola.api_key_ia, provedor_ia: escola.provedor_ia, modelo_ia: escola.modelo_ia } : null
        })
      });
      const data = await response.json();
      setResultado({ sucesso: response.ok, mensagem: data.mensagem || 'Escola cadastrada com sucesso!' });
      if (response.ok) {
        setEscola(vazioEscola);
        carregarEscolas();
        carregarResumo();
        setAbaAdmin('cadastradas');
      }
    } catch (err) {
      setResultado({ sucesso: false, mensagem: 'Erro ao conectar com servidor.' });
    }
    setLoading(false);
  };

  const atualizarChaveIa = async () => {
    if (!escolaSelecionada) return;
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas/${escolaSelecionada}/configuracao-ia`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'administrador' },
        body: JSON.stringify({
          api_key_ia: configIaAtual.api_key_ia || undefined,
          provedor_ia: configIaAtual.provedor_ia,
          modelo_ia: configIaAtual.modelo_ia
        })
      });
      const data = await response.json();
      setResultado({ sucesso: response.ok, mensagem: data.mensagem || 'Configuração de IA atualizada.' });
    } catch (err) {
      setResultado({ sucesso: false, mensagem: 'Erro de conexão ao atualizar chave.' });
    }
    setLoading(false);
  };

  const removerChaveIa = async () => {
    if (!escolaSelecionada) return;
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/admin/escolas/${escolaSelecionada}/configuracao-ia`, {
        method: 'DELETE',
        headers: { 'x-tipo-usuario': 'administrador' }
      });
      const data = await response.json();
      setResultado({ sucesso: response.ok, mensagem: data.mensagem || 'Chave de IA removida.' });
    } catch (err) {
      setResultado({ sucesso: false, mensagem: 'Erro de conexão.' });
    }
    setLoading(false);
  };

  const cadastrarProfessor = async () => {
    setLoading(true);
    setResultado(null);
    try {
      const response = await apiFetch(`${API_BASE}/admin/professores`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'administrador' },
        body: JSON.stringify({
          nome: professor.nome, email: professor.email, disciplina: professor.disciplina, escola_id: parseInt(professor.escola_id)
        })
      });
      const data = await response.json();
      const msg = data.senha_provisoria ? `${data.mensagem || 'Sucesso.'} Senha provisória: ${data.senha_provisoria}` : data.mensagem;
      setResultado({ sucesso: response.ok, mensagem: msg });
      if (response.ok) {
        setProfessor(vazioProfessor);
        carregarResumo();
      }
    } catch (err) {
      setResultado({ sucesso: false, mensagem: 'Erro de conexão.' });
    }
    setLoading(false);
  };

  const cadastrarAluno = async () => {
    setLoading(true);
    setResultado(null);
    try {
      const response = await apiFetch(`${API_BASE}/professor/alunos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'professor' },
        body: JSON.stringify({
          nome: aluno.nome, email: aluno.email, turma_id: parseInt(aluno.turma_id)
        })
      });
      const data = await response.json();
      const msg = data.senha_provisoria ? `${data.mensagem || 'Sucesso.'} Senha provisória: ${data.senha_provisoria}` : data.mensagem;
      setResultado({ sucesso: response.ok, mensagem: msg });
      if (response.ok) setAluno(vazioAluno);
    } catch (err) {
      setResultado({ sucesso: false, mensagem: 'Erro de conexão.' });
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {papel === 'administrador' && (
        <div className="bg-gradient-to-r from-indigo-900 to-indigo-800 rounded-3xl p-8 text-white shadow-lg mb-8">
          <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
            <Users className="w-8 h-8 text-indigo-300" />
            Gestão do Sistema
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl border border-white/10">
              <p className="text-indigo-200 text-sm font-medium mb-1">Total de Escolas</p>
              <p className="text-3xl font-bold">{resumo.total_escolas}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl border border-white/10">
              <p className="text-indigo-200 text-sm font-medium mb-1">Professores</p>
              <p className="text-3xl font-bold">{resumo.total_professores}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl border border-white/10">
              <p className="text-indigo-200 text-sm font-medium mb-1">Turmas Ativas</p>
              <p className="text-3xl font-bold">{resumo.total_turmas}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-2xl border border-white/10">
              <p className="text-indigo-200 text-sm font-medium mb-1">Alunos</p>
              <p className="text-3xl font-bold">{resumo.total_alunos}</p>
            </div>
          </div>
        </div>
      )}

      {resultado && (
        <div className={`p-4 rounded-xl border flex items-start gap-3 ${resultado.sucesso ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}`}>
          {resultado.sucesso ? <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />}
          <div className="text-sm font-medium whitespace-pre-wrap">{resultado.mensagem}</div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {papel === 'administrador' && (
          <div className="lg:col-span-3 space-y-6">
            <div className="flex space-x-2 bg-slate-100 p-1 rounded-xl w-fit">
              <button onClick={() => setAbaAdmin('cadastradas')} className={`px-6 py-2.5 rounded-lg font-bold text-sm transition-all ${abaAdmin === 'cadastradas' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                Escolas Cadastradas
              </button>
              <button onClick={() => setAbaAdmin('nova')} className={`px-6 py-2.5 rounded-lg font-bold text-sm transition-all ${abaAdmin === 'nova' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
                Cadastrar Nova Escola
              </button>
            </div>

            {abaAdmin === 'cadastradas' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                        <School className="w-5 h-5 text-indigo-500" /> Detalhes da Escola
                      </h3>
                      <select value={escolaSelecionada} onChange={(e) => setEscolaSelecionada(e.target.value)} className="border border-slate-300 rounded-lg p-2.5 bg-slate-50 font-medium text-slate-700 outline-none focus:border-indigo-500">
                        <option value="">Selecione uma escola...</option>
                        {escolas.map(e => <option key={e.id} value={e.id}>{e.nome}</option>)}
                      </select>
                    </div>

                    {escolaSelecionada ? (
                      <div className="space-y-6">
                        {usoEscola && (
                          <div className="border border-slate-200 rounded-xl overflow-hidden">
                            <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
                              <h4 className="font-bold text-slate-700 text-sm flex items-center gap-2">
                                <FileText className="w-4 h-4" /> Histórico de Uso de IA
                              </h4>
                              <span className="text-xs font-bold text-indigo-600 bg-indigo-100 px-2 py-1 rounded-full">
                                Custo Total: R$ {Number(usoEscola.custo_total || 0).toFixed(4)}
                              </span>
                            </div>
                            <div className="overflow-x-auto max-h-64">
                              <table className="w-full text-left border-collapse">
                                <thead className="bg-white sticky top-0 shadow-sm">
                                  <tr>
                                    <th className="px-4 py-3 text-xs font-bold text-slate-500 uppercase">Ação</th>
                                    <th className="px-4 py-3 text-xs font-bold text-slate-500 uppercase">Tokens</th>
                                    <th className="px-4 py-3 text-xs font-bold text-slate-500 uppercase">Custo (R$)</th>
                                    <th className="px-4 py-3 text-xs font-bold text-slate-500 uppercase">Data</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 bg-white">
                                  {(usoEscola.logs || []).length === 0 ? (
                                    <tr><td colSpan="4" className="px-4 py-6 text-center text-slate-400 text-sm">Nenhum uso registrado.</td></tr>
                                  ) : (
                                    usoEscola.logs.map((log, i) => (
                                      <tr key={i} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-4 py-3 text-sm text-slate-700">{log.descricao}</td>
                                        <td className="px-4 py-3 text-sm text-slate-700">{log.tokens_usados}</td>
                                        <td className="px-4 py-3 text-sm text-slate-700">R$ {Number(log.custo || 0).toFixed(4)}</td>
                                        <td className="px-4 py-3 text-sm text-slate-700">{new Date(log.created_at).toLocaleString('pt-BR')}</td>
                                      </tr>
                                    ))
                                  )}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5">
                          <h4 className="font-bold text-slate-800 text-sm mb-4">Adicionar Professor a esta Escola</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <input value={professor.nome} onChange={(e) => setProfessor({ ...professor, nome: e.target.value })} placeholder="Nome completo" className="w-full border border-slate-300 p-2.5 rounded-lg focus:border-indigo-500 outline-none text-sm" />
                            <input value={professor.email} onChange={(e) => setProfessor({ ...professor, email: e.target.value })} placeholder="Email profissional" className="w-full border border-slate-300 p-2.5 rounded-lg focus:border-indigo-500 outline-none text-sm" />
                            <input value={professor.disciplina} onChange={(e) => setProfessor({ ...professor, disciplina: e.target.value })} placeholder="Disciplina" className="w-full border border-slate-300 p-2.5 rounded-lg focus:border-indigo-500 outline-none text-sm" />
                            <div className="md:col-span-3 flex justify-end mt-2">
                              <button type="button" onClick={() => { professor.escola_id = escolaSelecionada; cadastrarProfessor(); }} disabled={loading} className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg font-bold transition-colors text-sm shadow-sm disabled:opacity-60">
                                Cadastrar Professor
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="p-10 text-center text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                        Nenhuma escola selecionada.
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-6">
                  {escolaSelecionada ? (
                    <>
                      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                          <Settings className="w-5 h-5 text-indigo-500" /> Configuração de IA
                        </h3>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Nova Chave da API</label>
                            <input type="password" value={configIaAtual.api_key_ia} onChange={(e) => setConfigIaAtual({ ...configIaAtual, api_key_ia: e.target.value })} placeholder="Insira para atualizar..." className="w-full border border-slate-300 p-2.5 rounded-lg outline-none text-sm focus:border-indigo-500" />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Provedor</label>
                            <select value={configIaAtual.provedor_ia} onChange={(e) => {
                              const prov = e.target.value;
                              setConfigIaAtual({ ...configIaAtual, provedor_ia: prov, modelo_ia: opcoesModeloPorProvedor[prov][0] });
                            }} className="w-full border border-slate-300 p-2.5 rounded-lg bg-white outline-none text-sm focus:border-indigo-500">
                              <option value="grok">Grok (xAI)</option>
                              <option value="groq">Groq (Rápido)</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Modelo</label>
                            <select value={configIaAtual.modelo_ia} onChange={(e) => setConfigIaAtual({ ...configIaAtual, modelo_ia: e.target.value })} className="w-full border border-slate-300 p-2.5 rounded-lg bg-white outline-none text-sm focus:border-indigo-500">
                              {(opcoesModeloPorProvedor[configIaAtual.provedor_ia] || opcoesModeloPorProvedor.groq).map((m) => (
                                <option key={m} value={m}>{m}</option>
                              ))}
                            </select>
                          </div>
                          <button type="button" onClick={atualizarChaveIa} disabled={loading} className="w-full bg-slate-900 hover:bg-slate-800 text-white py-2.5 rounded-lg font-bold transition-colors text-sm shadow-sm disabled:opacity-60">
                            Atualizar Configuração
                          </button>
                        </div>
                      </div>

                      <div className="bg-rose-50 p-6 rounded-2xl border border-rose-200 shadow-sm">
                        <h3 className="text-rose-800 font-bold mb-2 flex items-center gap-2">
                          <Trash2 className="w-4 h-4" /> Zona de Perigo
                        </h3>
                        <p className="text-xs text-rose-600 mb-4">Remover a chave forçará a escola a usar a chave global (se existir) ou paralisará a IA.</p>
                        <button type="button" onClick={removerChaveIa} disabled={loading} className="w-full border border-rose-300 text-rose-700 bg-white hover:bg-rose-100 py-2.5 rounded-lg font-bold transition-colors text-sm disabled:opacity-60">
                          Limpar Chave Própria da Escola
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="p-6 bg-slate-50 border border-slate-200 rounded-2xl text-center text-sm text-slate-500">
                      Selecione uma escola ao lado para gerenciar as credenciais de Inteligência Artificial.
                    </div>
                  )}
                </div>
              </div>
            )}

            {abaAdmin === 'nova' && (
              <div className="max-w-2xl bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
                <h3 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                  <PlusCircle className="w-6 h-6 text-indigo-500" /> Cadastrar Nova Instituição
                </h3>
                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-1">Nome da Escola</label>
                    <input value={escola.nome} onChange={(e) => setEscola({ ...escola, nome: e.target.value })} placeholder="Ex: Colégio Estadual..." className="w-full border border-slate-300 p-3 rounded-xl outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-1">Cidade</label>
                      <input value={escola.cidade} onChange={(e) => setEscola({ ...escola, cidade: e.target.value })} placeholder="Cidade" className="w-full border border-slate-300 p-3 rounded-xl outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-1">Estado</label>
                      <input value={escola.estado} onChange={(e) => setEscola({ ...escola, estado: e.target.value })} placeholder="UF" className="w-full border border-slate-300 p-3 rounded-xl outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-1">Diretor(a)</label>
                    <input value={escola.diretor} onChange={(e) => setEscola({ ...escola, diretor: e.target.value })} placeholder="Nome do responsável" className="w-full border border-slate-300 p-3 rounded-xl outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-50 transition-all" />
                  </div>
                  
                  <div className="rounded-2xl border border-indigo-100 bg-indigo-50/50 p-6 space-y-4 mt-6">
                    <div className="flex items-center gap-2 mb-2">
                      <Key className="w-5 h-5 text-indigo-600" />
                      <p className="text-base font-bold text-indigo-900">Configuração de IA Própria (Opcional)</p>
                    </div>
                    <p className="text-xs text-indigo-700 mb-2">Se deixado em branco, a escola utilizará as credenciais globais do servidor.</p>
                    <div>
                      <input type="password" value={escola.api_key_ia} onChange={(e) => setEscola({ ...escola, api_key_ia: e.target.value })} placeholder="Chave da API (gsk_...)" className="w-full border border-indigo-200 p-3 rounded-xl outline-none focus:border-indigo-500" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <select value={escola.provedor_ia} onChange={(e) => {
                        const prov = e.target.value;
                        setEscola({ ...escola, provedor_ia: prov, modelo_ia: opcoesModeloPorProvedor[prov][0] });
                      }} className="w-full border border-indigo-200 p-3 rounded-xl bg-white outline-none">
                        <option value="groq">Groq (Rápido)</option>
                        <option value="grok">Grok (xAI)</option>
                      </select>
                      <select value={escola.modelo_ia} onChange={(e) => setEscola({ ...escola, modelo_ia: e.target.value })} className="w-full border border-indigo-200 p-3 rounded-xl bg-white outline-none">
                        {(opcoesModeloPorProvedor[escola.provedor_ia] || opcoesModeloPorProvedor.groq).map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="pt-4">
                    <button type="button" onClick={cadastrarEscola} disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-4 rounded-xl font-bold text-lg transition-colors shadow-md disabled:opacity-60 flex items-center justify-center gap-2">
                      <CheckCircle2 className="w-5 h-5" /> Cadastrar Escola
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {papel === 'professor' && (
          <div className="lg:col-span-3 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <Users className="w-6 h-6 text-emerald-500" /> Cadastrar Aluno
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input value={aluno.nome} onChange={(e) => setAluno({ ...aluno, nome: e.target.value })} placeholder="Nome do aluno" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-emerald-500" />
              <input value={aluno.email} onChange={(e) => setAluno({ ...aluno, email: e.target.value })} placeholder="Email do aluno" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-emerald-500" />
              <input value={aluno.turma_id} onChange={(e) => setAluno({ ...aluno, turma_id: e.target.value })} placeholder="ID da turma" className="w-full border border-slate-300 p-3 rounded-lg outline-none focus:border-emerald-500" />
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
"""

with open('frontend/src/pages/GestaoUsuarios.jsx', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Updated GestaoUsuarios.jsx")
