# EcoMemory

Galería de fotografías de escritorio con un motor de erosión digital simulada. Aplicación local construida sobre PyWebView: una ventana nativa del sistema operativo que aloja una interfaz web completa comunicada con un backend Python.

---

## Concepto

EcoMemory aplica la metáfora de la degradación física al almacenamiento digital. Cada fotografía recibe un **nivel de deterioro** (valor flotante `[0, 1]`) que la clasifica en uno de cuatro estados de erosión. El sistema expone métricas agregadas del ciclo de vida de las imágenes en un panel lateral persistente.

El proyecto explora esta idea como comentario sobre conservación medioambiental: los archivos digitales, como los ecosistemas, pueden degradarse si no se cuidan.

---

## Estado del proyecto

**Prototipo funcional.** Las siguientes características están implementadas:

- Registro e inicio de sesión de usuarios (validación de correo único, persistencia local).
- Subida de fotografías mediante diálogo nativo del SO (filtrado a `.jpg`, `.jpeg`, `.png`).
- Cálculo y clasificación del nivel de deterioro al momento de la subida.
- Galería renderizada dinámicamente con tarjetas por fotografía.
- Panel lateral con conteo de fotos por estado de erosión y métricas de espacio liberado.
- Papelera de fotos eliminadas.
- Navegación multi-pantalla (login → registro → galería) con guardas de sesión.
**Limitaciones conocidas del prototipo:**

- El nivel de deterioro se genera de forma aleatoria en lugar de calcularse a partir de la antigüedad real o frecuencia de acceso.
- Las contraseñas se almacenan en texto plano.

---

## Arquitectura

```bash
EcoMemory/
├── app.py               # Punto de entrada: crea ventana PyWebView e inyecta la API
├── api.py               # EcoMemoryAPI: bridge Python ↔ JavaScript (SQLAlchemy)
├── index.html           # Pantalla de login
├── register.html        # Pantalla de registro
├── gallery.html         # Galería principal + panel de métricas
├── css/
│   └── main.css         # Sistema de diseño unificado (dark mode, CSS custom properties)
├── js/
│   ├── auth.js          # Autenticación, guardas de sesión, navegación
│   ├── storage.js       # Capa de datos: caché localStorage + llamadas a la API Python
│   ├── gallery.js       # Orquestador: renderizado de galería y subida de fotos
│   ├── erosion.js       # Motor de cálculo y clasificación de deterioro
│   └── dashboard.js     # Cómputo y renderizado de métricas del panel lateral
├── database/
│   ├── __init__.py
│   ├── models.py        # Modelos ORM: Usuario, Fotografia, RegistroEliminacion
│   ├── session.py       # Engine SQLite, fábrica de sesión, init_db()
│   └── migrate.py       # Script de migración one-shot: JSON → SQLite
├── tests/
│   └── test_api.py      # Suite de tests con pytest (5 tests)
├── data/
│   ├── ecomemory.db     # Base de datos SQLite
│   └── db.json.bak      # Backup del JSON original (pre-migración)
└── assets/
    ├── logo.svg
    └── images/          # Almacenamiento de imágenes subidas por el usuario
```

### Patrón de comunicación Python ↔ JavaScript

PyWebView expone la clase `EcoMemoryAPI` como objeto global en el contexto del navegador bajo `window.pywebview.api`. Cada método público de la clase es invocable desde JavaScript de forma asíncrona. El frontend no accede al sistema de archivos directamente; toda operación de I/O pasa por este bridge.

```bash
JavaScript
    │  await window.pywebview.api.<método>(args)
    ▼
EcoMemoryAPI (api.py)
    ├── get_db()           → consulta SQLite vía SQLAlchemy → serializa a camelCase → retorna a JS
    ├── register_user()    → valida unicidad de correo → INSERT en SQLite → commit
    └── pick_and_upload()  → diálogo OS nativo → copia archivo → INSERT en SQLite
                             → retorna lista de fotos nuevas a JS
```

### Capa de datos en el frontend

`storage.js` mantiene una caché en `localStorage` sincronizada con el estado retornado por la API Python. Las demás capas JS consumen `storage.js` en lugar de llamar a `window.pywebview.api` directamente, centralizando el acceso a datos.

### Motor de erosión

`erosion.js` define dos funciones puras:

- `calcularNivelDeterioro()` → `float [0, 1]` (actualmente aleatorio).
- `determinarEstado(nivel)` → uno de cuatro estados según umbrales fijos:
  - `DETERIORO_LEVE` — `< 0.25`
  - `DETERIORO_MENOR` — `0.25 – 0.50`
  - `DETERIORO_MAYOR` — `0.50 – 0.75`
  - `DETERIORO_CRÍTICO` — `≥ 0.75`

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Shell de escritorio | [PyWebView 6.x](https://pywebview.flowrl.com/) |
| Backend / I/O | Python 3.10+ |
| ORM | [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) |
| Persistencia | SQLite (`data/ecomemory.db`) |
| Frontend | HTML5, Vanilla JS (ES Modules), CSS con custom properties |
| UI framework | [Bootstrap 5.3](https://getbootstrap.com/) + Bootstrap Icons 1.11 |
| Tipografía | Inter (Google Fonts) |
| Testing | [pytest](https://docs.pytest.org/) |
| Almacenamiento de imágenes | Sistema de archivos local (`assets/images/`) |

---

## Requisitos mínimos

- Python 3.10+
- PyWebView 6.x
- SQLAlchemy 2.0+

```bash
# Windows
pip install -r requirements.txt
```

> [!IMPORTANT]
> Para usar el sistema en entornos linux es necesario indicar el motor gráfico al instalar pywebview:

```bash
pip install pywebview[qt]
```

---

## Ejecución

```bash
python app.py
```

Se abre una ventana nativa del SO. No se requiere servidor externo ni navegador.

### Tests

```bash
pytest tests/ -v
```

---

## Créditos

Desarrollado por [Kevin Esguerra Cardona](mailto:kevin.esguerra@utp.edu.co) y Juan Andrés Velásquez Jiménez.
