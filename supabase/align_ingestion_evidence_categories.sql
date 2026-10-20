-- Applied through Supabase migration align_ingestion_evidence_categories.
-- Preserve existing categories and permit the endpoint's metadata receipts.
ALTER TABLE public.research_engine_runs DROP CONSTRAINT research_engine_runs_evidence_level_check, ADD CONSTRAINT research_engine_runs_evidence_level_check CHECK (evidence_level IN ('synthetic','candidate','metadata_only','real_iq_descriptive','labeled_measured','verified_benchmark'));
