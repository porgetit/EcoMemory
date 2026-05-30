"""
EcoMemory - Modelos SQLAlchemy
Define las tablas: usuarios, fotografias, registros_eliminacion.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=False)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)
    fecha_registro = Column(DateTime, nullable=False)

    # Relaciones
    fotografias = relationship(
        'Fotografia', back_populates='usuario', cascade='all, delete-orphan'
    )
    registros_eliminacion = relationship(
        'RegistroEliminacion', back_populates='usuario'
    )

    def __repr__(self):
        return f'<Usuario(id={self.id}, nombre={self.nombre!r})>'


class Fotografia(Base):
    __tablename__ = 'fotografias'

    id = Column(Integer, primary_key=True, autoincrement=False)
    usuario_id = Column(
        Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False
    )
    nombre = Column(String, nullable=False)
    formato_archivo = Column(String(10), nullable=False)
    tamano_bytes = Column(Integer, nullable=False)
    ruta_original = Column(String, nullable=False)
    nivel_deterioro = Column(Float, nullable=False)
    estado_erosion = Column(String(20), nullable=False)
    fecha_subida = Column(DateTime, nullable=False)
    fecha_ultimo_acceso = Column(DateTime, nullable=False)
    en_papelera = Column(Boolean, nullable=False, default=False)

    # Relaciones
    usuario = relationship('Usuario', back_populates='fotografias')
    registros_eliminacion = relationship(
        'RegistroEliminacion', back_populates='fotografia',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Fotografia(id={self.id}, nombre={self.nombre!r})>'


class RegistroEliminacion(Base):
    __tablename__ = 'registros_eliminacion'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fotografia_id = Column(
        Integer, ForeignKey('fotografias.id', ondelete='CASCADE'), nullable=False
    )
    usuario_id = Column(
        Integer, ForeignKey('usuarios.id'), nullable=False
    )
    fecha_ingreso_papelera = Column(DateTime, nullable=False)
    fecha_eliminacion_definitiva = Column(DateTime, nullable=True)
    auto = Column(Boolean, nullable=False, default=False)

    # Relaciones
    fotografia = relationship('Fotografia', back_populates='registros_eliminacion')
    usuario = relationship('Usuario', back_populates='registros_eliminacion')

    def __repr__(self):
        return f'<RegistroEliminacion(id={self.id}, fotografia_id={self.fotografia_id})>'
