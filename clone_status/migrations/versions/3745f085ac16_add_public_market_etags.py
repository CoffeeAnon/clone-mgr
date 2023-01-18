"""empty message

Revision ID: 3745f085ac16
Revises: ddfdeb757929
Create Date: 2022-09-28 21:44:47.368069

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3745f085ac16"
down_revision = "ddfdeb757929"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "public_market_esi_etags",
        sa.Column("region_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("market_data", sa.Text(), nullable=True),
        sa.Column("market_etag_json", sa.Text(), nullable=True),
    )
    op.create_table(
        "private_market_esi_etags",
        sa.Column("character_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("structure_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("market_data", sa.Text(), nullable=True),
        sa.Column("market_etag_json", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table("public_market_esi_etags")
    op.drop_table("private_market_esi_etags")
