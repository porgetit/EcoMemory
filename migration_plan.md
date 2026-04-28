# Plan de migración: JSON → SQLite + SQLAlchemy (EcoMemory)

## Contexto

- Persistencia actual: lectura/escritura directa sobre `data/db.json` desde `EcoMemoryAPI` (`_read_db` / `_write_db`).
- Entidades identificadas en `api.py`:
  - `usuarios`: id, nombre, correo, contrasena, fechaRegistro
  - `fotografias`: id, usuarioId, nombre, formatoArchivo, tamanoBytes, rutaOriginal, nivelDeterioro, estadoErosion, fechaSubida, fechaUltimoAcceso, enPapelera, fechaIngresoPapelera
  - `registros_eliminacion`: entidad implícita (papelera); debe extraerse como tabla independiente.
- No hay ORM ni capa de abstracción de datos actualmente.

---

## Dependencias

Agregar a `requirements.txt` (o instalación directa):

```
sqlalchemy>=2.0
```

SQLite viene incluido en la stdlib de Python 3. No se requiere driver adicional.

---

## Fase 1 — Crear módulo de modelos (`database/models.py`)

Crear el directorio `database/` en la raíz del proyecto.

### Tareas

1. Definir `Base = declarative_base()`.
2. Implementar clase `Usuario` mapeada a tabla `usuarios`:
   - `id` INTEGER PK (no autoincrement; preservar IDs tipo timestamp del sistema actual)
   - `nombre` VARCHAR NOT NULL
   - `correo` VARCHAR UNIQUE NOT NULL
   - `contrasena` VARCHAR NOT NULL
   - `fecha_registro` DATETIME NOT NULL
3. Implementar clase `Fotografia` mapeada a tabla `fotografias`:
   - `id` INTEGER PK
   - `usuario_id` INTEGER FK → `usuarios.id` ON DELETE CASCADE
   - `nombre` VARCHAR NOT NULL
   - `formato_archivo` VARCHAR(10) NOT NULL
   - `tamano_bytes` INTEGER NOT NULL
   - `ruta_original` VARCHAR NOT NULL
   - `nivel_deterioro` FLOAT NOT NULL
   - `estado_erosion` VARCHAR(20) NOT NULL
   - `fecha_subida` DATETIME NOT NULL
   - `fecha_ultimo_acceso` DATETIME NOT NULL
   - `en_papelera` BOOLEAN NOT NULL DEFAULT FALSE
4. Implementar clase `RegistroEliminacion` mapeada a tabla `registros_eliminacion`:
   - `id` INTEGER PK AUTOINCREMENT
   - `fotografia_id` INTEGER FK → `fotografias.id` ON DELETE CASCADE
   - `usuario_id` INTEGER FK → `usuarios.id`
   - `fecha_ingreso_papelera` DATETIME NOT NULL
   - `fecha_eliminacion_definitiva` DATETIME NULLABLE

   > Esta tabla reemplaza los campos `enPapelera` / `fechaIngresoPapelera` del JSON. El campo `en_papelera` en `Fotografia` puede mantenerse como redundante o eliminarse; decidir según conveniencia de las queries JS-side.

5. Definir relaciones SQLAlchemy (`relationship`) entre las tres clases para soporte de joins y cascades.

---

## Fase 2 — Crear módulo de sesión/engine (`database/session.py`)

### Tareas

1. Crear función `get_engine(base_dir: str)` que devuelva un `create_engine` apuntando a `data/ecomemory.db` (ruta absoluta construida con `base_dir`).
2. Crear función `init_db(engine)` que ejecute `Base.metadata.create_all(engine)`.
3. Crear fábrica de sesión con `sessionmaker` y exponerla como `SessionLocal`.
4. El engine debe configurarse con `check_same_thread=False` (requisito de SQLite con PyWebView, que puede llamar desde múltiples threads).

---

## Fase 3 — Script de migración de datos (`database/migrate.py`)

Ejecutar una única vez para migrar `data/db.json` → `data/ecomemory.db`.

### Tareas

1. Leer `data/db.json`.
2. Llamar `init_db(engine)` para crear las tablas si no existen.
3. Insertar todos los registros de `usuarios` como instancias de `Usuario`.
4. Insertar todos los registros de `fotografias` como instancias de `Fotografia`.
5. Para cada fotografía donde `enPapelera == True`, crear un `RegistroEliminacion` con `fecha_ingreso_papelera` tomada de `fechaIngresoPapelera`.
6. Hacer commit. En caso de error, rollback y loguear.
7. El script debe ser idempotente: verificar si la DB ya contiene datos antes de insertar (evitar duplicados si se ejecuta dos veces).
8. No eliminar `data/db.json` al finalizar; renombrarlo a `data/db.json.bak`.

