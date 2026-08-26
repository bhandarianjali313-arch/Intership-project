import React, { useState, useRef, useEffect } from 'react';
import { ContractSummary, ChatMessage, Citation } from '../types/contract';
import { chatWithContract } from '../services/api';
import {
  MessageSquare,
  Send,
  Sparkles,
  Bot,
  User,
  FileText,
  Bookmark,
  ShieldCheck,
  AlertCircle,
  CornerDownLeft,
} from 'lucide-react';

interface ContractChatProps {
  contracts: ContractSummary[];
  selectedContractId: string;
  onSelectContract: (id: string) => void;
}

export const ContractChat: React.FC<ContractChatProps> = ({
  contracts,
  selectedContractId,
  onSelectContract,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        'Hello! I am your AI Contract Intelligence Assistant. Ask me any question about clauses, notice periods, liability caps, IP ownership, or payment terms. All answers are backed by verified page and section citations.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    'Can the other company cancel the agreement?',
    'What is the liability cap?',
    'Who owns the intellectual property?',
    'What happens if payment is delayed?',
    'Does the contract automatically renew?',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputValue).trim();
    if (!query || isLoading) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputValue('');
    setIsLoading(true);

    try {
      const res = await chatWithContract(selectedContractId, query);
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        confidence: res.confidence,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'An error occurred while analyzing the contract context. Please try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Selector Header */}
      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20 text-purple-400">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <span>RAG AI Contract Assistant</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-mono">
                Verified Citations
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Conversational semantic search with strict contractual evidence grounding
            </p>
          </div>
        </div>

        {/* Contract Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Chat Context:</span>
          <select
            value={selectedContractId}
            onChange={(e) => onSelectContract(e.target.value)}
            className="bg-slate-950 border border-slate-700 text-slate-200 text-xs font-bold rounded-lg px-3 py-1.5 focus:outline-hidden focus:border-purple-500 cursor-pointer max-w-xs truncate"
          >
            {contracts.map((c) => (
              <option key={c.id} value={c.id} className="bg-slate-900 text-slate-200">
                {c.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col h-[640px]">
        {/* Messages Scroll Area */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-3 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-xs shadow-md'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-xs shadow-md'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Evidence Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 space-y-2">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1">
                      <Bookmark className="w-3.5 h-3.5" />
                      <span>Verified Contract Citations</span>
                    </div>
                    {msg.citations.map((cite, cIdx) => (
                      <div
                        key={cIdx}
                        className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 text-[11px] text-slate-300 font-mono"
                      >
                        <div className="font-bold text-indigo-400 mb-0.5">
                          Section {cite.section_number} ({cite.section_title}) • Page{' '}
                          {cite.page_number}
                        </div>
                        <p className="text-slate-400 italic">"{cite.quote}"</p>
                      </div>
                    ))}
                  </div>
                )}

                <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1">
                  <span>{msg.timestamp}</span>
                  {msg.confidence !== undefined && (
                    <span className="text-emerald-400 font-semibold">
                      Confidence: {Math.round(msg.confidence * 100)}%
                    </span>
                  )}
                </div>
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-0.5">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 animate-pulse">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-900 border border-slate-800 p-3 rounded-2xl text-xs text-slate-400 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" />
                <span>Reading clauses & extracting citations...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Quick Prompts */}
        <div className="px-5 py-2 border-t border-slate-800/80 bg-slate-950/60 flex items-center gap-2 overflow-x-auto">
          <span className="text-[11px] font-bold text-slate-400 uppercase shrink-0 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-purple-400" />
            <span>Suggested:</span>
          </span>
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              disabled={isLoading}
              onClick={() => handleSendMessage(q)}
              className="text-xs px-3 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-full border border-slate-800 whitespace-nowrap hover:border-purple-500/40 transition-colors cursor-pointer shrink-0"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex items-center gap-3">
          <input
            type="text"
            placeholder="Ask anything about this contract (e.g., 'What is the termination notice period?')..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-hidden focus:border-purple-500"
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isLoading}
            className="p-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white rounded-xl font-bold transition-all shadow-md shadow-purple-600/20 cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
