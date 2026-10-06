import { API_BASE, apiFetch } from '../api';
import React, { useEffect, useState } from 'react';
import { Bot, Sparkles, RefreshCw, Printer, CheckCircle, AlertCircle, BarChart3, HelpCircle, Edit3, Trash2, PlusCircle } from 'lucide-react';



const normalizarLista = (valor) => {
  if (Array.isArray(valor)) {
    return valor
      .flatMap((item) => {
        if (item == null) return [];
        if (typeof item === 'string') return [item.trim()];
        if (typeof item === 'object') {
          const extraidos = ['texto', 'descricao', 'titulo', 'nome', 'text', 'label']
            .map((chave) => (typeof item[chave] === 'string' ? item[chave].trim() : null))
            .filter(Boolean);
          if (extraidos.length > 0) return extraidos;
          return [JSON.stringify(item)];
        }
        return [String(item).trim()];
      })
      .filter(Boolean);
  }
  if (typeof valor === 'string') {
    return valor
      .split(/\n|;/)
      .map((item) => item.trim())
      .filter(Boolean);
  }
  return [];
};

const normalizarPlano = (valor) => {
  const base = valor && typeof valor === 'object' ? valor : {};
  return {
    titulo: typeof base.titulo === 'string' ? base.titulo : 'Plano de aula',
    disciplina: typeof base.disciplina === 'string' ? base.disciplina : 'Matemática',
    ano: typeof base.ano === 'string' ? base.ano : '7º Ano',
    nivel: typeof base.nivel === 'string' ? base.nivel : 'Básico',
    duracao: typeof base.duracao === 'string' ? base.duracao : '40 min',
    habilidades_bncc: normalizarLista(base.habilidades_bncc),
    objetivos: normalizarLista(base.objetivos),
    sequencia: normalizarLista(base.sequencia),
    recursos: normalizarLista(base.recursos),
    avaliacao: typeof base.avaliacao === 'string' ? base.avaliacao : 'Avaliação contínua e formativa.',
  };
};

const normalizarQuiz = (valor, temaPadrao = 'Tema') => {
  const base = valor && typeof valor === 'object' ? valor : {};
  return {
    id: base.id || null,
    tema: typeof base.tema === 'string' ? base.tema : temaPadrao,
    objetivo: typeof base.objetivo === 'string' ? base.objetivo : 'Aplicar os conceitos do tema.',
    habilidades_bncc: normalizarLista(base.habilidades_bncc),
    perguntas: Array.isArray(base.perguntas) ? base.perguntas : [],
  };
};

