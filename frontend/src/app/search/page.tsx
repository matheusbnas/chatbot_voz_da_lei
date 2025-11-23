"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Filter,
  Calendar,
  FileText,
  MapPin,
  Loader2,
  ChevronDown,
  X,
} from "lucide-react";
import Navigation from "@/components/Navigation";
import { searchApi, legislationApi } from "@/services/api";
import { Legislation } from "@/services/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Legislation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  // Filtros
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    year: "",
    type: "",
    source: "",
    status: "",
  });
  const [availableFilters, setAvailableFilters] = useState<any>(null);

  // Autocomplete
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    // Carregar filtros disponíveis
    searchApi
      .getFilters()
      .then(setAvailableFilters)
      .catch(console.error);
  }, []);

  useEffect(() => {
    // Autocomplete quando o usuário digita
    if (query.length >= 2) {
      searchApi
        .autocomplete(query)
        .then(setSuggestions)
        .catch(() => setSuggestions([]));
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query]);

  const handleSearch = async (searchPage: number = 1) => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const searchFilters: any = {};
      if (filters.year) searchFilters.year = parseInt(filters.year);
      if (filters.type) searchFilters.type = filters.type;
      if (filters.source) searchFilters.source = filters.source;
      if (filters.status) searchFilters.status = filters.status;

      const result = await searchApi.search({
        query: query.trim(),
        filters: Object.keys(searchFilters).length > 0 ? searchFilters : undefined,
        page: searchPage,
        page_size: pageSize,
      });

      setResults(result.results);
      setTotal(result.total);
      setPage(searchPage);
    } catch (error: any) {
      console.error("Erro na busca:", error);
      alert(
        error?.formattedMessage ||
          "Erro ao buscar legislação. Verifique sua conexão e tente novamente."
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-sky-50">
      <Navigation />

      <main className="max-w-7xl mx-auto px-4 py-8 sm:py-12 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="inline-block bg-gradient-to-br from-blue-500 to-blue-600 p-3 rounded-2xl mb-4 shadow-lg">
            <Search className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Busca Avançada de Legislação
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Encontre projetos de lei, leis e normas por palavras-chave, tema,
            autor ou período
          </p>
        </div>

        {/* Barra de Busca */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => query.length >= 2 && setShowSuggestions(true)}
                placeholder="Buscar por palavras-chave, tema, autor..."
                className="w-full pl-12 pr-4 py-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 text-lg"
              />

              {/* Autocomplete */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => {
                        setQuery(suggestion);
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
                disabled={!query.trim() || isLoading}
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
            </div>

            {/* Filtros */}
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

        {/* Resultados */}
        {results.length > 0 && (
          <div className="mb-4 text-sm text-gray-600">
            {total} resultado{total !== 1 ? "s" : ""} encontrado
            {total !== 1 ? "s" : ""}
          </div>
        )}

        <div className="space-y-4">
          {results.map((legislation) => (
            <div
              key={legislation.id}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                      {legislation.type} {legislation.number}/{legislation.year}
                    </span>
                    {legislation.status && (
                      <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                        {legislation.status}
                      </span>
                    )}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {legislation.title}
                  </h3>
                  {legislation.summary && (
                    <p className="text-gray-600 mb-3">{legislation.summary}</p>
                  )}
                  <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                    {legislation.author && (
                      <span>Autor: {legislation.author}</span>
                    )}
                    {legislation.presentation_date && (
                      <span>
                        Apresentado em:{" "}
                        {new Date(legislation.presentation_date).toLocaleDateString(
                          "pt-BR"
                        )}
                      </span>
                    )}
                  </div>
                  {legislation.tags && legislation.tags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {legislation.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Buscando legislação...</p>
            </div>
          )}

          {!isLoading && results.length === 0 && query && (
            <div className="text-center py-12 bg-white rounded-lg">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 text-lg">
                Nenhum resultado encontrado para "{query}"
              </p>
              <p className="text-gray-500 text-sm mt-2">
                Tente usar palavras-chave diferentes ou ajustar os filtros
              </p>
            </div>
          )}

          {!query && !isLoading && (
            <div className="text-center py-12 bg-white rounded-lg">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 text-lg">
                Digite palavras-chave para buscar legislação
              </p>
            </div>
          )}

          {/* Paginação */}
          {results.length > 0 && total > pageSize && (
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
      </main>
    </div>
  );
}

