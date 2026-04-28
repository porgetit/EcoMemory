"""
EcoMemory - Suite de tests
Ejecutar con: pytest tests/ -v
"""
import json
import os
import shutil
import tempfile
import sys

import pytest

# Agregar raíz del proyecto al path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.models import Usuario, Fotografia, RegistroEliminacion
from database.session import get_engine, init_db, get_session_factory


# ─────────────────────────────────────────────────────────────────────────────
# Fixture: directorio temporal con estructura de proyecto
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_project(tmp_path):
    """Crea un directorio temporal con la estructura esperada por EcoMemoryAPI."""
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    images_dir = tmp_path / 'assets' / 'images'
    images_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def api(tmp_project):
    """Crea una instancia de EcoMemoryAPI apuntando a un proyecto temporal."""
    from api import EcoMemoryAPI
    return EcoMemoryAPI(str(tmp_project))


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Registro exitoso de usuario
# ─────────────────────────────────────────────────────────────────────────────

def test_register_user_success(api, tmp_project):
    result = api.register_user('Juan Perez', 'juan@example.com', 'pass123')
    assert result['success'] is True

    # Verificar existencia en la DB
    engine = get_engine(str(tmp_project))
    Session = get_session_factory(engine)
    with Session() as session:
        user = session.query(Usuario).filter_by(correo='juan@example.com').first()
        assert user is not None
        assert user.nombre == 'Juan Perez'


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Registro con correo duplicado
# ─────────────────────────────────────────────────────────────────────────────

def test_register_user_duplicate_email(api):
    api.register_user('Juan Perez', 'juan@example.com', 'pass123')
    result = api.register_user('Maria Lopez', 'juan@example.com', 'pass456')
    assert result['success'] is False
    assert result['error'] == 'EMAIL_EXISTS'


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Estructura de get_db()
# ─────────────────────────────────────────────────────────────────────────────

def test_get_db_structure(api):
    db = api.get_db()
    assert 'usuarios' in db
    assert 'fotografias' in db
    assert isinstance(db['usuarios'], list)
    assert isinstance(db['fotografias'], list)


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: get_db() refleja el usuario registrado
# ─────────────────────────────────────────────────────────────────────────────

def test_get_db_after_register(api):
    api.register_user('Ana Garcia', 'ana@example.com', 'seguro789')
    db = api.get_db()
    correos = [u['correo'] for u in db['usuarios']]
    assert 'ana@example.com' in correos

    # Verificar que los campos camelCase están presentes
    usuario = next(u for u in db['usuarios'] if u['correo'] == 'ana@example.com')
    assert 'id' in usuario
    assert 'nombre' in usuario
    assert 'correo' in usuario
    assert 'contrasena' in usuario
    assert 'fechaRegistro' in usuario


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Script de migración
# ─────────────────────────────────────────────────────────────────────────────

def test_migration_script(tmp_path):
    """Verifica que migrate.py importa correctamente datos desde un JSON fixture."""
    # Crear estructura de directorios
    data_dir = tmp_path / 'data'
    data_dir.mkdir()

    # Crear JSON fixture
    fixture = {
        'usuarios': [
            {
                'id': 1,
                'nombre': 'Test User',
                'correo': 'test@example.com',
                'contrasena': 'test123',
                'fechaRegistro': '2026-03-16T12:00:00.000Z'
            }
        ],
        'fotografias': [
            {
                'id': 101,
                'usuarioId': 1,
                'nombre': 'foto1.jpg',
                'formatoArchivo': 'jpg',
                'tamanoBytes': 1024,
                'rutaOriginal': 'assets/images/foto1.jpg',
                'nivelDeterioro': 0.15,
                'estadoErosion': 'DETERIORO_LEVE',
                'fechaSubida': '2026-03-10T00:00:00.000Z',
                'fechaUltimoAcceso': '2026-03-16T00:00:00.000Z',
                'enPapelera': False,
                'fechaIngresoPapelera': None
            },
            {
                'id': 102,
                'usuarioId': 1,
                'nombre': 'foto2.png',
                'formatoArchivo': 'png',
                'tamanoBytes': 2048,
                'rutaOriginal': 'assets/images/foto2.png',
                'nivelDeterioro': 0.85,
                'estadoErosion': 'DETERIORO_CRITICO',
                'fechaSubida': '2026-02-20T00:00:00.000Z',
                'fechaUltimoAcceso': '2026-02-25T00:00:00.000Z',
                'enPapelera': True,
                'fechaIngresoPapelera': '2026-03-01T00:00:00.000Z'
            }
        ]
    }

    json_path = data_dir / 'db.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(fixture, f)

    # Ejecutar migración
    from database.migrate import migrate
    migrate(str(tmp_path))

    # Verificar datos migrados
    engine = get_engine(str(tmp_path))
    Session = get_session_factory(engine)

    with Session() as session:
        assert session.query(Usuario).count() == 1
        assert session.query(Fotografia).count() == 2
        assert session.query(RegistroEliminacion).count() == 1

        # Verificar que el registro de eliminación corresponde a la foto en papelera
        reg = session.query(RegistroEliminacion).first()
        assert reg.fotografia_id == 102
        assert reg.usuario_id == 1

    # Verificar que db.json fue renombrado a db.json.bak
    assert not json_path.exists()
    assert (data_dir / 'db.json.bak').exists()
