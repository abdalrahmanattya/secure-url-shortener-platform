import sqlalchemy as sa
from alembic import op

revision = "001_create_links"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("destination", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("disabled_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.Column("click_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("code", name="uq_links_code"),
    )


def downgrade() -> None:
    op.drop_table("links")
