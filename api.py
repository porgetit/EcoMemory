"""
EcoMemory - API Python expuesta a JavaScript via PyWebView
Todos los métodos públicos son accesibles desde JS con: window.pywebview.api.<metodo>()
"""
import os
import shutil
import threading
import webview
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from database.models import Usuario, Fotografia, RegistroEliminacion
from database.session import get_engine, init_db, get_session_factory


VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


# ──────────────────────────────────────────────────────────────────────────────
# Constante del Motor de Erosión
# ──────────────────────────────────────────────────────────────────────────────
TIEMPO_MAXIMO_VIDA = 100    # Segundos para alcanzar 100% deterioro
DAEMON_INTERVALO = TIEMPO_MAXIMO_VIDA * 0.05  # 5% del tiempo de vida (= polling frontend)


class EcoMemoryAPI:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.images_dir = os.path.join(base_dir, 'assets', 'images')

        # Inicializar SQLAlchemy
        engine = get_engine(base_dir)
        init_db(engine)
        self.SessionLocal = get_session_factory(engine)

        # Control del daemon de erosión (se arranca con start_session)
        self._daemon_stop_event = threading.Event()
        self._daemon_thread = None

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers internos
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _log(msg: str):
        ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f'[EcoMemory {ts}] {msg}')

    def _ahora_iso(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def _ahora_dt(self) -> datetime:
        return datetime.now(timezone.utc)

    def _calcular_nivel_deterioro(self) -> float:
        """Las fotos nuevas empiezan sin deterioro; el daemon lo incrementa."""
        return 0.0

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
    # Daemon de Erosión Temporal
    # ──────────────────────────────────────────────────────────────────────────

    def _iniciar_daemon_erosion(self, usuario_id: int):
        """Arranca un hilo daemon que incrementa el nivel_deterioro de las
        fotos activas del usuario indicado."""
        def _loop():
            self._log(f'Daemon iniciado (usuario={usuario_id}, intervalo={DAEMON_INTERVALO}s, vida={TIEMPO_MAXIMO_VIDA}s)')
            while not self._daemon_stop_event.is_set():
                try:
                    with self.SessionLocal() as session:
                        ahora = datetime.now(timezone.utc)
                        fotos = session.query(Fotografia).filter(
                            Fotografia.usuario_id == usuario_id,
                            Fotografia.en_papelera == False,
                            Fotografia.nivel_deterioro < 1.0,
                        ).all()

                        if fotos:
                            self._log(f'Ciclo: {len(fotos)} foto(s) activa(s)')

                        for foto in fotos:
                            # Fix #1: SQLite devuelve datetimes naive;
                            # forzar UTC para evitar "offset-naive vs aware".
                            fecha_base_aware = foto.fecha_ultimo_acceso.replace(
                                tzinfo=timezone.utc
                            )
                            transcurrido = (
                                ahora - fecha_base_aware
                            ).total_seconds()
                            nuevo_nivel = min(
                                transcurrido / TIEMPO_MAXIMO_VIDA, 1.0
                            )
                            pct = round(nuevo_nivel * 100, 1)
                            foto.nivel_deterioro = nuevo_nivel
                            foto.estado_erosion = self._determinar_estado(
                                nuevo_nivel
                            )

                            self._log(
                                f'  ↳ "{foto.nombre}" → {pct}% '
                                f'({foto.estado_erosion}) [{transcurrido:.1f}s transcurridos]'
                            )

                            # Fix #2: Auto-eliminación al alcanzar 100%.
                            if nuevo_nivel >= 1.0:
                                foto.en_papelera = True
                                registro = RegistroEliminacion(
                                    fotografia_id=foto.id,
                                    usuario_id=usuario_id,
                                    fecha_ingreso_papelera=ahora,
                                )
                                session.add(registro)
                                self._log(
                                    f'  ⚠ AUTO-ELIMINADA: "{foto.nombre}" → papelera'
                                )

                        session.commit()
                except Exception as exc:
                    self._log(f'ERROR en daemon: {exc}')

                # Esperar N segundos o salir de inmediato si se activa el evento
                self._daemon_stop_event.wait(DAEMON_INTERVALO)

            self._log('Daemon detenido')

        self._daemon_thread = threading.Thread(target=_loop, daemon=True)
        self._daemon_thread.start()

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

    def get_config(self) -> dict:
        """Retorna configuración dinámica para el frontend."""
        return {
            'pollingIntervalMs': int(TIEMPO_MAXIMO_VIDA * 0.05 * 1000),
        }

    def start_session(self, usuario_id: int) -> dict:
        """Arranca el daemon de erosión para el usuario indicado.
        Si ya existía un daemon previo, lo detiene primero."""
        self._log(f'start_session(usuario_id={usuario_id})')
        self.end_session()
        self._daemon_stop_event.clear()
        self._iniciar_daemon_erosion(usuario_id)
        return {'success': True}

    def end_session(self) -> dict:
        """Detiene el daemon de erosión de forma segura."""
        self._log('end_session() → deteniendo daemon...')
        self._daemon_stop_event.set()
        if self._daemon_thread and self._daemon_thread.is_alive():
            self._daemon_thread.join(timeout=DAEMON_INTERVALO + 1)
        self._daemon_thread = None
        return {'success': True}

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

    def delete_photo(self, foto_id: int, usuario_id: int) -> dict:
        """
        Soft-delete: marca la foto como en_papelera y crea un RegistroEliminacion.
        Retorna: { success: bool, error?: str }
        """
        with self.SessionLocal() as session:
            foto = session.query(Fotografia).filter(
                Fotografia.id == foto_id,
                Fotografia.usuario_id == usuario_id,
            ).first()

            if not foto:
                return {'success': False, 'error': 'NOT_FOUND'}

            foto.en_papelera = True
            ahora = self._ahora_dt()

            registro = RegistroEliminacion(
                fotografia_id=foto.id,
                usuario_id=usuario_id,
                fecha_ingreso_papelera=ahora,
            )
            session.add(registro)
            session.commit()

            return {'success': True}

    def get_photo_detail(self, foto_id: int, usuario_id: int) -> dict:
        """
        Retorna los datos de una fotografía específica del usuario.
        Retorna: { success: bool, foto?: dict, error?: str }
        """
        with self.SessionLocal() as session:
            foto = session.query(Fotografia).filter(
                Fotografia.id == foto_id,
                Fotografia.usuario_id == usuario_id,
            ).first()
    
            if not foto:
                return {'success': False, 'error': 'NOT_FOUND'}
    
            return {'success': True, 'foto': self._serializar_fotografia(foto)}

    def view_photo(self, foto_id: int, usuario_id: int) -> dict:
        """
        Registra que el usuario visualizó la foto individualmente:
        - Guarda el nivel de deterioro previo para mostrárselo al usuario
        - Resetea nivel_deterioro a 0.0 y estado_erosion a 'DETERIORO_LEVE'
        - Actualiza fecha_ultimo_acceso a ahora
        Retorna: { success: bool, nivelPrevio?: float, foto?: dict, error?: str }
        """
        with self.SessionLocal() as session:
            foto = session.query(Fotografia).filter(
                Fotografia.id == foto_id,
                Fotografia.usuario_id == usuario_id,
                Fotografia.en_papelera == False,
            ).first()
    
            if not foto:
                return {'success': False, 'error': 'NOT_FOUND'}
    
            nivel_previo = foto.nivel_deterioro
    
            foto.nivel_deterioro = 0.0
            foto.estado_erosion = 'DETERIORO_LEVE'
            foto.fecha_ultimo_acceso = self._ahora_dt()
    
            session.commit()
    
            return {
                'success': True,
                'nivelPrevio': nivel_previo,
                'foto': self._serializar_fotografia(foto),
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
