import os
from logging.config import fileConfig
import streamlit as st
from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine
from alembic import context
from src.models import Base
# from models import Base  # Import your models here

from dotenv import load_dotenv

load_dotenv()

username = os.environ.get("DB_USER")
password = os.environ.get("DB_PASS")
host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")
database = os.environ.get("DB_NAME")

connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Retrieve database credentials from Streamlit secrets
db_credentials = st.secrets["mysql"]
DATABASE_URL = f'mysql+pymysql://{db_credentials["username"]}:{db_credentials["password"]}@{db_credentials["host"]}:{db_credentials["port"]}/{db_credentials["database"]}'

if db_credentials:
    # Set the SQLAlchemy URL
    config.set_main_option('sqlalchemy.url', DATABASE_URL)
else:
    config.set_main_option('sqlalchemy.url', connection_string)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migration()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migration()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
