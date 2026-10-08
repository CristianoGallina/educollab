import React, { useState } from 'react';
import { Target, X, Send, BrainCircuit, Activity } from 'lucide-react';
import { API_BASE, apiFetch } from '../../api';

export default function TrilhaReforco({ isOpen, onClose }) {
  const [fase, setFase] = useState('inicio'); // inicio, carregando, desafio, feedback
  const [desafio, setDesafio] = useState('');
  const [resposta, setResposta] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const gerarDesafio = async () => {
    setFase('carregando');
    setLoading(true);
    try {
      // Usar a rota do tutor socrático passando uma instrução especial
      const response = await apiFetch(`${API_BASE}/aluno/chat-tutor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'aluno' },
        body: JSON.stringify({
          mensagem: "Sou o sistema solicitando um desafio. Crie UM ÚNICO desafio ou pergunta de revisão rápida (nível fácil/médio) para reforço adaptativo. Vá direto ao ponto, não diga 'olá'. Apenas o enunciado do desafio."
        })
      });
      const data = await response.json();
      setDesafio(data.resposta);
      setFase('desafio');
    } catch (e) {
      setDesafio("Erro ao gerar desafio adaptativo. Verifique sua conexão.");
      setFase('desafio');
    }
    setLoading(false);
  };

  const enviarResposta = async () => {
    if (!resposta.trim()) return;
    setLoading(true);
    try {
      const response = await apiFetch(`${API_BASE}/aluno/chat-tutor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'aluno' },
        body: JSON.stringify({
          historico: [{ role: "assistant", content: desafio }],
          mensagem: `Minha resposta para o desafio é: ${resposta}. Avalie minha resposta usando maiêutica socrática. Não dê a resposta completa, apenas me guie ou parabenize se eu acertei.`
        })
      });
      const data = await response.json();
      setFeedback(data.resposta);
      setFase('feedback');
    } catch (e) {
      setFeedback("Erro ao enviar resposta.");
      setFase('feedback');
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden border border-emerald-100 flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 p-5 flex justify-between items-center text-white">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
              <Target className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-lg">Trilha de Reforço Adaptativa</h3>
              <p className="text-emerald-100 text-xs">Aprenda no seu ritmo com a IA</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-8 min-h-[300px] flex flex-col justify-center bg-slate-50 relative">
          
          {fase === 'inicio' && (
            <div className="text-center space-y-6">
              <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto shadow-inner">
                <Activity className="w-10 h-10 text-emerald-600" />
              </div>
              <div className="space-y-2">
                <h4 className="text-2xl font-bold text-slate-800">Pronto para o próximo nível?</h4>
                <p className="text-slate-600 max-w-sm mx-auto leading-relaxed">
                  Baseado no seu histórico, a IA vai gerar um desafio rápido sob medida para consolidar seu aprendizado.
                </p>
              </div>
              <button 
                onClick={gerarDesafio}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3.5 rounded-full font-bold shadow-lg shadow-emerald-200 transition-all transform hover:scale-105 flex items-center gap-2 mx-auto"
              >
                <BrainCircuit className="w-5 h-5" /> Iniciar Desafio Agora
              </button>
            </div>
          )}

          {fase === 'carregando' && (
            <div className="text-center space-y-4">
              <div className="animate-spin w-12 h-12 border-4 border-emerald-200 border-t-emerald-600 rounded-full mx-auto"></div>
              <p className="text-emerald-700 font-bold animate-pulse">A IA está analisando seu perfil e gerando um desafio...</p>
            </div>
          )}

          {fase === 'desafio' && (
            <div className="space-y-6 animate-fade-in w-full">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div className="flex items-center gap-2 text-emerald-600 mb-3 font-bold text-sm uppercase tracking-wide">
                  <Target className="w-4 h-4" /> Desafio Gerado
                </div>
                <p className="text-slate-800 text-lg leading-relaxed">{desafio}</p>
              </div>
              
              <div className="space-y-3">
                <textarea 
                  value={resposta}
                  onChange={(e) => setResposta(e.target.value)}
                  placeholder="Escreva sua linha de raciocínio ou resposta aqui..."
                  className="w-full border border-slate-300 rounded-xl p-4 min-h-[100px] outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-50 transition-all resize-none"
                />
                <button 
                  onClick={enviarResposta}
                  disabled={loading || !resposta.trim()}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white py-3.5 rounded-xl font-bold transition-all disabled:opacity-50 flex justify-center items-center gap-2"
                >
                  {loading ? <div className="animate-spin w-5 h-5 border-2 border-slate-500 border-t-white rounded-full"></div> : <><Send className="w-5 h-5" /> Enviar Resposta</>}
                </button>
              </div>
            </div>
          )}

          {fase === 'feedback' && (
            <div className="space-y-6 animate-fade-in">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-emerald-200">
                <div className="flex items-center gap-2 text-emerald-600 mb-3 font-bold text-sm uppercase tracking-wide">
                  <BrainCircuit className="w-4 h-4" /> Feedback Socrático
                </div>
                <div className="prose prose-emerald max-w-none text-slate-800 whitespace-pre-wrap leading-relaxed">
                  {feedback}
                </div>
              </div>
              <button 
                onClick={() => {
                  setResposta('');
                  setFeedback('');
                  gerarDesafio();
                }}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl font-bold transition-all shadow-md"
              >
                Tentar Outro Desafio
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
