"""increase clause_number length

Revision ID: 20260309_002
Revises: 20260309_001
Create Date: 2026-03-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Increase clause_number column from VARCHAR(50) to VARCHAR(255)."""
    op.alter_column('extracted_clauses', 'clause_number',
                    existing_type=sa.String(50),
                    type_=sa.String(255),
                    existing_nullable=True)


def downgrade():
    """Revert clause_number column back to VARCHAR(50)."""
    op.alter_column('extracted_clauses', 'clause_number',
                    existing_type=sa.String(255),
                    type_=sa.String(50),
                    existing_nullable=True)
