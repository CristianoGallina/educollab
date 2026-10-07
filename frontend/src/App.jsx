import React, { useState, useEffect } from 'react';
import { BookOpen, Home, Users, BrainCircuit, UserCircle, ShieldCheck, LogOut } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import MinhasTurmas from './pages/MinhasTurmas';
import FerramentasIA from './pages/FerramentasIA';
import FazerExercicio from './pages/FazerExercicio';
import GestaoUsuarios from './pages/GestaoUsuarios';
import Login from './pages/Login';
import TutorChat from './components/chat/TutorChat';
import CopilotoChat from './components/chat/CopilotoChat';
import AdminCopilotoChat from './components/chat/AdminCopilotoChat';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [usuario, setUsuario] = useState(() => {
    const saved = localStorage.getItem('usuario');
    return saved ? JSON.parse(saved) : null;
  });

  const [telaAtiva, setTelaAtiva] = useState('pitch');
  const [turmaSelecionadaId, setTurmaSelecionadaId] = useState(null);

  const papel = usuario?.tipo || null;

  useEffect(() => {
    const handleUnauthorized = () => {
      setToken(null);
      setUsuario(null);
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
    };

    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, []);

  useEffect(() => {
    // Segurança e Controle de Acesso no Frontend:
    if (telaAtiva === 'ferramentas-ia' && papel !== 'professor') {
      setTelaAtiva('dashboard');
    }
    if (telaAtiva === 'gestao-usuarios' && papel !== 'administrador') {
      setTelaAtiva('dashboard');
    }
    if (telaAtiva === 'exercicios' && papel !== 'aluno') {
      setTelaAtiva('dashboard');
    }
  }, [papel, telaAtiva]);

  const handleLogin = (newToken, newUsuario) => {
    setToken(newToken);
    setUsuario(newUsuario);
    localStorage.setItem('token', newToken);
    localStorage.setItem('usuario', JSON.stringify(newUsuario));
    setTelaAtiva('dashboard');
  };

  const handleLogout = () => {
    setToken(null);
    setUsuario(null);
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    setTelaAtiva('pitch');
  };

  if (!token || !usuario) {
    return <Login onLogin={handleLogin} />;
  }

  const acessarTurma = (turmaId) => {
    setTurmaSelecionadaId(turmaId);
    if (papel === 'aluno') {
      setTelaAtiva('exercicios');
    } else if (papel === 'professor') {
      setTelaAtiva('ferramentas-ia');
    } else {
      setTelaAtiva('turmas');
    }
  };

  const menuItems = [
    { id: 'pitch', label: 'Introdução', icon: Home, roles: ['aluno', 'professor', 'administrador'] },
    { id: 'dashboard', label: 'Dashboard', icon: Home, roles: ['aluno', 'professor', 'administrador'] },
    { id: 'turmas', label: papel === 'administrador' ? 'Turmas da Rede' : 'Minhas Turmas', icon: Users, roles: ['aluno', 'professor', 'administrador'] },
    { id: 'exercicios', label: 'Meus Exercícios', icon: BookOpen, roles: ['aluno'] },
    { id: 'ferramentas-ia', label: 'Copiloto IA & Raio-X', icon: BrainCircuit, roles: ['professor'] },
    { id: 'gestao-usuarios', label: 'Gestão de Usuários & IA', icon: ShieldCheck, roles: ['administrador'] },
  ];

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-400">EduCollab</h1>
          <p className="text-xs text-slate-400 mt-1">IA para educação escolar</p>
          <p className="mt-2 text-[11px] leading-relaxed text-slate-300">
            Organização escolar, apoio ao professor e acompanhamento do aluno em um só ambiente.
          </p>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {menuItems.filter(item => item.roles.includes(papel)).map(item => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTelaAtiva(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${telaAtiva === item.id ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-4 bg-slate-800 m-4 rounded-xl border border-slate-700">
          <div className="flex items-center space-x-3 mb-4 text-sm text-slate-300">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
              <UserCircle size={20} className="text-slate-400" />
            </div>
            <div className="overflow-hidden">
              <p className="font-medium text-white truncate" title={usuario.nome}>{usuario.nome}</p>
              <p className="text-xs text-slate-400 capitalize">{usuario.tipo}</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 bg-slate-900 hover:bg-red-900/50 text-slate-300 hover:text-red-400 py-2 rounded-lg text-sm transition-colors"
          >
            <LogOut size={16} />
            <span>Sair do sistema</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-8">
        {telaAtiva === 'pitch' && (
          <div className="space-y-6">
            <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-sky-900 to-blue-700 p-6 text-white shadow-xl border border-white/10">
              <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
                <div className="max-w-3xl">
                  <p className="text-xs uppercase tracking-[0.3em] text-blue-200">EduCollab</p>
                  <h2 className="text-3xl md:text-4xl font-bold mt-3">A escola com IA para ganhar tempo, melhorar resultados e acompanhar cada aluno com clareza.</h2>
                  <p className="mt-3 text-slate-200 text-sm md:text-base max-w-2xl">
                    EduCollab reúne gestão escolar, apoio ao professor e acompanhamento do aluno em uma mesma plataforma. A IA ajuda a criar planos, avaliações, trilhas e feedbacks, enquanto a escola mantém controle, visão e qualidade pedagógica.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-3 text-sm">
                    <span className="rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-blue-50">Gestão institucional</span>
                    <span className="rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-blue-50">Suporte ao professor</span>
                    <span className="rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-blue-50">Acompanhamento do aluno</span>
                  </div>
                  <div className="mt-6 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => setTelaAtiva('dashboard')}
                      className="bg-white text-slate-900 font-semibold px-5 py-3 rounded-lg shadow-sm hover:bg-slate-100"
                    >
                      Ir para o Dashboard
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 min-w-[260px]">
                  {[
                    ['Escolas', '24'],
                    ['Turmas', '48'],
                    ['Alunos', '1.2k'],
                  ].map(([label, valor]) => (
                    <div key={label} className="rounded-2xl bg-white/10 border border-white/15 p-3 text-center backdrop-blur-sm">
                      <p className="text-xs uppercase tracking-[0.2em] text-blue-100">{label}</p>
                      <p className="text-2xl font-bold mt-2">{valor}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs uppercase tracking-[0.3em] text-sky-700 font-semibold">Boas-vindas</p>
              <h3 className="mt-3 text-2xl md:text-3xl font-bold text-slate-800">Você está logado como {usuario.nome} ({usuario.tipo})</h3>
              <p className="mt-2 text-slate-600">Use o menu lateral para navegar pelas funcionalidades disponíveis para o seu perfil.</p>
            </div>
          </div>
        )}

        {telaAtiva === 'dashboard' && (
          <div className="space-y-6">
            <Dashboard
              papel={papel}
              onIniciarTrilha={() => setTelaAtiva('exercicios')}
              onNavegar={(tela) => setTelaAtiva(tela)}
            />
          </div>
        )}

        {telaAtiva === 'turmas' && <MinhasTurmas papel={papel} onAcessarTurma={acessarTurma} onNavegar={(tela) => setTelaAtiva(tela)} />}
        {telaAtiva === 'exercicios' && <FazerExercicio emailAluno={usuario.email} onNavegar={(tela) => setTelaAtiva(tela)} />}
        {telaAtiva === 'ferramentas-ia' && (
          <FerramentasIA
            turmaIdInicial={turmaSelecionadaId}
            papel={papel}
            onVoltarTurmas={() => setTelaAtiva('turmas')}
            onNavegar={(tela) => setTelaAtiva(tela)}
          />
        )}
        {telaAtiva === 'gestao-usuarios' && <GestaoUsuarios papel={papel} onNavegar={(tela) => setTelaAtiva(tela)} />}
      </main>
      {papel === 'aluno' && <TutorChat />}
      {papel === 'professor' && <CopilotoChat />}
      {papel === 'administrador' && <AdminCopilotoChat />}
    </div>
  );
}