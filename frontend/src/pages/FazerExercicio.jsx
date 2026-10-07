import { API_BASE, apiFetch } from '../api';
import React, { useEffect, useState, useRef } from 'react';
import { BookOpen, Sparkles, HelpCircle, CheckCircle, AlertTriangle, ArrowRight, ArrowLeft, Trophy, Award, History, MessageSquare, X, Send, Target } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function FazerExercicio({ emailAluno = 'aluno@educollab.demo', onNavegar }) {
  const [fase, setFase] = useState('inicio');
  const [quizzesDisponiveis, setQuizzesDisponiveis] = useState([]);
  const [quizAtual, setQuizAtual] = useState(null);
  const [respostas, setRespostas] = useState({});
  const [questaoAtualIdx, setQuestaoAtualIdx] = useState(0);
  const [loading, setLoading] = useState(false);
  const [feedbackIA, setFeedbackIA] = useState(null);
  const [notaCalculada, setNotaCalculada] = useState(0);
  const [dicaSocratica, setDicaSocratica] = useState(null);
  const [loadingDica, setLoadingDica] = useState(false);
  const [historico, setHistorico] = useState([]);
  const [loadingHistorico, setLoadingHistorico] = useState(false);

  // Chat do Tutor
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([{ role: 'assistant', content: 'Olá! Sou seu Tutor IA. Como posso ajudar você hoje?' }]);
  const [chatInput, setChatInput] = useState('');
  const [loadingChat, setLoadingChat] = useState(false);
  const chatEndRef = useRef(null);

  const quizPadrao = {
    id: 1,
    tema: 'Frações e Equivalências',
    objetivo: 'Compreender a simplificação e equivalência de frações ordinárias.',
    perguntas: [
      { pergunta: 'Qual é a forma irredutível da fração 4/8?', opcoes: ['1/4', '1/2', '2/3', '4/4'], resposta_correta: '1/2' },
      { pergunta: 'Se uma pizza for dividida em 6 pedaços e você comer 3, qual fração representa a parte comida?', opcoes: ['3/6 ou 1/2', '1/3', '2/6', '3/4'], resposta_correta: '3/6 ou 1/2' },
    ],
  };

  const carregarQuizzesTurma = async () => {
    try {
      const response = await apiFetch(`${API_BASE}/aluno/conteudo-turma?email_aluno=${emailAluno}`);
      const data = await response.json();
      const listaQuizzes = (data?.quizzes || []).map((q) => ({
        id: q.id,
        tema: q.quiz?.tema || q.tema || 'Quiz da Turma',
        objetivo: q.quiz?.objetivo || q.objetivo || '',
        perguntas: q.quiz?.perguntas || [],
      })).filter((q) => q.perguntas && q.perguntas.length > 0);

      setQuizzesDisponiveis(listaQuizzes.length > 0 ? listaQuizzes : [quizPadrao]);
    } catch (error) {
      setQuizzesDisponiveis([quizPadrao]);
    }
  };

  const carregarHistorico = async () => {
    setLoadingHistorico(true);
    try {
      const response = await apiFetch(`${API_BASE}/aluno/historico-submissoes?email_aluno=${emailAluno}`);
      const data = await response.json();
      setHistorico(data?.submissoes || []);
    } catch (error) {} finally {
      setLoadingHistorico(false);
    }
  };

  useEffect(() => {
    carregarQuizzesTurma();
    carregarHistorico();
  }, [emailAluno]);

  useEffect(() => {
    if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isChatOpen]);

  const enviarMensagemChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || loadingChat) return;

    const userMsg = { role: 'user', content: chatInput };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput('');
    setLoadingChat(true);

    try {
      const payloadHist = chatMessages.filter(m => m.role !== 'assistant' || m.content !== 'Olá! Sou seu Tutor IA. Como posso ajudar você hoje?');
      const response = await apiFetch(`${API_BASE}/aluno/chat-tutor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensagem: userMsg.content, historico: payloadHist }),
      });
      const data = await response.json();
      setChatMessages((prev) => [...prev, { role: 'assistant', content: data.resposta || 'Não consegui processar agora.' }]);
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: 'Erro de conexão com o Tutor.' }]);
    } finally {
      setLoadingChat(false);
    }
  };

  const gerarRevisao = async (temaFalho) => {
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/aluno/gerar-revisao`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tema: temaFalho })
      });
      const data = await response.json();
      if (data.quiz && data.quiz.perguntas) {
        setQuizAtual({ ...data.quiz, tema: `Revisão: ${data.quiz.tema}` });
        setRespostas({});
        setQuestaoAtualIdx(0);
        setFase('quiz');
      }
    } catch(e) {} finally {
      setLoading(false);
    }
  };

  const iniciarQuiz = (quizSelecionado) => {
    setQuizAtual(quizSelecionado || quizPadrao);
    setRespostas({});
    setQuestaoAtualIdx(0);
    setDicaSocratica(null);
    setFeedbackIA(null);
    setFase('quiz');
  };

  const pedirDicaSocratica = async () => {
    const questao = quizAtual?.perguntas[questaoAtualIdx];
    const respostaAtual = respostas[questaoAtualIdx] || 'Ainda não escolhi com certeza';

    setLoadingDica(true);
    try {
      const response = await apiFetch(`${API_BASE}/aluno/pedir-dica`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta: questao.pergunta, resposta_aluno: respostaAtual, tema: quizAtual.tema }),
      });
      const data = await response.json();
      setDicaSocratica(data);
    } catch (error) {} finally {
      setLoadingDica(false);
    }
  };

  const handleSubmissao = async () => {
    if (!quizAtual) return;
    setLoading(true);

    const perguntas = quizAtual.perguntas || [];
    let acertos = 0;
    const listaRespostas = [];
    const listaGabarito = [];

    perguntas.forEach((q, idx) => {
      const respostaDada = respostas[idx] || 'Sem resposta';
      listaRespostas.push(respostaDada);
      listaGabarito.push(q.resposta_correta);
      if (respostaDada === q.resposta_correta) acertos++;
    });

    const notaCalculadaFinal = Math.round((acertos / perguntas.length) * 10 * 10) / 10;
    setNotaCalculada(notaCalculadaFinal);

    try {
      const response = await apiFetch(`${API_BASE}/aluno/feedback-quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_exercicio: `QUIZ_${quizAtual.id || Date.now()}`,
          email_aluno: emailAluno,
          quiz_id: quizAtual.id || null,
          nota_final: notaCalculadaFinal,
          respostas_aluno: listaRespostas,
          gabarito_oficial: listaGabarito,
        }),
      });
      const data = await response.json();
      setFeedbackIA(data.feedback_ia);
      setFase('feedback');
      await carregarHistorico();
    } catch (error) {
      setFase('feedback');
    } finally {
      setLoading(false);
    }
  };

  // Preparar dados do Gráfico
  const chartData = [...historico].reverse().map((sub, i) => ({
    name: `Q${i+1}`,
    nota: sub.nota_final
  }));
  const mediaNotas = historico.length ? (historico.reduce((acc, curr) => acc + curr.nota_final, 0) / historico.length).toFixed(1) : 0;
  const pontosXP = historico.length * 50;

  // Encontrar tópicos para revisão (nota < 7)
  const sugestoesRevisao = historico.filter(h => h.nota_final < 7.0).slice(0, 2);

  return (
    <div className="max-w-5xl mx-auto space-y-6 relative pb-20">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md">
            Espaço do Aluno
          </span>
          <h2 className="text-3xl font-bold text-slate-800 mt-2">Sua Jornada de Aprendizado</h2>
        </div>
        <div className="flex items-center space-x-2">
          <button onClick={() => setFase('inicio')} className={`px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${fase === 'inicio' ? 'bg-blue-600 text-white' : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'}`}>
            Painel Principal
          </button>
        </div>
      </div>

      {fase === 'inicio' && (
        <div className="space-y-6">
          {/* Gamificação e Gráfico */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 flex flex-col gap-4">
              <div className="bg-gradient-to-br from-indigo-600 to-blue-700 rounded-3xl p-6 text-white shadow-lg relative overflow-hidden">
                <div className="relative z-10">
                  <h3 className="text-lg font-bold opacity-90">Seu Progresso</h3>
                  <div className="mt-4 flex items-baseline space-x-2">
                    <span className="text-4xl font-extrabold">{pontosXP}</span>
                    <span className="text-sm font-medium opacity-80">XP Acumulado</span>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs opacity-70 uppercase tracking-wider">Atividades</p>
                      <p className="text-xl font-bold">{historico.length}</p>
                    </div>
                    <div>
                      <p className="text-xs opacity-70 uppercase tracking-wider">Média Geral</p>
                      <p className="text-xl font-bold flex items-center gap-1">
                        {mediaNotas} <Target size={16} />
                      </p>
                    </div>
                  </div>
                </div>
                <Sparkles className="absolute -bottom-4 -right-4 w-32 h-32 text-white opacity-10" />
              </div>

              {sugestoesRevisao.length > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 shadow-sm">
                  <h4 className="font-bold text-amber-900 flex items-center gap-2 mb-3">
                    <AlertTriangle size={18} />
                    Revisão Inteligente
                  </h4>
                  <p className="text-xs text-amber-800 mb-4">A IA notou que você pode melhorar nestes tópicos. Quer treinar agora?</p>
                  <div className="space-y-2">
                    {sugestoesRevisao.map(sub => (
                      <button key={sub.id} onClick={() => gerarRevisao("Conceitos do quiz anterior")} className="w-full text-left bg-white border border-amber-300 p-3 rounded-xl text-sm font-medium text-amber-900 hover:bg-amber-100 transition flex justify-between items-center">
                        <span className="truncate">Treino Focado</span>
                        <ArrowRight size={14} />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="lg:col-span-2 bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col">
              <h3 className="text-lg font-bold text-slate-800 mb-6">Evolução nas Avaliações</h3>
              <div className="flex-1 min-h-[200px]">
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={10} />
                      <YAxis domain={[0, 10]} axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dx={-10} />
                      <Tooltip contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                      <Line type="monotone" dataKey="nota" stroke="#4f46e5" strokeWidth={4} dot={{r: 6, fill: '#4f46e5', strokeWidth: 2, stroke: '#fff'}} activeDot={{r: 8}} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                    Complete atividades para ver seu gráfico de evolução.
                  </div>
                )}
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-bold text-slate-800 mb-4">Atividades Pendentes da Turma</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {quizzesDisponiveis.map((q, idx) => (
                <div key={q.id || idx} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between group">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md">
                      {q.perguntas?.length || 0} Questões
                    </span>
                    <h4 className="text-lg font-bold text-slate-800 mt-3 group-hover:text-blue-600 transition-colors">{q.tema}</h4>
                    <p className="text-xs text-slate-500 mt-2 line-clamp-2">{q.objetivo}</p>
                  </div>
                  <button onClick={() => iniciarQuiz(q)} className="mt-5 w-full bg-slate-50 hover:bg-blue-50 text-blue-700 font-semibold py-2.5 rounded-xl text-sm flex items-center justify-center gap-2 border border-slate-200 hover:border-blue-300 transition-colors">
                    Iniciar Atividade <ArrowRight size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {fase === 'quiz' && quizAtual?.perguntas && (
        <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <button onClick={() => setFase('inicio')} className="text-slate-500 hover:text-slate-800 text-sm font-medium flex items-center gap-1">
              <ArrowLeft size={16} /> Sair
            </button>
            <div className="flex-1 px-8">
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-blue-600 h-full transition-all" style={{ width: `${((questaoAtualIdx + 1) / quizAtual.perguntas.length) * 100}%` }} />
              </div>
            </div>
            <span className="text-sm font-bold text-blue-600">
              {questaoAtualIdx + 1} / {quizAtual.perguntas.length}
            </span>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <h3 className="text-xl font-bold text-slate-800 mb-6 leading-relaxed">
              {quizAtual.perguntas[questaoAtualIdx].pergunta}
            </h3>
            <div className="space-y-3">
              {quizAtual.perguntas[questaoAtualIdx].opcoes?.map((opcao, idx) => (
                <label key={idx} className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all ${respostas[questaoAtualIdx] === opcao ? 'border-blue-600 bg-blue-50 text-blue-900' : 'border-slate-100 bg-white hover:border-slate-300 hover:bg-slate-50'}`}>
                  <input type="radio" name={`q_${questaoAtualIdx}`} checked={respostas[questaoAtualIdx] === opcao} onChange={() => { setRespostas({ ...respostas, [questaoAtualIdx]: opcao }); setDicaSocratica(null); }} className="w-5 h-5 text-blue-600" />
                  <span className="ml-4 font-medium">{opcao}</span>
                </label>
              ))}
            </div>

            <div className="mt-8 pt-6 border-t border-slate-100 flex items-center justify-between">
              <button onClick={pedirDicaSocratica} disabled={loadingDica} className="text-amber-600 hover:bg-amber-50 px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition-colors">
                <Sparkles size={18} /> {loadingDica ? 'Pensando...' : 'Pedir Dica IA'}
              </button>
              
              <div className="flex gap-2">
                <button onClick={() => setQuestaoAtualIdx(Math.max(0, questaoAtualIdx - 1))} disabled={questaoAtualIdx === 0} className="px-5 py-2.5 rounded-xl text-sm font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 transition-colors">
                  Anterior
                </button>
                {questaoAtualIdx < quizAtual.perguntas.length - 1 ? (
                  <button onClick={() => setQuestaoAtualIdx(questaoAtualIdx + 1)} className="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 transition-colors">
                    Próxima
                  </button>
                ) : (
                  <button onClick={handleSubmissao} disabled={loading} className="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition-colors shadow-lg shadow-emerald-200">
                    {loading ? 'Analisando...' : 'Finalizar'}
                  </button>
                )}
              </div>
            </div>

            {dicaSocratica && (
              <div className="mt-6 bg-amber-50 border border-amber-200 rounded-2xl p-5 animate-fadeIn">
                <h4 className="text-amber-800 font-bold text-sm mb-2 flex items-center gap-2"><Sparkles size={16}/> Dica Socrática</h4>
                <p className="text-amber-900 text-sm leading-relaxed">{dicaSocratica.dica}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {fase === 'feedback' && feedbackIA && (
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="bg-white p-8 rounded-3xl border border-slate-200 text-center">
            <Trophy size={48} className="mx-auto text-yellow-400 mb-4" />
            <h3 className="text-3xl font-black text-slate-800 mb-2">Quiz Concluído!</h3>
            <div className="text-5xl font-black text-blue-600 my-6">{notaCalculada}</div>
            <button onClick={() => setFase('inicio')} className="bg-slate-900 text-white px-8 py-3 rounded-xl font-bold hover:bg-slate-800 transition">
              Voltar ao Início
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-emerald-50 border border-emerald-200 p-6 rounded-2xl">
              <h4 className="text-emerald-800 font-bold flex items-center gap-2 mb-3"><CheckCircle size={20}/> Pontos Fortes</h4>
              <ul className="space-y-2 text-sm text-emerald-900">
                {(feedbackIA.pontos_fortes || []).map((p, i) => <li key={i}>• {p}</li>)}
              </ul>
            </div>
            <div className="bg-amber-50 border border-amber-200 p-6 rounded-2xl">
              <h4 className="text-amber-800 font-bold flex items-center gap-2 mb-3"><AlertTriangle size={20}/> Para Melhorar</h4>
              <ul className="space-y-2 text-sm text-amber-900">
                {(feedbackIA.pontos_atencao || []).map((p, i) => <li key={i}>• {p}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}

      

    </div>
  );
}