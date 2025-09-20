"""initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240920_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wine",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("producer", sa.String(length=255), nullable=True),
        sa.Column("label_text_norm", sa.Text(), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("region", sa.String(length=128), nullable=True),
        sa.Column("subregion", sa.String(length=128), nullable=True),
        sa.Column("appellation", sa.String(length=128), nullable=True),
        sa.Column("grapes", sa.JSON(), nullable=True),
        sa.Column("vintage", sa.Integer(), nullable=True),
        sa.Column("style", sa.Enum("RED", "WHITE", "ROSE", "SPARKLING", "DESSERT", "FORTIFIED", "UNKNOWN", name="winestyle"), nullable=False, server_default="UNKNOWN"),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=True),
    )

    op.create_table(
        "wine_embedding",
        sa.Column("wine_id", sa.Integer(), sa.ForeignKey("wine.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("image_vec", sa.LargeBinary(), nullable=True),
        sa.Column("text_vec", sa.LargeBinary(), nullable=True),
        sa.Column("model_version", sa.String(length=64), nullable=False, server_default="unknown"),
    )

    op.create_table(
        "upload",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_session_id", sa.String(length=128), nullable=True),
        sa.Column("stored_path", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("store_image", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("consent_flags", sa.JSON(), nullable=True),
    )

    op.create_table(
        "inference_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("upload_id", sa.String(length=36), sa.ForeignKey("upload.id"), nullable=True),
        sa.Column("wine_id", sa.Integer(), sa.ForeignKey("wine.id"), nullable=True),
        sa.Column("topk", sa.JSON(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column("explain", sa.JSON(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("model_versions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("upload_id", sa.String(length=36), sa.ForeignKey("upload.id"), nullable=True),
        sa.Column("chosen_wine_id", sa.Integer(), sa.ForeignKey("wine.id"), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("inference_log")
    op.drop_table("upload")
    op.drop_table("wine_embedding")
    op.drop_table("wine")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS winestyle")
