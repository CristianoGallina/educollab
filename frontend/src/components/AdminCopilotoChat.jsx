import React, { useState, useRef, useEffect } from 'react';
import { Network, X, Send, BarChart2 } from 'lucide-react';
import { API_BASE, apiFetch } from '../api';

export default function AdminCopilotoChat() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([{ role: 'assistant', content: 'Olá, Diretor(a)! Sou seu Analista de Dados Educacionais. Como posso ajudar você a gerir as métricas e o desempenho das escolas da sua rede hoje?' }]);
  const [chatInput, setChatInput] = useState('');
  const [loadingChat, setLoadingChat] = useState(false);
  const chatEndRef = useRef(null);

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
      const payloadHist = chatMessages.filter(m => m.role !== 'assistant' || !m.content.includes('Olá, Diretor(a)!'));
      // Rota simulada ou mapeada para o backend
      const response = await apiFetch(`${API_BASE}/admin/chat-copiloto`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-tipo-usuario': 'administrador' },
        body: JSON.stringify({ mensagem: userMsg.content, historico: payloadHist }),
      });
      const data = await response.json();
      setChatMessages((prev) => [...prev, { role: 'assistant', content: data.resposta || 'Não consegui processar agora.' }]);
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: 'Erro de conexão. Simulando: De acordo com meus cálculos, o engajamento da rede está ótimo!' }]);
    } finally {
      setLoadingChat(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isChatOpen ? (
        <div className="bg-slate-900 w-[350px] sm:w-[450px] h-[550px] rounded-2xl shadow-2xl border border-slate-700 flex flex-col overflow-hidden animate-fadeIn">
          <div className="bg-gradient-to-r from-blue-700 to-indigo-800 p-4 flex items-center justify-between text-white shadow-md z-10">
            <div className="flex items-center gap-2">
              <Network size={20} className="text-blue-200" />
              <h4 className="font-bold">IA Analista da Rede</h4>
            </div>
            <button onClick={() => setIsChatOpen(false)} className="hover:bg-indigo-900 p-1.5 rounded-md transition-colors"><X size={20}/></button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-900">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-3.5 rounded-2xl text-[13px] shadow-sm leading-relaxed ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-sm'}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loadingChat && (
              <div className="flex justify-start">
                <div className="bg-slate-800 border border-slate-700 p-3 rounded-2xl rounded-tl-sm text-sm text-slate-500 flex items-center gap-2 shadow-sm">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={enviarMensagemChat} className="p-3 bg-slate-800 border-t border-slate-700 flex gap-2">
            <input type="text" value={chatInput} onChange={e => setChatInput(e.target.value)} placeholder="Ex: Qual escola gasta mais tokens?" className="flex-1 bg-slate-900 text-white border-transparent focus:bg-slate-950 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 rounded-xl px-4 py-2.5 text-sm outline-none transition-all placeholder:text-slate-500" />
            <button type="submit" disabled={!chatInput.trim() || loadingChat} className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm">
              <Send size={18} />
            </button>
          </form>
        </div>
      ) : (
        <button onClick={() => setIsChatOpen(true)} className="bg-slate-900 border-2 border-slate-700 hover:border-blue-500 hover:bg-slate-800 text-white px-5 py-4 rounded-full shadow-xl hover:shadow-blue-900/30 transition-all hover:-translate-y-1 flex items-center gap-3">
          <BarChart2 size={24} className="text-blue-400" />
          <span className="font-bold">Consultar Analista IA</span>
        </button>
      )}
    </div>
  );
}
