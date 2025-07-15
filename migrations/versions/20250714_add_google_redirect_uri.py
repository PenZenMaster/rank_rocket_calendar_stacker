"""
Revision ID: add_google_redirect_uri
Revises: 41c15dd39005
Create Date: 2025-07-14

Add google_redirect_uri field to OAuthCredential model
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = "add_google_redirect_uri"
down_revision = "41c15dd39005"  # Replace with actual previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "oauth_credentials",
        sa.Column("google_redirect_uri", sa.String(length=512), nullable=True),
    )


def downgrade():
    op.drop_column("oauth_credentials", "google_redirect_uri")
