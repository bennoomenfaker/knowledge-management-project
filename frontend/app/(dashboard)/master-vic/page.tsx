"use client";

import { useEffect, useState } from "react";
import { GraduationCap, Mail, Target, TrendingUp, Users, Award, BookOpen, Globe, Calendar, ArrowRight, CheckCircle } from "lucide-react";

const timeline = [
  { year: 2014, event: "Lancement du Master VIC", description: "Partenariat ISCAE - ESEN" },
  { year: 2015, event: "Première promotion", description: "Première cohorte de diplômé.e.s" },
  { year: 2016, event: "Partenariat international", description: "Accords avec des universités européennes" },
  { year: 2017, event: "Intégration outils IA", description: "Introduction des technologies d'IA dans le programme" },
  { year: 2018, event: "Certification", description: "Obtention de la certification nationale" },
  { year: 2019, event: "Upgrade programme", description: "Mise à niveau vers VIC 2.0" },
  { year: 2020, event: "Digitalisation", description: "Adaptation au contexte pandémique" },
  { year: 2021, event: "Veille pandémie", description: "Focus sur la veille sectorielle santé" },
  { year: 2022, event: "AI & VIC", description: "Intégration LLMs et IA générative" },
  { year: 2023, event: "Expansion", description: "Nouveaux partenariats industriels" },
  { year: 2024, event: "10 ans VIC", description: "Célébration du 10e anniversaire" },
  { year: 2025, event: "Transformation digitale", description: "Modernisation complète du programme" },
  { year: 2026, event: "Nouvelle ère", description: "VIC - Intelligence Artificielle" }
];

const objectives = [
  { icon: Target, title: "Intelligence Compétitive", description: "Développer les compétences en intelligence compétitive" },
  { icon: TrendingUp, title: "Veille Stratégique", description: "Maîtriser les techniques de veille stratégique" },
  { icon: Users, title: "Analyse des Environnements", description: "Analyser les environnements complexes" },
  { icon: BookOpen, title: "Gestion de l'Information", description: "Gestion de l'information stratégique" }
];

const competences = [
  "Intelligence Compétitive",
  "Veille Stratégique",
  "Analyse des Environnements",
  "Gestion de l'Information",
  "Management de la Connaissance",
  "Veille Technologique"
];

const debouches = [
  "Analyste en intelligence économique",
  "Consultant en management de l'information",
  "Chargé de veille stratégique",
  "Chef de projet VIC",
  "Médiateur de veille",
  "Responsable Knowledge Management"
];

export default function MasterVICPage() {
  const [activeYear, setActiveYear] = useState(2014);

  return (
    <div className="space-y-12 animate-fade-in">
      <div className="text-center py-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl text-white">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/20 rounded-full text-sm mb-6">
          <GraduationCap className="w-4 h-4" />
          <span>Master Professionnel</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4">Master VIC</h1>
        <p className="text-xl text-blue-100 max-w-2xl mx-auto">
          Master en Intelligence Compétitive et Veille Stratégique
        </p>
        <div className="flex items-center justify-center gap-6 mt-8 text-sm">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <span>Lancé en 2014</span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            <span>ISCAE + ESEN</span>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Coordinateur</h2>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-xl font-bold text-blue-600">AB</span>
            </div>
            <div>
              <p className="font-semibold text-slate-900">Afef Belghith</p>
              <a href="mailto:afef.belghith@iscae.uma.tn" className="flex items-center gap-2 text-sm text-blue-600 hover:underline">
                <Mail className="w-4 h-4" />
                afef.belghith@iscae.uma.tn
              </a>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Institutions Partenaires</h2>
          <div className="flex items-center gap-6">
            <div className="flex-1 p-4 bg-blue-50 rounded-lg text-center">
              <span className="text-lg font-bold text-blue-600">ISCAE</span>
              <p className="text-xs text-blue-600/70">Institut Supérieur des Sciences Comptables</p>
            </div>
            <ArrowRight className="w-5 h-5 text-slate-400" />
            <div className="flex-1 p-4 bg-green-50 rounded-lg text-center">
              <span className="text-lg font-bold text-green-600">ESEN</span>
              <p className="text-xs text-green-600/70">École Supérieure d'Expertise</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-6">Objectifs Pédagogiques</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {objectives.map((obj) => (
            <div key={obj.title} className="flex items-start gap-3 p-4 bg-slate-50 rounded-lg">
              <obj.icon className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium text-slate-900">{obj.title}</p>
                <p className="text-sm text-slate-600">{obj.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-6">Compétences Développées</h2>
        <div className="flex flex-wrap gap-2">
          {competences.map((comp) => (
            <span key={comp} className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
              {comp}
            </span>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-6">Débouchés Professionnels</h2>
        <div className="grid sm:grid-cols-2 gap-3">
          {debouches.map((job) => (
            <div key={job} className="flex items-center gap-2 text-slate-700">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>{job}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-6">Timeline Interactive (2014-2026)</h2>
        <div className="flex overflow-x-auto pb-4 gap-2">
          {timeline.map((item) => (
            <button
              key={item.year}
              onClick={() => setActiveYear(item.year)}
              className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition ${
                activeYear === item.year
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {item.year}
            </button>
          ))}
        </div>
        <div className="mt-6 p-6 bg-slate-50 rounded-xl">
          {timeline.filter(t => t.year === activeYear).map(t => (
            <div key={t.year}>
              <p className="text-2xl font-bold text-blue-600 mb-2">{t.year}</p>
              <p className="text-lg font-semibold text-slate-900">{t.event}</p>
              <p className="text-slate-600">{t.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Modèle Théorique</h2>
        <div className="flex items-center justify-center gap-4 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl">
          <div className="text-center px-4">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mb-2">
              <span className="font-bold text-purple-600">S</span>
            </div>
            <p className="text-sm font-medium">Socialization</p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-400" />
          <div className="text-center px-4">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-2">
              <span className="font-bold text-blue-600">E</span>
            </div>
            <p className="text-sm font-medium">Externalization</p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-400" />
          <div className="text-center px-4">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-2">
              <span className="font-bold text-green-600">C</span>
            </div>
            <p className="text-sm font-medium">Combination</p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-400" />
          <div className="text-center px-4">
            <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center mb-2">
              <span className="font-bold text-orange-600">I</span>
            </div>
            <p className="text-sm font-medium">Internalization</p>
          </div>
        </div>
        <p className="text-center text-slate-600 mt-4">SECI Model (Nonaka & Takeuchi)</p>
      </div>
    </div>
  );
}