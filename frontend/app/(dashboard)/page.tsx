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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [overviewRes, domainsRes, timelineRes] = await Promise.all([
        fetch("/api/v1/analytics/overview").then(r => r.json()).catch(() => null),
        fetch("/api/v1/analytics/domains").then(r => r.json()).catch(() => ({ domains: [] })),
        fetch("/api/v1/analytics/timeline").then(r => r.json()).catch(() => ({ years: [] }))
      ]);

      if (overviewRes) setStats(overviewRes);
      if (domainsRes?.domains) setDomains(domainsRes.domains);
      if (timelineRes?.years) setTimeline(timelineRes.years);
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
          <h2 className="text-lg font-semibold text-slate-900">Actions Rapides</h2>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/pfe/upload" className="flex items-center gap-4 p-4 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <Upload className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="font-medium text-slate-900">Uploader un PFE</p>
              <p className="text-sm text-slate-500">Ajouter un mémoire</p>
            </div>
          </Link>
          
          <Link href="/search" className="flex items-center gap-4 p-4 rounded-lg border border-slate-200 hover:border-green-300 hover:bg-green-50 transition">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Search className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="font-medium text-slate-900">Rechercher</p>
              <p className="text-sm text-slate-500">Recherche IA</p>
            </div>
          </Link>
          
          <Link href="/pfe" className="flex items-center gap-4 p-4 rounded-lg border border-slate-200 hover:border-purple-300 hover:bg-purple-50 transition">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="font-medium text-slate-900">Tous les PFE</p>
              <p className="text-sm text-slate-500">Parcourir</p>
            </div>
          </Link>
          
          <Link href="/analytics" className="flex items-center gap-4 p-4 rounded-lg border border-slate-200 hover:border-orange-300 hover:bg-orange-50 transition">
            <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="font-medium text-slate-900">Analytics</p>
              <p className="text-sm text-slate-500">Statistiques</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}