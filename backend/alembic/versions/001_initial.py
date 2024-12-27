"""Migration initiale."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('username', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'USER', 'ANALYST', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('preferences', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('profile', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
    )

    # Analyses
    op.create_table(
        'analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('repository_url', sa.String(), nullable=True),
        sa.Column('code_snippet', sa.Text(), nullable=True),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='analysisstatus'), nullable=False),
        sa.Column('metrics', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('issues', postgresql.ARRAY(postgresql.JSONB()), nullable=False, default=[]),
        sa.Column('suggestions', postgresql.ARRAY(postgresql.JSONB()), nullable=False, default=[]),
        sa.Column('lines_of_code', sa.Integer(), nullable=False, default=0),
        sa.Column('complexity_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('security_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('performance_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
    )

def downgrade():
    op.drop_table('analyses')
    op.drop_table('users')
    op.execute('DROP TYPE userrole')
    op.execute('DROP TYPE analysisstatus') 