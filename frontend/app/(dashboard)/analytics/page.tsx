"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";
import { TrendingUp, TrendingDown, BarChart3, PieChart, Target, AlertTriangle, Building2, Calendar, Users, BookOpen } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPie, Pie, Cell } from "recharts";

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

interface EmergingTopic {
  topic: string;
  count: number;
  trend: string;
}

interface GapAnalysis {
  domaine_vic: string;
  missing_keywords: string[];
  opportunity_score: number;
}

interface Comparison {
  iscae_count: number;
  esen_count: number;
  common_domains: string[];
  unique_iscae: string[];
  unique_esen: string[];
}

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#06b6d4", "#84cc16"];

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

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<Stats | null>(null);
  const [domains, setDomains] = useState<DomainStat[]>([]);
  const [timeline, setTimeline] = useState<YearStat[]>([]);
  const [emerging, setEmerging] = useState<EmergingTopic[]>([]);
  const [gaps, setGaps] = useState<GapAnalysis[]>([]);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    const supabase = createClient();
    try {
      // Récupère la session utilisateur
      const { data: { session } } = await supabase.auth.getSession();
      const authToken = session?.access_token;
      if (!authToken) {
        // Redirige vers login si pas connecté
        window.location.href = "/login";
        return;
      }

      const headers = { "Authorization": `Bearer ${authToken}` };

      const [overviewRes, domainsRes, timelineRes, emergingRes, gapsRes, comparisonRes] = await Promise.all([
        fetch("/api/v1/analytics/overview", { headers }).then(r => r.json()).catch(() => null),
        fetch("/api/v1/analytics/domains", { headers }).then(r => r.json()).catch(() => ({ domains: [] })),
        fetch("/api/v1/analytics/timeline", { headers }).then(r => r.json()).catch(() => ({ years: [] })),
        fetch("/api/v1/analytics/emerging", { headers }).then(r => r.json()).catch(() => ({ topics: [] })),
        fetch("/api/v1/analytics/gaps", { headers }).then(r => r.json()).catch(() => ({ gaps: [] })),
        fetch("/api/v1/analytics/comparison", { headers }).then(r => r.json()).catch(() => null)
      ]);

      if (overviewRes) setOverview(overviewRes);
      if (domainsRes?.domains) setDomains(domainsRes.domains);
      if (timelineRes?.years) setTimeline(timelineRes.years);
      if (emergingRes?.topics) setEmerging(emergingRes.topics);
      if (gapsRes?.gaps) setGaps(gapsRes.gaps);
      if (comparisonRes) setComparison(comparisonRes);
    } catch (error) {
      console.error("Error loading analytics:", error);
    } finally {
      setLoading(false);
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
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Analytics</h1>
        <p className="text-slate-600">Tableaux de bord analytiques du Master VIC</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">{overview?.total_pfe || 0}</p>
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
              <p className="text-2xl font-bold text-slate-900">{overview?.total_auteurs || 0}</p>
              <p className="text-sm text-slate-600">Auteurs</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">{overview?.domains_count || 0}</p>
              <p className="text-sm text-slate-600">Domaines VIC</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <Calendar className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900">
                {overview?.annee_min || 2014} - {overview?.annee_max || 2026}
              </p>
              <p className="text-sm text-slate-600">Période</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">Répartition par Domaine VIC</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPie>
                <Pie
                  data={domains}
                  dataKey="count"
                  nameKey="domaine_vic"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
                >
                  {domains.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPie>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            {domains.map((d, i) => (
              <div key={d.domaine_vic} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                <span className="text-xs text-slate-600">{domainLabels[d.domaine_vic] || d.domaine_vic}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">Évolution des PFE</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="annee" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">
            <TrendingUp className="w-5 h-5 inline mr-2" />
            Sujets Émergents
          </h2>
          <div className="space-y-3">
            {emerging.length === 0 ? (
              <p className="text-slate-500 text-center py-4">Aucune donnée disponible</p>
            ) : (
              emerging.map((topic) => (
                <div key={topic.topic} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                  <span className="text-sm text-slate-700">{topic.topic}</span>
                  <div className="flex items-center gap-2">
                    {topic.trend === "up" && <TrendingUp className="w-4 h-4 text-green-600" />}
                    <span className="text-sm font-medium text-slate-900">{topic.count}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">
            <AlertTriangle className="w-5 h-5 inline mr-2 text-yellow-600" />
            Lacunes de Recherche
          </h2>
          <div className="space-y-4">
            {gaps.length === 0 ? (
              <p className="text-slate-500 text-center py-4">Aucune donnée disponible</p>
            ) : (
              gaps.map((gap) => (
                <div key={gap.domaine_vic} className="p-4 bg-yellow-50 rounded-lg">
                  <p className="font-medium text-slate-900 mb-2">{domainLabels[gap.domaine_vic] || gap.domaine_vic}</p>
                  <p className="text-sm text-slate-600">Score: {Math.round(gap.opportunity_score * 100)}%</p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {gap.missing_keywords.slice(0, 3).map((kw) => (
                      <span key={kw} className="px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded text-xs">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-6">
          <Building2 className="w-5 h-5 inline mr-2" />
          Comparaison ISCAE vs ESEN
        </h2>
        <div className="grid sm:grid-cols-2 gap-8">
          <div className="text-center p-6 bg-blue-50 rounded-xl">
            <p className="text-3xl font-bold text-blue-600">{comparison?.iscae_count || 0}</p>
            <p className="text-sm text-blue-600">PFE ISCAE</p>
          </div>
          <div className="text-center p-6 bg-green-50 rounded-xl">
            <p className="text-3xl font-bold text-green-600">{comparison?.esen_count || 0}</p>
            <p className="text-sm text-green-600">PFE ESEN</p>
          </div>
        </div>
        
        <div className="mt-6 grid sm:grid-cols-3 gap-4">
          <div>
            <p className="text-sm font-medium text-slate-700 mb-2">Domaines Communs</p>
            <div className="flex flex-wrap gap-1">
              {(comparison?.common_domains || []).map((d) => (
                <span key={d} className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs">
                  {domainLabels[d] || d}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-slate-700 mb-2">Uniques ISCAE</p>
            <div className="flex flex-wrap gap-1">
              {(comparison?.unique_iscae || []).map((d) => (
                <span key={d} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                  {domainLabels[d] || d}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-slate-700 mb-2">Uniques ESEN</p>
            <div className="flex flex-wrap gap-1">
              {(comparison?.unique_esen || []).map((d) => (
                <span key={d} className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                  {domainLabels[d] || d}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}