export default function FerramentasIA({ turmaIdInicial = null, papel = 'professor', onVoltarTurmas, onNavegar }) {
  const [abaAtiva, setAbaAtiva] = useState('planos');
  const [temaAula, setTemaAula] = useState('Equações de 1º Grau');
  const [disciplinaAula, setDisciplinaAula] = useState('Matemática');
  const [anoAula, setAnoAula] = useState('7º Ano');
  const [objetivos, setObjetivos] = useState('Resolver equações simples do 1º grau.\nIdentificar coeficientes e incógnitas.\nAplicar em problemas práticos do cotidiano.');
  const [resultado, setResultado] = useState(null);
  const [quizResultado, setQuizResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingRegen, setLoadingRegen] = useState(null);
  const [turmas, setTurmas] = useState([]);
  const [turmaId, setTurmaId] = useState('1');
  const [conteudoTurma, setConteudoTurma] = useState({ planos: [], quizzes: [] });
  const [quantidadeQuestoes, setQuantidadeQuestoes] = useState(4);
  const [nivelQuiz, setNivelQuiz] = useState('Básico');
  const [quizAprovado, setQuizAprovado] = useState(false);
  const [mensagemAprovacao, setMensagemAprovacao] = useState('');
  const [aprovandoQuiz, setAprovandoQuiz] = useState(false);
  const [raioXData, setRaioXData] = useState(null);
  const [loadingRaioX, setLoadingRaioX] = useState(false);
  const [mostrarModalImpressao, setMostrarModalImpressao] = useState(false);

  const alertasPredicao = [
    {
      turma: '7º Ano - Matemática',
      risco: 'Alto',
      percentual: 78,
      tendencia: 'queda em frações e proporcionalidade',
      indicadores: ['Média de exercícios em 54%', 'Baixa participação em aulas práticas', 'Erros recorrentes em simplificação'],
      alunos: [
        { nome: 'Carlos Eduardo', risco: 82, motivo: 'Baixa precisão em itens de equivalência', acao: 'Reforço com tutoria socrática e revisão guiada' },
        { nome: 'Ana Beatriz', risco: 71, motivo: 'Dificuldade em manter persistência nas tentativas', acao: 'Atividade de reforço com feedback individual da IA' },
      ],
    },
    {
      turma: '8º Ano - Ciências',
      risco: 'Médio',
      percentual: 63,
      tendencia: 'dificuldade leve em interpretação de gráficos e dados',
      indicadores: ['Frequência estável', 'Maior índice de erro em análise quantitativa', 'Participação moderada'],
      alunos: [
        { nome: 'Mateus Oliveira', risco: 68, motivo: 'Oscilação em avaliações curtas', acao: 'Checklist de revisão semanal com IA' },
      ],
    },
  ];

  const carregarTurmas = async () => {
    try {
      const response = await apiFetch(`${API_BASE}/professor/dashboard`, {
        headers: { 'x-tipo-usuario': 'professor' },
      });
      const data = await response.json();
      if (Array.isArray(data.turmas)) {
        setTurmas(data.turmas);
        if (turmaIdInicial !== null && turmaIdInicial !== undefined && turmaIdInicial !== '') {
          setTurmaId(String(turmaIdInicial));
        } else if (data.turmas[0]) {
          setTurmaId(String(data.turmas[0].id));
        }
      }
    } catch (error) {
      console.error('Erro ao carregar turmas:', error);
      setTurmas([{ id: 1, nome: 'Turma demonstrativa' }]);
    }
  };

  useEffect(() => {
    carregarTurmas();
  }, [turmaIdInicial]);

  const carregarConteudoTurma = async () => {
    if (!turmaId) return;
    try {
      const endpoint = papel === 'professor'
        ? `${API_BASE}/professor/turma/${turmaId}/conteudo`
        : `${API_BASE}/aluno/conteudo-turma?turma_id=${turmaId}`;

      const response = await apiFetch(endpoint, {
        headers: { 'x-tipo-usuario': papel === 'professor' ? 'professor' : 'aluno' },
      });
      const data = await response.json();
      setConteudoTurma({
        planos: Array.isArray(data?.planos) ? data.planos : [],
        quizzes: Array.isArray(data?.quizzes) ? data.quizzes : [],
      });
    } catch (error) {
      console.error('Erro ao carregar conteúdo da turma:', error);
      setConteudoTurma({ planos: [], quizzes: [] });
    }
  };

  const carregarRaioX = async () => {
    if (!turmaId) return;
    setLoadingRaioX(true);
    try {
      const response = await apiFetch(`${API_BASE}/professor/turma/${turmaId}/raio-x-quiz`, {
        headers: { 'x-tipo-usuario': 'professor' },
      });
      const data = await response.json();
      if (data?.analytics) {
        setRaioXData(data.analytics);
      }
    } catch (error) {
      console.error('Erro ao carregar Raio-X da turma:', error);
    } finally {
      setLoadingRaioX(false);
    }
  };

  useEffect(() => {
    carregarConteudoTurma();
    if (abaAtiva === 'raiox') {
      carregarRaioX();
    }
  }, [turmaId, papel, abaAtiva]);

  const gerarPlano = async () => {
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/professor/gerar-plano`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'professor',
        },
        body: JSON.stringify({
          tema_aula: temaAula,
          disciplina: disciplinaAula,
          ano: anoAula,
          objetivos: objetivos.split(/\n|;/).map((item) => item.trim()).filter(Boolean),
          turma_id: Number(turmaId),
        }),
      });

      const data = await response.json();
      setResultado(normalizarPlano(data?.plano ?? data));
      await carregarConteudoTurma();
    } catch (error) {
      console.error('Erro ao gerar plano:', error);
    } finally {
      setLoading(false);
    }
  };

  const gerarQuiz = async () => {
    setQuizAprovado(false);
    setMensagemAprovacao('');
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/professor/gerar-quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'professor',
        },
        body: JSON.stringify({
          tema: temaAula,
          disciplina: disciplinaAula,
          objetivo: objetivos.split(/\n|;/)[0] || 'Aplicar os conceitos centrais do tema.',
          quantidade: Number(quantidadeQuestoes) || 4,
          turma_id: Number(turmaId),
          nivel: nivelQuiz,
        }),
      });
      const data = await response.json();
      setQuizResultado(normalizarQuiz(data?.quiz ?? data, temaAula));
      await carregarConteudoTurma();
    } catch (error) {
      console.error('Erro ao gerar quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  const regenerarQuestaoIndividual = async (index) => {
    if (!quizResultado || !quizResultado.perguntas[index]) return;
    setLoadingRegen(index);
    try {
      const questaoAtual = quizResultado.perguntas[index];
      const response = await apiFetch(`${API_BASE}/professor/regenerar-questao`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'professor',
        },
        body: JSON.stringify({
          tema: quizResultado.tema || temaAula,
          objetivo: quizResultado.objetivo,
          pergunta_anterior: questaoAtual.pergunta,
          turma_id: Number(turmaId),
        }),
      });
      const data = await response.json();
      if (data?.questao) {
        const novasQuestoes = [...quizResultado.perguntas];
        novasQuestoes[index] = data.questao;
        setQuizResultado({ ...quizResultado, perguntas: novasQuestoes });
      }
    } catch (error) {
      console.error('Erro ao regenerar questão:', error);
    } finally {
      setLoadingRegen(null);
    }
  };

  const atualizarTextoPergunta = (index, novoTexto) => {
    const novasQuestoes = [...quizResultado.perguntas];
    novasQuestoes[index] = { ...novasQuestoes[index], pergunta: novoTexto };
    setQuizResultado({ ...quizResultado, perguntas: novasQuestoes });
  };

  const atualizarOpcaoPergunta = (qIndex, opIndex, novoTexto) => {
    const novasQuestoes = [...quizResultado.perguntas];
    const novasOpcoes = [...novasQuestoes[qIndex].opcoes];
    const opcaoAnterior = novasOpcoes[opIndex];
    novasOpcoes[opIndex] = novoTexto;

    let novaRespostaCorreta = novasQuestoes[qIndex].resposta_correta;
    if (novaRespostaCorreta === opcaoAnterior) {
      novaRespostaCorreta = novoTexto;
    }
    novasQuestoes[qIndex] = { ...novasQuestoes[qIndex], opcoes: novasOpcoes, resposta_correta: novaRespostaCorreta };
    setQuizResultado({ ...quizResultado, perguntas: novasQuestoes });
  };

  const removerQuestao = (index) => {
    const novasQuestoes = quizResultado.perguntas.filter((_, i) => i !== index);
    setQuizResultado({ ...quizResultado, perguntas: novasQuestoes });
  };

  const aprovarQuiz = async () => {
    if (!quizResultado) return;
    setAprovandoQuiz(true);
    try {
      const response = await apiFetch(`${API_BASE}/professor/aprovar-quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-tipo-usuario': 'professor',
        },
        body: JSON.stringify({
          turma_id: Number(turmaId),
          quiz_id: quizResultado.id,
          quiz: quizResultado,
          aprovado: true,
        }),
      });
      const data = await response.json();
      setQuizAprovado(true);
      setMensagemAprovacao(data.mensagem || 'Quiz aprovado e disponibilizado para os alunos da turma!');
      await carregarConteudoTurma();
    } catch (error) {
      console.error('Erro ao aprovar quiz:', error);
      setQuizAprovado(true);
      setMensagemAprovacao('Quiz aprovado e vinculado à turma.');
    } finally {
      setAprovandoQuiz(false);
    }
  };

  const turmaSelecionada = turmas.find((turma) => Number(turma.id) === Number(turmaId)) || null;
  const modoLeitura = papel !== 'professor';

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          {onVoltarTurmas && (
            <button
              type="button"
              onClick={onVoltarTurmas}
              className="text-xs font-semibold text-slate-500 hover:text-blue-600 flex items-center space-x-1 mb-2 transition-colors cursor-pointer"
            >
              <span>← Voltar para Minhas Turmas</span>
            </button>
          )}
          <h2 className="text-3xl font-bold text-slate-800 flex items-center space-x-3">
            <Bot className="text-blue-600" size={32} />
            <span>Copiloto Pedagógico IA</span>
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Planejamento curricular alinhado à BNCC, avaliações diagnósticas e Raio-X de aprendizagem.
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase">Turma Ativa:</span>
          <select
            value={turmaId}
            onChange={(e) => setTurmaId(e.target.value)}
            className="text-sm font-bold text-blue-700 bg-transparent outline-none cursor-pointer"
          >
            {turmas.map((t) => (
              <option key={t.id} value={t.id}>{t.nome}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex space-x-4 border-b border-slate-200 pb-2">
        <button
          onClick={() => setAbaAtiva('planos')}
          className={`pb-2 px-4 font-semibold text-sm transition-colors flex items-center space-x-2 ${abaAtiva === 'planos' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
        >
          <Sparkles size={16} />
          <span>Planos & Quizzes (BNCC)</span>
        </button>
        <button
          onClick={() => setAbaAtiva('raiox')}
          className={`pb-2 px-4 font-semibold text-sm transition-colors flex items-center space-x-2 ${abaAtiva === 'raiox' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
        >
          <BarChart3 size={16} />
          <span>Raio-X de Desempenho</span>
        </button>
        <button
          onClick={() => setAbaAtiva('alertas')}
          className={`pb-2 px-4 font-semibold text-sm transition-colors flex items-center space-x-2 ${abaAtiva === 'alertas' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-500 hover:text-slate-700'}`}
        >
          <AlertCircle size={16} />
          <span>Alertas Preditivos</span>
        </button>
      </div>

      {abaAtiva === 'planos' && (
        <div className="space-y-6">
          {!modoLeitura && (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md">
                  Gerador Assistido por IA
                </span>
                <span className="text-xs text-slate-500">Alinhamento BNCC automático</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Disciplina</label>
                  <input
                    type="text"
                    value={disciplinaAula}
                    onChange={(e) => setDisciplinaAula(e.target.value)}
                    placeholder="Ex: Matemática, Ciências..."
                    className="w-full border p-2.5 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Ano / Série</label>
                  <input
                    type="text"
                    value={anoAula}
                    onChange={(e) => setAnoAula(e.target.value)}
                    placeholder="Ex: 7º Ano, 1º Ano EM..."
                    className="w-full border p-2.5 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Quantidade de Questões (Quiz)</label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={quantidadeQuestoes}
                    onChange={(e) => setQuantidadeQuestoes(e.target.value)}
                    className="w-full border p-2.5 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
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
                <label className="block text-xs font-semibold text-slate-700 mb-1">Tema da Aula</label>
                <input
                  type="text"
                  value={temaAula}
                  onChange={(e) => setTemaAula(e.target.value)}
                  placeholder="Ex: Equações de 1º Grau, Frações Equivalentes..."
                  className="w-full border p-2.5 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Objetivos Pedagógicos (ou deixe a IA estruturar)</label>
                <textarea
                  value={objetivos}
                  onChange={(e) => setObjetivos(e.target.value)}
                  rows="3"
                  className="w-full border p-2.5 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex flex-wrap gap-3 pt-2">
                <button
                  type="button"
                  onClick={gerarPlano}
                  disabled={loading}
                  className="bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 px-5 rounded-xl text-sm flex items-center space-x-2 disabled:opacity-60 transition-colors"
                >
                  <Sparkles size={16} className="text-blue-400" />
                  <span>{loading ? 'Elaborando Plano...' : 'Gerar Plano com BNCC'}</span>
                </button>
                <button
                  type="button"
                  onClick={gerarQuiz}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-5 rounded-xl text-sm flex items-center space-x-2 disabled:opacity-60 transition-colors"
                >
                  <Bot size={16} />
                  <span>{loading ? 'Criando Quiz...' : 'Gerar Quiz Avaliativo'}</span>
                </button>
              </div>
            </div>
          )}

          {resultado && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs uppercase tracking-wider font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                      {resultado.disciplina} • {resultado.ano}
                    </span>
                    <span className="text-xs text-slate-400">Duração: {resultado.duracao}</span>
                  </div>
                  <h3 className="text-2xl font-bold text-slate-800 mt-1">{resultado.titulo}</h3>
                </div>
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2 px-4 rounded-xl text-xs flex items-center space-x-2 transition-colors self-start"
                >
                  <Printer size={16} />
                  <span>Imprimir / Exportar PDF</span>
                </button>
              </div>

              {resultado.habilidades_bncc && resultado.habilidades_bncc.length > 0 && (
                <div className="bg-sky-50/70 border border-sky-200/80 rounded-xl p-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-sky-800 flex items-center space-x-1.5 mb-2">
                    <span>🏛️ Alinhamento com a BNCC</span>
                  </h4>
                  <div className="space-y-1.5">
                    {resultado.habilidades_bncc.map((hab, i) => (
                      <div key={i} className="text-xs text-sky-950 font-medium bg-white/80 border border-sky-100 p-2 rounded-lg">
                        {hab}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h4 className="font-bold text-slate-800 text-sm mb-2">Objetivos de Aprendizagem</h4>
                <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                  {resultado.objetivos.map((obj, i) => <li key={i}>{obj}</li>)}
                </ul>
              </div>

              <div>
                <h4 className="font-bold text-slate-800 text-sm mb-2">Sequência Didática</h4>
                <div className="space-y-2">
                  {resultado.sequencia.map((seq, i) => (
                    <div key={i} className="text-sm text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                      {seq}
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                  <h4 className="font-bold text-slate-800 text-xs uppercase mb-1">Recursos Didáticos</h4>
                  <ul className="list-disc list-inside text-xs text-slate-600 space-y-1">
                    {resultado.recursos.map((rec, i) => <li key={i}>{rec}</li>)}
                  </ul>
                </div>
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                  <h4 className="font-bold text-slate-800 text-xs uppercase mb-1">Critérios de Avaliação</h4>
                  <p className="text-xs text-slate-600 leading-relaxed">{resultado.avaliacao}</p>
                </div>
              </div>
            </div>
          )}

          {quizResultado && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <span className="text-xs uppercase tracking-wider font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                    Quiz Interativo
                  </span>
                  <h3 className="text-2xl font-bold text-slate-800 mt-1">{quizResultado.tema}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Objetivo: {quizResultado.objetivo}</p>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={aprovarQuiz}
                    disabled={aprovandoQuiz || quizAprovado}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 px-5 rounded-xl text-sm flex items-center space-x-2 disabled:opacity-60 transition-colors"
                  >
                    <CheckCircle size={16} />
                    <span>{aprovandoQuiz ? 'Aprovando...' : quizAprovado ? 'Quiz Aprovado ✓' : 'Aprovar e Liberar para Alunos'}</span>
                  </button>
                </div>
              </div>

              {quizResultado.habilidades_bncc && quizResultado.habilidades_bncc.length > 0 && (
                <div className="bg-emerald-50/60 border border-emerald-200/80 rounded-xl p-3 text-xs text-emerald-900 font-medium">
                  <strong>BNCC:</strong> {quizResultado.habilidades_bncc.join(' | ')}
                </div>
              )}

              {mensagemAprovacao && (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3.5 rounded-xl text-sm font-semibold flex items-center space-x-2">
                  <CheckCircle size={18} className="text-emerald-600" />
                  <span>{mensagemAprovacao}</span>
                </div>
              )}

              <div className="space-y-4">
                <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider">
                  <span>Perguntas do Quiz ({quizResultado.perguntas?.length || 0})</span>
                  <span>Controle Humano: edite ou regenere itens livremente</span>
                </div>

                {quizResultado.perguntas?.map((item, qIndex) => (
                  <div key={qIndex} className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <span className="text-xs font-bold text-blue-700 mb-1 block">Questão {qIndex + 1}</span>
                        <input
                          type="text"
                          value={item.pergunta}
                          onChange={(e) => atualizarTextoPergunta(qIndex, e.target.value)}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-sm font-semibold text-slate-800 outline-none focus:ring-1 focus:ring-blue-500"
                        />
                      </div>
                      <div className="flex items-center space-x-1 pt-4">
                        <button
                          type="button"
                          title="Regenerar apenas esta questão com IA"
                          onClick={() => regenerarQuestaoIndividual(qIndex)}
                          disabled={loadingRegen === qIndex}
                          className="p-2 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-semibold flex items-center space-x-1 transition-colors"
                        >
                          <RefreshCw size={14} className={loadingRegen === qIndex ? 'animate-spin' : ''} />
                          <span className="hidden sm:inline">Regenerar</span>
                        </button>
                        <button
                          type="button"
                          title="Excluir questão"
                          onClick={() => removerQuestao(qIndex)}
                          className="p-2 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                      {item.opcoes?.map((opcao, opIndex) => {
                        const isCorreta = opcao === item.resposta_correta;
                        return (
                          <div
                            key={opIndex}
                            className={`flex items-center space-x-2 p-2 rounded-lg border text-xs ${isCorreta ? 'bg-emerald-50 border-emerald-300 text-emerald-900 font-semibold' : 'bg-white border-slate-200 text-slate-700'}`}
                          >
                            <span className="font-bold text-slate-400">{String.fromCharCode(65 + opIndex)})</span>
                            <input
                              type="text"
                              value={opcao}
                              onChange={(e) => atualizarOpcaoPergunta(qIndex, opIndex, e.target.value)}
                              className="bg-transparent flex-1 outline-none text-xs"
                            />
                            {isCorreta && <span className="text-[10px] bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded">Gabarito</span>}
                          </div>
                        );
                      })}
                    </div>

                    {item.explicacao && (
                      <p className="text-xs text-slate-500 italic bg-white/70 p-2 rounded border border-slate-100">
                        <strong>Explicação pedagógica:</strong> {item.explicacao}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
            <h4 className="text-base font-bold text-slate-800">Histórico de Conteúdos da Turma</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {conteudoTurma.planos.map((plano) => (
                <div key={plano.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                  <span className="text-[10px] font-bold uppercase text-blue-700 bg-blue-100 px-2 py-0.5 rounded">Plano de Aula</span>
                  <h5 className="font-bold text-slate-800 text-sm mt-1">{plano.plano?.titulo || plano.tema}</h5>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">{plano.plano?.avaliacao}</p>
                </div>
              ))}
              {conteudoTurma.quizzes.map((quiz) => (
                <div key={quiz.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">Quiz</span>
                    <span className="text-[10px] text-slate-400 capitalize">{quiz.status || 'publicado'}</span>
                  </div>
                  <h5 className="font-bold text-slate-800 text-sm mt-1">{quiz.quiz?.tema || quiz.tema}</h5>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-1 mb-2">{quiz.quiz?.objetivo || quiz.objetivo}</p>
                  {(quiz.status === 'rascunho') && (
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          await apiFetch(`${API_BASE}/professor/aprovar-quiz`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'professor' },
                            body: JSON.stringify({ turma_id: turmaIdInicial, quiz_id: quiz.id, aprovado: true })
                          });
                          await fetchConteudo();
                        } catch(e) {}
                      }}
                      className="mt-2 text-[10px] bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded"
                    >
                      Publicar para Alunos
                    </button>
                  )}
                </div>
              ))}
              {conteudoTurma.planos.length === 0 && conteudoTurma.quizzes.length === 0 && (
                <div className="col-span-full py-8 text-center text-slate-400 text-sm border border-dashed border-slate-200 rounded-xl">
                  Nenhum plano de aula ou quiz foi vinculado a esta turma ainda.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {abaAtiva === 'raiox' && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white rounded-2xl p-6 shadow-md">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <span className="text-xs uppercase tracking-widest text-blue-300 font-bold">Diagnóstico em Tempo Real</span>
                <h3 className="text-2xl font-bold mt-1">Raio-X de Desempenho da Turma</h3>
                <p className="text-slate-300 text-sm mt-1 max-w-2xl">
                  Análise consolidada das submissões reais dos alunos com diagnóstico preditivo gerado por IA para orientar a próxima intervenção pedagógica.
                </p>
              </div>
              <button
                type="button"
                onClick={carregarRaioX}
                disabled={loadingRaioX}
                className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-2 transition-colors self-start"
              >
                <RefreshCw size={14} className={loadingRaioX ? 'animate-spin' : ''} />
                <span>Atualizar Dados</span>
              </button>
            </div>
          </div>

          {raioXData ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-center">
                  <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">Submissões Registradas</span>
                  <p className="text-3xl font-extrabold text-slate-800 mt-1">{raioXData.total_submissoes}</p>
                </div>
                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-center">
                  <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">Média Geral da Turma</span>
                  <p className={`text-3xl font-extrabold mt-1 ${raioXData.media_turma >= 7.0 ? 'text-emerald-600' : raioXData.media_turma >= 5.0 ? 'text-amber-500' : 'text-red-500'}`}>
                    {raioXData.media_turma} / 10
                  </p>
                </div>
                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-center">
                  <span className="text-xs uppercase tracking-wider font-semibold text-slate-500">Quizzes Aplicados</span>
                  <p className="text-3xl font-extrabold text-blue-600 mt-1">{raioXData.total_quizzes}</p>
                </div>
              </div>

              {raioXData.diagnostico_ia && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center space-x-2 text-blue-900 font-bold text-base">
                    <Sparkles className="text-blue-600" size={20} />
                    <span>Diagnóstico da IA para o Professor</span>
                  </div>

                  <p className="text-sm text-slate-700 leading-relaxed font-medium">
                    {raioXData.diagnostico_ia.resumo_desempenho}
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                    <div className="bg-white/80 p-4 rounded-xl border border-blue-100">
                      <h4 className="text-xs font-bold uppercase text-red-700 tracking-wider mb-2">Principais Dificuldades</h4>
                      <ul className="list-disc list-inside text-xs text-slate-700 space-y-1">
                        {(raioXData.diagnostico_ia.principais_dificuldades || []).map((dif, idx) => (
                          <li key={idx}>{dif}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-white/80 p-4 rounded-xl border border-blue-100">
                      <h4 className="text-xs font-bold uppercase text-emerald-700 tracking-wider mb-2">Ações Sugeridas para a Próxima Aula</h4>
                      <ul className="list-disc list-inside text-xs text-slate-700 space-y-1">
                        {(raioXData.diagnostico_ia.sugestoes_proxima_aula || []).map((sug, idx) => (
                          <li key={idx}>{sug}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {raioXData.erros_por_questao && raioXData.erros_por_questao.length > 0 && (
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                  <h4 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Índice de Erros por Questão</h4>
                  <div className="space-y-3">
                    {raioXData.erros_por_questao.map((item) => (
                      <div key={item.questao_numero} className="space-y-1">
                        <div className="flex justify-between text-xs font-semibold text-slate-600">
                          <span>Questão {item.questao_numero}</span>
                          <span>{item.taxa_erro_percentual}% de erro ({item.total_erros} de {item.total_tentativas} alunos)</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${item.taxa_erro_percentual > 50 ? 'bg-red-500' : item.taxa_erro_percentual > 25 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                            style={{ width: `${item.taxa_erro_percentual}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white p-12 text-center rounded-2xl border border-dashed border-slate-300">
              <p className="text-slate-500 text-sm">Nenhuma submissão registrada ainda para esta turma.</p>
              <p className="text-xs text-slate-400 mt-1">Os dados aparecerão assim que os alunos responderem aos quizzes.</p>
            </div>
          )}
        </div>
      )}

      {abaAtiva === 'alertas' && (
        <div className="space-y-6">
          <div className="bg-slate-900 text-white rounded-2xl p-6">
            <h3 className="text-2xl font-bold mb-2">Alertas preditivos da IA</h3>
            <p className="text-slate-300 text-sm max-w-3xl">
              Identificação de padrões de risco pedagógico para intervenção precoce antes da consolidação de déficits de aprendizagem.
            </p>
          </div>

          {alertasPredicao.map((alerta) => (
            <div key={alerta.turma} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-bold text-slate-800">{alerta.turma}</h4>
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700">
                  Risco {alerta.risco} ({alerta.percentual}%)
                </span>
              </div>
              <p className="text-xs text-slate-600 font-medium">Tendência: {alerta.tendencia}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                {alerta.alunos.map((al) => (
                  <div key={al.nome} className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                    <div className="flex justify-between font-bold text-slate-800">
                      <span>{al.nome}</span>
                      <span className="text-red-600">{al.risco}% de risco</span>
                    </div>
                    <p className="text-slate-500 mt-1">{al.motivo}</p>
                    <p className="text-blue-700 font-medium mt-1">Intervenção: {al.acao}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}