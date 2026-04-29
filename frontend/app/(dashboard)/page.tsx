"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { BookOpen, Users, TrendingUp, Award, ArrowUpRight, FileText, BarChart3 } from "lucide-react";

interface Stats {
  total_pfe: number;
  total_auteurs: number;
  annee_min: number;
  annee_max: number;
  domains_count: number;
  institutions_count: number;
}

interface DomainStat {
  domaine_vic: string;
  count: number;
  percentage: number;
}

interface YearStat {
  annee: number;
  count: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [domains, setDomains] = useState<DomainStat[]>([]);
  const [timeline, setTimeline] = useState<YearStat[]>([]);
  const [emerging, setEmerging] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [overviewRes, domainsRes, timelineRes, emergingRes] = await Promise.all([
        fetch("/api/v1/analytics/overview").then(r => r.json()).catch(() => null),
        fetch("/api/v1/analytics/domains").then(r => r.json()).catch(() => ({ domains: [] })),
        fetch("/api/v1/analytics/timeline").then(r => r.json()).catch(() => ({ years: [] })),
        fetch("/api/v1/analytics/emerging").then(r => r.json()).catch(() => ({ topics: [] }))
      ]);
      
      if (overviewRes) setStats(overviewRes);
      if (domainsRes?.domains) setDomains(domainsRes.domains);
      if (timelineRes?.years) setTimeline(timelineRes.years);
      if (emergingRes?.topics) setEmerging(emergingRes.topics);
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const domainLabels: Record<string, string> = {
    intelligence_competitive: "Intelligence Compétitive",
    veille_strategique: "Veille Stratégique",
    management_information: "Management de l'Info",
    analyse_strategique: "Analyse Stratégique",
    intelligence_economique: "Intelligence Économique",
    gestion_connaissance: "Gestion des Connaissances",
    data_intelligence: "Data Intelligence",
    securite_informationnelle: "Sécurité Informationnelle"
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-600">Vue d'ensemble des PFE du Master VIC</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">{stats?.total_pfe || 0}</p>
              <p className="text-sm text-slate-600">Total PFE</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">{stats?.total_auteurs || 0}</p>
              <p className="text-sm text-slate-600">Auteurs</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">{stats?.domains_count || 0}</p>
              <p className="text-sm text-slate-600">Domaines VIC</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <Award className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {stats?.annee_min || 2014} - {stats?.annee_max || 2026}
              </p>
              <p className="text-sm text-slate-600">Période</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-900">Répartition par Domaine VIC</h2>
            <Link href="/analytics" className="text-sm text-blue-600 hover:underline">Voir tout</Link>
          </div>
          <div className="space-y-4">
            {domains.slice(0, 5).map((domain, index) => (
              <div key={domain.domaine_vic} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-700">
                    {domainLabels[domain.domaine_vic] || domain.domaine_vic}
                  </span>
                  <span className="text-sm font-medium text-slate-900">{domain.count}</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 rounded-full transition-all"
                    style={{ width: `${domain.percentage}%` }}
                  />
                </div>
              </div>
            ))}
            {domains.length === 0 && (
              <p className="text-slate-500 text-center py-4">Aucune donnée disponible</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-900">Évolution des PFE</h2>
            <Link href="/analytics" className="text-sm text-blue-600 hover:underline">Voir tout</Link>
          </div>
          <div className="space-y-3">
            {timeline.slice(0, 6).map((year) => (
              <div key={year.annee} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                <span className="text-sm text-slate-700">{year.annee}</span>
                <span className="text-sm font-medium text-slate-900">{year.count} PFE</span>
              </div>
            ))}
            {timeline.length === 0 && (
              <p className="text-slate-500 text-center py-4">Aucune donnée disponible</p>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-slate-900">Moteur d'Intelligence Documentaire</h2>
          <Link href="/search" className="text-sm text-blue-600 hover:underline">Tester la recherche</Link>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">TF-IDF</h3>
            <p className="text-sm text-blue-700">Algorithme de pertinence basé sur la fréquence des termes</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <h3 className="font-medium text-green-900 mb-2">Parsing de Sections</h3>
            <p className="text-sm text-green-700">Extraction automatique: Problématique, Solution, Conclusion</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <h3 className="font-medium text-purple-900 mb-2">PostgreSQL Full-Text</h3>
            <p className="text-sm text-purple-700">Recherche dans titre, résumé, mots-clés</p>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg">
            <h3 className="font-medium text-orange-900 mb-2">Surlignage</h3>
            <p className="text-sm text-orange-700">Extraits pertinents avec mots surlignés en <mark>jaune</mark></p>
          </div>
        </div>
        <div className="mt-4 p-4 bg-slate-50 rounded-lg">
          <p className="text-sm text-slate-600">
            <strong>Fonctionnement:</strong> Ce moteur fonctionne SANS IA cloud. Il utilise l'analyse de texte (PyMuPDF), 
            le classement TF-IDF et la recherche plein texte PostgreSQL pour trouver les documents pertinents.
          </p>
        </div>
      </div>
    </div>
  );
}