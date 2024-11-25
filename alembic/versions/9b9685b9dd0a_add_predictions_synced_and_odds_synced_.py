"""Add predictions_synced and odds_synced to Match

Revision ID: 9b9685b9dd0a
Revises: 22282d607a79
Create Date: 2024-11-24 21:23:45.728562

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b9685b9dd0a'
down_revision: Union[str, None] = '22282d607a79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('predictions_synced', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('last_predictions_sync', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('odds_synced', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('last_odds_sync', sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table('seasons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('matches_synced', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('last_match_sync', sa.DateTime(timezone=True), nullable=True))

    # Supprimer les valeurs par défaut une fois les colonnes mises à jour (facultatif)
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.alter_column('predictions_synced', server_default=None)
        batch_op.alter_column('odds_synced', server_default=None)

    with op.batch_alter_table('seasons', schema=None) as batch_op:
        batch_op.alter_column('matches_synced', server_default=None)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('seasons', schema=None) as batch_op:
        batch_op.drop_column('last_match_sync')
        batch_op.drop_column('matches_synced')

    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.drop_column('last_odds_sync')
        batch_op.drop_column('odds_synced')
        batch_op.drop_column('last_predictions_sync')
        batch_op.drop_column('predictions_synced')

    # ### end Alembic commands ###