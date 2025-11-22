import Link from 'next/link';
import { MessageSquare, Search, FileText, Volume2 } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-primary-600">Voz da Lei</h1>
              <p className="text-gray-600 mt-1">A democracia que você entende, ouve e participa</p>
            </div>
            <nav className="flex gap-4">
              <Link href="/chat" className="text-gray-600 hover:text-primary-600">
                Chat
              </Link>
              <Link href="/search" className="text-gray-600 hover:text-primary-600">
                Buscar
              </Link>
              <Link href="/trending" className="text-gray-600 hover:text-primary-600">
                Em Destaque
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            Entenda as Leis de Forma Simples
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Conectamos você às decisões legislativas através de IA, 
            traduzindo o juridiquês para linguagem que todos entendem.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <FeatureCard
            icon={<MessageSquare className="w-12 h-12" />}
            title="Chat Inteligente"
            description="Converse com nossa IA sobre qualquer lei ou projeto"
            href="/chat"
          />
          <FeatureCard
            icon={<FileText className="w-12 h-12" />}
            title="Simplificação"
            description="Textos jurídicos em linguagem simples e acessível"
            href="/simplify"
          />
          <FeatureCard
            icon={<Search className="w-12 h-12" />}
            title="Busca Avançada"
            description="Encontre leis por tema, autor ou região"
            href="/search"
          />
          <FeatureCard
            icon={<Volume2 className="w-12 h-12" />}
            title="Áudio & Voz"
            description="Ouça explicações e converse por voz"
            href="/audio"
          />
        </div>

        {/* CTA Section */}
        <div className="bg-primary-600 rounded-2xl p-12 text-center text-white">
          <h3 className="text-3xl font-bold mb-4">
            Pronto para participar da democracia?
          </h3>
          <p className="text-xl mb-8 text-primary-100">
            Comece agora a entender e acompanhar as decisões que afetam sua vida
          </p>
          <Link 
            href="/chat"
            className="inline-block bg-white text-primary-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-primary-50 transition"
          >
            Começar Agora
          </Link>
        </div>

        {/* Stats Section */}
        <div className="mt-16 grid grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold text-primary-600">10k+</div>
            <div className="text-gray-600 mt-2">Leis Simplificadas</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary-600">50k+</div>
            <div className="text-gray-600 mt-2">Consultas Respondidas</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary-600">100%</div>
            <div className="text-gray-600 mt-2">Gratuito e Acessível</div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-20">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-400">
              © 2024 Voz da Lei - Democratizando o acesso à legislação brasileira
            </p>
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
      <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition cursor-pointer">
        <div className="text-primary-600 mb-4">{icon}</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </Link>
  );
}