---

## Fase 4 — Refactorizar `EcoMemoryAPI` (`api.py`)

### Tareas

1. Eliminar `_read_db()` y `_write_db()`.
2. En `__init__`, inicializar engine y `SessionLocal` importados desde `database/session.py`. Llamar `init_db(engine)`.
3. Reescribir `get_db()`:
   - Abrir sesión, hacer query de todas las entidades necesarias.
   - Serializar a `dict` compatible con el contrato JSON que espera el JS (mantener los mismos keys que el frontend consume en `storage.js`).
   - Cerrar sesión y retornar el dict.
4. Reescribir `register_user()`:
   - Abrir sesión.
   - Query de unicidad por correo.
   - Insertar `Usuario`, commit, retornar `{'success': True}`.
5. Reescribir `pick_and_upload()`:
   - Mantener la lógica de diálogo nativo y copia de archivos sin cambios.
   - Reemplazar escritura en JSON por inserción de instancias `Fotografia` en sesión + commit.
   - Serializar las fotos nuevas al mismo formato dict que retornaba antes.
6. Usar context manager (`with SessionLocal() as session`) en todos los métodos para garantizar cierre de sesión.
7. Agregar manejo de `IntegrityError` de SQLAlchemy donde corresponda (ej. correo duplicado).

---

## Fase 5 — Verificación de contrato con el frontend

El JS (`storage.js`, `auth.js`, `gallery.js`) consume los datos retornados por `get_db()` y `pick_and_upload()`. El refactor en Python no debe alterar la forma del JSON retornado.

### Tareas

1. Mapear todos los keys del JSON original (`usuarios`, `fotografias`, y sus campos en camelCase) a los alias usados en la serialización de los modelos SQLAlchemy.
2. Confirmar que `get_db()` retorna exactamente `{ "usuarios": [...], "fotografias": [...] }` con los mismos campos que el JS espera.
3. Confirmar que `pick_and_upload()` retorna `{ "success": bool, "fotos": [...] }` con los campos de fotografía en camelCase.

> Si los modelos usan snake_case internamente, la serialización debe convertir a camelCase antes de retornar a JS.

---

## Fase 6 — Testing

Sin intervención humana; el agente ejecuta directamente.

### Tests a implementar (`tests/test_api.py`)

Usar `pytest`. Crear un `EcoMemoryAPI` con `base_dir` apuntando a un directorio temporal para cada test.

1. `test_register_user_success`: registrar usuario nuevo → verificar `success: True` y existencia en DB.
2. `test_register_user_duplicate_email`: registrar mismo correo dos veces → segundo intento retorna `error: EMAIL_EXISTS`.
3. `test_get_db_structure`: llamar `get_db()` → verificar que retorna dict con keys `usuarios` y `fotografias`.
4. `test_get_db_after_register`: registrar usuario, luego `get_db()` → verificar que el usuario aparece en la respuesta.
5. `test_migration_script`: ejecutar `migrate.py` sobre un JSON de fixture → verificar que las tres tablas tienen el número correcto de registros.

### Ejecución

```
pip install pytest sqlalchemy
pytest tests/ -v
```

---

## Estructura final del proyecto

```
EcoMemory/
├── database/
│   ├── __init__.py
│   ├── models.py       # Clases Usuario, Fotografia, RegistroEliminacion
│   ├── session.py      # Engine, SessionLocal, init_db
│   └── migrate.py      # Script de migración one-shot
├── data/
│   ├── db.json.bak     # Backup post-migración
│   └── ecomemory.db    # Nueva base de datos SQLite
├── tests/
│   └── test_api.py
├── api.py              # Refactorizado (sin JSON I/O)
├── app.py              # Sin cambios
└── ...
```

---

## Orden de ejecución para el agente

1. Instalar dependencias: `pip install sqlalchemy pytest`
2. Crear `database/__init__.py` (vacío)
3. Implementar `database/models.py` (Fase 1)
4. Implementar `database/session.py` (Fase 2)
5. Implementar `database/migrate.py` (Fase 3)
6. Ejecutar migración: `python database/migrate.py`
7. Refactorizar `api.py` (Fase 4)
8. Verificar contrato de serialización (Fase 5)
9. Implementar `tests/test_api.py` (Fase 6)
10. Ejecutar tests: `pytest tests/ -v`
11. Si todos pasan: confirmar arranque con `python app.py`
