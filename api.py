"""
EcoMemory - API Python expuesta a JavaScript via PyWebView
Todos los métodos públicos son accesibles desde JS con: window.pywebview.api.<metodo>()
"""
import json
import os
import random
import shutil
import webview
from datetime import datetime, timezone


VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


class EcoMemoryAPI:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, 'data', 'db.json')
        self.images_dir = os.path.join(base_dir, 'assets', 'images')

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers internos
    # ──────────────────────────────────────────────────────────────────────────

    def _read_db(self) -> dict:
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_db(self, data: dict) -> None:
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _ahora_iso(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def _calcular_nivel_deterioro(self) -> float:
        return random.random()

    def _determinar_estado(self, nivel: float) -> str:
        if nivel < 0.25:
            return 'DETERIORO_LEVE'
        elif nivel < 0.50:
            return 'DETERIORO_MENOR'
        elif nivel < 0.75:
            return 'DETERIORO_MAYOR'
        return 'DETERIORO_CRITICO'

    def _nombre_unico(self, filename: str) -> str:
        """Añade timestamp al nombre si el archivo ya existe en assets/images/."""
        dest = os.path.join(self.images_dir, filename)
        if not os.path.exists(dest):
            return filename
        name, ext = os.path.splitext(filename)
        ts = int(datetime.now().timestamp() * 1000)
        return f"{name}_{ts}{ext}"

    # ──────────────────────────────────────────────────────────────────────────
    # API pública (accesible desde JS)
    # ──────────────────────────────────────────────────────────────────────────

    def get_db(self) -> dict:
        """Retorna el contenido completo de db.json como objeto JS."""
        return self._read_db()

    def register_user(self, nombre: str, correo: str, contrasena: str) -> dict:
        """
        Registra un nuevo usuario en db.json.
        Retorna: { success: bool, error?: 'EMAIL_EXISTS' }
        """
        db = self._read_db()
        # Validar unicidad de correo
        if any(u['correo'].lower() == correo.lower() for u in db['usuarios']):
            return {'success': False, 'error': 'EMAIL_EXISTS'}

        nuevo_usuario = {
            'id': int(datetime.now().timestamp() * 1000),
            'nombre': nombre,
            'correo': correo,
            'contrasena': contrasena,
            'fechaRegistro': self._ahora_iso()
        }
        db['usuarios'].append(nuevo_usuario)
        self._write_db(db)
        return {'success': True}

    def pick_and_upload(self, usuario_id: int) -> dict:
        """
        Abre el diálogo nativo del SO (filtrado a JPG/PNG),
        copia los archivos seleccionados a assets/images/,
        genera los registros en db.json y los retorna a JS.
        Retorna: { success: bool, fotos: [...] }
        """
        # Abrir diálogo nativo del SO
        rutas = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=True,
            file_types=('Imágenes (*.jpg;*.jpeg;*.png)', 'Todos los archivos (*.*)')
        )

        if not rutas:
            # Usuario canceló el diálogo
            return {'success': True, 'fotos': []}

        db = self._read_db()
        nuevas_fotos = []

        for ruta in rutas:
            ext = os.path.splitext(ruta)[1].lower()
            # Validación de extensión (doble seguridad)
            if ext not in VALID_EXTENSIONS:
                continue

            nombre_orig = os.path.basename(ruta)
            nombre_final = self._nombre_unico(nombre_orig)
            dest_path = os.path.join(self.images_dir, nombre_final)

            try:
                shutil.copy2(ruta, dest_path)
            except OSError as e:
                print(f'[EcoMemory] Error copiando {ruta}: {e}')
                continue

            nivel = self._calcular_nivel_deterioro()
            tamano = os.path.getsize(ruta)

            foto = {
                'id': int(datetime.now().timestamp() * 1000) + len(nuevas_fotos),
                'usuarioId': usuario_id,
                'nombre': nombre_final,
                'formatoArchivo': ext.lstrip('.'),
                'tamanoBytes': tamano,
                'rutaOriginal': f'assets/images/{nombre_final}',
                'nivelDeterioro': nivel,
                'estadoErosion': self._determinar_estado(nivel),
                'fechaSubida': self._ahora_iso(),
                'fechaUltimoAcceso': self._ahora_iso(),
                'enPapelera': False,
                'fechaIngresoPapelera': None
            }

            db['fotografias'].append(foto)
            nuevas_fotos.append(foto)

        self._write_db(db)
        return {'success': True, 'fotos': nuevas_fotos}
