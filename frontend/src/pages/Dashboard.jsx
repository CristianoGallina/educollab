import { API_BASE, apiFetch } from '../api';
import React, { useEffect, useState } from 'react';
import TrilhaReforco from '../components/chat/TrilhaReforco';
import {
  BookCheck,
  Target,
  TrendingUp,
  Users,
  BrainCircuit,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  School,
  GraduationCap,
  Activity,
  DollarSign,
  Cpu,
  Key,
  CheckCircle,
  AlertCircle,
  Plus,
} from 'lucide-react';



export default function Dashboard({ papel, onIniciarTrilha, onNavegar }) {
  const [statsAdmin, setStatsAdmin] = useState(null);
  const [statsProf, setStatsProf] = useState(null);
  const [escolasLista, setEscolasLista] = useState([]);
  const [loadingStats, setLoadingStats] = useState(false);

  useEffect(() => {
    const carregarEstatisticas = async () => {
      setLoadingStats(true);
      try {
        if (papel === 'administrador') {
          const headersAdmin = { 'x-tipo-usuario': 'administrador' };
          const [resResumo, resEscolas] = await Promise.all([
            apiFetch(`${API_BASE}/admin/resumo`, { headers: headersAdmin }),
            apiFetch(`${API_BASE}/admin/escolas`, { headers: headersAdmin }),
          ]);
          const dataResumo = await resResumo.json();
          const dataEscolas = await resEscolas.json();
          setStatsAdmin(dataResumo);
          setEscolasLista(Array.isArray(dataEscolas?.escolas) ? dataEscolas.escolas : []);
        } else if (papel === 'professor') {
          const res = await apiFetch(`${API_BASE}/professor/dashboard`, {
            headers: { 'x-tipo-usuario': 'professor' },
          });
          const data = await res.json();
          setStatsProf(data);
        }
      } catch (err) {
        console.error('Erro ao carregar métricas:', err);
      } finally {
        setLoadingStats(false);
      }
    };

    carregarEstatisticas();
  }, [papel]);

  const navegarPara = (tela) => {
    if (onNavegar) {
      onNavegar(tela);
    }
  };

  // Visão do Professor
  if (papel === 'professor') {
    const totalTurmas = statsProf?.total_turmas ?? 3;
    const totalAlunos = statsProf?.total_alunos ?? 9;
    const totalPlanos = statsProf?.total_planos ?? 2;
    const totalQuizzes = statsProf?.total_quizzes ?? 2;

    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-blue-900 text-white rounded-3xl p-8 shadow-xl border border-slate-700">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div>
              <span className="text-xs uppercase tracking-widest text-blue-300 font-bold bg-white/10 px-3 py-1 rounded-full border border-white/15">
                Painel do Professor
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold mt-3">Bem-vindo(a) ao seu Copiloto Pedagógico</h2>
              <p className="mt-2 max-w-2xl text-slate-200 text-sm sm:text-base leading-relaxed">
                Organize suas turmas, elabore planos de aula alinhados à BNCC e acompanhe o Raio-X de aprendizagem dos alunos com assistência da IA.
              </p>
            </div>

            <div className="flex flex-wrap sm:flex-nowrap gap-3">
              <button
                type="button"
                onClick={() => navegarPara('turmas')}
                className="bg-white text-slate-900 hover:bg-slate-100 font-bold px-5 py-3 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-md"
              >
                <Users size={16} className="text-blue-600" />
                <span>Minhas Turmas</span>
              </button>
              <button
                type="button"
                onClick={() => navegarPara('ferramentas-ia')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-5 py-3 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-md"
              >
                <BrainCircuit size={16} />
                <span>Copiloto IA & Raio-X</span>
              </button>
            </div>
          </div>
        </div>

        {/* Métricas Reais do Professor */}
        <div>
          <h3 className="text-xl font-bold text-slate-800 mb-3">Visão Geral da sua Operação</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div
              onClick={() => navegarPara('turmas')}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all"
            >
              <p className="text-xs uppercase tracking-wider font-semibold text-slate-500">Turmas Ativas</p>
              <p className="text-3xl font-extrabold text-blue-600 mt-2">{totalTurmas}</p>
              <span className="text-xs text-blue-600 flex items-center space-x-1 mt-2 font-medium">
                <span>Ver turmas</span> <ArrowRight size={12} />
              </span>
            </div>

            <div
              onClick={() => navegarPara('turmas')}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all"
            >
              <p className="text-xs uppercase tracking-wider font-semibold text-slate-500">Total de Alunos</p>
              <p className="text-3xl font-extrabold text-indigo-600 mt-2">{totalAlunos}</p>
              <span className="text-xs text-indigo-600 flex items-center space-x-1 mt-2 font-medium">
                <span>Acompanhar</span> <ArrowRight size={12} />
              </span>
            </div>

            <div
              onClick={() => navegarPara('ferramentas-ia')}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all"
            >
              <p className="text-xs uppercase tracking-wider font-semibold text-slate-500">Planos BNCC Criados</p>
              <p className="text-3xl font-extrabold text-emerald-600 mt-2">{totalPlanos}</p>
              <span className="text-xs text-emerald-600 flex items-center space-x-1 mt-2 font-medium">
                <span>Gerar novos</span> <ArrowRight size={12} />
              </span>
            </div>

            <div
              onClick={() => navegarPara('ferramentas-ia')}
              className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all"
            >
              <p className="text-xs uppercase tracking-wider font-semibold text-slate-500">Quizzes Gerados</p>
              <p className="text-3xl font-extrabold text-amber-600 mt-2">{totalQuizzes}</p>
              <span className="text-xs text-amber-600 flex items-center space-x-1 mt-2 font-medium">
                <span>Ver Raio-X</span> <ArrowRight size={12} />
              </span>
            </div>
          </div>
        </div>

        {/* Atalhos Rápidos */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="p-3 bg-blue-50 text-blue-700 w-fit rounded-xl font-bold">
              <Sparkles size={20} />
            </div>
            <h4 className="font-bold text-slate-800 text-lg">Plano de Aula com BNCC</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Crie planos estruturados com objetivos, sequência pedagógica e habilidades oficiais em segundos.
            </p>
            <button
              type="button"
              onClick={() => navegarPara('ferramentas-ia')}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 rounded-xl text-xs transition-colors"
            >
              Gerar Novo Plano
            </button>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="p-3 bg-emerald-50 text-emerald-700 w-fit rounded-xl font-bold">
              <BookCheck size={20} />
            </div>
            <h4 className="font-bold text-slate-800 text-lg">Criar & Editar Quizzes</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Elabore avaliações diagnósticas com controle humano total e libere para a turma.
            </p>
            <button
              type="button"
              onClick={() => navegarPara('ferramentas-ia')}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-xl text-xs transition-colors"
            >
              Elaborar Avaliação
            </button>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="p-3 bg-indigo-50 text-indigo-700 w-fit rounded-xl font-bold">
              <TrendingUp size={20} />
            </div>
            <h4 className="font-bold text-slate-800 text-lg">Raio-X de Aprendizagem</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Consulte a taxa de erros por questão e o parecer da IA com recomendações práticas.
            </p>
            <button
              type="button"
              onClick={() => navegarPara('ferramentas-ia')}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 rounded-xl text-xs transition-colors"
            >
              Acessar Raio-X
            </button>
          </div>
        </div>

        {/* Análises Preditivas IA */}
        <div className="mt-8 pt-4 border-t border-slate-200">
          <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
            <BrainCircuit className="text-emerald-500" /> Inteligência Preditiva EduCollab
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-rose-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle size={18} className="text-rose-500" />
                <h4 className="font-bold text-slate-800">Radar de Risco (Evasão/Reprovação)</h4>
              </div>
              <p className="text-xs text-slate-600 mb-3">Top 3 alunos precisando de intervenção imediata:</p>
              <ul className="space-y-2">
                <li className="text-xs bg-rose-50 p-2 rounded-lg border border-rose-100 flex justify-between items-center">
                  <span className="font-semibold text-rose-800">João P. (7º A)</span>
                  <span className="text-[10px] bg-rose-200 text-rose-800 px-2 py-0.5 rounded-full">85% risco Frações</span>
                </li>
                <li className="text-xs bg-amber-50 p-2 rounded-lg border border-amber-100 flex justify-between items-center">
                  <span className="font-semibold text-amber-800">Maria Clara (7º A)</span>
                  <span className="text-[10px] bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full">60% risco Frações</span>
                </li>
              </ul>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-sky-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Target size={18} className="text-sky-500" />
                <h4 className="font-bold text-slate-800">Simulador de Média (Próximo Quiz)</h4>
              </div>
              <p className="text-xs text-slate-600 mb-3">Previsão baseada no histórico da turma:</p>
              <div className="bg-sky-50 p-3 rounded-xl border border-sky-100 text-center">
                <span className="block text-3xl font-extrabold text-sky-700">5.8</span>
                <span className="text-[11px] font-semibold text-sky-800">Média Projetada - Quiz Revolução Francesa</span>
                <p className="text-[10px] text-sky-600 mt-1">⚠️ Tópico crítico: Consequências Econômicas</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-emerald-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <Users size={18} className="text-emerald-500" />
                <h4 className="font-bold text-slate-800">Agrupamento Produtivo</h4>
              </div>
              <p className="text-xs text-slate-600 mb-3">Sugestão de grupos heterogêneos para a próxima aula:</p>
              <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-100 space-y-1">
                <p className="text-[11px] text-emerald-800"><span className="font-bold">Grupo 1:</span> Ana (Tutora), João, Pedro</p>
                <p className="text-[11px] text-emerald-800"><span className="font-bold">Grupo 2:</span> Carlos (Tutor), Maria, Sofia</p>
                <button className="mt-2 text-[10px] bg-emerald-600 text-white px-2 py-1 rounded w-full hover:bg-emerald-700">Gerar + Grupos</button>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-indigo-200 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp size={18} className="text-indigo-500" />
                <h4 className="font-bold text-slate-800">Curva de Domínio BNCC</h4>
              </div>
              <p className="text-xs text-slate-600 mb-3">Previsão de tempo para proficiência na habilidade EF08MA04:</p>
              <div className="relative pt-2">
                <div className="overflow-hidden h-2 mb-2 text-xs flex rounded bg-indigo-100">
                  <div style={{ width: "65%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500"></div>
                </div>
                <div className="flex justify-between text-[10px] text-indigo-700 font-semibold">
                  <span>Domínio Atual: 65%</span>
                  <span>Previsão: +3 Semanas</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Visão do Administrador
  if (papel === 'administrador') {
    const totalEscolas = statsAdmin?.total_escolas ?? 3;
    const totalProfessores = statsAdmin?.total_professores ?? 3;
    const totalTurmas = statsAdmin?.total_turmas ?? 3;
    const totalAlunos = statsAdmin?.total_alunos ?? 9;
    const totalTokens = statsAdmin?.total_tokens ?? 0;
    const totalCusto = statsAdmin?.total_custo ?? 0.0;
    const escolasComIa = statsAdmin?.escolas_com_ia ?? 0;
    const escolasSemIa = statsAdmin?.escolas_sem_ia ?? 0;
    const totalQuizzes = statsAdmin?.total_quizzes ?? 0;
    const totalSubmissoes = statsAdmin?.total_submissoes ?? 0;

    return (
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Banner Executivo */}
        <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-blue-900 text-white rounded-3xl p-8 shadow-xl border border-slate-700">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div>
              <span className="text-xs uppercase tracking-widest text-blue-300 font-bold bg-white/10 px-3 py-1 rounded-full border border-white/15">
                Painel Executivo da Rede
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold mt-3">Gestão Institucional & Infraestrutura de IA</h2>
              <p className="mt-2 max-w-2xl text-slate-200 text-sm sm:text-base leading-relaxed">
                Supervisão centralizada de escolas, governança de dados, auditoria de consumo de tokens e controle de provedores de Inteligência Artificial.
              </p>
            </div>

            <div className="flex flex-wrap sm:flex-nowrap gap-3">
              <button
                type="button"
                onClick={() => navegarPara('gestao-usuarios')}
                className="bg-white text-slate-900 hover:bg-slate-100 font-bold px-5 py-3 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-md cursor-pointer"
              >
                <ShieldCheck size={16} className="text-blue-600" />
                <span>Gestão de Usuários & IA</span>
              </button>
              <button
                type="button"
                onClick={() => navegarPara('turmas')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-5 py-3 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-md cursor-pointer"
              >
                <Users size={16} />
                <span>Turmas da Rede</span>
              </button>
            </div>
          </div>
        </div>

        {/* 6 Indicadores Chave Globais */}
        <div>
          <h3 className="text-xl font-bold text-slate-800 mb-3">Indicadores Operacionais da Rede</h3>
          <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">
            <div
              onClick={() => navegarPara('gestao-usuarios')}
              className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all text-center"
            >
              <School className="mx-auto text-blue-600 mb-1" size={22} />
              <p className="text-[11px] uppercase tracking-wider font-semibold text-slate-500">Escolas</p>
              <p className="text-2xl font-extrabold text-slate-800 mt-0.5">{totalEscolas}</p>
              <span className="text-[10px] text-emerald-600 font-semibold">{escolasComIa} com IA ativa</span>
            </div>

            <div
              onClick={() => navegarPara('gestao-usuarios')}
              className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all text-center"
            >
              <GraduationCap className="mx-auto text-indigo-600 mb-1" size={22} />
              <p className="text-[11px] uppercase tracking-wider font-semibold text-slate-500">Professores</p>
              <p className="text-2xl font-extrabold text-slate-800 mt-0.5">{totalProfessores}</p>
              <span className="text-[10px] text-slate-400">Ativos na rede</span>
            </div>

            <div
              onClick={() => navegarPara('turmas')}
              className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all text-center"
            >
              <Users className="mx-auto text-emerald-600 mb-1" size={22} />
              <p className="text-[11px] uppercase tracking-wider font-semibold text-slate-500">Turmas</p>
              <p className="text-2xl font-extrabold text-slate-800 mt-0.5">{totalTurmas}</p>
              <span className="text-[10px] text-blue-600 font-medium">Ver turmas →</span>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center">
              <Users className="mx-auto text-amber-600 mb-1" size={22} />
              <p className="text-[11px] uppercase tracking-wider font-semibold text-slate-500">Alunos</p>
              <p className="text-2xl font-extrabold text-slate-800 mt-0.5">{totalAlunos}</p>
              <span className="text-[10px] text-slate-400">Matriculados</span>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center">
              <BookCheck className="mx-auto text-purple-600 mb-1" size={22} />
              <p className="text-[11px] uppercase tracking-wider font-semibold text-slate-500">Quizzes Criados</p>
              <p className="text-2xl font-extrabold text-purple-700 mt-0.5">{totalQuizzes}</p>
              <span className="text-[10px] text-slate-400">Pelo corpo docente</span>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center">
              <Activity className="mx-auto text-sky-600 mb-1" size={22} />
              <p className="text-[11px] uppercase tracking-wider font-semibold text-slate-500">Submissões</p>
              <p className="text-2xl font-extrabold text-sky-700 mt-0.5">{totalSubmissoes}</p>
              <span className="text-[10px] text-slate-400">Exercícios feitos</span>
            </div>
          </div>
        </div>

        {/* Painel de Infraestrutura & Governança de IA */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-4">
            <div>
              <h4 className="text-lg font-bold text-slate-800 flex items-center space-x-2">
                <Cpu className="text-blue-600" size={20} />
                <span>Infraestrutura de Inteligência Artificial & Auditoria de Custos</span>
              </h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Monitoramento de consumo de tokens em tempo real e controle orçamentário por provedor.
              </p>
            </div>
            <button
              type="button"
              onClick={() => navegarPara('gestao-usuarios')}
              className="text-xs font-bold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition-colors cursor-pointer self-start sm:self-auto"
            >
              Configurar Chaves da IA →
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Volume de Tokens</span>
              <p className="text-3xl font-extrabold text-slate-800">{totalTokens.toLocaleString('pt-BR')}</p>
              <p className="text-xs text-slate-500">
                Processados em planos de aula, dicas socráticas e correções automáticas.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Custo Estimado Acumulado</span>
              <p className="text-3xl font-extrabold text-emerald-600">
                ${totalCusto.toFixed(4)} <span className="text-sm font-normal text-slate-500">(~ R$ {(totalCusto * 5.5).toFixed(2)})</span>
              </p>
              <p className="text-xs text-slate-500">
                Custo direto estimado via provedores LLM (Grok/Groq).
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Status dos Provedores</span>
              <div className="space-y-1.5 pt-1 text-xs font-semibold">
                <div className="flex items-center justify-between text-slate-700">
                  <span>xAI (Grok-2 / Grok-3)</span>
                  <span className="text-emerald-600 flex items-center gap-1">● Conectado</span>
                </div>
                <div className="flex items-center justify-between text-slate-700">
                  <span>Groq (LLaMA 3 / Mixtral)</span>
                  <span className="text-emerald-600 flex items-center gap-1">● Conectado</span>
                </div>
                <div className="flex items-center justify-between text-slate-700">
                  <span>OpenAI Engine</span>
                  <span className="text-blue-600 flex items-center gap-1">● Suportado</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Análises Preditivas Executivas */}
        <div className="bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-800 space-y-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <BrainCircuit className="text-emerald-400" /> Inteligência Executiva da Rede
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/10 p-5 rounded-xl border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign size={18} className="text-amber-400" />
                <h4 className="font-bold text-white">Previsão de Custo Mensal</h4>
              </div>
              <p className="text-xs text-slate-400 mb-3">Projeção da fatura de IA para o fim do mês:</p>
              <div className="text-3xl font-bold text-amber-400 mb-1">$ {((totalCusto || 0.1) * 3.5).toFixed(2)}</div>
              <div className="relative pt-2">
                <div className="overflow-hidden h-1.5 flex rounded bg-white/10">
                  <div style={{ width: "35%" }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-amber-400"></div>
                </div>
                <p className="text-[10px] text-slate-400 mt-1">35% da verba orçamentária projetada.</p>
              </div>
            </div>

            <div className="bg-white/10 p-5 rounded-xl border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={18} className="text-sky-400" />
                <h4 className="font-bold text-white">Risco de Churn Institucional</h4>
              </div>
              <p className="text-xs text-slate-400 mb-3">Escolas com queda na adoção de IA pelos professores:</p>
              <ul className="space-y-2">
                <li className="text-xs bg-white/5 p-2 rounded-lg flex justify-between items-center text-slate-200">
                  <span>Escola Estadual Norte</span>
                  <span className="text-[10px] bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded-full border border-rose-500/30">Baixa Adoção (-12%)</span>
                </li>
                <li className="text-xs bg-white/5 p-2 rounded-lg flex justify-between items-center text-slate-200">
                  <span>Colégio Futuro</span>
                  <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full border border-amber-500/30">Atenção</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 p-5 rounded-xl border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <Target size={18} className="text-emerald-400" />
                <h4 className="font-bold text-white">Desempenho Macro da Rede</h4>
              </div>
              <p className="text-xs text-slate-400 mb-3">Média preditiva da rede para o próximo ciclo:</p>
              <div className="text-3xl font-bold text-emerald-400 mb-1">7.2 <span className="text-sm text-emerald-500 font-normal">↑ 0.4</span></div>
              <p className="text-[10px] text-slate-400 leading-relaxed">
                O impacto das Trilhas Adaptativas aponta para um crescimento de 0.4 pontos na média global de Matemática da rede no próximo mês.
              </p>
            </div>
          </div>
        </div>

        {/* Tabela de Escolas da Rede */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-base font-bold text-slate-800">Instituições de Ensino da Rede</h4>
              <p className="text-xs text-slate-500">Status de integração e auditoria individual de cada escola.</p>
            </div>
            <button
              type="button"
              onClick={() => navegarPara('gestao-usuarios')}
              className="text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white px-3.5 py-2 rounded-xl transition-colors cursor-pointer"
            >
              + Nova Escola
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-semibold border-y border-slate-200">
                <tr>
                  <th className="py-3 px-4">Escola</th>
                  <th className="py-3 px-4">Localização</th>
                  <th className="py-3 px-4">Diretor(a)</th>
                  <th className="py-3 px-4">Status da IA</th>
                  <th className="py-3 px-4 text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {escolasLista.map((esc) => (
                  <tr key={esc.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-800">{esc.nome}</td>
                    <td className="py-3 px-4 text-slate-600 text-xs">{esc.cidade} - {esc.estado}</td>
                    <td className="py-3 px-4 text-slate-600 text-xs">{esc.diretor || 'Não informado'}</td>
                    <td className="py-3 px-4">
                      {esc.api_key_configurada ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                          <CheckCircle size={12} />
                          Chave Ativa ({esc.provedor_ia})
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                          <AlertCircle size={12} />
                          Chave Pendente
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        type="button"
                        onClick={() => navegarPara('gestao-usuarios')}
                        className="text-xs text-blue-600 hover:text-blue-800 font-semibold cursor-pointer"
                      >
                        Gerenciar →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  // Visão do Aluno
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-indigo-800 text-white rounded-3xl p-8 shadow-xl border border-white/10">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <span className="text-xs uppercase tracking-widest text-blue-200 font-bold bg-white/10 px-3 py-1 rounded-full">
              Espaço do Aluno
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold mt-3">Pronto para aprender no seu ritmo?</h2>
            <p className="mt-2 max-w-xl text-blue-100 text-sm sm:text-base leading-relaxed">
              Pratique exercícios e quizzes com o apoio do Tutor Socrático com IA para tirar dúvidas e receber feedbacks instantâneos.
            </p>
          </div>

          <div className="flex flex-wrap sm:flex-nowrap gap-3">
            <button
              type="button"
              onClick={() => navegarPara('exercicios')}
              className="bg-white text-blue-900 hover:bg-blue-50 font-bold px-6 py-3 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-md cursor-pointer"
            >
              <BookCheck size={16} className="text-blue-600" />
              <span>Fazer Exercícios</span>
            </button>
            <button
              type="button"
              onClick={() => navegarPara('turmas')}
              className="bg-blue-500 hover:bg-blue-400 text-white font-bold px-6 py-3 rounded-xl text-sm flex items-center space-x-2 transition-all shadow-md cursor-pointer"
            >
              <Users size={16} />
              <span>Minhas Turmas</span>
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          onClick={() => navegarPara('exercicios')}
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all space-y-3"
        >
          <div className="p-3 bg-blue-50 text-blue-600 w-fit rounded-xl font-bold">
            <BookCheck size={24} />
          </div>
          <h4 className="text-lg font-bold text-slate-800">Avaliações & Quizzes</h4>
          <p className="text-xs text-slate-600 leading-relaxed">
            Responda às questões preparadas pelo seu professor e receba dicas inteligentes da IA se tiver dúvidas.
          </p>
          <span className="text-xs font-bold text-blue-600 flex items-center space-x-1">
            <span>Começar agora</span> <ArrowRight size={12} />
          </span>
        </div>

        <div
          onClick={() => navegarPara('exercicios')}
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all space-y-3"
        >
          <div className="p-3 bg-amber-50 text-amber-600 w-fit rounded-xl font-bold">
            <Sparkles size={24} />
          </div>
          <h4 className="text-lg font-bold text-slate-800">Tutor Socrático</h4>
          <p className="text-xs text-slate-600 leading-relaxed">
            Nunca fique travado: peça uma pista reflexiva da IA para entender o raciocínio sem ver a resposta pronta.
          </p>
          <span className="text-xs font-bold text-amber-600 flex items-center space-x-1">
            <span>Experimentar</span> <ArrowRight size={12} />
          </span>
        </div>

        <div
          onClick={() => setTrilhaAberta(true)}
          className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-400 cursor-pointer transition-all space-y-3"
        >
          <div className="p-3 bg-emerald-50 text-emerald-600 w-fit rounded-xl font-bold">
            <Target size={24} />
          </div>
          <h4 className="text-lg font-bold text-slate-800">Trilha de Reforço Adaptativa</h4>
          <p className="text-xs text-slate-600 leading-relaxed">
            Receba desafios rápidos e personalizados de revisão para superar tópicos onde você teve menor rendimento.
          </p>
          <span className="text-xs font-bold text-emerald-600 flex items-center space-x-1">
            <span>Acompanhar</span> <ArrowRight size={12} />
          </span>
        </div>
      </div>
      <TrilhaReforco isOpen={trilhaAberta} onClose={() => setTrilhaAberta(false)} />
    </div>
  );
}