"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Calendar,
  Tag,
  ExternalLink,
  Volume2,
  Filter,
  Loader2,
  X,
  MapPin,
  FileText,
} from "lucide-react";
import { LegislativeProject } from "@/types";
import { searchApi, simplificationApi, legislationApi } from "@/services/api";
import { Legislation } from "@/services/api";

interface ProjectWithSimplification extends LegislativeProject {
  originalData?: Legislation;
  isLoadingSimplification?: boolean;
}

export default function Publications() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [speakingId, setSpeakingId] = useState<string | null>(null);
  const [projects, setProjects] = useState<ProjectWithSimplification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Filtros avançados
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    year: "",
    type: "",
    source: "",
    status: "",
  });
  const [availableFilters, setAvailableFilters] = useState<any>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const categories = [
    "all",
    "Educação",
    "Saúde",
    "Transporte",
    "Economia",
    "Segurança",
    "Meio Ambiente",
    "Trabalho",
  ];

  // Carregar filtros disponíveis
  useEffect(() => {
    searchApi.getFilters().then(setAvailableFilters).catch(console.error);
  }, []);

  // Autocomplete
  useEffect(() => {
    if (searchTerm.length >= 2) {
      searchApi
        .autocomplete(searchTerm)
        .then(setSuggestions)
        .catch(() => setSuggestions([]));
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchTerm]);

  // Carregar projetos iniciais ou buscar
  useEffect(() => {
    if (!searchTerm.trim()) {
      loadInitialProjects();
    }
  }, []);

  const loadInitialProjects = async () => {
    setIsLoading(true);
    try {
      const trending = await legislationApi.getTrending(20);
      const projectsWithSimplification = await Promise.all(
        trending.map(async (legislation) => {
          return await enrichProjectWithSimplification(legislation);
        })
      );
      setProjects(projectsWithSimplification);
      setTotal(projectsWithSimplification.length);
    } catch (error: any) {
      console.error("Erro ao carregar projetos:", error);
      // Em caso de erro, usar dados mockados como fallback
      setProjects(getMockProjects());
    } finally {
      setIsLoading(false);
    }
  };

  const enrichProjectWithSimplification = async (
    legislation: Legislation
  ): Promise<ProjectWithSimplification> => {
    const summary = legislation.summary || legislation.title || "";

    // Se já tem texto simplificado, usar
    if (legislation.simplified_text) {
      return convertToProject(legislation, legislation.simplified_text);
    }

    // Simplificar o resumo
    try {
      const simplified = await simplificationApi.simplify({
        text: summary,
        target_level: "simple",
        include_audio: false,
      });

      return convertToProject(legislation, simplified.simplified_text);
    } catch (error) {
      console.error("Erro ao simplificar:", error);
      // Se falhar, usar o resumo original
      return convertToProject(legislation, summary);
    }
  };

  const convertToProject = (
    legislation: Legislation,
    simplifiedText: string
  ): ProjectWithSimplification => {
    // Extrair pontos-chave do texto simplificado
    const impacts = extractKeyPoints(simplifiedText, legislation);

    // Determinar categoria baseada em tags ou título
    const category = determineCategory(legislation);

    return {
      id: String(legislation.id),
      title: `${legislation.type} ${legislation.number}/${legislation.year} - ${legislation.title}`,
      original_number: `${legislation.type} ${legislation.number}/${legislation.year}`,
      summary: legislation.summary || legislation.title,
      simplified_summary: simplifiedText,
      status: legislation.status || "Em tramitação",
      category: category,
      published_at: legislation.presentation_date
        ? new Date(legislation.presentation_date).toISOString().split("T")[0]
        : new Date().toISOString().split("T")[0],
      impacts: impacts,
      originalData: legislation,
    };
  };

  const extractKeyPoints = (
    text: string,
    legislation: Legislation
  ): string[] => {
    const points: string[] = [];
    const sentences = text.split(/[.!?]+/).filter((s) => s.trim().length > 20);

    // Extrair 3-4 pontos principais
    sentences.slice(0, 4).forEach((sentence) => {
      const trimmed = sentence.trim();
      if (trimmed.length > 30 && trimmed.length < 200) {
        // Capitalizar primeira letra
        const capitalized = trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
        points.push(capitalized);
      }
    });

    // Se não tiver pontos suficientes, criar baseado no tipo
    if (points.length < 2) {
      if (legislation.type?.includes("PL")) {
        points.push("Aplica-se a projetos de lei em tramitação");
      }
      if (legislation.author) {
        points.push(`Proposto por ${legislation.author}`);
      }
    }

    return points.slice(0, 4);
  };

  const determineCategory = (legislation: Legislation): string => {
    const title = (legislation.title || "").toLowerCase();
    const tags = legislation.tags || [];

    if (
      title.includes("educação") ||
      title.includes("escola") ||
      title.includes("ensino") ||
      tags.some((t) => t.toLowerCase().includes("educação"))
    ) {
      return "Educação";
    }
    if (
      title.includes("saúde") ||
      title.includes("hospital") ||
      title.includes("médico") ||
      tags.some((t) => t.toLowerCase().includes("saúde"))
    ) {
      return "Saúde";
    }
    if (
      title.includes("transporte") ||
      title.includes("ônibus") ||
      title.includes("metrô") ||
      tags.some((t) => t.toLowerCase().includes("transporte"))
    ) {
      return "Transporte";
    }
    if (
      title.includes("imposto") ||
      title.includes("tributo") ||
      title.includes("iptu") ||
      tags.some((t) => t.toLowerCase().includes("economia"))
    ) {
      return "Economia";
    }
    if (
      title.includes("segurança") ||
      title.includes("policia") ||
      tags.some((t) => t.toLowerCase().includes("segurança"))
    ) {
      return "Segurança";
    }
    if (
      title.includes("meio ambiente") ||
      title.includes("ambiental") ||
      tags.some((t) => t.toLowerCase().includes("ambiente"))
    ) {
      return "Meio Ambiente";
    }
    if (
      title.includes("trabalho") ||
      title.includes("emprego") ||
      tags.some((t) => t.toLowerCase().includes("trabalho"))
    ) {
      return "Trabalho";
    }

    return "Geral";
  };

  const handleSearch = async (searchPage: number = 1) => {
    if (!searchTerm.trim()) {
      loadInitialProjects();
      return;
    }

    setIsLoading(true);
    try {
      const searchFilters: any = {};
      if (filters.year) searchFilters.year = parseInt(filters.year);
      if (filters.type) searchFilters.type = filters.type;
      if (filters.source) searchFilters.source = filters.source;
      if (filters.status) searchFilters.status = filters.status;

      const result = await searchApi.search({
        query: searchTerm.trim(),
        filters:
          Object.keys(searchFilters).length > 0 ? searchFilters : undefined,
        page: searchPage,
        page_size: pageSize,
      });

      // Enriquecer cada resultado com simplificação
      const enrichedProjects = await Promise.all(
        result.results.map(async (legislation) => {
          return await enrichProjectWithSimplification(legislation);
        })
      );

      setProjects(enrichedProjects);
      setTotal(result.total);
      setPage(searchPage);
    } catch (error: any) {
      console.error("Erro na busca:", error);
      alert(
        error?.formattedMessage ||
          "Erro ao buscar projetos. Verifique sua conexão e tente novamente."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(1);
  };

  const clearFilters = () => {
    setFilters({
      year: "",
      type: "",
      source: "",
      status: "",
    });
  };

  const hasActiveFilters = Object.values(filters).some((v) => v !== "");

  const filteredProjects = projects.filter((project) => {
    const matchesCategory =
      selectedCategory === "all" || project.category === selectedCategory;
    return matchesCategory;
  });

  const speakText = (text: string, id: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "pt-BR";
      utterance.rate = 0.9;
      utterance.onstart = () => setSpeakingId(id);
      utterance.onend = () => setSpeakingId(null);
      window.speechSynthesis.speak(utterance);
    }
  };

  const getStatusColor = (status: string) => {
    if (status.includes("Aprovado") || status.includes("Aprovada")) {
      return "bg-green-100 text-green-800";
    }
    if (status.includes("Senado") || status.includes("análise")) {
      return "bg-blue-100 text-blue-800";
    }
    if (status.includes("Rejeitado") || status.includes("Arquivado")) {
      return "bg-red-100 text-red-800";
    }
    return "bg-yellow-100 text-yellow-800";
  };

  // Dados mockados como fallback
  const getMockProjects = (): ProjectWithSimplification[] => {
    return [
      {
        id: "1",
        title:
          "PL 1234/2024 - Programa de Internet Gratuita em Escolas Públicas",
        original_number: "PL 1234/2024",
        summary:
          "Institui programa nacional de acesso gratuito à internet em todas as escolas públicas do Brasil",
        simplified_summary:
          "Este projeto quer levar internet de graça para todas as escolas públicas do país. A ideia é que todos os alunos possam estudar online, fazer pesquisas e ter as mesmas chances de aprender, não importa se moram na cidade ou no interior.",
        status: "Em tramitação",
        category: "Educação",
        published_at: "2024-03-15",
        impacts: [
          "Mais de 150 mil escolas receberiam internet",
          "Beneficia cerca de 40 milhões de estudantes",
          "Ajuda a reduzir desigualdade digital",
        ],
      },
    ];
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Projetos de Lei Explicados
          </h1>
          <p className="text-lg text-gray-600">
            Entenda as leis que estão sendo discutidas agora, em linguagem clara
            e simples
          </p>
        </div>

        {/* Barra de Busca Avançada */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Buscar por assunto, palavra-chave..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onFocus={() =>
                  searchTerm.length >= 2 && setShowSuggestions(true)
                }
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
              />

              {/* Autocomplete */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => {
                        setSearchTerm(suggestion);
                        setShowSuggestions(false);
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-blue-50 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Buscando...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Buscar
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
              >
                <Filter className="w-5 h-5" />
                Filtros
                {hasActiveFilters && (
                  <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                    {Object.values(filters).filter((v) => v !== "").length}
                  </span>
                )}
              </button>

              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat === "all" ? "Todas as áreas" : cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Filtros Avançados */}
            {showFilters && (
              <div className="border-t border-gray-200 pt-4 mt-4">
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {availableFilters && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          <Calendar className="w-4 h-4 inline mr-1" />
                          Ano
                        </label>
                        <select
                          value={filters.year}
                          onChange={(e) =>
                            setFilters({ ...filters, year: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Todos os anos</option>
                          {availableFilters.years?.map((year: number) => (
                            <option key={year} value={year}>
                              {year}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          <FileText className="w-4 h-4 inline mr-1" />
                          Tipo
                        </label>
                        <select
                          value={filters.type}
                          onChange={(e) =>
                            setFilters({ ...filters, type: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Todos os tipos</option>
                          {availableFilters.types?.map((type: string) => (
                            <option key={type} value={type}>
                              {type}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          <MapPin className="w-4 h-4 inline mr-1" />
                          Fonte
                        </label>
                        <select
                          value={filters.source}
                          onChange={(e) =>
                            setFilters({ ...filters, source: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Todas as fontes</option>
                          {availableFilters.sources?.map((source: string) => (
                            <option key={source} value={source}>
                              {source.charAt(0).toUpperCase() + source.slice(1)}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Status
                        </label>
                        <select
                          value={filters.status}
                          onChange={(e) =>
                            setFilters({ ...filters, status: e.target.value })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Todos os status</option>
                          {availableFilters.status?.map((status: string) => (
                            <option key={status} value={status}>
                              {status}
                            </option>
                          ))}
                        </select>
                      </div>
                    </>
                  )}
                </div>

                {hasActiveFilters && (
                  <div className="mt-4 flex justify-end">
                    <button
                      type="button"
                      onClick={clearFilters}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                    >
                      <X className="w-4 h-4" />
                      Limpar filtros
                    </button>
                  </div>
                )}
              </div>
            )}
          </form>
        </div>

        {/* Contador de resultados */}
        {filteredProjects.length > 0 && (
          <div className="mb-4 text-sm text-gray-600">
            {filteredProjects.length} projeto
            {filteredProjects.length !== 1 ? "s" : ""} encontrado
            {filteredProjects.length !== 1 ? "s" : ""}
          </div>
        )}

        {/* Lista de Projetos */}
        <div className="grid gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden"
            >
              <div className="p-6">
                <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                          project.status
                        )}`}
                      >
                        {project.status}
                      </span>
                      <span className="flex items-center text-sm text-gray-500">
                        <Tag className="h-4 w-4 mr-1" />
                        {project.category}
                      </span>
                      <span className="flex items-center text-sm text-gray-500">
                        <Calendar className="h-4 w-4 mr-1" />
                        {new Date(project.published_at).toLocaleDateString(
                          "pt-BR"
                        )}
                      </span>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-3">
                      {project.title}
                    </h2>
                  </div>
                </div>

                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4 rounded">
                  <p className="text-gray-700 font-medium mb-2">
                    Em palavras simples:
                  </p>
                  <p className="text-gray-800 leading-relaxed">
                    {project.simplified_summary}
                  </p>
                  <button
                    onClick={() =>
                      speakText(project.simplified_summary, project.id)
                    }
                    className="mt-3 flex items-center space-x-2 text-blue-700 hover:text-blue-800 font-medium"
                  >
                    <Volume2 className="h-5 w-5" />
                    <span>
                      {speakingId === project.id
                        ? "Falando..."
                        : "Ouvir explicação"}
                    </span>
                  </button>
                </div>

                <div className="mb-4">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Como isso afeta você:
                  </h3>
                  <ul className="space-y-2">
                    {project.impacts.map((impact, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-600 mr-2">•</span>
                        <span className="text-gray-700">{impact}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <details className="group">
                    <summary className="cursor-pointer text-blue-700 hover:text-blue-800 font-medium flex items-center">
                      <span>Ver texto oficial completo</span>
                      <ExternalLink className="h-4 w-4 ml-1" />
                    </summary>
                    <p className="mt-3 text-sm text-gray-600 bg-gray-50 p-4 rounded">
                      {project.summary}
                    </p>
                  </details>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Estados vazios e loading */}
        {isLoading && filteredProjects.length === 0 && (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Carregando projetos...</p>
          </div>
        )}

        {!isLoading && filteredProjects.length === 0 && searchTerm && (
          <div className="text-center py-12 bg-white rounded-lg">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 text-lg">
              Nenhum projeto encontrado com os filtros selecionados.
            </p>
          </div>
        )}

        {!isLoading && filteredProjects.length === 0 && !searchTerm && (
          <div className="text-center py-12 bg-white rounded-lg">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 text-lg">
              Digite palavras-chave para buscar projetos de lei
            </p>
          </div>
        )}

        {/* Paginação */}
        {filteredProjects.length > 0 && total > pageSize && (
          <div className="flex justify-center items-center gap-4 mt-8">
            <button
              onClick={() => handleSearch(page - 1)}
              disabled={page === 1 || isLoading}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Anterior
            </button>
            <span className="text-gray-600">
              Página {page} de {Math.ceil(total / pageSize)}
            </span>
            <button
              onClick={() => handleSearch(page + 1)}
              disabled={page >= Math.ceil(total / pageSize) || isLoading}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Próxima
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
