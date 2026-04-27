"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, FileText, User, Calendar, Building2, Tag, Download, Eye } from "lucide-react";
import { supabase } from "@/lib/supabase";

interface PFE {
  id: string;
  titre: string;
  auteur: string;
  email_auteur: string;
  annee: number;
  institution: string;
  domaine_vic: string;
  type_veille: string;
  mots_cles: string[];
  resume: string;
  problematic: string;
  methodology: string;
  file_path: string;
  file_url?: string;
  file_size: number;
  status: string;
  created_at: string;
}

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

export default function PFEDetailPage() {
  const params = useParams();
  const pfeId = params?.id as string;
  const [pfe, setPFE] = useState<PFE | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);

  useEffect(() => {
    if (pfeId) {
      loadPFE();
    }
  }, [pfeId]);

  const loadPFE = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      
      const response = await fetch(`/api/v1/pfe/${pfeId}`, {
        headers: token ? { "Authorization": `Bearer ${token}` } : {}
      });
      
      if (response.ok) {
        const data = await response.json();
        setPFE(data);
        
        if (data.file_url) {
          setViewerUrl(data.file_url);
        } else if (data.file_path) {
          generateViewerUrl(data.file_path);
        }
      }
    } catch (error) {
      console.error("Error loading PFE:", error);
    } finally {
      setLoading(false);
    }
  };

  const generateViewerUrl = (filePath: string) => {
    const minioHost = "127.0.0.1:9000";
    const encodedPath = btoa(filePath).replace(/=/g, '');
    const url = `http://${minioHost}/documents/${filePath}`;
    console.log("PDF URL:", url);
    setViewerUrl(url);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!pfe) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-600">PFE non trouvé</p>
        <Link href="/pfe" className="text-blue-600 hover:underline mt-2 inline-block">
          Retour à la liste
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link href="/pfe" className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900">
        <ArrowLeft className="w-4 h-4" />
        Retour à la liste
      </Link>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 mb-2">{pfe.titre}</h1>
            <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600">
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
              <span className={`px-2 py-0.5 rounded text-xs ${
                pfe.status === 'complete' ? 'bg-green-100 text-green-700' :
                pfe.status === 'en_traitement' ? 'bg-yellow-100 text-yellow-700' :
                'bg-slate-100 text-slate-700'
              }`}>
                {pfe.status}
              </span>
            </div>
          </div>
        </div>

        {pfe.resume && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-2">Résumé</h2>
            <p className="text-slate-600">{pfe.resume}</p>
          </div>
        )}

        {pfe.problematic && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-2">Problématique</h2>
            <p className="text-slate-600">{pfe.problematic}</p>
          </div>
        )}

        {pfe.methodology && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-2">Méthodologie</h2>
            <p className="text-slate-600">{pfe.methodology}</p>
          </div>
        )}

        {pfe.mots_cles && pfe.mots_cles.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-2">Mots-clés</h2>
            <div className="flex flex-wrap gap-2">
              {pfe.mots_cles.map((kw, i) => (
                <span key={i} className="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm">
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center gap-3">
          <Tag className="w-4 h-4 text-slate-400" />
          <span className="text-sm text-slate-500">
            {domainLabels[pfe.domaine_vic] || pfe.domaine_vic}
          </span>
          {pfe.type_veille && (
            <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
              {typeVeilleLabels[pfe.type_veille] || pfe.type_veille}
            </span>
          )}
        </div>
      </div>

      {viewerUrl && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Document PDF</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-blue-600" />
                <div>
                  <p className="font-medium text-slate-900">Document attaché</p>
                  <p className="text-sm text-slate-500">{formatFileSize(pfe.file_size || 0)}</p>
                </div>
              </div>
              <a
                href={viewerUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Eye className="w-4 h-4" />
               Voir le PDF
              </a>
            </div>
            
            <iframe
              src={viewerUrl}
              className="w-full h-[600px] border border-slate-200 rounded-lg"
              title="PDF Viewer"
            />
          </div>
        </div>
      )}
    </div>
  );
}