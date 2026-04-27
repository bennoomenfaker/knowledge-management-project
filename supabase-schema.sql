-- Knowledge Hub for PFE Database Schema
-- Run this in Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create domain enum
CREATE TYPE domaine_vic AS ENUM (
    'intelligence_competitive',
    'veille_strategique',
    'management_information',
    'analyse_strategique',
    'intelligence_economique',
    'gestion_connaissance',
    'data_intelligence',
    'securite_informationnelle'
);

-- Create user role enum
CREATE TYPE user_role AS ENUM ('etudiant', 'administrateur', 'visiteur');

-- Create PFE status enum
CREATE TYPE pfe_status AS ENUM ('en_attente', 'en_traitement', 'complete', 'erreur');

-- Create pfe_documents table
CREATE TABLE IF NOT EXISTS pfe_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    email_auteur TEXT,
    annee INTEGER NOT NULL CHECK (annee BETWEEN 2014 AND 2026),
    institution TEXT NOT NULL CHECK (institution IN ('ISCAE', 'ESEN')),
    domaine_vic domaine_vic NOT NULL,
    type_veille TEXT CHECK (type_veille IN ('strategique', 'concurrentielle', 'reglementaire', 'technologique', 'juridique', 'commerciale', 'marketing', 'organisationnelle')),
    mots_cles TEXT[],
    resume TEXT,
    problematic TEXT,
    methodology TEXT,
    file_path TEXT,
    file_size BIGINT,
    status pfe_status DEFAULT 'en_attente',
    embedding_id UUID,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create pfe_embeddings table
CREATE TABLE IF NOT EXISTS pfe_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pfe_id UUID REFERENCES pfe_documents(id) ON DELETE CASCADE,
    embedding VECTOR(1536),
    model_used TEXT DEFAULT 'mxbai-embed-large',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    role user_role DEFAULT 'visiteur',
    institution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create analytics_events table
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    event_data JSONB,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS pfe_annee_idx ON pfe_documents(annee);
CREATE INDEX IF NOT EXISTS pfe_domaine_idx ON pfe_documents(domaine_vic);
CREATE INDEX IF NOT EXISTS pfe_institution_idx ON pfe_documents(institution);
CREATE INDEX IF NOT EXISTS pfe_created_by_idx ON pfe_documents(created_by);
CREATE INDEX IF NOT EXISTS pfe_status_idx ON pfe_documents(status);
CREATE INDEX IF NOT EXISTS pfe_embeddings_pfe_idx ON pfe_embeddings(pfe_id);

-- Create RLS policies
ALTER TABLE pfe_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE pfe_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- PFE Documents policies
CREATE POLICY "Enable read access for all users" ON pfe_documents FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON pfe_documents FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable update for owners and admins" ON pfe_documents FOR UPDATE USING (
    auth.uid() = created_by OR
    EXISTS (SELECT 1 FROM user_profiles WHERE id = auth.uid() AND role = 'administrateur')
);
CREATE POLICY "Enable delete for owners and admins" ON pfe_documents FOR DELETE USING (
    auth.uid() = created_by OR
    EXISTS (SELECT 1 FROM user_profiles WHERE id = auth.uid() AND role = 'administrateur')
);

-- User profiles policies
CREATE POLICY "Enable read access for all users" ON user_profiles FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Enable update for users themselves" ON user_profiles FOR UPDATE USING (auth.uid() = id);

-- Embeddings policies (read-only for authenticated)
CREATE POLICY "Enable read access for authenticated users" ON pfe_embeddings FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Enable insert for authenticated users" ON pfe_embeddings FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Analytics events policies
CREATE POLICY "Enable all access for authenticated users" ON analytics_events FOR ALL USING (auth.role() = 'authenticated');

-- Storage bucket for PFE documents
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('pfe-documents', 'pfe-documents', true, 52428800, ARRAY['application/pdf'])
ON CONFLICT (id) DO NOTHING;

-- Storage policies
CREATE POLICY "Enable public read access for PFE files" ON storage.objects FOR SELECT USING (bucket_id = 'pfe-documents');
CREATE POLICY "Enable authenticated insert for PFE files" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'pfe-documents' AND auth.role() = 'authenticated');
CREATE POLICY "Enable owner update for PFE files" ON storage.objects FOR UPDATE USING (bucket_id = 'pfe-documents' AND auth.uid() = (storage.foldername(name))[1]::uuid);
CREATE POLICY "Enable owner delete for PFE files" ON storage.objects FOR DELETE USING (bucket_id = 'pfe-documents' AND auth.uid() = (storage.foldername(name))[1]::uuid);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
CREATE TRIGGER update_pfe_updated_at
    BEFORE UPDATE ON pfe_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Comments
COMMENT ON TABLE pfe_documents IS 'Table containing all PFE documents';
COMMENT ON TABLE pfe_embeddings IS 'Table containing vector embeddings for PFE documents';
COMMENT ON TABLE user_profiles IS 'Table containing user profiles and roles';
COMMENT ON TABLE analytics_events IS 'Table for tracking analytics events';