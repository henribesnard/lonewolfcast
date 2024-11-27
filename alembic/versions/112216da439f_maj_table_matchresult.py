"""maj table matchResult

Revision ID: 112216da439f
Revises: 30693b096ee0
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision: str = '112216da439f'
down_revision: Union[str, None] = '30693b096ee0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Créer une nouvelle table temporaire avec la structure souhaitée
    op.create_table('match_results_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('home_score', sa.Integer(), nullable=False),
        sa.Column('away_score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Copier les données existantes
    op.execute('''
        INSERT INTO match_results_new (id, match_id, home_score, away_score, created_at, updated_at)
        SELECT id, match_id, home_score, away_score, created_at, updated_at
        FROM match_results
    ''')

    # Supprimer l'ancienne table
    op.drop_table('match_results')

    # Renommer la nouvelle table
    op.rename_table('match_results_new', 'match_results')

def downgrade() -> None:
    # Recréer l'ancienne structure si nécessaire
    # Cette partie dépendra de votre besoin de pouvoir revenir en arrière
    pass