"""Initial migration - create tables.

Revision ID: 001
Revises: 
Create Date: 2026-03-09
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables."""
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    
    # Create standard_clauses table
    op.create_table(
        'standard_clauses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_standard_clauses_category'), 'standard_clauses', ['category'], unique=False)
    op.create_index(op.f('ix_standard_clauses_id'), 'standard_clauses', ['id'], unique=False)
    
    # Create extracted_clauses table
    op.create_table(
        'extracted_clauses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('clause_number', sa.String(length=50), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('start_position', sa.Integer(), nullable=True),
        sa.Column('end_position', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extracted_clauses_id'), 'extracted_clauses', ['id'], unique=False)
    
    # Create clause_analyses table
    op.create_table(
        'clause_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('standard_clause_id', sa.Integer(), nullable=False),
        sa.Column('extracted_clause_id', sa.Integer(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('OK', 'MISSING', 'REVIEW', name='clausestatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['extracted_clause_id'], ['extracted_clauses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['standard_clause_id'], ['standard_clauses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clause_analyses_id'), 'clause_analyses', ['id'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_clause_analyses_id'), table_name='clause_analyses')
    op.drop_table('clause_analyses')
    op.drop_index(op.f('ix_extracted_clauses_id'), table_name='extracted_clauses')
    op.drop_table('extracted_clauses')
    op.drop_index(op.f('ix_standard_clauses_id'), table_name='standard_clauses')
    op.drop_index(op.f('ix_standard_clauses_category'), table_name='standard_clauses')
    op.drop_table('standard_clauses')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    op.execute('DROP EXTENSION IF EXISTS vector')
