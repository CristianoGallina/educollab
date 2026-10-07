import React, { useState, useRef, useEffect } from 'react';
import { BrainCircuit, X, Send, MessageSquareText } from 'lucide-react';
import { API_BASE, apiFetch } from '../../api';

export default function CopilotoChat() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([{ role: 'assistant', content: 'Olá, educador! Sou seu Copiloto Pedagógico. Precisa de ideias para aulas, criar questões rápidas ou ajuda para analisar os dados da sua turma?' }]);
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
      const payloadHist = chatMessages.filter(m => m.role !== 'assistant' || !m.content.includes('Olá, educador!'));
      // Utilizamos o mesmo endpoint ou um específico de professor. Para o demo, usamos um endpoint novo ou o tutor com prompt ajustado.
      // Vamos assumir que vamos criar ou adaptar /professor/chat-copiloto no backend, ou enviamos via gerar_dica genérico.
      // Para o frontend agora, simularemos a chamada com uma rota genérica que vamos criar no backend.
      const response = await apiFetch(`${API_BASE}/professor/chat-copiloto`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensagem: userMsg.content, historico: payloadHist }),
      });
      const data = await response.json();
      setChatMessages((prev) => [...prev, { role: 'assistant', content: data.resposta || 'Não consegui processar agora.' }]);
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: 'Erro de conexão com o Copiloto. Verifique sua rede.' }]);
    } finally {
      setLoadingChat(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isChatOpen ? (
        <div className="bg-white w-[350px] sm:w-[450px] h-[550px] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-fadeIn">
          <div className="bg-slate-900 p-4 flex items-center justify-between text-white shadow-md z-10">
            <div className="flex items-center gap-2">
              <BrainCircuit size={20} className="text-emerald-400" />
              <h4 className="font-bold">Copiloto IA do Professor</h4>
            </div>
            <button onClick={() => setIsChatOpen(false)} className="hover:bg-slate-700 p-1.5 rounded-md transition-colors"><X size={20}/></button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-3.5 rounded-2xl text-[13px] shadow-sm leading-relaxed ${msg.role === 'user' ? 'bg-slate-900 text-white rounded-tr-sm' : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm'}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loadingChat && (
              <div className="flex justify-start">
                <div className="bg-white border border-slate-200 p-3 rounded-2xl rounded-tl-sm text-sm text-slate-500 flex items-center gap-2 shadow-sm">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                  <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={enviarMensagemChat} className="p-3 bg-white border-t border-slate-100 flex gap-2">
            <input type="text" value={chatInput} onChange={e => setChatInput(e.target.value)} placeholder="Ex: Crie 2 questões difíceis sobre mitose..." className="flex-1 bg-slate-100 border-transparent focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 rounded-xl px-4 py-2.5 text-sm outline-none transition-all" />
            <button type="submit" disabled={!chatInput.trim() || loadingChat} className="bg-emerald-600 text-white p-3 rounded-xl hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-sm">
              <Send size={18} />
            </button>
          </form>
        </div>
      ) : (
        <button onClick={() => setIsChatOpen(true)} className="bg-slate-900 hover:bg-slate-800 text-white px-5 py-4 rounded-full shadow-xl hover:shadow-slate-900/30 transition-all hover:-translate-y-1 flex items-center gap-3">
          <BrainCircuit size={24} className="text-emerald-400" />
          <span className="font-bold">Assistente do Professor</span>
        </button>
      )}
    </div>
  );
}
