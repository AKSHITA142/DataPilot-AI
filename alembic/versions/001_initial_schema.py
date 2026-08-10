"""Initial schema setup for DataPilot-AI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Datasets table
    op.create_table(
        'datasets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('owner_id', sa.String(length=36), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('column_count', sa.Integer(), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('semantic_profile', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_datasets_owner_id', 'datasets', ['owner_id'], unique=False)

    # Jobs table
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('dataset_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('objective', sa.String(length=1024), nullable=True),
        sa.Column('mission_brief', sa.TEXT(), nullable=True),
        sa.Column('progress_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('error_message', sa.String(length=2048), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_jobs_dataset_id', 'jobs', ['dataset_id'], unique=False)
    op.create_index('ix_jobs_status', 'jobs', ['status'], unique=False)

    # Experiments table
    op.create_table(
        'experiments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('experiment_id_code', sa.String(length=50), nullable=False),
        sa.Column('pipeline', sa.TEXT(), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('hyperparameters', sa.TEXT(), nullable=True),
        sa.Column('metrics', sa.TEXT(), nullable=True),
        sa.Column('runtime_seconds', sa.Float(), nullable=True),
        sa.Column('memory_mb', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('artifact_paths', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_experiments_job_id', 'experiments', ['job_id'], unique=False)

    # Knowledge entries table
    op.create_table(
        'knowledge_entries',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('finding', sa.String(length=2048), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('source_experiment_ids', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_knowledge_entries_job_id', 'knowledge_entries', ['job_id'], unique=False)

    # Reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('winning_experiment_id', sa.String(length=36), nullable=True),
        sa.Column('report_file_path', sa.String(length=1024), nullable=True),
        sa.Column('summary', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_index('ix_knowledge_entries_job_id', table_name='knowledge_entries')
    op.drop_table('knowledge_entries')
    op.drop_index('ix_experiments_job_id', table_name='experiments')
    op.drop_table('experiments')
    op.drop_index('ix_jobs_status', table_name='jobs')
    op.drop_index('ix_jobs_dataset_id', table_name='jobs')
    op.drop_table('jobs')
    op.drop_index('ix_datasets_owner_id', table_name='datasets')
    op.drop_table('datasets')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
