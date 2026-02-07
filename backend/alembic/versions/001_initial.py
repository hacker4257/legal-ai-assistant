"""初始化数据库表

Revision ID: 001
Revises:
Create Date: 2024-02-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('user_type', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 创建案例表
    op.create_table(
        'cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_number', sa.String(length=100), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('court', sa.String(length=200), nullable=True),
        sa.Column('case_type', sa.String(length=50), nullable=True),
        sa.Column('judgment_date', sa.Date(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parties', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('legal_basis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cases_case_number'), 'cases', ['case_number'], unique=True)
    op.create_index(op.f('ix_cases_case_type'), 'cases', ['case_type'], unique=False)
    op.create_index(op.f('ix_cases_id'), 'cases', ['id'], unique=False)

    # 创建搜索历史表
    op.create_table(
        'search_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('results_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_history_id'), 'search_history', ['id'], unique=False)
    op.create_index(op.f('ix_search_history_user_id'), 'search_history', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_search_history_user_id'), table_name='search_history')
    op.drop_index(op.f('ix_search_history_id'), table_name='search_history')
    op.drop_table('search_history')
    op.drop_index(op.f('ix_cases_id'), table_name='cases')
    op.drop_index(op.f('ix_cases_case_type'), table_name='cases')
    op.drop_index(op.f('ix_cases_case_number'), table_name='cases')
    op.drop_table('cases')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
