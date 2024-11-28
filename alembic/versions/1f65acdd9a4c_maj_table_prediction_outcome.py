"""maj table prediction_outcome

Revision ID: 1f65acdd9a4c
Revises: 112216da439f
Create Date: 2024-11-28 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '1f65acdd9a4c'
down_revision: Union[str, None] = '112216da439f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Ajouter la colonne avec une valeur par défaut
    op.add_column('prediction_outcomes', sa.Column('both_teams_scored', sa.Boolean(), 
                  server_default=sa.text('0'), nullable=False))
    
    # 2. Mettre à jour les valeurs existantes basées sur les résultats des matchs
    conn = op.get_bind()
    conn.execute(text("""
        UPDATE prediction_outcomes 
        SET both_teams_scored = (
            SELECT 
                CASE 
                    WHEN mr.home_score > 0 AND mr.away_score > 0 THEN 1 
                    ELSE 0 
                END
            FROM match_results mr
            JOIN matches m ON m.id = mr.match_id
            JOIN predictions p ON p.match_id = m.id
            WHERE p.id = prediction_outcomes.prediction_id
        )
    """))

def downgrade() -> None:
    op.drop_column('prediction_outcomes', 'both_teams_scored')