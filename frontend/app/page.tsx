"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { BookOpen, GraduationCap, Users, Search, BarChart3, Building2, User, LogOut } from 'lucide-react';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function HomePage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      setLoading(false);
    };
    getUser();
  }, []);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.refresh();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg gradient-primary flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-900">Knowledge Hub</h1>
                <p className="text-xs text-slate-500">Master VIC - ISCAE/ESEN</p>
              </div>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              <Link href="/master-vic" className="text-sm text-slate-600 hover:text-slate-900">Master VIC</Link>
              <Link href="/search" className="text-sm text-slate-600 hover:text-slate-900">Recherche</Link>
              <Link href="/analytics" className="text-sm text-slate-600 hover:text-slate-900">Analytics</Link>
            </nav>
            
            {user ? (
              <div className="flex items-center gap-3">
                <Link href="/" className="flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-100 rounded-lg">
                  <User className="w-4 h-4" />
                  <span className="font-medium">
                    {user.user_metadata?.first_name && user.user_metadata?.last_name
                      ? `${user.user_metadata.first_name} ${user.user_metadata.last_name}`
                      : user.email?.split('@')[0] || 'Utilisateur'}
                  </span>
                </Link>
                <button onClick={handleSignOut} className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg">
                  <LogOut className="w-4 h-4" />
                  <span>Déconnexion</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login" className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900">Connexion</Link>
                <Link href="/register" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">Inscription</Link>
              </div>
            )}
          </div>
        </div>
      </header>

      <main>
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-full text-sm text-blue-700 mb-6">
              <BookOpen className="w-4 h-4" />
              <span>Master en Intelligence Compétitive et Veille Stratégique</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
              Gérez vos PFE avec
              <span className="text-blue-600 block">l'Intelligence Artificielle</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-10">
              Une plateforme intelligente pour la gestion, la structuration et l'exploitation des mémoires académiques du Master VIC.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register" className="px-8 py-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition">
                Commencer maintenant
              </Link>
              <Link href="/master-vic" className="px-8 py-4 border border-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition">
                Découvrir le Master VIC
              </Link>
            </div>
          </div>
        </section>

        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 card-hover">
                <Search className="w-10 h-10 text-blue-600 mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Recherche Intelligente</h3>
                <p className="text-slate-600">Recherche sémantique basée sur l'IA pour trouver les PFE les plus pertinents.</p>
              </div>
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 card-hover">
                <BarChart3 className="w-10 h-10 text-purple-600 mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Analytics Avancé</h3>
                <p className="text-slate-600">Tableaux de bord analytiques pour comprendre les tendances de recherche.</p>
              </div>
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 card-hover">
                <BookOpen className="w-10 h-10 text-green-600 mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">État de l'Art</h3>
                <p className="text-slate-600">Générez automatiquement des synthèses basées sur les PFE existants.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center gap-3 mb-8">
              <Building2 className="w-8 h-8 text-slate-700" />
              <h2 className="text-3xl font-bold text-slate-900">Institutions Partenaires</h2>
            </div>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="p-8 rounded-xl border border-slate-200 bg-white">
                <div className="w-16 h-16 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-blue-600">ISCAE</span>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">Institut Supérieur des Sciences Comptables</h3>
                <p className="text-slate-600">Institut Supérieur des Sciences Comptables et d'Administration des Entreprises</p>
              </div>
              <div className="p-8 rounded-xl border border-slate-200 bg-white">
                <div className="w-16 h-16 rounded-lg bg-green-100 flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-green-600">ESEN</span>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">École Supérieure d'Expertise</h3>
                <p className="text-slate-600">École Supérieure d'Expertise et de Gestion des Entreprises</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-slate-900 text-slate-400 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p>© 2026 Knowledge Hub for PFE | Master VIC - ISCAE/ESEN</p>
          <p className="mt-2">Coordinateur: Afef Belghith - afef.belghith@iscae.uma.tn</p>
        </div>
      </footer>
    </div>
  );
}