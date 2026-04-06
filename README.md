# EcoMemory

> Archivo digital de fotografías con un motor de erosión simulada. Prototipo de aplicación de escritorio construido con HTML/CSS/JS y Python.

## Descripción

EcoMemory es una galería de imágenes local donde cada fotografía tiene un nivel de deterioro digital que refleja su "edad" y acceso. El sistema clasifica las fotos en cuatro estados de erosión (Leve, Menor, Mayor, Crítico) y expone métricas globales del ciclo de vida en un panel lateral.

El proyecto explora el concepto de *erosión digital* —la idea de que los archivos, como los objetos físicos, pueden degradarse con el tiempo— como metáfora de conservación medioambiental.

## Arquitectura

```
EcoMemory/
├── app.py               # Punto de entrada PyWebView (ventana nativa)
├── api.py               # EcoMemoryAPI: bridge Python ↔ JavaScript
├── index.html           # Pantalla de Login
├── register.html        # Pantalla de Registro
├── gallery.html         # Galería principal + panel de métricas
├── css/
│   └── main.css         # Sistema de diseño unificado (dark mode)
├── js/
│   ├── storage.js       # Capa de datos: caché localStorage + API Python
│   ├── auth.js          # Autenticación y guardas de sesión
│   ├── gallery.js       # Orquestador de galería y subida de fotos
│   ├── erosion.js       # Motor de cálculo y clasificación de deterioro
│   └── dashboard.js     # Métricas del panel lateral
├── data/
│   └── db.json          # Base de datos JSON (usuarios, fotografías, estadísticas)
└── assets/
    └── images/          # Almacenamiento de imágenes subidas por el usuario
```

### Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Shell de escritorio | [PyWebView 6.x](https://pywebview.flowrl.com/) |
| Backend (lógica / I/O) | Python 3 (`api.py`) |
| Frontend | HTML5 + Vanilla JS (ES Modules) + CSS Variables |
| Estilos | CSS propio + Bootstrap 5 (layout y utilidades) + Bootstrap Icons |
| Persistencia | `data/db.json` (lectura/escritura directa via Python) |

### Flujo de datos

```
JavaScript (browser context)
    │  window.pywebview.api.<método>()
    ▼
api.py — EcoMemoryAPI
    ├── get_db()           → lee data/db.json → retorna a JS
    ├── register_user()    → valida email, escribe en db.json
    └── pick_and_upload()  → abre diálogo OS → copia a assets/images/
                             → escribe en db.json → retorna fotos nuevas

JS recibe respuesta → actualiza localStorage (caché) → re-renderiza UI
```

### Motor de erosión (`erosion.js`)

- `calcularNivelDeterioro()` → `float [0, 1]` (aleatorio en fotos nuevas)
- `determinarEstado(nivel)` → `DETERIORO_LEVE | MENOR | MAYOR | CRÍTICO`
- Umbrales: `<0.25` Leve · `0.25–0.50` Menor · `0.50–0.75` Mayor · `≥0.75` Crítico

## Requisitos

- [Python 3.10+](https://www.python.org/)
- [PyWebView 6.x](https://pywebview.flowrl.com/guide/installation.html)

```bash
pip install pywebview
```

## Ejecución

```bash
python app.py
```

> Se abre una ventana nativa del SO con la aplicación. No se requiere ningún servidor ni navegador externo.

## Créditos

Desarrollado por [**Kevin Esguerra Cardona**](mailto:kevin.esguerra@utp.edu.co) y **Juan Andrés Velásquez Jiménez** usando Antigravity.
