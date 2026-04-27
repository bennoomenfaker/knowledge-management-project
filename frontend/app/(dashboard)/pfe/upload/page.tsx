"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { Upload, FileText, AlertCircle, Check, Loader, X } from "lucide-react";

const typeVeille = [
  { value: "strategique", label: "Veille Stratégique" },
  { value: "concurrentielle", label: "Veille Concurrentielle" },
  { value: "reglementaire", label: "Veille Réglementaire" },
  { value: "technologique", label: "Veille Technologique" },
  { value: "juridique", label: "Veille Juridique" },
  { value: "commerciale", label: "Veille Commerciale" },
  { value: "marketing", label: "Veille Marketing" },
  { value: "organisationnelle", label: "Veille Organisationnelle" }
];

const domaines = [
  { value: "intelligence_competitive", label: "Intelligence Compétitive" },
  { value: "veille_strategique", label: "Veille Stratégique" },
  { value: "management_information", label: "Management de l'Information" },
  { value: "analyse_strategique", label: "Analyse Stratégique" },
  { value: "intelligence_economique", label: "Intelligence Économique" },
  { value: "gestion_connaissance", label: "Gestion des Connaissances" },
  { value: "data_intelligence", label: "Data Intelligence" },
  { value: "securite_informationnelle", label: "Sécurité Informationnelle" }
];

interface FormErrors {
  titre?: string;
  auteur?: string;
  file?: string;
}

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [success, setSuccess] = useState(false);
  
  const [metadata, setMetadata] = useState({
    titre: "",
    auteur: "",
    annee: new Date().getFullYear(),
    type_veille: "strategique",
    domaine_vic: "intelligence_competitive",
    mots_cles: ""
  });

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    if (!metadata.titre || metadata.titre.trim().length < 5) {
      newErrors.titre = "Le titre doit contenir au moins 5 caractères";
    }
    
    if (!metadata.auteur || metadata.auteur.trim().length < 2) {
      newErrors.auteur = "Le nom de l'auteur doit contenir au moins 2 caractères";
    }
    
    if (!file) {
      newErrors.file = "Veuillez sélectionner un fichier PDF";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        setError("Veuillez sélectionner un fichier PDF");
        setErrors({ ...errors, file: "Veuillez sélectionner un fichier PDF" });
        return;
      }
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError("La taille du fichier ne doit pas dépasser 50MB");
        setErrors({ ...errors, file: "La taille du fichier ne doit pas dépasser 50MB" });
        return;
      }
      setFile(selectedFile);
      setError("");
      setErrors({ ...errors, file: undefined });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    if (!file) {
      setError("Veuillez sélectionner un fichier PDF");
      return;
    }
    
    setUploading(true);
    setUploadProgress(0);
    setError("");
    
    try {
      const { data: { user }, error: userError } = await supabase.auth.getUser();
      
      if (userError || !user) {
        router.push("/login");
        return;
      }
      
      const { data: { session } } = await supabase.auth.getSession();
      const authToken = session?.access_token;
      
      const formData = new FormData();
      formData.append("file", file);
      formData.append("metadata", JSON.stringify({
        ...metadata,
        mots_cles: metadata.mots_cles.split(",").map(k => k.trim()).filter(Boolean)
      }));
      
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
          const percent = Math.round((e.loaded / e.total) * 100);
          setUploadProgress(percent);
        }
      });
      
      xhr.open("POST", "/api/v1/pfe/upload");
      if (authToken) {
        xhr.setRequestHeader("Authorization", `Bearer ${authToken}`);
      }
      
      await new Promise<void>((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve();
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText);
              reject(new Error(errorData.detail || "Échec de l'upload"));
            } catch {
              reject(new Error("Échec de l'upload"));
            }
          }
        };
        xhr.onerror = () => reject(new Error("Erreur réseau"));
        xhr.send(formData);
      });
      
      setUploadProgress(100);
      setSuccess(true);
      setTimeout(() => router.push("/pfe"), 2000);
    } catch (err: any) {
      setError(err.message || "Une erreur est survenue");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Upload un PFE</h1>
        <p className="text-slate-600">Ajoutez un nouveau mémoire PFE à la plateforme</p>
      </div>

      {success && (
        <div className="flex items-center gap-3 p-4 bg-green-50 text-green-700 rounded-lg">
          <Check className="w-5 h-5" />
          <span>PFE uploadé avec succès!</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-lg">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Fichier PDF *</label>
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
              errors.file 
                ? "border-red-300 bg-red-50 hover:border-red-400" 
                : "border-slate-300 hover:border-blue-400 hover:bg-blue-50"
            }`}
          >
            {file ? (
              <div className="flex items-center justify-center gap-3">
                <FileText className="w-8 h-8 text-blue-600" />
                <div className="text-left">
                  <p className="font-medium text-slate-900">{file.name}</p>
                  <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button 
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="ml-4 p-2 text-slate-400 hover:text-red-500"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div>
                <Upload className="w-10 h-10 text-slate-400 mx-auto mb-3" />
                <p className="text-slate-600">Cliquez pour sélectionner un PDF</p>
                <p className="text-sm text-slate-500 mt-1">Maximum 50MB</p>
              </div>
            )}
          </div>
          {errors.file && (
            <p className="text-red-500 text-sm mt-1">{errors.file}</p>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-2">Titre du PFE *</label>
            <input
              type="text"
              value={metadata.titre}
              onChange={(e) => { setMetadata({ ...metadata, titre: e.target.value }); setErrors({...errors, titre: undefined}); }}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.titre ? "border-red-300 bg-red-50" : "border-slate-300"
              }`}
              placeholder="Titre de votre mémoire"
              required
            />
            {errors.titre && (
              <p className="text-red-500 text-sm mt-1">{errors.titre}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Auteur *</label>
            <input
              type="text"
              value={metadata.auteur}
              onChange={(e) => { setMetadata({ ...metadata, auteur: e.target.value }); setErrors({...errors, auteur: undefined}); }}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.auteur ? "border-red-300 bg-red-50" : "border-slate-300"
              }`}
              placeholder="Nom et prénom"
              required
            />
            {errors.auteur && (
              <p className="text-red-500 text-sm mt-1">{errors.auteur}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Année *</label>
            <input
              type="number"
              value={metadata.annee}
              onChange={(e) => setMetadata({ ...metadata, annee: parseInt(e.target.value) })}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min={2014}
              max={2026}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Type de Veille *</label>
            <select
              value={metadata.type_veille}
              onChange={(e) => setMetadata({ ...metadata, type_veille: e.target.value })}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              {typeVeille.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Domaine VIC *</label>
            <select
              value={metadata.domaine_vic}
              onChange={(e) => setMetadata({ ...metadata, domaine_vic: e.target.value })}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              {domaines.map((dom) => (
                <option key={dom.value} value={dom.value}>{dom.label}</option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-2">Mots-clés</label>
            <input
              type="text"
              value={metadata.mots_cles}
              onChange={(e) => setMetadata({ ...metadata, mots_cles: e.target.value })}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="veille stratégique, intelligence économique (séparés par virgules)"
            />
          </div>
        </div>

        {uploading && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-slate-600">
              <span>Upload en cours...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={uploading || !file}
          className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Upload en cours... ({uploadProgress}%)
            </>
          ) : (
            <>
              <Upload className="w-5 h-5" />
              Uploader le PFE
            </>
          )}
        </button>
      </form>
    </div>
  );
}