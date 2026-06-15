"""pitchly schema and supabase storage

Revision ID: 9c2d7b01f0d1
Revises: f7b84db08d70
Create Date: 2026-06-14 23:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "9c2d7b01f0d1"
down_revision: Union[str, None] = "f7b84db08d70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        CREATE TABLE IF NOT EXISTS public.users (
          id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
          full_name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          avatar_url TEXT,
          extraversion_score INT DEFAULT 0,
          total_sessions INT DEFAULT 0,
          interview_sessions INT DEFAULT 0,
          social_sessions INT DEFAULT 0,
          avg_global_score NUMERIC(5,2) DEFAULT 0,
          streak_days INT DEFAULT 0,
          last_session_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS public.sessions (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
          mode TEXT NOT NULL CHECK (mode IN ('interview', 'social')),
          job_title TEXT,
          scenario TEXT,
          status TEXT DEFAULT 'processing'
            CHECK (status IN ('processing', 'complete', 'error')),
          video_url TEXT,
          duration_s INT,
          created_at TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS public.results (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          session_id UUID UNIQUE REFERENCES public.sessions(id) ON DELETE CASCADE,
          transcript TEXT,
          score_clarity INT CHECK (score_clarity BETWEEN 0 AND 100),
          score_confidence INT CHECK (score_confidence BETWEEN 0 AND 100),
          score_structure INT CHECK (score_structure BETWEEN 0 AND 100),
          score_relevance INT CHECK (score_relevance BETWEEN 0 AND 100),
          score_listening INT CHECK (score_listening BETWEEN 0 AND 100),
          score_global INT CHECK (score_global BETWEEN 0 AND 100),
          feedback_text TEXT,
          posture_notes TEXT,
          emotion_summary JSONB,
          created_at TIMESTAMPTZ DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_user
          ON public.sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_status
          ON public.sessions(status);
        CREATE INDEX IF NOT EXISTS idx_sessions_created
          ON public.sessions(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_results_session
          ON public.results(session_id);

        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.results ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS users_own_profile ON public.users;
        CREATE POLICY users_own_profile
          ON public.users FOR ALL
          USING (auth.uid() = id)
          WITH CHECK (auth.uid() = id);

        DROP POLICY IF EXISTS users_own_sessions ON public.sessions;
        CREATE POLICY users_own_sessions
          ON public.sessions FOR ALL
          USING (auth.uid() = user_id)
          WITH CHECK (auth.uid() = user_id);

        DROP POLICY IF EXISTS users_own_results ON public.results;
        CREATE POLICY users_own_results
          ON public.results FOR ALL
          USING (
            session_id IN (
              SELECT id FROM public.sessions WHERE user_id = auth.uid()
            )
          )
          WITH CHECK (
            session_id IN (
              SELECT id FROM public.sessions WHERE user_id = auth.uid()
            )
          );

        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS TRIGGER AS $$
        BEGIN
          INSERT INTO public.users (id, full_name, email)
          VALUES (
            NEW.id,
            COALESCE(NEW.raw_user_meta_data->>'full_name', 'User'),
            NEW.email
          )
          ON CONFLICT (id) DO NOTHING;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;

        DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
        CREATE TRIGGER on_auth_user_created
          AFTER INSERT ON auth.users
          FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

        INSERT INTO storage.buckets (
          id,
          name,
          public,
          file_size_limit,
          allowed_mime_types
        )
        VALUES (
          'pitchly-videos',
          'pitchly-videos',
          false,
          104857600,
          ARRAY['video/webm', 'video/mp4', 'video/quicktime']
        )
        ON CONFLICT (id) DO UPDATE
        SET
          public = EXCLUDED.public,
          file_size_limit = EXCLUDED.file_size_limit,
          allowed_mime_types = EXCLUDED.allowed_mime_types;

        DROP POLICY IF EXISTS users_upload_own_videos ON storage.objects;
        CREATE POLICY users_upload_own_videos
          ON storage.objects FOR INSERT TO authenticated
          WITH CHECK (
            bucket_id = 'pitchly-videos'
            AND (storage.foldername(name))[1] = auth.uid()::text
          );

        DROP POLICY IF EXISTS users_read_own_videos ON storage.objects;
        CREATE POLICY users_read_own_videos
          ON storage.objects FOR SELECT TO authenticated
          USING (
            bucket_id = 'pitchly-videos'
            AND (storage.foldername(name))[1] = auth.uid()::text
          );

        DROP POLICY IF EXISTS users_delete_own_videos ON storage.objects;
        CREATE POLICY users_delete_own_videos
          ON storage.objects FOR DELETE TO authenticated
          USING (
            bucket_id = 'pitchly-videos'
            AND (storage.foldername(name))[1] = auth.uid()::text
          );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP POLICY IF EXISTS users_delete_own_videos ON storage.objects;
        DROP POLICY IF EXISTS users_read_own_videos ON storage.objects;
        DROP POLICY IF EXISTS users_upload_own_videos ON storage.objects;
        DELETE FROM storage.buckets WHERE id = 'pitchly-videos';

        DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
        DROP FUNCTION IF EXISTS public.handle_new_user();

        DROP POLICY IF EXISTS users_own_results ON public.results;
        DROP POLICY IF EXISTS users_own_sessions ON public.sessions;
        DROP POLICY IF EXISTS users_own_profile ON public.users;

        DROP TABLE IF EXISTS public.results;
        DROP TABLE IF EXISTS public.sessions;
        DROP TABLE IF EXISTS public.users;
        """
    )
