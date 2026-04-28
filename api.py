"""
EcoMemory - API Python expuesta a JavaScript via PyWebView
Todos los métodos públicos son accesibles desde JS con: window.pywebview.api.<metodo>()
"""
import os
import random
import shutil
import webview
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from database.models import Usuario, Fotografia, RegistroEliminacion
from database.session import get_engine, init_db, get_session_factory


VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


class EcoMemoryAPI:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.images_dir = os.path.join(base_dir, 'assets', 'images')

        # Inicializar SQLAlchemy
        engine = get_engine(base_dir)
        init_db(engine)
        self.SessionLocal = get_session_factory(engine)

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers internos
    # ──────────────────────────────────────────────────────────────────────────

    def _ahora_iso(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def _ahora_dt(self) -> datetime:
        return datetime.now(timezone.utc)

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
    # Serialización: snake_case (DB) → camelCase (JS)
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _serializar_usuario(u: Usuario) -> dict:
        return {
            'id': u.id,
            'nombre': u.nombre,
            'correo': u.correo,
            'contrasena': u.contrasena,
            'fechaRegistro': u.fecha_registro.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                if u.fecha_registro else None,
        }

    @staticmethod
    def _serializar_fotografia(f: Fotografia) -> dict:
        # Determinar si tiene registro de eliminación con fecha de ingreso
        fecha_ingreso = None
        if f.registros_eliminacion:
            reg = f.registros_eliminacion[0]
            if reg.fecha_ingreso_papelera:
                fecha_ingreso = reg.fecha_ingreso_papelera.strftime(
                    '%Y-%m-%dT%H:%M:%S.000Z'
                )

        return {
            'id': f.id,
            'usuarioId': f.usuario_id,
            'nombre': f.nombre,
            'formatoArchivo': f.formato_archivo,
            'tamanoBytes': f.tamano_bytes,
            'rutaOriginal': f.ruta_original,
            'nivelDeterioro': f.nivel_deterioro,
            'estadoErosion': f.estado_erosion,
            'fechaSubida': f.fecha_subida.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                if f.fecha_subida else None,
            'fechaUltimoAcceso': f.fecha_ultimo_acceso.strftime(
                '%Y-%m-%dT%H:%M:%S.000Z'
            ) if f.fecha_ultimo_acceso else None,
            'enPapelera': f.en_papelera,
            'fechaIngresoPapelera': fecha_ingreso,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # API pública (accesible desde JS)
    # ──────────────────────────────────────────────────────────────────────────

    def get_db(self) -> dict:
        """Retorna el contenido completo de la DB como objeto JS."""
        with self.SessionLocal() as session:
            usuarios = session.query(Usuario).all()
            fotografias = session.query(Fotografia).all()

            return {
                'usuarios': [self._serializar_usuario(u) for u in usuarios],
                'fotografias': [
                    self._serializar_fotografia(f) for f in fotografias
                ],
            }

    def register_user(self, nombre: str, correo: str, contrasena: str) -> dict:
        """
        Registra un nuevo usuario en la base de datos.
        Retorna: { success: bool, error?: 'EMAIL_EXISTS' }
        """
        with self.SessionLocal() as session:
            # Validar unicidad de correo
            existente = session.query(Usuario).filter(
                Usuario.correo.ilike(correo)
            ).first()
            if existente:
                return {'success': False, 'error': 'EMAIL_EXISTS'}

            nuevo_usuario = Usuario(
                id=int(datetime.now().timestamp() * 1000),
                nombre=nombre,
                correo=correo,
                contrasena=contrasena,
                fecha_registro=self._ahora_dt(),
            )
            session.add(nuevo_usuario)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return {'success': False, 'error': 'EMAIL_EXISTS'}

            return {'success': True}

    def pick_and_upload(self, usuario_id: int) -> dict:
        """
        Abre el diálogo nativo del SO (filtrado a JPG/PNG),
        copia los archivos seleccionados a assets/images/,
        genera los registros en la DB y los retorna a JS.
        Retorna: { success: bool, fotos: [...] }
        """
        # Abrir diálogo nativo del SO
        rutas = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=True,
            file_types=(
                'Imágenes (*.jpg;*.jpeg;*.png)',
                'Todos los archivos (*.*)'
            )
        )

        if not rutas:
            # Usuario canceló el diálogo
            return {'success': True, 'fotos': []}

        nuevas_fotos_dict = []

        with self.SessionLocal() as session:
            for i, ruta in enumerate(rutas):
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
                ahora = self._ahora_dt()

                fotografia = Fotografia(
                    id=int(datetime.now().timestamp() * 1000) + i,
                    usuario_id=usuario_id,
                    nombre=nombre_final,
                    formato_archivo=ext.lstrip('.'),
                    tamano_bytes=tamano,
                    ruta_original=f'assets/images/{nombre_final}',
                    nivel_deterioro=nivel,
                    estado_erosion=self._determinar_estado(nivel),
                    fecha_subida=ahora,
                    fecha_ultimo_acceso=ahora,
                    en_papelera=False,
                )
                session.add(fotografia)
                nuevas_fotos_dict.append(
                    self._serializar_fotografia(fotografia)
                )

            session.commit()

        return {'success': True, 'fotos': nuevas_fotos_dict}
