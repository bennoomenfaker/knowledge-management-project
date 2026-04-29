"use client";

import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import { Search as SearchIcon, Filter, FileText, User, Calendar, Building2, Tag, Loader, X, Brain, ChevronRight } from "lucide-react";
import Link from "next/link";

const domaines = [
  { value: "", label: "Tous les domaines" },
  { value: "intelligence_competitive", label: "Intelligence Compétitive" },
  { value: "veille_strategique", label: "Veille Stratégique" },
  { value: "management_information", label: "Management de l'Information" },
  { value: "analyse_strategique", label: "Analyse Stratégique" },
  { value: "intelligence_economique", label: "Intelligence Économique" },
  { value: "gestion_connaissance", label: "Gestion des Connaissances" },
  { value: "data_intelligence", label: "Data Intelligence" },
  { value: "securite_informationnelle", label: "Sécurité Informationnelle" }
];

const institutions = [
  { value: "", label: "Toutes les institutions" },
  { value: "ISCAE", label: "ISCAE" },
  { value: "ESEN", label: "ESEN" }
];

const domainLabels: Record<string, string> = {
  intelligence_competitive: "Intelligence Compétitive",
  veille_strategique: "Veille Stratégique",
  management_information: "Management de l'Info",
  analyse_strategique: "Analyse Stratégique",
  intelligence_economique: "Intelligence Économique",
  gestion_connaissance: "Gestion des Connaissances",
  data_intelligence: "Data Intelligence",
  securite_informationnelle: "Sécurité Info"
};

