"""add document content hash

Revision ID: 709a6c637446
Revises: 4e529e57d42d
Create Date: 2026-10-16 14:51:00.292030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '709a6c637446'
down_revision: Union[str, Sequence[str], None] = '4e529e57d42d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('documents', sa.Column('content_hash', sa.String(length=64), nullable=True), schema='finguard')
    op.create_unique_constraint("uq_documents_content_hash", 'documents', ['content_hash'], schema='finguard')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint("uq_documents_content_hash", 'documents', schema='finguard', type_='unique')
    op.drop_column('documents', 'content_hash', schema='finguard')
    # ### end Alembic commands ###
