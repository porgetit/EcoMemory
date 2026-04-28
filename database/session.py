"""
EcoMemory - Engine y sesión SQLAlchemy
Proporciona get_engine(), init_db() y SessionLocal.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base


def get_engine(base_dir: str):
    """Crea y retorna un engine SQLite apuntando a data/ecomemory.db."""
    db_path = os.path.join(base_dir, 'data', 'ecomemory.db')
    url = f'sqlite:///{db_path}'
    return create_engine(url, connect_args={'check_same_thread': False})


def init_db(engine):
    """Crea todas las tablas definidas en Base.metadata si no existen."""
    Base.metadata.create_all(engine)


def get_session_factory(engine):
    """Retorna una fábrica de sesión vinculada al engine."""
    return sessionmaker(bind=engine)

"""
Object-Relational Mapping (ORM) is a programming technique that connects object-oriented programming (OOP) to relational databases,
allowing developers to manipulate database data using code objects instead of writing raw SQL queries. It acts as an abstraction layer,
increasing developer productivity and improving code maintainability. 
"""