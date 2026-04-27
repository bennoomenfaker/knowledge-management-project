-- Migration to add missing columns to pfe_documents table
-- Run this in Supabase SQL Editor

-- Add type_veille column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='pfe_documents' AND column_name='type_veille') THEN
        ALTER TABLE pfe_documents ADD COLUMN type_veille TEXT;
        ALTER TABLE pfe_documents ADD CONSTRAINT type_veille_check 
            CHECK (type_veille IN ('strategique', 'concurrentielle', 'reglementaire', 'technologique', 'juridique', 'commerciale', 'marketing', 'organisationnelle'));
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='pfe_documents' AND column_name='problematic') THEN
        ALTER TABLE pfe_documents ADD COLUMN problematic TEXT;
    END IF;
END $$;

-- Update the CHECK constraint if needed (for existing constraint)
ALTER TABLE pfe_documents DROP CONSTRAINT IF EXISTS type_veille_check;
ALTER TABLE pfe_documents ADD CONSTRAINT type_veille_check 
    CHECK (type_veille IN ('strategique', 'concurrentielle', 'reglementaire', 'technologique', 'juridique', 'commerciale', 'marketing', 'organisationnelle'));

-- Verify the changes
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'pfe_documents'
ORDER BY ordinal_position;
