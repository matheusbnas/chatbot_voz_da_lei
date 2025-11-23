'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MessageSquare, BookOpen, Home, Sparkles, FileText } from 'lucide-react';

export default function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { id: 'home', label: 'Início', icon: Home, href: '/' },
    { id: 'chatbot', label: 'Chatbot', icon: MessageSquare, href: '/chat' },
    { id: 'simplification', label: 'Simplificação', icon: FileText, href: '/simplify' },
    { id: 'publications', label: 'Projetos de Lei', icon: BookOpen, href: '/publications' },
  ];

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/';
    }
    return pathname?.startsWith(href);
  };

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-2 rounded-xl shadow-lg">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                Voz da Lei
              </span>
              <p className="text-xs text-gray-600">A democracia que você entende</p>
            </div>
          </Link>
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.id}
                  href={item.href}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    active
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium hidden sm:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}

