"""Add etag table

Revision ID: ddfdeb757929
Revises: fab636b98bc7
Create Date: 2022-05-22 17:46:29.947969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ddfdeb757929"
down_revision = "fab636b98bc7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "character_esi_etags",
        sa.Column("character_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("asset_etag", sa.String(length=255), nullable=True),
        sa.Column("asset_data", sa.Text(), nullable=True),
        sa.Column("asset_header", sa.Text(), nullable=True),
        sa.Column("asset_etag_json", sa.Text(), nullable=True),
        sa.Column("location_etag", sa.String(length=255), nullable=True),
        sa.Column("location_data", sa.Text(), nullable=True),
        sa.Column("location_header", sa.Text(), nullable=True),
        sa.Column("location_etag_json", sa.Text(), nullable=True),
        sa.Column("transaction_etag_json", sa.Text(), nullable=True),
        sa.Column("transaction_data", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table("character_esi_etags")
