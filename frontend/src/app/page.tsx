import Link from 'next/link';
import { MessageSquare, Search, FileText, Volume2, Sparkles, ArrowRight, ChevronRight } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-sky-50">
      <header className="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-50 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2.5 rounded-xl shadow-lg">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">Voz da Lei</h1>
                <p className="text-xs sm:text-sm text-gray-600 mt-0.5">A democracia que você entende</p>
              </div>
            </div>
            <nav className="hidden md:flex gap-2">
              <Link href="/chat" className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium">
                Chat
              </Link>
              <Link href="/search" className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium">
                Buscar
              </Link>
              <Link href="/trending" className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium">
                Em Destaque
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12 sm:py-20 sm:px-6 lg:px-8">
        <div className="text-center mb-16 animate-fade-in">
          <div className="inline-block mb-6 px-4 py-2 bg-blue-50 border border-blue-100 rounded-full text-sm font-semibold text-blue-700">
            Powered by IA
          </div>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Entenda as Leis de<br />Forma <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">Simples e Clara</span>
          </h2>
          <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
            Conectamos você às decisões legislativas através de IA, traduzindo o juridiquês para linguagem que todos entendem.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/chat"
              className="group inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl"
            >
              Começar Agora
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/search"
              className="inline-flex items-center gap-2 bg-white text-gray-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all border-2 border-gray-200 hover:border-blue-200"
            >
              Explorar Leis
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          <FeatureCard
            icon={<MessageSquare className="w-10 h-10" />}
            title="Chat Inteligente"
            description="Converse com nossa IA sobre qualquer lei ou projeto"
            href="/chat"
          />
          <FeatureCard
            icon={<FileText className="w-10 h-10" />}
            title="Simplificação"
            description="Textos jurídicos em linguagem simples e acessível"
            href="/simplify"
          />
          <FeatureCard
            icon={<Search className="w-10 h-10" />}
            title="Busca Avançada"
            description="Encontre leis por tema, autor ou região"
            href="/search"
          />
          <FeatureCard
            icon={<Volume2 className="w-10 h-10" />}
            title="Áudio & Voz"
            description="Ouça explicações e converse por voz"
            href="/audio"
          />
        </div>

        <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 rounded-3xl p-12 sm:p-16 text-center text-white shadow-2xl">
          <div className="absolute inset-0 bg-grid-white/10"></div>
          <div className="relative z-10">
            <div className="inline-block bg-white/20 backdrop-blur-sm p-3 rounded-2xl mb-6">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-3xl sm:text-4xl font-bold mb-4">
              Pronto para participar da democracia?
            </h3>
            <p className="text-lg sm:text-xl mb-10 text-blue-100 max-w-2xl mx-auto">
              Comece agora a entender e acompanhar as decisões que afetam sua vida
            </p>
            <Link
              href="/chat"
              className="group inline-flex items-center gap-2 bg-white text-blue-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-blue-50 transition-all shadow-lg hover:shadow-xl"
            >
              Começar Agora
              <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-1 sm:grid-cols-3 gap-8 text-center">
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-gray-100">
            <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent mb-2">10k+</div>
            <div className="text-gray-600 font-medium">Leis Simplificadas</div>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-gray-100">
            <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent mb-2">50k+</div>
            <div className="text-gray-600 font-medium">Consultas Respondidas</div>
          </div>
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-gray-100">
            <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent mb-2">100%</div>
            <div className="text-gray-600 font-medium">Gratuito e Acessível</div>
          </div>
        </div>
      </main>

      <footer className="bg-gradient-to-br from-gray-900 to-gray-800 text-white mt-24">
        <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2 rounded-xl">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold">Voz da Lei</h3>
            </div>
            <p className="text-gray-400 mb-6 max-w-md">
              Democratizando o acesso à legislação brasileira através de inteligência artificial
            </p>
            <div className="flex gap-6 mb-6">
              <Link href="/chat" className="text-gray-400 hover:text-white transition-colors">Chat</Link>
              <Link href="/search" className="text-gray-400 hover:text-white transition-colors">Buscar</Link>
              <Link href="/trending" className="text-gray-400 hover:text-white transition-colors">Em Destaque</Link>
            </div>
            <div className="border-t border-gray-700 pt-6 w-full">
              <p className="text-gray-500 text-sm">
                © 2024 Voz da Lei. Todos os direitos reservados.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
}

function FeatureCard({ icon, title, description, href }: FeatureCardProps) {
  return (
    <Link href={href}>
      <div className="group bg-white p-6 rounded-2xl shadow-sm hover:shadow-xl transition-all cursor-pointer border border-gray-100 hover:border-blue-200 hover:-translate-y-1">
        <div className="bg-gradient-to-br from-blue-50 to-sky-50 w-16 h-16 rounded-xl flex items-center justify-center mb-4 group-hover:from-blue-100 group-hover:to-sky-100 transition-colors">
          <div className="text-blue-600">{icon}</div>
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-700 transition-colors">{title}</h3>
        <p className="text-gray-600 leading-relaxed mb-3">{description}</p>
        <div className="flex items-center text-blue-600 font-medium text-sm group-hover:gap-2 transition-all">
          Saiba mais
          <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
  );
}
