# EcoMemory

Galería de fotografías de escritorio con un motor de erosión digital simulada. Aplicación local construida sobre PyWebView: una ventana nativa del sistema operativo que aloja una interfaz web completa comunicada con un backend Python.

---

## Concepto

EcoMemory aplica la metáfora de la degradación física al almacenamiento digital. Cada fotografía subida inicia con un **nivel de deterioro** de `0.0` que incrementa progresivamente hasta `1.0` conforme pasa el tiempo. Un daemon de erosión en segundo plano recalcula el deterioro de cada imagen en tiempo real, y al alcanzar el 100% la foto se auto-elimina del sistema.

La degradación se refleja visualmente mediante una **máscara de pixelado dinámica** renderizada con HTML5 Canvas: a medida que el nivel de deterioro crece, la imagen se descompone en bloques de píxeles cada vez más grandes, hasta volverse irreconocible.

El proyecto explora esta idea como comentario sobre conservación medioambiental: los archivos digitales, como los ecosistemas, pueden degradarse si no se cuidan.

---

## Características

- **Registro e inicio de sesión** de usuarios (validación de correo único, persistencia SQLite).
- **Subida de fotografías** mediante diálogo nativo del SO (filtrado a `.jpg`, `.jpeg`, `.png`).
- **Motor de erosión temporal** — daemon en segundo plano que incrementa el deterioro basado en el tiempo real transcurrido desde la subida.
- **Auto-eliminación** — las fotos se mueven automáticamente a la papelera al alcanzar el 100% de deterioro.
- **Eliminación manual** — botón de papelera superpuesto en cada tarjeta (soft delete con `RegistroEliminacion`).
- **Máscara de pixelado con Canvas** — reemplaza las imágenes estáticas con un efecto visual de degradación progresiva en tiempo real.
- **Polling dinámico** — el frontend sincroniza automáticamente con el backend a intervalos derivados de la configuración de erosión.
- **Ciclo de vida del daemon ligado a la sesión** — el daemon arranca al iniciar sesión (filtrado por usuario) y se detiene limpiamente al cerrar sesión.
- **Panel lateral** con conteo de fotos por estado de erosión y métricas de espacio liberado.
- **Logging por consola** con marcas temporales en cada acción del daemon.
- **Navegación multi-pantalla** (login → registro → galería) con guardas de sesión.

**Limitaciones conocidas:**

- Las contraseñas se almacenan en texto plano.

---

## Arquitectura

```
EcoMemory/
├── app.py               # Punto de entrada: crea ventana PyWebView e inyecta la API
├── api.py               # EcoMemoryAPI: bridge Python ↔ JavaScript (SQLAlchemy + daemon)
├── index.html           # Pantalla de login
├── register.html        # Pantalla de registro
├── gallery.html         # Galería principal + panel de métricas
├── css/
│   └── main.css         # Sistema de diseño unificado (dark mode, CSS custom properties)
├── js/
│   ├── auth.js          # Autenticación, guardas de sesión, control de ciclo de vida del daemon
│   ├── storage.js       # Capa de datos: caché localStorage + bridges a la API Python
│   ├── gallery.js       # Renderizado de galería con Canvas, eliminación, polling dinámico
│   ├── erosion.js       # Clasificación de deterioro y utilidades de estado
│   └── dashboard.js     # Cómputo y renderizado de métricas del panel lateral
├── database/
│   ├── __init__.py
│   ├── models.py        # Modelos ORM: Usuario, Fotografia, RegistroEliminacion
│   ├── session.py       # Engine SQLite, fábrica de sesión, init_db()
│   └── migrate.py       # Script de migración one-shot: JSON → SQLite
├── tests/
│   └── test_api.py      # Suite de tests con pytest
├── data/
│   └── ecomemory.db     # Base de datos SQLite (generada automáticamente)
└── assets/
    ├── logo.svg
    └── images/          # Almacenamiento de imágenes subidas por el usuario
```

### Patrón de comunicación Python ↔ JavaScript

PyWebView expone la clase `EcoMemoryAPI` como objeto global en el contexto del navegador bajo `window.pywebview.api`. Cada método público de la clase es invocable desde JavaScript de forma asíncrona. El frontend no accede al sistema de archivos directamente; toda operación de I/O pasa por este bridge.

```
JavaScript
    │  await window.pywebview.api.<método>(args)
    ▼
EcoMemoryAPI (api.py)
    ├── get_db()           → consulta SQLite vía SQLAlchemy → serializa a camelCase → retorna a JS
    ├── get_config()       → retorna intervalo de polling dinámico derivado de TIEMPO_MAXIMO_VIDA
    ├── register_user()    → valida unicidad de correo → INSERT en SQLite → commit
    ├── pick_and_upload()  → diálogo OS nativo → copia archivo → INSERT en SQLite → retorna fotos nuevas
    ├── delete_photo()     → soft delete → marca en_papelera + crea RegistroEliminacion
    ├── start_session()    → arranca daemon de erosión para el usuario indicado
    └── end_session()      → detiene el daemon de forma segura vía threading.Event
```

### Motor de erosión

El motor de erosión opera como un **hilo daemon** en el backend que se ejecuta cada `TIEMPO_MAXIMO_VIDA * 5%` segundos. Para cada foto activa del usuario:

1. Calcula `nivel_deterioro = tiempo_transcurrido / TIEMPO_MAXIMO_VIDA` (acotado a `[0, 1]`).
2. Determina el `estado_erosion` según umbrales fijos:
   - `DETERIORO_LEVE` — `< 0.25`
   - `DETERIORO_MENOR` — `0.25 – 0.50`
   - `DETERIORO_MAYOR` — `0.50 – 0.75`
   - `DETERIORO_CRÍTICO` — `≥ 0.75`
3. Si `nivel_deterioro >= 1.0`, ejecuta auto-eliminación (soft delete).

### Máscara de pixelado

El frontend reemplaza las etiquetas `<img>` por elementos `<canvas>` donde se aplica un algoritmo de doble dibujo:

1. La imagen se dibuja a escala reducida (proporcional al deterioro).
2. Se re-escala al tamaño original con `imageSmoothingEnabled = false`, produciendo bloques de píxeles cuadrados.

### Capa de datos en el frontend

`storage.js` mantiene una caché en `localStorage` sincronizada con el estado retornado por la API Python. Las demás capas JS consumen `storage.js` en lugar de llamar a `window.pywebview.api` directamente, centralizando el acceso a datos.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Shell de escritorio | [PyWebView 6.x](https://pywebview.flowrl.com/) |
| Backend / I/O | Python 3.10+ |
| ORM | [SQLAlchemy 2.0+](https://www.sqlalchemy.org/) |
| Persistencia | SQLite (`data/ecomemory.db`) |
| Concurrencia | `threading` (daemon thread + `threading.Event`) |
| Frontend | HTML5, Vanilla JS (ES Modules), CSS con custom properties |
| Renderizado visual | HTML5 Canvas (pixelado dinámico) |
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
