"""add coaching fields to results table

Revision ID: b1a2c3d4e5f6
Revises: 9c2d7b01f0d1
Create Date: 2026-06-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b1a2c3d4e5f6"
down_revision: Union[str, None] = "9c2d7b01f0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE public.results
          ADD COLUMN IF NOT EXISTS strengths JSONB DEFAULT '[]'::jsonb,
          ADD COLUMN IF NOT EXISTS weaknesses JSONB DEFAULT '[]'::jsonb,
          ADD COLUMN IF NOT EXISTS recommendations JSONB DEFAULT '[]'::jsonb,
          ADD COLUMN IF NOT EXISTS practice_exercises JSONB DEFAULT '[]'::jsonb,
          ADD COLUMN IF NOT EXISTS filler_words_detected TEXT DEFAULT '',
          ADD COLUMN IF NOT EXISTS speech_pace TEXT DEFAULT '',
          ADD COLUMN IF NOT EXISTS opening_quality TEXT DEFAULT '',
          ADD COLUMN IF NOT EXISTS closing_quality TEXT DEFAULT '',
          ADD COLUMN IF NOT EXISTS vocabulary_assessment TEXT DEFAULT '',
          ADD COLUMN IF NOT EXISTS body_language JSONB DEFAULT '{}'::jsonb,
          ADD COLUMN IF NOT EXISTS facial_expression JSONB DEFAULT '{}'::jsonb,
          ADD COLUMN IF NOT EXISTS audio_quality JSONB DEFAULT '{}'::jsonb,
          ADD COLUMN IF NOT EXISTS transcript_metadata JSONB DEFAULT '{}'::jsonb;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE public.results
          DROP COLUMN IF EXISTS strengths,
          DROP COLUMN IF EXISTS weaknesses,
          DROP COLUMN IF EXISTS recommendations,
          DROP COLUMN IF EXISTS practice_exercises,
          DROP COLUMN IF EXISTS filler_words_detected,
          DROP COLUMN IF EXISTS speech_pace,
          DROP COLUMN IF EXISTS opening_quality,
          DROP COLUMN IF EXISTS closing_quality,
          DROP COLUMN IF EXISTS vocabulary_assessment,
          DROP COLUMN IF EXISTS body_language,
          DROP COLUMN IF EXISTS facial_expression,
          DROP COLUMN IF EXISTS audio_quality,
          DROP COLUMN IF EXISTS transcript_metadata;
        """
    )