interface PFE {
  id: string;
  titre: string;
  auteur: string;
  annee: number;
  institution: string;
  domaine_vic: string;
  mots_cles: string[];
  resume: string;
  summary: string;
  keywords: string[];
  problematic: string;
  solutions: string;
  status?: string;
  relevance_score?: number;
  snippet?: string;
  highlighted_sections?: {
    problematic?: string;
    solution?: string;
    resume?: string;
    summary?: string;
  };
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PFE[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [searchType, setSearchType] = useState<"full-text" | "semantic" | "hybrid" | "global">("global");
  const [filters, setFilters] = useState({
    domaine_vic: "",
    institution: "",
    annee: ""
  });
  const [selectedPFE, setSelectedPFE] = useState<PFE | null>(null);
  const [aiQuestion, setAiQuestion] = useState("");
  const [aiAnswer, setAiAnswer] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    // Load with initial filters if any
    if (filters.domaine_vic || filters.institution || filters.annee) {
      handleSearchWithFilters();
    } else {
      loadAllPFE();
    }
  }, []);

  useEffect(() => {
    // Real-time filtering when filters change (if already searched)
    if (searched) {
      if (query.trim()) {
        handleSearch(searchType);
      } else {
        handleSearchWithFilters();
      }
    }
  }, [filters]);

  const handleSearchWithFilters = async () => {
    setLoading(true);
    setSearched(true);
    
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const authToken = session?.access_token;
      
      const filterParams: any = {};
      if (filters.domaine_vic) filterParams.domaine_vic = filters.domaine_vic;
      if (filters.institution) filterParams.institution = filters.institution;
      if (filters.annee) filterParams.annee = parseInt(filters.annee);
      
      const headers: any = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }
      
      const response = await fetch("/api/v1/search/all?limit=50", {
        headers
      });
      let allResults = await response.json();
      
      // Apply filters locally
      let filtered = allResults.results || [];
      if (filterParams.domaine_vic) {
        filtered = filtered.filter((r: PFE) => r.domaine_vic === filterParams.domaine_vic);
      }
      if (filterParams.institution) {
        filtered = filtered.filter((r: PFE) => r.institution === filterParams.institution);
      }
      if (filterParams.annee) {
        filtered = filtered.filter((r: PFE) => r.annee === filterParams.annee);
      }
      
      setResults(filtered);
    } catch (error) {
      console.error("Filter error:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAllPFE = async () => {
    setLoading(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const authToken = session?.access_token;
      
      const headers: any = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }
      
      const response = await fetch("/api/v1/search/all?limit=50", {
        headers
      });
      const data = await response.json();
      setResults(data.results || []);
      setSearched(true);
    } catch (error) {
      console.error("Load PFE error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (type: "full-text" | "semantic" | "hybrid" | "global" = "global") => {
    if (!query.trim()) return;
    
    setLoading(true);
    setSearched(true);
    setSearchType(type);
    
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const authToken = session?.access_token;
      
      const endpoint = type === "global" ? `/api/v1/search/global` : `/api/v1/search/${type}`;
      const body: any = { query, limit: 20 };
      
      const filterParams: any = {};
      if (filters.domaine_vic) filterParams.domaine_vic = filters.domaine_vic;
      if (filters.institution) filterParams.institution = filters.institution;
      if (filters.annee) filterParams.annee = parseInt(filters.annee);
      
      if (Object.keys(filterParams).length > 0) {
        body.filters = filterParams;
      }
      
      const headers: any = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers,
        body: JSON.stringify(body)
      });
      
      const data = await response.json();
      
      // Global search returns {results: [{pfe, relevance_score, snippet, highlighted_sections}]}
      if (type === "global" && data.results) {
        setResults(data.results.map((r: any) => ({
          ...r.pfe,
          relevance_score: r.relevance_score,
          snippet: r.snippet,
          highlighted_sections: r.highlighted_sections
        })));
      } else {
        setResults(data.results || []);
      }
    } catch (error) {
      console.error("Search error:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({ domaine_vic: "", institution: "", annee: "" });
  };

  const handleAIAnalysis = async (pfe: PFE) => {
    if (!aiQuestion.trim()) return;
    
    setAiLoading(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const authToken = session?.access_token;
      
      const headers: any = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }
      
      const response = await fetch(`/api/v1/ai/analyze-pfe?pfe_id=${pfe.id}&question=${encodeURIComponent(aiQuestion)}`, {
        headers
      });
      
      const data = await response.json();
      setAiAnswer(data.answer || "");
    } catch (error) {
      console.error("AI analysis error:", error);
      setAiAnswer("Erreur lors de l'analyse");
    } finally {
      setAiLoading(false);
    }
  };

  const suggestedQuestions = [
    "Donne-moi un résumé du PFE",
    "Quel est l'état de l'art sur ce sujet?",
    "Propose une analyse critique",
    "Quelles méthodologies sont utilisées?",
    "Quelles sont les limites de cette étude?"
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Recherche</h1>
        <p className="text-slate-600">Recherchez dans les PFE du Master VIC</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex flex-col gap-4">
          <div className="relative">
            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="w-full pl-12 pr-4 py-4 text-lg border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Rechercher un sujet, thème, auteur..."
            />
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-500" />
              <span className="text-sm text-slate-600">Filtres:</span>
            </div>
            
            <select
              value={filters.domaine_vic}
              onChange={(e) => setFilters({ ...filters, domaine_vic: e.target.value })}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              {domaines.map((d) => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
            
            <select
              value={filters.institution}
              onChange={(e) => setFilters({ ...filters, institution: e.target.value })}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              {institutions.map((i) => (
                <option key={i.value} value={i.value}>{i.label}</option>
              ))}
            </select>
            
            <input
              type="number"
              value={filters.annee}
              onChange={(e) => setFilters({ ...filters, annee: e.target.value })}
              placeholder="Année"
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm w-24"
              min={2014}
              max={2026}
            />
            
            {(filters.domaine_vic || filters.institution || filters.annee) && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-1 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg"
              >
                <X className="w-4 h-4" />
                Effacer
              </button>
            )}
            
            <div className="flex-1" />
            
            <button
              onClick={() => query.trim() ? handleSearch("full-text") : handleSearchWithFilters()}
              disabled={loading}
              className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 text-sm"
            >
              Texte
            </button>
            <button
              onClick={() => query.trim() ? handleSearch("semantic") : handleSearchWithFilters()}
              disabled={loading}
              className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 text-sm"
            >
              Sémantique
            </button>
            <button
              onClick={() => query.trim() ? handleSearch("hybrid") : handleSearchWithFilters()}
              disabled={loading}
              className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50 text-sm"
            >
              Hybride
            </button>
            <button
              onClick={() => query.trim() ? handleSearch("global") : handleSearchWithFilters()}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm flex items-center gap-2"
            >
              <SearchIcon className="w-4 h-4" />
              Global (IA Document)
            </button>
          </div>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-slate-600">Recherche en cours...</span>
        </div>
      )}

      {!loading && searched && (
        <div className="space-y-4">
          <p className="text-slate-600">
            {(() => {
              const filterParts = [];
              if (filters.domaine_vic) filterParts.push(domainLabels[filters.domaine_vic] || filters.domaine_vic);
              if (filters.institution) filterParts.push(filters.institution);
              if (filters.annee) filterParts.push(filters.annee);
              
              if (!query.trim()) {
                if (filterParts.length > 0) {
                  return <>PFE filtrés par {filterParts.join(", ")} ({results.length} résultats)</>;
                }
                return <>Tous les PFE ({results.length} résultats)</>;
              }
              return <> {results.length} résultat{results.length !== 1 ? "s" : ""} pour "{query}"</>;
            })()}
          </p>
          
          {results.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              Aucun résultat trouvé
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((pfe) => (
                <div key={pfe.id} className="bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-300 transition">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-slate-900">{pfe.titre}</h3>
                        {pfe.relevance_score !== undefined && (
                          <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">
                            {Math.round(pfe.relevance_score * 100)}% pertinent
                          </span>
                        )}
                      </div>
                      
                      <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 mb-3">
                        <div className="flex items-center gap-1">
                          <User className="w-4 h-4" />
                          <span>{pfe.auteur}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          <span>{pfe.annee}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Building2 className="w-4 h-4" />
                          <span>{pfe.institution}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Tag className="w-4 h-4" />
                          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                            {domainLabels[pfe.domaine_vic] || pfe.domaine_vic}
                          </span>
                        </div>
                      </div>

                      {/* AI Summary */}
                      {pfe.summary && (
                        <p className="text-slate-600 text-sm line-clamp-2 mb-2">
                          <span className="font-medium">Résumé IA:</span> {pfe.summary}
                        </p>
                      )}

                      {/* Highlighted Snippet from Document Intelligence */}
                      {pfe.snippet && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                          <p className="text-sm text-slate-700">
                            <span className="font-medium">Extrait pertinent:</span>{' '}
                            <span dangerouslySetInnerHTML={{ __html: pfe.snippet }} />
                          </p>
                        </div>
                      )}

                      {/* Highlighted Sections */}
                      {pfe.highlighted_sections && (
                        <div className="space-y-2 mb-3">
                          {pfe.highlighted_sections.problematic && (
                            <div className="bg-blue-50 rounded p-2">
                              <p className="text-xs font-semibold text-blue-900 mb-1">Problématique:</p>
                              <p className="text-sm text-blue-800" dangerouslySetInnerHTML={{ __html: pfe.highlighted_sections.problematic }} />
                            </div>
                          )}
                          {pfe.highlighted_sections.solution && (
                            <div className="bg-green-50 rounded p-2">
                              <p className="text-xs font-semibold text-green-900 mb-1">Solution:</p>
                              <p className="text-sm text-green-800" dangerouslySetInnerHTML={{ __html: pfe.highlighted_sections.solution }} />
                            </div>
                          )}
                        </div>
                      )}

                      {/* Keywords */}
                      {pfe.keywords && pfe.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {pfe.keywords.slice(0, 5).map((kw, i) => (
                            <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                              {kw}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Traditional resume */}
                      {pfe.resume && !pfe.snippet && (
                        <p className="text-slate-600 text-sm line-clamp-2">{pfe.resume}</p>
                      )}
                    </div>

                    <div className="flex flex-col gap-2">
                      <Link
                        href={`/pfe/${pfe.id}`}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                      >
                        <ChevronRight className="w-5 h-5" />
                      </Link>
                      <button
                        onClick={() => {
                          setSelectedPFE(pfe);
                          setAiAnswer("");
                          setAiQuestion("");
                        }}
                        className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg"
                        title="Analyser avec l'IA"
                      >
                        <Brain className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!searched && !loading && (
        <div className="text-center py-12 text-slate-500">
          Entrez un terme de recherche pour commencer
        </div>
      )}

      {selectedPFE && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-slate-200">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{selectedPFE.titre}</h2>
                  <p className="text-sm text-slate-600 mt-1">
                    {selectedPFE.auteur} • {selectedPFE.annee} • {selectedPFE.institution}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedPFE(null)}
                  className="p-2 hover:bg-slate-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <div>
                <h3 className="font-semibold text-slate-900 mb-2">Analyse IA</h3>
                <div className="flex flex-wrap gap-2 mb-4">
                  {suggestedQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => setAiQuestion(q)}
                      className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-full text-sm hover:bg-purple-100"
                    >
                      {q}
                    </button>
                  ))}
                </div>
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAIAnalysis(selectedPFE)}
                    placeholder="Posez votre question..."
                    className="flex-1 px-4 py-2 border border-slate-300 rounded-lg"
                  />
                  <button
                    onClick={() => handleAIAnalysis(selectedPFE)}
                    disabled={aiLoading || !aiQuestion.trim()}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                  >
                    {aiLoading ? <Loader className="w-5 h-5 animate-spin" /> : <Brain className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              
              {aiAnswer && (
                <div className="bg-purple-50 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-900 mb-2">Réponse:</h4>
                  <p className="text-purple-800 whitespace-pre-wrap">{aiAnswer}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}