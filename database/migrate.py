"""
EcoMemory - Script de migración one-shot
Migra data/db.json → data/ecomemory.db (SQLite).

Ejecutar: python -m database.migrate
"""
import json
import os
import sys
from datetime import datetime

# Agregar directorio raíz al path para imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.models import Usuario, Fotografia, RegistroEliminacion
from database.session import get_engine, init_db, get_session_factory


def parse_iso_date(iso_str: str) -> datetime | None:
    """Convierte una fecha ISO 8601 del JSON a un objeto datetime."""
    if not iso_str:
        return None
    # Manejar formatos con y sin 'Z'
    iso_str = iso_str.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(iso_str)
    except ValueError:
        # Fallback: parsear formato fijo
        return datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%f%z')


def migrate(base_dir: str | None = None):
    """Ejecuta la migración de db.json a SQLite."""
    if base_dir is None:
        base_dir = BASE_DIR

    json_path = os.path.join(base_dir, 'data', 'db.json')
    backup_path = os.path.join(base_dir, 'data', 'db.json.bak')

    # Verificar que el JSON existe
    if not os.path.exists(json_path):
        print(f'[migrate] No se encontró {json_path}. Nada que migrar.')
        return

    # Leer datos JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Inicializar DB
    engine = get_engine(base_dir)
    init_db(engine)
    SessionLocal = get_session_factory(engine)

    session = SessionLocal()
    try:
        # Idempotencia: verificar si ya hay datos
        existing_users = session.query(Usuario).count()
        if existing_users > 0:
            print(f'[migrate] La base de datos ya contiene {existing_users} usuario(s). '
                  'Omitiendo migración para evitar duplicados.')
            return

        # ── Insertar usuarios ────────────────────────────────────────────
        usuarios_data = data.get('usuarios', [])
        for u in usuarios_data:
            usuario = Usuario(
                id=u['id'],
                nombre=u['nombre'],
                correo=u['correo'],
                contrasena=u['contrasena'],
                fecha_registro=parse_iso_date(u['fechaRegistro']),
            )
            session.add(usuario)
        print(f'[migrate] {len(usuarios_data)} usuario(s) insertado(s).')

        # ── Insertar fotografías ─────────────────────────────────────────
        fotos_data = data.get('fotografias', [])
        for foto in fotos_data:
            fotografia = Fotografia(
                id=foto['id'],
                usuario_id=foto['usuarioId'],
                nombre=foto['nombre'],
                formato_archivo=foto['formatoArchivo'],
                tamano_bytes=foto['tamanoBytes'],
                ruta_original=foto['rutaOriginal'],
                nivel_deterioro=foto['nivelDeterioro'],
                estado_erosion=foto['estadoErosion'],
                fecha_subida=parse_iso_date(foto['fechaSubida']),
                fecha_ultimo_acceso=parse_iso_date(foto['fechaUltimoAcceso']),
                en_papelera=foto.get('enPapelera', False),
            )
            session.add(fotografia)

            # Si la foto está en papelera, crear registro de eliminación
            if foto.get('enPapelera'):
                reg = RegistroEliminacion(
                    fotografia_id=foto['id'],
                    usuario_id=foto['usuarioId'],
                    fecha_ingreso_papelera=parse_iso_date(
                        foto.get('fechaIngresoPapelera')
                    ) or datetime.utcnow(),
                )
                session.add(reg)

        print(f'[migrate] {len(fotos_data)} fotografia(s) insertada(s).')

        session.commit()
        print('[migrate] Commit exitoso.')

        # Renombrar db.json -> db.json.bak
        if os.path.exists(json_path):
            os.rename(json_path, backup_path)
            print(f'[migrate] {json_path} -> {backup_path}')

    except Exception as e:
        session.rollback()
        print(f'[migrate] ERROR -- rollback ejecutado: {e}')
        raise
    finally:
        session.close()


if __name__ == '__main__':
    migrate()
