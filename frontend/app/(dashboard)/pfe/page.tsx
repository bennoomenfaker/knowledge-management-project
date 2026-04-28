"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { FileText, User, Calendar, Building2, Tag, MoreVertical, Edit, Trash2, Eye, Grid, List } from "lucide-react";

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

const typeVeilleLabels: Record<string, string> = {
  strategique: "Veille Stratégique",
  concurrentielle: "Veille Concurrentielle",
  reglementaire: "Veille Réglementaire",
  technologique: "Veille Technologique",
  juridique: "Veille Juridique",
  commerciale: "Veille Commerciale",
  marketing: "Veille Marketing",
  organisationnelle: "Veille Organisationnelle"
};

interface PFE {
  id: string;
  titre: string;
  auteur: string;
  annee: number;
  institution: string;
  domaine_vic: string;
  type_veille: string;
  mots_cles: string[];
  resume: string;
  status: string;
  created_at: string;
}

export default function PFEListPage() {
  const [pfeList, setPFEList] = useState<PFE[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");

  useEffect(() => {
    checkUserAndLoadPFE();
  }, []);

  const checkUserAndLoadPFE = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      
      if (user) {
        await loadPFE();
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadPFE = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const authToken = session?.access_token;
      if (!authToken) return;
      const response = await fetch("/api/v1/pfe?limit=50", {
        headers: { "Authorization": `Bearer ${authToken}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPFEList(data);
      }
    } catch (error) {
      console.error("Error loading PFE:", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Tous les PFE</h1>
          <p className="text-slate-600">{pfeList.length} mémoire(s) disponible(s)</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode("grid")}
            className={`p-2 rounded-lg ${viewMode === "grid" ? "bg-blue-100 text-blue-600" : "text-slate-400 hover:text-slate-600"}`}
            title="Vue grille"
          >
            <Grid className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`p-2 rounded-lg ${viewMode === "list" ? "bg-blue-100 text-blue-600" : "text-slate-400 hover:text-slate-600"}`}
            title="Vue liste"
          >
            <List className="w-5 h-5" />
          </button>
          <Link href="/pfe/upload" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 ml-2">
            Uploader un PFE
          </Link>
        </div>
      </div>

      {pfeList.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-600 mb-4">Aucun PFE disponible pour le moment</p>
          <Link href="/pfe/upload" className="text-blue-600 hover:underline">
            Uploader le premier PFE
          </Link>
        </div>
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pfeList.map((pfe) => (
            <Link key={pfe.id} href={`/pfe/${pfe.id}`} className="bg-white rounded-xl border border-slate-200 p-4 hover:border-blue-300 transition flex flex-col">
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 line-clamp-2">{pfe.titre}</h3>
                <p className="text-sm text-slate-600 mt-1">{pfe.auteur} • {pfe.annee}</p>
                <p className="text-xs text-slate-500 mt-2">{pfe.institution}</p>
              </div>
              {pfe.resume && (
                <p className="text-slate-600 text-sm mt-3 line-clamp-3">{pfe.resume}</p>
              )}
              {pfe.mots_cles && pfe.mots_cles.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {pfe.mots_cles.slice(0, 3).map((kw, i) => (
                    <span key={i} className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs">
                      {kw}
                    </span>
                  ))}
                </div>
              )}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
                <span className={`px-2 py-0.5 rounded text-xs ${
                  pfe.status === 'complete' ? 'bg-green-100 text-green-700' :
                  pfe.status === 'en_traitement' ? 'bg-yellow-100 text-yellow-700' :
                  pfe.status === 'erreur' ? 'bg-red-100 text-red-700' :
                  'bg-slate-100 text-slate-700'
                }`}>
                  {pfe.status}
                </span>
                <span className="text-xs text-slate-500">
                  {domainLabels[pfe.domaine_vic] || pfe.domaine_vic}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {pfeList.map((pfe) => (
            <div key={pfe.id} className="bg-white rounded-xl border border-slate-200 p-6 hover:border-blue-300 transition">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <Link href={`/pfe/${pfe.id}`} className="text-lg font-semibold text-slate-900 hover:text-blue-600">
                    {pfe.titre}
                  </Link>
                  
                  <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 mt-2">
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
                    {pfe.type_veille && (
                      <span className="px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-700">
                        {typeVeilleLabels[pfe.type_veille] || pfe.type_veille}
                      </span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      pfe.status === 'complete' ? 'bg-green-100 text-green-700' :
                      pfe.status === 'en_traitement' ? 'bg-yellow-100 text-yellow-700' :
                      pfe.status === 'erreur' ? 'bg-red-100 text-red-700' :
                      'bg-slate-100 text-slate-700'
                    }`}>
                      {pfe.status}
                    </span>
                  </div>
                  
                  {pfe.resume && (
                    <p className="text-slate-600 text-sm mt-3 line-clamp-2">{pfe.resume}</p>
                  )}
                  
                  {pfe.mots_cles && pfe.mots_cles.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {pfe.mots_cles.slice(0, 5).map((kw, i) => (
                        <span key={i} className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs">
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  <Tag className="w-4 h-4 text-slate-400" />
                  <span className="text-xs text-slate-500">
                    {domainLabels[pfe.domaine_vic] || pfe.domaine_vic}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}