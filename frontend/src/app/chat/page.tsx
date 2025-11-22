'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Volume2, Mic, Sparkles, Home, RotateCcw, MessageSquare } from 'lucide-react';
import Link from 'next/link';
import { chatApi, ChatMessage } from '@/services/api';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load suggestions on mount
    chatApi.getSuggestions().then(setSuggestions).catch(console.error);
  }, []);

  const sendMessage = async (text?: string) => {
    const messageText = text || input;
    if (!messageText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: messageText,
        conversation_history: messages,
        use_audio: false,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro. Tente novamente.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    chatApi.getSuggestions().then(setSuggestions).catch(console.error);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 via-white to-sky-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2 rounded-xl shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">Voz da Lei</h1>
                <p className="text-sm text-gray-600">Chat Inteligente sobre Legislação</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {messages.length > 0 && (
                <button
                  onClick={clearChat}
                  className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors flex items-center gap-2 text-sm font-medium text-gray-700"
                  title="Limpar conversa"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span className="hidden sm:inline">Nova Conversa</span>
                </button>
              )}
              <Link
                href="/"
                className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                title="Voltar ao início"
              >
                <Home className="w-5 h-5 text-gray-700" />
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-8 sm:py-16 animate-fade-in">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-200">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                Como posso ajudar você hoje?
              </h2>
              <p className="text-lg text-gray-600 mb-10 max-w-2xl mx-auto">
                Pergunte sobre qualquer lei, projeto ou dúvida sobre legislação brasileira
              </p>
              <div className="grid sm:grid-cols-2 gap-3 max-w-3xl mx-auto">
                {suggestions.slice(0, 4).map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => sendMessage(suggestion)}
                    className="group p-4 bg-white rounded-xl shadow-sm hover:shadow-lg transition-all text-left border border-gray-100 hover:border-blue-200 hover:-translate-y-0.5"
                  >
                    <div className="flex items-start gap-3">
                      <div className="bg-blue-50 p-2 rounded-lg group-hover:bg-blue-100 transition-colors">
                        <MessageSquare className="w-4 h-4 text-blue-600" />
                      </div>
                      <p className="text-sm text-gray-700 font-medium flex-1">{suggestion}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 animate-fade-in ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2.5 rounded-xl flex-shrink-0 shadow-md">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
              )}
              <div
                className={`max-w-2xl p-4 rounded-2xl shadow-sm ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-blue-200'
                    : 'bg-white border border-gray-100'
                }`}
              >
                <p className={`whitespace-pre-wrap leading-relaxed ${
                  message.role === 'user' ? 'text-white' : 'text-gray-800'
                }`}>{message.content}</p>
              </div>
              {message.role === 'user' && (
                <div className="bg-gray-200 p-2.5 rounded-xl flex-shrink-0">
                  <MessageSquare className="w-5 h-5 text-gray-700" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex items-start gap-3 animate-fade-in">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2.5 rounded-xl flex-shrink-0 shadow-md">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-gray-100 shadow-sm p-5 rounded-2xl">
                <div className="flex space-x-2">
                  <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" />
                  <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2.5 h-2.5 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggestions */}
      {messages.length > 0 && suggestions.length > 0 && (
        <div className="border-t border-gray-200 p-4 bg-white/80 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto">
            <p className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-500" />
              Perguntas sugeridas:
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestions.slice(0, 6).map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(suggestion)}
                  className="px-4 py-2 bg-gradient-to-r from-blue-50 to-sky-50 border border-blue-100 rounded-full text-sm font-medium text-gray-700 hover:from-blue-100 hover:to-sky-100 hover:border-blue-200 transition-all hover:shadow-sm"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 p-4 bg-white/80 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-2 items-end">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-xl transition-all flex-shrink-0 ${
                isRecording
                  ? 'bg-red-100 hover:bg-red-200 text-red-600'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
              title="Gravar áudio"
            >
              <Mic className="w-5 h-5" />
            </button>
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Digite sua pergunta sobre legislação..."
                className="w-full p-4 pr-12 border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm bg-white"
                disabled={isLoading}
              />
              {input.trim() && (
                <div className="absolute right-3 bottom-3 text-xs text-gray-400">
                  {input.length} caracteres
                </div>
              )}
            </div>
            <button
              onClick={() => sendMessage()}
              disabled={isLoading || !input.trim()}
              className="p-4 rounded-2xl bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg flex-shrink-0 disabled:shadow-none"
              title="Enviar mensagem"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-3 text-center">
            Pressione Enter para enviar ou Shift + Enter para nova linha
          </p>
        </div>
      </div>
    </div>
  );
}
