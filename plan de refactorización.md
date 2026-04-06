# 🏗️ PLAN DE REFACTORIZACIÓN - EcoMemory

## Documento Estratégico: De Prototipo a Arquitectura Documentada

**Objetivo General:** Transformar el MVP actual (33% cobertura) en una base consistente con la arquitectura documentada (70%+ cobertura) que permita desarrollo futuro apegado al diseño propuesto.

**Duración Estimada:** 4-5 semanas (160-200 horas de desarrollo)  
**Equipos Recomendados:** 2-3 desarrolladores  
**Entregables Finales:** Sistema funcional con erosión, papelera y 14/14 casos de uso

---

## FASE 0: PREPARACIÓN Y PLANNING (1 semana)

### 0.1 Auditoría Técnica Actual

**Objetivo:** Entender exactamente qué existe y en qué estado está.

#### Tareas:
```
[ ] 0.1.1 - Ejecutar análisis estático de código
    └─ Lines of Code (LOC): Python + JS
    └─ Complejidad ciclomática (CC)
    └─ Cobertura de tests actual
    └─ Dependencias faltantes

[ ] 0.1.2 - Mapear puntos de integración
    └─ Identificar APIs Python existentes
    └─ Identificar llamadas JS → Python
    └─ Diagrama de dependencias actual

[ ] 0.1.3 - Documentar deuda técnica
    └─ Código procedural (no OOP)
    └─ Funciones sin tests
    └─ Duplicación de lógica
    └─ Violaciones de DRY

[ ] 0.1.4 - Crear rama de trabajo
    └─ git checkout -b refactor/architecture-alignment
    └─ Mantener main intacto

[ ] 0.1.5 - Backup de datos
    └─ Copiar data/db.json → backups/db.json.original
    └─ Copiar assets/images/ → backups/images.original
```

**Entregables:**
- Reporte de auditoría (estado_actual.md)
- Diagrama de dependencias actual
- Lista de deuda técnica

---

### 0.2 Preparación del Entorno

**Objetivo:** Instalar todas las dependencias necesarias para la arquitectura completa.

#### Tareas:
```
[ ] 0.2.1 - Crear requirements.txt con dependencias nuevas
    └─ APScheduler==3.10.4  (tareas periódicas)
    └─ Pillow==10.0.0       (procesamiento imágenes)
    └─ bcrypt==4.0.1        (hashing contraseñas)
    └─ python-dotenv==1.0.0 (variables entorno)
    └─ pytest==7.4.0        (testing)
    └─ pytest-cov==4.1.0    (cobertura)

[ ] 0.2.2 - pip install -r requirements.txt

[ ] 0.2.3 - Crear estructura de directorios
    ├── src/
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── core.py          (EcoMemoryAPI)
    │   │   └── handlers.py      (métodos públicos)
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── auth_service.py
    │   │   ├── photo_service.py
    │   │   ├── erosion_service.py
    │   │   ├── trash_service.py
    │   │   ├── dashboard_service.py
    │   │   └── image_processor.py
    │   ├── repositories/
    │   │   ├── __init__.py
    │   │   ├── base_repository.py
    │   │   ├── user_repository.py
    │   │   ├── photo_repository.py
    │   │   ├── trash_repository.py
    │   │   └── stats_repository.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   ├── photo.py
    │   │   ├── trash_item.py
    │   │   └── deletion_record.py
    │   ├── tasks/
    │   │   ├── __init__.py
    │   │   └── scheduler.py     (tareas periódicas)
    │   └── utils/
    │       ├── __init__.py
    │       ├── validators.py
    │       ├── decorators.py
    │       └── logger.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_auth_service.py
    │   ├── test_photo_service.py
    │   ├── test_erosion_service.py
    │   ├── test_trash_service.py
    │   └── test_integration.py
    ├── app.py          (mantener, solo usar nueva API)
    ├── requirements.txt
    ├── .env.example
    └── pytest.ini

[ ] 0.2.4 - Configurar logging
    └─ Crear config/logging.py
    └─ Setup logger global
    └─ Logs a console + file

[ ] 0.2.5 - Crear .gitignore
    └─ __pycache__/
    └─ *.pyc
    └─ .env
    └─ venv/
    └─ dist/
    └─ build/
    └─ .pytest_cache/
    └─ .coverage
```

**Entregables:**
- requirements.txt actualizado
- Estructura de directorios creada
- Variables entorno configuradas
- Logging listo

---

### 0.3 Planificación Detallada

**Objetivo:** Detallar exactamente qué se hace en cada fase.

#### Tareas:
```
[ ] 0.3.1 - Crear timeline Gantt
    └─ Fase 1: Weeks 1-2
    └─ Fase 2: Weeks 2-3
    └─ Fase 3: Weeks 3-4
    └─ Fase 4: Week 4-5
    └─ Testing & Fixes: Week 5-6

[ ] 0.3.2 - Definir criterios de aceptación
    └─ Por cada requerimiento funcional
    └─ Por cada caso de uso
    └─ Por cada servicio

[ ] 0.3.3 - Crear matriz de riesgos
    └─ Riesgos técnicos
    └─ Riesgos de cronograma
    └─ Plan de mitigación

[ ] 0.3.4 - Definir estrategia de testing
    └─ Unit tests para servicios (>80% coverage)
    └─ Integration tests para APIs
    └─ E2E tests para flujos críticos
    └─ Load tests para scheduler

[ ] 0.3.5 - Crear documento de decisiones arquitectónicas
    └─ Por qué OOP vs Procedural
    └─ Por qué Repository Pattern
    └─ Por qué Service Layer
    └─ Por qué APScheduler
```

**Entregables:**
- Timeline detallado (timeline.md)
- Criterios de aceptación (acceptance_criteria.md)
- Matriz de riesgos (risk_matrix.md)
- Estrategia de testing (testing_strategy.md)

---

## FASE 1: ARQUITECTURA FUNDAMENTAL (Weeks 1-2)

### 1.1 Implementar Patrón Repository

**Objetivo:** Crear capa de acceso a datos consistente y testeable.

#### Tareas:

```python
# src/repositories/base_repository.py
[ ] 1.1.1 - Crear clase base abstracta
    class IRepository(ABC):
        @abstractmethod
        def get_all(self) -> list: pass
        
        @abstractmethod
        def get_by_id(self, id: int) -> object: pass
        
        @abstractmethod
        def create(self, data: dict) -> object: pass
        
        @abstractmethod
        def update(self, id: int, data: dict) -> object: pass
        
        @abstractmethod
        def delete(self, id: int) -> bool: pass

# src/repositories/user_repository.py
[ ] 1.1.2 - Implementar UserRepository
    class UserRepository(IRepository):
        - get_all() → list[Usuario]
        - get_by_id(id) → Usuario | None
        - get_by_email(email) → Usuario | None
        - create(nombre, email, pwd_hash) → Usuario
        - update(id, data) → Usuario
        - delete(id) → bool
        - email_exists(email) → bool

# src/repositories/photo_repository.py
[ ] 1.1.3 - Implementar PhotoRepository
    class PhotoRepository(IRepository):
        - get_all_by_user(user_id) → list[Foto]
        - get_active_by_user(user_id) → list[Foto]  (sin papelera)
        - get_by_id(id) → Foto | None
        - create(foto_data) → Foto
        - update(id, data) → Foto
        - update_last_access(id, datetime) → None
        - update_decay_level(id, nivel) → None
        - move_to_trash(id) → None
        - restore_from_trash(id) → None

# src/repositories/trash_repository.py
[ ] 1.1.4 - Implementar TrashRepository
    class TrashRepository(IRepository):
        - get_all_by_user(user_id) → list[Foto]
        - get_trashed(user_id) → list[Foto]
        - get_old_trash(user_id, days=30) → list[Foto]
        - move_to_trash(foto_id, datetime) → None
        - restore_from_trash(foto_id) → None
        - delete_permanently(foto_id) → bool
        - cleanup_old_trash() → int (count deleted)

# src/repositories/stats_repository.py
[ ] 1.1.5 - Implementar StatsRepository
    class StatsRepository(IRepository):
        - get_stats(user_id) → Estadisticas
        - increment_deleted_count() → None
        - add_freed_bytes(bytes) → None
        - update_stats_by_decay_state() → None
        - get_photos_by_decay_level(user_id) → dict
```

#### Testing:
```python
# tests/test_repositories.py
[ ] 1.1.6 - Tests para cada repositorio
    - test_user_repository_get_all()
    - test_user_repository_get_by_email()
    - test_user_repository_email_already_exists()
    - test_photo_repository_get_active_by_user()
    - test_photo_repository_update_last_access()
    - test_trash_repository_move_to_trash()
    - test_trash_repository_cleanup_old_trash()
    └─ Target: >90% coverage
```

**Entregables:**
- 5 implementaciones de Repository
- Tests unitarios (>90% coverage)
- Documentación de interfaces

---

### 1.2 Crear Modelos de Dominio

**Objetivo:** Definir estructuras de datos tipadas y validadas.

#### Tareas:

```python
# src/models/user.py
[ ] 1.2.1 - Crear modelo Usuario
    class Usuario:
        id: int
        nombre: str
        correo: str
        contrasena_hash: str  (bcrypt)
        fecha_registro: datetime
        
        @staticmethod
        def hash_password(pwd: str) -> str:
            return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
        
        def verify_password(self, pwd: str) -> bool:
            return bcrypt.checkpw(pwd.encode(), self.contrasena_hash)
        
        @staticmethod
        def validate_email(email: str) -> bool:
            # RFC 5322 simple check
            return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email))

# src/models/photo.py
[ ] 1.2.2 - Crear modelo Fotografia
    class Fotografia:
        id: int
        usuario_id: int
        nombre: str
        formato_archivo: str  (jpg, png)
        tamano_bytes: int
        ruta_original: str
        nivel_deterioro: float  (0.0-1.0)
        estado_erosion: EstadoErosion  (ENUM)
        fecha_subida: datetime
        fecha_ultimo_acceso: datetime
        en_papelera: bool
        fecha_ingreso_papelera: datetime | None
        
        @property
        def dias_inactividad(self) -> int:
            return (datetime.now() - self.fecha_ultimo_acceso).days
        
        @property
        def porcentaje_deterioro(self) -> int:
            return int(self.nivel_deterioro * 100)

# src/models/trash_item.py
[ ] 1.2.3 - Crear modelo ElementoPapelera
    class ElementoPapelera(Fotografia):
        fecha_ingreso_papelera: datetime
        
        @property
        def dias_en_papelera(self) -> int:
            return (datetime.now() - self.fecha_ingreso_papelera).days
        
        @property
        def debe_eliminarse_automaticamente(self) -> bool:
            return self.dias_en_papelera >= 30

# src/models/deletion_record.py
[ ] 1.2.4 - Crear modelo RegistroEliminacion
    class RegistroEliminacion:
        id: int
        usuario_id: int
        nombre_archivo: str
        tamano_bytes: int
        fecha_eliminacion: datetime
        motivo: str  (ENUM: 'manual', 'automatic_trash_cleanup', 'automatic_erosion')

# src/models/decay_state.py
[ ] 1.2.5 - Crear ENUM EstadoErosion
    class EstadoErosion(Enum):
        DETERIORO_LEVE = "DETERIORO_LEVE"       # <25%
        DETERIORO_MENOR = "DETERIORO_MENOR"     # 25-50%
        DETERIORO_MAYOR = "DETERIORO_MAYOR"     # 50-75%
        DETERIORO_CRITICO = "DETERIORO_CRITICO" # >75%
```

#### Testing:
```python
[ ] 1.2.6 - Tests de modelos
    - test_usuario_hash_password()
    - test_usuario_verify_password_correct()
    - test_usuario_verify_password_incorrect()
    - test_usuario_validate_email_valid()
    - test_usuario_validate_email_invalid()
    - test_fotografia_dias_inactividad()
    - test_elemento_papelera_debe_eliminarse_automaticamente()
    └─ Target: 100% coverage
```

**Entregables:**
- 5 modelos de dominio con validación
- Enums para estados
- Tests exhaustivos (100% coverage)

---

### 1.3 Crear Servicios de Negocio (Parte 1)

**Objetivo:** Implementar lógica de negocio aislada de UI y persistencia.

#### Tareas:

```python
# src/services/auth_service.py
[ ] 1.3.1 - AuthService (mejorado)
    class AuthService:
        def __init__(self, user_repository: UserRepository):
            self.user_repo = user_repository
        
        def registrar_usuario(self, nombre: str, email: str, pwd: str) 
            → (bool, str | Usuario):
            # Validar email no existe
            if self.user_repo.email_exists(email):
                return False, "EMAIL_EXISTS"
            # Validar contraseña
            if not self._validate_password(pwd):
                return False, "INVALID_PASSWORD"
            # Hash y crear
            pwd_hash = Usuario.hash_password(pwd)
            usuario = self.user_repo.create(nombre, email, pwd_hash)
            return True, usuario
        
        def verificar_credenciales(self, email: str, pwd: str) 
            → (bool, Usuario | None):
            usuario = self.user_repo.get_by_email(email)
            if not usuario or not usuario.verify_password(pwd):
                return False, None
            return True, usuario
        
        @staticmethod
        def _validate_password(pwd: str) -> bool:
            # Mín 8 chars, 1 mayúscula, 1 número
            if len(pwd) < 8:
                return False
            if not any(c.isupper() for c in pwd):
                return False
            if not any(c.isdigit() for c in pwd):
                return False
            return True

# src/services/photo_service.py
[ ] 1.3.2 - PhotoService (mejorado)
    class PhotoService:
        def __init__(self, photo_repo: PhotoRepository, 
                     image_processor: ImageProcessor):
            self.photo_repo = photo_repo
            self.image_processor = image_processor
        
        def subir_fotografia(self, usuario_id: int, ruta_original: str, 
                            nombre: str) → (bool, Fotografia | str):
            # Validar formato
            if not self._is_valid_format(nombre):
                return False, "INVALID_FORMAT"
            # Copiar archivo
            nombre_unico = self._generate_unique_name(nombre)
            dest_path = self._copy_file(ruta_original, nombre_unico)
            # Crear registro
            foto = Fotografia(
                usuario_id=usuario_id,
                nombre=nombre_unico,
                formato_archivo=self._get_extension(nombre),
                tamano_bytes=os.path.getsize(dest_path),
                ruta_original=f"assets/images/{nombre_unico}",
                nivel_deterioro=random.random(),
                estado_erosion=EstadoErosion.DETERIORO_LEVE,
                fecha_subida=datetime.now(),
                fecha_ultimo_acceso=datetime.now(),
                en_papelera=False,
                fecha_ingreso_papelera=None
            )
            saved = self.photo_repo.create(foto)
            return True, saved
        
        def obtener_fotos_usuario(self, usuario_id: int) 
            → list[Fotografia]:
            return self.photo_repo.get_active_by_user(usuario_id)
        
        def acceder_fotografia(self, foto_id: int) 
            → (bool, Fotografia | str):
            foto = self.photo_repo.get_by_id(foto_id)
            if not foto:
                return False, "NOT_FOUND"
            # Actualizar fecha acceso
            self.photo_repo.update_last_access(foto_id, datetime.now())
            # Si estaba deteriorada, restaurar
            if foto.nivel_deterioro > 0:
                foto.nivel_deterioro = 0
                foto.estado_erosion = EstadoErosion.DETERIORO_LEVE
                self.photo_repo.update(foto_id, {
                    'nivel_deterioro': 0,
                    'estado_erosion': EstadoErosion.DETERIORO_LEVE,
                    'fecha_ultimo_acceso': datetime.now()
                })
            return True, foto
        
        @staticmethod
        def _is_valid_format(filename: str) -> bool:
            ext = os.path.splitext(filename)[1].lower()
            return ext in {'.jpg', '.jpeg', '.png'}
```

#### Testing:
```python
[ ] 1.3.3 - Tests de servicios
    - test_auth_service_registrar_usuario_success()
    - test_auth_service_registrar_usuario_email_exists()
    - test_auth_service_verificar_credenciales_correct()
    - test_auth_service_verificar_credenciales_incorrect()
    - test_photo_service_subir_fotografia()
    - test_photo_service_obtener_fotos_usuario()
    - test_photo_service_acceder_fotografia_restaura_calidad()
    └─ Target: >85% coverage
```

**Entregables:**
- AuthService mejorado con validación
- PhotoService refactorizado
- Tests de servicios

---

### 1.4 Actualizar api.py para Usar Nueva Arquitectura

**Objetivo:** Mantener API PyWebView pero usar nuevos servicios.

#### Tareas:

```python
# src/api/core.py (nuevo nombre de api.py)
[ ] 1.4.1 - Refactorizar EcoMemoryAPI
    class EcoMemoryAPI:
        def __init__(self, base_dir: str):
            self.base_dir = base_dir
            # Inyectar repositorios
            self.user_repo = UserRepository(base_dir)
            self.photo_repo = PhotoRepository(base_dir)
            self.trash_repo = TrashRepository(base_dir)
            self.stats_repo = StatsRepository(base_dir)
            # Inyectar servicios
            self.auth_service = AuthService(self.user_repo)
            self.photo_service = PhotoService(
                self.photo_repo, 
                ImageProcessor(base_dir)
            )
            # Scheduler (iniciar en próxima fase)
            self.scheduler = None
        
        # MÉTODOS PÚBLICOS (API)
        def get_db(self) -> dict:
            """Retorna snapshot completo de BD (solo para compatibility)"""
            return {
                'usuarios': self.user_repo.get_all(),
                'fotografias': self.photo_repo.get_all(),
                'registrosEliminacion': self.stats_repo.get_deletion_records(),
                'estadisticas': self.stats_repo.get_stats()
            }
        
        def register_user(self, nombre: str, correo: str, 
                         contrasena: str) → dict:
            """CU01: Registrar usuario"""
            success, result = self.auth_service.registrar_usuario(
                nombre, correo, contrasena
            )
            if success:
                return {'success': True}
            else:
                return {'success': False, 'error': result}
        
        def login(self, correo: str, contrasena: str) → dict:
            """CU02: Iniciar sesión"""
            success, usuario = self.auth_service.verificar_credenciales(
                correo, contrasena
            )
            if success:
                return {
                    'success': True,
                    'usuario': {
                        'id': usuario.id,
                        'nombre': usuario.nombre,
                        'correo': usuario.correo
                    }
                }
            else:
                return {'success': False, 'error': 'INVALID_CREDENTIALS'}
        
        def pick_and_upload(self, usuario_id: int) → dict:
            """CU03: Subir fotografía"""
            rutas = webview.windows[0].create_file_dialog(
                webview.FileDialog.OPEN,
                allow_multiple=True,
                file_types=('Imágenes (*.jpg;*.jpeg;*.png)', 
                           'Todos los archivos (*.*)')
            )
            if not rutas:
                return {'success': True, 'fotos': []}
            
            nuevas_fotos = []
            for ruta in rutas:
                success, result = self.photo_service.subir_fotografia(
                    usuario_id, ruta, os.path.basename(ruta)
                )
                if success:
                    nuevas_fotos.append(result.to_dict())
            
            return {'success': True, 'fotos': nuevas_fotos}

[ ] 1.4.2 - Mantener compatibilidad con JS existente
    └─ Los métodos públicos mantienen misma firma
    └─ Retornos mantienen mismo formato
    └─ Sin breaking changes en API
```

**Entregables:**
- EcoMemoryAPI refactorizada
- Inyección de dependencias funcional
- Tests de API (>80% coverage)

**Checkpoints:**
```
✅ Fase 1 completada cuando:
  - [ ] 5 repositorios implementados + tests
  - [ ] 5 modelos con validación + tests
  - [ ] AuthService + PhotoService refactorizados
  - [ ] EcoMemoryAPI usa nuevos servicios
  - [ ] Tests totales >80% coverage
  - [ ] Código funciona en `app.py` sin cambios
  - [ ] Todos los commits en rama `refactor/architecture-alignment`
```

---

## FASE 2: MOTOR DE EROSIÓN (Weeks 2-3)

### 2.1 Implementar ErosionService

**Objetivo:** Crear servicio que calcule y aplique deterioro digital.

#### Tareas:

```python
# src/services/erosion_service.py
[ ] 2.1.1 - Crear clase ErosionService
    class ErosionService:
        UMBRALES = {
            0.25: EstadoErosion.DETERIORO_LEVE,
            0.50: EstadoErosion.DETERIORO_MENOR,
            0.75: EstadoErosion.DETERIORO_MAYOR,
            1.00: EstadoErosion.DETERIORO_CRITICO
        }
        
        def __init__(self, photo_repo: PhotoRepository, 
                     image_processor: ImageProcessor):
            self.photo_repo = photo_repo
            self.image_processor = image_processor
        
        def calcular_nivel_deterioro(self, foto: Fotografia) 
            → float:
            """
            Calcula nivel deterioro basado en:
            - Días sin acceso (factor principal)
            - Fórmula: min(1.0, dias_inactividad / 180)
            Alternativa: random() para MVP
            """
            dias = foto.dias_inactividad
            # Escala lineal: 180 días = 100% deterioro
            nivel = min(1.0, dias / 180.0)
            return nivel
        
        def determinar_estado_erosion(self, nivel: float) 
            → EstadoErosion:
            """Mapea nivel (0.0-1.0) a estado de erosión"""
            if nivel < 0.25:
                return EstadoErosion.DETERIORO_LEVE
            elif nivel < 0.50:
                return EstadoErosion.DETERIORO_MENOR
            elif nivel < 0.75:
                return EstadoErosion.DETERIORO_MAYOR
            else:
                return EstadoErosion.DETERIORO_CRITICO
        
        def aplicar_deterioro_automatico(self, usuario_id: int) 
            → list[Fotografia]:
            """
            CU06: Aplica deterioro a todas las fotos activas
            Llamado por task periódica cada hora
            """
            fotos = self.photo_repo.get_active_by_user(usuario_id)
            fotos_actualizadas = []
            
            for foto in fotos:
                nivel_nuevo = self.calcular_nivel_deterioro(foto)
                estado_nuevo = self.determinar_estado_erosion(nivel_nuevo)
                
                # Generar versión degradada
                if nivel_nuevo > 0:
                    self.image_processor.generar_version_degradada(
                        foto.ruta_original, 
                        nivel_nuevo
                    )
                
                # Actualizar en BD
                self.photo_repo.update(foto.id, {
                    'nivel_deterioro': nivel_nuevo,
                    'estado_erosion': estado_nuevo
                })
                
                # Si supera umbral crítico, enviar a papelera
                if estado_nuevo == EstadoErosion.DETERIORO_CRITICO:
                    self.photo_repo.move_to_trash(
                        foto.id, 
                        datetime.now()
                    )
                
                fotos_actualizadas.append(foto)
            
            return fotos_actualizadas
        
        def restaurar_calidad_original(self, foto_id: int) 
            → bool:
            """
            CU05: Restaura foto a calidad original
            Cuando usuario la abre individualmente
            """
            foto = self.photo_repo.get_by_id(foto_id)
            if not foto:
                return False
            
            # Resetear a cero
            self.photo_repo.update(foto_id, {
                'nivel_deterioro': 0.0,
                'estado_erosion': EstadoErosion.DETERIORO_LEVE,
                'fecha_ultimo_acceso': datetime.now()
            })
            
            # Eliminar versión degradada si existe
            self.image_processor.eliminar_version_degradada(foto.ruta_original)
            
            return True
        
        def supera_umbral_critico(self, nivel: float) → bool:
            """Verifica si foto debe ir a papelera automáticamente"""
            return nivel > 0.75

[ ] 2.1.2 - Crear ImageProcessor
    # src/services/image_processor.py
    class ImageProcessor:
        def __init__(self, base_dir: str):
            self.base_dir = base_dir
            self.degraded_dir = os.path.join(base_dir, 'assets/degraded')
            os.makedirs(self.degraded_dir, exist_ok=True)
        
        def generar_version_degradada(self, ruta_original: str, 
                                      nivel: float) → str:
            """
            Genera versión degradada manteniendo original
            Modificaciones:
            - Reduce resolución: 100% - (nivel * 70%)
            - Reduce saturación: 100% - (nivel * 80%)
            - Añade ruido: nivel * 30
            """
            from PIL import Image, ImageEnhance
            import numpy as np
            
            # Abrir imagen original
            img = Image.open(ruta_original)
            
            # Reducir resolución
            nuevo_ancho = int(img.width * (1 - nivel * 0.7))
            nuevo_alto = int(img.height * (1 - nivel * 0.7))
            img_small = img.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)
            img_rescaled = img_small.resize((img.width, img.height), 
                                           Image.LANCZOS)
            
            # Reducir saturación
            enhancer = ImageEnhance.Color(img_rescaled)
            img_desaturated = enhancer.enhance(1 - nivel * 0.8)
            
            # Añadir ruido
            if nivel * 30 > 0:
                img_array = np.array(img_desaturated, dtype=np.float32)
                noise = np.random.normal(0, nivel * 30, img_array.shape)
                img_array = np.clip(img_array + noise, 0, 255)
                img_noisy = Image.fromarray(np.uint8(img_array))
            else:
                img_noisy = img_desaturated
            
            # Guardar con nombre unique
            basename = os.path.splitext(
                os.path.basename(ruta_original)
            )[0]
            degraded_name = f"{basename}_degraded_{int(nivel*100)}.png"
            degraded_path = os.path.join(self.degraded_dir, degraded_name)
            
            img_noisy.save(degraded_path, "PNG")
            return degraded_path
        
        def obtener_version_apropiada(self, ruta_original: str, 
                                      nivel: float) → str:
            """
            Retorna ruta de versión degradada si existe,
            sino retorna original
            """
            if nivel == 0:
                return ruta_original
            
            basename = os.path.splitext(
                os.path.basename(ruta_original)
            )[0]
            degraded_name = f"{basename}_degraded_{int(nivel*100)}.png"
            degraded_path = os.path.join(self.degraded_dir, degraded_name)
            
            if os.path.exists(degraded_path):
                return degraded_path
            
            return ruta_original
        
        def eliminar_version_degradada(self, ruta_original: str) 
            → bool:
            """Elimina archivo degradado cuando se restaura"""
            basename = os.path.splitext(
                os.path.basename(ruta_original)
            )[0]
            # Eliminar todos los .png degradados
            for entry in os.listdir(self.degraded_dir):
                if entry.startswith(basename) and entry.endswith('.png'):
                    try:
                        os.remove(os.path.join(self.degraded_dir, entry))
                    except:
                        pass
            return True
```

#### Testing:
```python
# tests/test_erosion_service.py
[ ] 2.1.3 - Tests de ErosionService
    - test_calcular_nivel_deterioro_0_dias()
    - test_calcular_nivel_deterioro_90_dias()
    - test_calcular_nivel_deterioro_180_dias()
    - test_calcular_nivel_deterioro_max_100()
    - test_determinar_estado_erosion_leve()
    - test_determinar_estado_erosion_menor()
    - test_determinar_estado_erosion_mayor()
    - test_determinar_estado_erosion_critico()
    - test_aplicar_deterioro_automatico()
    - test_restaurar_calidad_original()
    - test_supera_umbral_critico()
    - test_image_processor_generar_version_degradada()
    - test_image_processor_obtener_version_apropiada()
    └─ Target: >85% coverage
```

**Entregables:**
- ErosionService completo
- ImageProcessor funcional
- Tests >85% coverage

---

### 2.2 Implementar Scheduler de Tareas Periódicas

**Objetivo:** Crear sistema que ejecute tareas automáticamente.

#### Tareas:

```python
# src/tasks/scheduler.py
[ ] 2.2.1 - Crear gestor de tareas
    from apscheduler.schedulers.background import BackgroundScheduler
    
    class TaskScheduler:
        def __init__(self, api_instance):
            self.api = api_instance
            self.scheduler = BackgroundScheduler()
            self.is_running = False
        
        def start(self):
            """Inicia todas las tareas periódicas"""
            if self.is_running:
                return
            
            # Tarea 1: Aplicar deterioro automático (cada hora)
            self.scheduler.add_job(
                self._apply_decay_all_users,
                'interval',
                hours=1,
                id='apply_decay',
                name='Aplicar deterioro digital',
                replace_existing=True
            )
            
            # Tarea 2: Limpiar papelera (cada 6 horas)
            self.scheduler.add_job(
                self._cleanup_old_trash,
                'interval',
                hours=6,
                id='cleanup_trash',
                name='Limpiar papelera antigua',
                replace_existing=True
            )
            
            # Tarea 3: Actualizar estadísticas (cada 12 horas)
            self.scheduler.add_job(
                self._update_statistics,
                'interval',
                hours=12,
                id='update_stats',
                name='Actualizar estadísticas',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Task scheduler iniciado")
        
        def stop(self):
            """Detiene todas las tareas"""
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Task scheduler detenido")
        
        def _apply_decay_all_users(self):
            """Tarea: Aplicar deterioro a todos los usuarios"""
            try:
                logger.info("Iniciando aplicación de deterioro...")
                usuarios = self.api.user_repo.get_all()
                
                for usuario in usuarios:
                    self.api.erosion_service.aplicar_deterioro_automatico(
                        usuario.id
                    )
                    logger.info(f"Deterioro aplicado para usuario {usuario.id}")
                
                logger.info("Deterioro aplicado a todos los usuarios")
            except Exception as e:
                logger.error(f"Error aplicando deterioro: {e}")
        
        def _cleanup_old_trash(self):
            """Tarea: Eliminar items de papelera >30 días"""
            try:
                logger.info("Iniciando limpieza de papelera...")
                usuarios = self.api.user_repo.get_all()
                
                for usuario in usuarios:
                    self.api.trash_service.eliminar_papelera_antigua(
                        usuario.id
                    )
                    logger.info(f"Papelera limpiada para usuario {usuario.id}")
                
                logger.info("Papelera limpiada para todos los usuarios")
            except Exception as e:
                logger.error(f"Error limpiando papelera: {e}")
        
        def _update_statistics(self):
            """Tarea: Actualizar estadísticas globales"""
            try:
                logger.info("Actualizando estadísticas...")
                usuarios = self.api.user_repo.get_all()
                
                for usuario in usuarios:
                    self.api.dashboard_service.recalcular_estadisticas(
                        usuario.id
                    )
                    logger.info(f"Estadísticas actualizadas para usuario {usuario.id}")
                
                logger.info("Estadísticas actualizadas")
            except Exception as e:
                logger.error(f"Error actualizando estadísticas: {e}")

[ ] 2.2.2 - Integrar en app.py
    # En app.py
    if __name__ == '__main__':
        base_dir = os.path.dirname(os.path.abspath(__file__))
        api = EcoMemoryAPI(base_dir)
        
        # Iniciar scheduler
        scheduler = TaskScheduler(api)
        scheduler.start()
        
        # Crear ventana PyWebView
        window = webview.create_window(
            title='EcoMemory',
            url=os.path.join(base_dir, 'index.html'),
            js_api=api,
            width=1280,
            height=800,
            min_size=(800, 600),
            resizable=True,
        )
        
        try:
            webview.start(debug=False)
        finally:
            # Detener scheduler al cerrar
            scheduler.stop()
```

#### Testing:
```python
# tests/test_scheduler.py
[ ] 2.2.3 - Tests de scheduler
    - test_scheduler_start_stops()
    - test_scheduler_decay_task_executes()
    - test_scheduler_cleanup_task_executes()
    - test_scheduler_stats_task_executes()
    - test_scheduler_handles_exceptions()
    └─ Target: >80% coverage (sin mock de tiempo real)
```

**Entregables:**
- Scheduler funcional
- 3 tareas periódicas configuradas
- Logging de tareas
- Tests >80% coverage

---

### 2.3 Actualizar API para Exponer ErosionService

**Objetivo:** Exponer métodos de erosión vía PyWebView API.

#### Tareas:

```python
# En src/api/core.py (EcoMemoryAPI)
[ ] 2.3.1 - Agregar métodos públicos para erosión
    class EcoMemoryAPI:
        # ... código anterior ...
        
        def get_foto_individual(self, foto_id: int) → dict:
            """CU05: Obtener foto individual y restaurar calidad"""
            success, foto = self.photo_service.acceder_fotografia(foto_id)
            
            if success:
                # Restaurar calidad si es necesario
                if foto.nivel_deterioro > 0:
                    self.erosion_service.restaurar_calidad_original(foto_id)
                
                return {
                    'success': True,
                    'foto': {
                        'id': foto.id,
                        'nombre': foto.nombre,
                        'rutaOriginal': foto.ruta_original,
                        'nivelDeterioro': foto.nivel_deterioro,
                        'estadoErosion': foto.estado_erosion.value,
                        'fechaSubida': foto.fecha_subida.isoformat(),
                        'fechaUltimoAcceso': foto.fecha_ultimo_acceso.isoformat(),
                        'diasInactividad': foto.dias_inactividad,
                        'porcentajeDeterioro': foto.porcentaje_deterioro
                    }
                }
            else:
                return {'success': False, 'error': result}
        
        def get_galeria(self, usuario_id: int) → dict:
            """CU04: Obtener galería con estado de erosión"""
            fotos = self.photo_service.obtener_fotos_usuario(usuario_id)
            
            return {
                'success': True,
                'fotos': [
                    {
                        'id': f.id,
                        'nombre': f.nombre,
                        'rutaOriginal': f.ruta_original,
                        'nivelDeterioro': f.nivel_deterioro,
                        'estadoErosion': f.estado_erosion.value,
                        'porcentajeDeterioro': f.porcentaje_deterioro,
                        'tamanoBytes': f.tamano_bytes,
                        'diasInactividad': f.dias_inactividad
                    }
                    for f in fotos
                ]
            }
        
        def get_estado_erosion(self, foto_id: int) → dict:
            """CU07: Consultar estado de erosión detallado"""
            foto = self.photo_repo.get_by_id(foto_id)
            
            if not foto:
                return {'success': False, 'error': 'NOT_FOUND'}
            
            return {
                'success': True,
                'erosion': {
                    'fotoId': foto.id,
                    'nivelDeterioro': foto.nivel_deterioro,
                    'porcentajeDeterioro': foto.porcentaje_deterioro,
                    'estadoErosion': foto.estado_erosion.value,
                    'diasInactividad': foto.dias_inactividad,
                    'diasHastaSiguienteNivel': self._calcular_dias_siguiente_nivel(foto),
                    'enPapelera': foto.en_papelera,
                    'fechaUltimoAcceso': foto.fecha_ultimo_acceso.isoformat()
                }
            }
        
        def _calcular_dias_siguiente_nivel(self, foto: Fotografia) 
            → int:
            """Calcula cuántos días hasta siguiente nivel de deterioro"""
            # Función auxiliar
            pass
```

**Entregables:**
- 4 métodos nuevos en API
- Mantenimiento de compatibilidad
- Tests de API >80% coverage

**Checkpoints:**
```
✅ Fase 2 completada cuando:
  - [ ] ErosionService implementado + tests
  - [ ] ImageProcessor funcional + tests
  - [ ] Scheduler activo con 3 tareas
  - [ ] API expone métodos de erosión
  - [ ] Tests totales >80% coverage
  - [ ] Deterioro se calcula automáticamente
  - [ ] Imágenes se degradan visualmente
```

---

## FASE 3: PAPELERA Y CICLO DE VIDA (Week 3-4)

### 3.1 Implementar TrashService

**Objetivo:** Gestionar papelera y eliminación de fotos.

#### Tareas:

```python
# src/services/trash_service.py
[ ] 3.1.1 - Crear TrashService
    class TrashService:
        def __init__(self, photo_repo: PhotoRepository,
                     trash_repo: TrashRepository,
                     stats_repo: StatsRepository):
            self.photo_repo = photo_repo
            self.trash_repo = trash_repo
            self.stats_repo = stats_repo
        
        def enviar_a_papelera_manual(self, foto_id: int, usuario_id: int) 
            → (bool, str):
            """CU09: Enviar a papelera manualmente desde galería"""
            foto = self.photo_repo.get_by_id(foto_id)
            
            # Validar que pertenece al usuario
            if not foto or foto.usuario_id != usuario_id:
                return False, "NOT_FOUND"
            
            # Validar que no esté ya en papelera
            if foto.en_papelera:
                return False, "ALREADY_IN_TRASH"
            
            # Mover a papelera
            self.photo_repo.move_to_trash(foto_id, datetime.now())
            
            return True, "OK"
        
        def enviar_a_papelera_automatico(self, foto_id: int) 
            → (bool, str):
            """CU10: Enviar a papelera automáticamente (después deterioro crítico)"""
            return self._mover_a_papelera_interno(foto_id, 
                                                  'automatic_erosion')
        
        def visualizar_papelera(self, usuario_id: int) → list[Fotografia]:
            """CU11: Obtener fotos en papelera"""
            return self.trash_repo.get_all_by_user(usuario_id)
        
        def restaurar_desde_papelera(self, foto_id: int, usuario_id: int) 
            → (bool, str):
            """CU12: Restaurar foto desde papelera a galería activa"""
            foto = self.photo_repo.get_by_id(foto_id)
            
            if not foto or foto.usuario_id != usuario_id:
                return False, "NOT_FOUND"
            
            if not foto.en_papelera:
                return False, "NOT_IN_TRASH"
            
            # Restaurar a estado original
            self.photo_repo.restore_from_trash(foto_id)
            # Limpiar degradación
            # ...
            
            return True, "OK"
        
        def eliminar_definitivamente_manual(self, foto_id: int, 
                                           usuario_id: int) 
            → (bool, str):
            """CU13: Eliminar definitivamente (manual desde papelera)"""
            foto = self.photo_repo.get_by_id(foto_id)
            
            if not foto or foto.usuario_id != usuario_id:
                return False, "NOT_FOUND"
            
            if not foto.en_papelera:
                return False, "NOT_IN_TRASH"
            
            return self._eliminar_definitivamente_interno(
                foto_id, 
                'manual'
            )
        
        def eliminar_papelera_antigua(self, usuario_id: int) 
            → int:
            """CU14: Eliminar automáticamente fotos >30 días en papelera"""
            fotos_antiguas = self.trash_repo.get_old_trash(usuario_id, 30)
            count = 0
            
            for foto in fotos_antiguas:
                success, _ = self._eliminar_definitivamente_interno(
                    foto.id,
                    'automatic_trash_cleanup'
                )
                if success:
                    count += 1
            
            return count
        
        def _eliminar_definitivamente_interno(self, foto_id: int, 
                                              motivo: str) 
            → (bool, str):
            """Helper: elimina archivo físico y registro"""
            foto = self.photo_repo.get_by_id(foto_id)
            
            if not foto:
                return False, "NOT_FOUND"
            
            try:
                # Eliminar archivo físico
                ruta = os.path.join(
                    self.base_dir, 
                    foto.ruta_original
                )
                if os.path.exists(ruta):
                    os.remove(ruta)
                
                # Registrar eliminación
                registro = RegistroEliminacion(
                    usuario_id=foto.usuario_id,
                    nombre_archivo=foto.nombre,
                    tamano_bytes=foto.tamano_bytes,
                    fecha_eliminacion=datetime.now(),
                    motivo=motivo
                )
                self.stats_repo.crear_registro_eliminacion(registro)
                
                # Actualizar estadísticas
                self.stats_repo.add_freed_bytes(foto.tamano_bytes)
                self.stats_repo.increment_deleted_count()
                
                # Eliminar de BD
                self.photo_repo.delete(foto_id)
                
                return True, "OK"
            
            except Exception as e:
                logger.error(f"Error eliminando foto {foto_id}: {e}")
                return False, str(e)
        
        def _mover_a_papelera_interno(self, foto_id: int, 
                                      motivo: str) 
            → (bool, str):
            """Helper: mover a papelera"""
            foto = self.photo_repo.get_by_id(foto_id)
            
            if not foto:
                return False, "NOT_FOUND"
            
            if foto.en_papelera:
                return False, "ALREADY_IN_TRASH"
            
            self.photo_repo.move_to_trash(foto_id, datetime.now())
            return True, "OK"
```

#### Testing:
```python
[ ] 3.1.2 - Tests de TrashService
    - test_enviar_a_papelera_manual()
    - test_enviar_a_papelera_ya_existe()
    - test_visualizar_papelera()
    - test_restaurar_desde_papelera()
    - test_restaurar_no_en_papelera()
    - test_eliminar_definitivamente_manual()
    - test_eliminar_papelera_antigua()
    - test_registra_eliminacion_en_bd()
    - test_actualiza_estadisticas()
    └─ Target: >85% coverage
```

**Entregables:**
- TrashService completo
- Lógica de ciclo de vida funcional
- Historial de eliminaciones registrado
- Tests >85% coverage

---

### 3.2 Actualizar API para Exponer TrashService

**Objetivo:** Exponer métodos de papelera vía API.

#### Tareas:

```python
# En src/api/core.py
[ ] 3.2.1 - Agregar métodos públicos para papelera
    class EcoMemoryAPI:
        def move_to_trash(self, foto_id: int, usuario_id: int) 
            → dict:
            """CU09: Enviar a papelera (manual)"""
            success, msg = self.trash_service.enviar_a_papelera_manual(
                foto_id, usuario_id
            )
            
            return {
                'success': success,
                'error': msg if not success else None
            }
        
        def get_papelera(self, usuario_id: int) → dict:
            """CU11: Visualizar papelera"""
            fotos = self.trash_service.visualizar_papelera(usuario_id)
            
            return {
                'success': True,
                'fotos': [
                    {
                        'id': f.id,
                        'nombre': f.nombre,
                        'diasEnPapelera': f.dias_en_papelera,
                        'debe_eliminarse_automaticamente': 
                            f.debe_eliminarse_automaticamente
                    }
                    for f in fotos
                ]
            }
        
        def restore_from_trash(self, foto_id: int, usuario_id: int) 
            → dict:
            """CU12: Restaurar desde papelera"""
            success, msg = self.trash_service.restaurar_desde_papelera(
                foto_id, usuario_id
            )
            
            return {
                'success': success,
                'error': msg if not success else None
            }
        
        def delete_permanently(self, foto_id: int, usuario_id: int) 
            → dict:
            """CU13: Eliminar definitivamente (manual)"""
            success, msg = self.trash_service.eliminar_definitivamente_manual(
                foto_id, usuario_id
            )
            
            return {
                'success': success,
                'error': msg if not success else None
            }
```

**Entregables:**
- 4 métodos nuevos en API
- Tests >80% coverage

---

### 3.3 Actualizar Frontend para Soportar Papelera

**Objetivo:** Crear interfaz para visualizar y gestionar papelera.

#### Tareas:

```
[ ] 3.3.1 - Crear papelera.html
    - Lista de fotos en papelera
    - Mostrar días en papelera
    - Botones: Restaurar, Eliminar Definitivamente
    - Indicador: "Se eliminará en X días si no actúas"

[ ] 3.3.2 - Crear js/trash.js
    - Module para interacción con papelera
    - Funciones:
        ├─ loadTrash(usuarioId)
        ├─ restorePhoto(fotoId)
        ├─ deleteForever(fotoId)
        └─ updateTrashUI()

[ ] 3.3.3 - Actualizar gallery.html
    - Agregar botón "Ir a papelera"
    - Agregar botón "Eliminar" en cada foto (no borrar, enviar a papelera)
    - Mostrar indicador si foto está en papelera

[ ] 3.3.4 - Actualizar js/gallery.js
    - Agregar evento click para botón eliminar
    - Llamar move_to_trash() vía API
    - Actualizar UI tras acción
```

**Entregables:**
- papelera.html funcional
- js/trash.js con lógica
- Integración con gallery.html
- Tests E2E

**Checkpoints:**
```
✅ Fase 3 completada cuando:
  - [ ] TrashService implementado + tests
  - [ ] API expone métodos de papelera
  - [ ] papelera.html funcional
  - [ ] Usuarios pueden mover/restaurar/eliminar
  - [ ] Historial registra eliminaciones
  - [ ] Eliminación automática funciona
  - [ ] Tests totales >80% coverage
```

---

## FASE 4: DASHBOARD Y MÉTRICAS (Week 4)

### 4.1 Implementar DashboardService

**Objetivo:** Crear servicio que calcule y mantenga estadísticas actualizadas.

#### Tareas:

```python
# src/services/dashboard_service.py
[ ] 4.1.1 - Crear DashboardService
    class DashboardService:
        def __init__(self, photo_repo: PhotoRepository,
                     stats_repo: StatsRepository):
            self.photo_repo = photo_repo
            self.stats_repo = stats_repo
        
        def get_metricas_globales(self, usuario_id: int) → dict:
            """CU08: Obtener estadísticas del panel"""
            fotos_activas = self.photo_repo.get_active_by_user(usuario_id)
            
            # Contar por estado
            conteos = {
                EstadoErosion.DETERIORO_LEVE: 0,
                EstadoErosion.DETERIORO_MENOR: 0,
                EstadoErosion.DETERIORO_MAYOR: 0,
                EstadoErosion.DETERIORO_CRITICO: 0
            }
            
            for foto in fotos_activas:
                conteos[foto.estado_erosion] += 1
            
            stats = self.stats_repo.get_stats(usuario_id)
            
            return {
                'totalFotosActivas': len(fotos_activas),
                'totalFotosEliminadas': stats.totalEliminadasSistema,
                'totalBytesLiberados': stats.bytesLiberados,
                'fotosEnEstadoLeve': conteos[EstadoErosion.DETERIORO_LEVE],
                'fotosEnEstadoMenor': conteos[EstadoErosion.DETERIORO_MENOR],
                'fotosEnEstadoMayor': conteos[EstadoErosion.DETERIORO_MAYOR],
                'fotosEnEstadoCritico': conteos[EstadoErosion.DETERIORO_CRITICO],
                'promedioDiasAntesDeErosion': 
                    self._calcular_promedio_inactividad(fotos_activas)
            }
        
        def recalcular_estadisticas(self, usuario_id: int) → dict:
            """
            Recalcula todas las estadísticas
            Llamado por task periódica
            """
            fotos_activas = self.photo_repo.get_active_by_user(usuario_id)
            
            conteos = {}
            total_dias = 0
            
            for foto in fotos_activas:
                estado = foto.estado_erosion
                conteos[estado] = conteos.get(estado, 0) + 1
                total_dias += foto.dias_inactividad
            
            # Actualizar BD
            self.stats_repo.update_stats_by_decay_state(
                usuario_id, conteos
            )
            
            return self.get_metricas_globales(usuario_id)
        
        def _calcular_promedio_inactividad(self, fotos: list[Fotografia]) 
            → float:
            """Promedio de días sin acceso"""
            if not fotos:
                return 0.0
            
            total = sum(f.dias_inactividad for f in fotos)
            return total / len(fotos)

[ ] 4.1.2 - Actualizar StatsRepository
    class StatsRepository(IRepository):
        # ... métodos anteriores ...
        
        def get_stats(self, usuario_id: int) 
            → dict:
            """Obtiene estadísticas actuales del usuario"""
            db = self._read_db()
            stats = db.get('estadisticas', {})
            return stats.get(str(usuario_id), {
                'totalEliminadasSistema': 0,
                'bytesLiberados': 0,
                'fotosPorEstado': {}
            })
        
        def increment_deleted_count(self, usuario_id: int) → None:
            """Incrementa contador de fotos eliminadas"""
            db = self._read_db()
            stats = db.get('estadisticas', {})
            user_stats = stats.get(str(usuario_id), {
                'totalEliminadasSistema': 0,
                'bytesLiberados': 0
            })
            user_stats['totalEliminadasSistema'] += 1
            stats[str(usuario_id)] = user_stats
            db['estadisticas'] = stats
            self._write_db(db)
        
        def add_freed_bytes(self, usuario_id: int, bytes: int) 
            → None:
            """Agrega bytes a contador de liberados"""
            db = self._read_db()
            stats = db.get('estadisticas', {})
            user_stats = stats.get(str(usuario_id), {
                'totalEliminadasSistema': 0,
                'bytesLiberados': 0
            })
            user_stats['bytesLiberados'] += bytes
            stats[str(usuario_id)] = user_stats
            db['estadisticas'] = stats
            self._write_db(db)
        
        def crear_registro_eliminacion(self, 
                                       registro: RegistroEliminacion) 
            → None:
            """Crea registro de eliminación"""
            db = self._read_db()
            registros = db.get('registrosEliminacion', [])
            registros.append({
                'id': registro.id,
                'usuarioId': registro.usuario_id,
                'nombreArchivo': registro.nombre_archivo,
                'tamanoBytes': registro.tamano_bytes,
                'fechaEliminacion': 
                    registro.fecha_eliminacion.isoformat(),
                'motivo': registro.motivo
            })
            db['registrosEliminacion'] = registros
            self._write_db(db)
```

#### Testing:
```python
[ ] 4.1.3 - Tests de DashboardService
    - test_get_metricas_globales_sin_fotos()
    - test_get_metricas_globales_con_fotos()
    - test_get_metricas_globales_cuenta_correctamente()
    - test_recalcular_estadisticas()
    - test_calcula_promedio_inactividad()
    └─ Target: >85% coverage
```

**Entregables:**
- DashboardService completo
- StatsRepository mejorado
- Tests >85% coverage

---

### 4.2 Actualizar API para Exponer DashboardService

**Objetivo:** Exponer métricas vía API.

#### Tareas:

```python
# En src/api/core.py
[ ] 4.2.1 - Agregar métodos públicos para dashboard
    class EcoMemoryAPI:
        def get_dashboard(self, usuario_id: int) → dict:
            """CU08: Obtener estadísticas panel"""
            metricas = self.dashboard_service.get_metricas_globales(
                usuario_id
            )
            
            return {
                'success': True,
                'metricas': metricas
            }
```

---

### 4.3 Actualizar Frontend para Dashboard

**Objetivo:** Mostrar métricas en tiempo real.

#### Tareas:

```
[ ] 4.3.1 - Actualizar gallery.html
    - Agregar panel lateral con estadísticas
    - Cards para:
        ├─ Fotos eliminadas
        ├─ Bytes liberados
        ├─ Conteos por estado
        └─ Promedio inactividad

[ ] 4.3.2 - Actualizar js/dashboard.js
    - Cargar métricas del servidor
    - Actualizar en tiempo real
    - Formatear bytes a GB
    - Mostrar gráficos (opcional)
```

**Entregables:**
- Dashboard actualizado
- Métricas en tiempo real
- UI mejorada

**Checkpoints:**
```
✅ Fase 4 completada cuando:
  - [ ] DashboardService implementado
  - [ ] API expone estadísticas
  - [ ] Dashboard muestra métricas actualizadas
  - [ ] Usuarios ven impacto de sus acciones
  - [ ] Tests >85% coverage
```

---

## FASE 5: SEGURIDAD Y TESTING (Week 4-5)

### 5.1 Implementar Bcrypt para Contraseñas

**Objetivo:** Usar hashing seguro en lugar de plaintext.

#### Tareas:

```python
[ ] 5.1.1 - Actualizar AuthService
    # Ya hecho en Fase 1 (refactoring)
    # Solo verificar:
    ├─ Hash en registrar_usuario()
    ├─ Verify en verificar_credenciales()
    └─ Rehash de db.json existente

[ ] 5.1.2 - Script para rehash de contraseñas existentes
    # scripts/rehash_passwords.py
    import bcrypt
    import json
    
    with open('data/db.json', 'r') as f:
        db = json.load(f)
    
    for usuario in db['usuarios']:
        pwd = usuario.get('contrasena')
        if pwd and not pwd.startswith('$2b$'):
            # Es plaintext, rehashear
            pwd_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
            usuario['contrasena'] = pwd_hash.decode()
    
    with open('data/db.json', 'w') as f:
        json.dump(db, f, indent=4)

[ ] 5.1.3 - Tests de seguridad
    - test_contrasena_hasheada_no_plaintext()
    - test_contrasena_hash_diferente_cada_vez()
    - test_contrasena_incorrecta_no_verifica()
```

---

### 5.2 Agregar Validación de Entrada

**Objetivo:** Validar datos en client y server.

#### Tareas:

```
[ ] 5.2.1 - Client-side validation (HTML/JS)
    - Email: validar formato
    - Contraseña: mín 8 chars, 1 mayús, 1 número
    - Nombre: no vacío, <100 chars
    - Feedback visual en tiempo real

[ ] 5.2.2 - Server-side validation (Python)
    # En AuthService
    def _validate_password(pwd: str) → bool:
        if len(pwd) < 8:
            return False
        if not any(c.isupper() for c in pwd):
            return False
        if not any(c.isdigit() for c in pwd):
            return False
        return True
    
    def _validate_email(email: str) → bool:
        # RFC 5322 simple
        import re
        return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email))
    
    def _validate_nombre(nombre: str) → bool:
        return 1 <= len(nombre) <= 100

[ ] 5.2.3 - Tests de validación
    - test_validar_password_muy_corta()
    - test_validar_password_sin_mayuscula()
    - test_validar_password_sin_numero()
    - test_validar_password_valida()
    - test_validar_email_formato_invalido()
    - test_validar_email_valida()
```

---

### 5.3 Suite de Testing Completa

**Objetivo:** Lograr >80% cobertura en código nuevo.

#### Tareas:

```
[ ] 5.3.1 - Tests unitarios (ya en cada fase)
    - Cada servicio: >85%
    - Cada repositorio: >90%
    - Cada modelo: 100%
    Total target: >85%

[ ] 5.3.2 - Tests de integración
    # tests/test_integration.py
    Flujos completos:
    ├─ Registrar → Login → Subir foto → Ver deterioro
    ├─ Foto deteriora automáticamente
    ├─ Enviar a papelera → Restaurar
    ├─ Eliminar definitivamente
    └─ Estadísticas actualizadas

[ ] 5.3.3 - Tests E2E (con webview simulado)
    # tests/test_e2e.py
    ├─ test_user_workflow_complete()
    ├─ test_auto_decay_workflow()
    ├─ test_trash_and_cleanup()
    └─ test_dashboard_updates()

[ ] 5.3.4 - Ejecutar coverage
    pytest --cov=src --cov-report=html
    # Target: >80% overall
```

#### Testing:
```
[ ] 5.3.5 - Generar reporte de cobertura
    - Identificar gaps
    - Agregar tests faltantes
    - Alcanzar >80% coverage
```

---

### 5.4 Documentación de Código

**Objetivo:** Documentar arquitectura y APIs.

#### Tareas:

```
[ ] 5.4.1 - Docstrings en Python
    - Cada clase: descripción + atributos
    - Cada método: descripción + parámetros + retorno
    - Ejemplos de uso donde sea relevante

[ ] 5.4.2 - API Documentation
    # docs/API.md
    - Listar todos los métodos públicos
    - Parámetros + tipos
    - Retornos esperados
    - Ejemplos de uso

[ ] 5.4.3 - Architecture Documentation
    # docs/ARCHITECTURE.md
    - Diagrama de dependencias
    - Explicar cada componente
    - Patrones usados
    - Decisiones de diseño

[ ] 5.4.4 - Developer Guide
    # docs/DEVELOPER.md
    - Cómo ejecutar en dev
    - Cómo correr tests
    - Cómo agregar nuevas features
    - Convenciones de código
```

**Entregables:**
- Código con 100% docstrings
- API documentation completa
- Architecture documentation
- Developer guide
- Coverage >80% en código nuevo

**Checkpoints:**
```
✅ Fase 5 completada cuando:
  - [ ] Contraseñas hasheadas con bcrypt
  - [ ] Validación en client + server
  - [ ] Tests >80% coverage overall
  - [ ] API documentada
  - [ ] Arquitectura documentada
  - [ ] Developer guide completo
```

---

## FASE 6: INTEGRACIÓN Y TESTING FINAL (Week 5)

### 6.1 Testing End-to-End

**Objetivo:** Verificar que todos los flujos funcionan correctamente.

#### Tareas:

```python
[ ] 6.1.1 - Crear test suite E2E
    # tests/test_complete_workflows.py
    
    def test_workflow_complete_usuario(webview_mock):
        """CU01-14: Flujo completo de usuario"""
        # 1. Registrarse
        result = api.register_user("Juan", "juan@example.com", "Pwd123456")
        assert result['success']
        
        # 2. Login
        result = api.login("juan@example.com", "Pwd123456")
        assert result['success']
        usuario_id = result['usuario']['id']
        
        # 3. Subir foto
        result = api.pick_and_upload(usuario_id)
        assert result['success']
        foto_id = result['fotos'][0]['id']
        
        # 4. Ver en galería
        result = api.get_galeria(usuario_id)
        assert len(result['fotos']) == 1
        
        # 5. Ver individual
        result = api.get_foto_individual(foto_id)
        assert result['success']
        
        # 6. Simular paso del tiempo (mock)
        # ... avanzar fecha de acceso ...
        
        # 7. Aplicar deterioro automático
        scheduler._apply_decay_all_users()
        
        # 8. Verificar deterioro
        result = api.get_estado_erosion(foto_id)
        assert result['erosion']['nivelDeterioro'] > 0
        
        # 9. Mover a papelera
        result = api.move_to_trash(foto_id, usuario_id)
        assert result['success']
        
        # 10. Ver papelera
        result = api.get_papelera(usuario_id)
        assert len(result['fotos']) == 1
        
        # 11. Restaurar
        result = api.restore_from_trash(foto_id, usuario_id)
        assert result['success']
        
        # 12. Eliminar definitivamente
        result = api.delete_permanently(foto_id, usuario_id)
        assert result['success']
        
        # 13. Verificar estadísticas
        result = api.get_dashboard(usuario_id)
        assert result['metricas']['totalFotosEliminadas'] == 1
        assert result['metricas']['totalBytesLiberados'] > 0

[ ] 6.1.2 - Tests de carga
    # Simular múltiples usuarios + fotos
    ├─ 10 usuarios
    ├─ 50 fotos cada uno
    ├─ Verificar scheduler no se bloquea
    └─ Medir tiempo de ejecución

[ ] 6.1.3 - Tests de recuperación
    # Simular fallos
    ├─ Base de datos corrupta
    ├─ Archivo faltante
    ├─ Scheduler fail
    └─ Verificar manejo de errores
```

**Entregables:**
- Suite E2E con >10 tests
- Tests de carga pasando
- Tests de recuperación pasando

---

### 6.2 Performance y Optimización

**Objetivo:** Asegurar que el sistema es eficiente.

#### Tareas:

```
[ ] 6.2.1 - Profiling de código
    # Identificar bottlenecks
    ├─ Lectura de BD
    ├─ Procesamiento de imágenes
    ├─ Ejecución de scheduler
    └─ Rendering de UI

[ ] 6.2.2 - Optimizaciones
    ├─ Cache de fotos frecentes
    ├─ Lazy loading de imágenes
    ├─ Batch updates en BD
    └─ Compresión de imágenes degradadas

[ ] 6.2.3 - Benchmarks
    ├─ Tiempo para subir 50 fotos
    ├─ Tiempo para aplicar deterioro (100 fotos)
    ├─ Tiempo para limpiar papelera (50 items)
    └─ Memoria usada
```

---

### 6.3 Verificación de Requisitos

**Objetivo:** Confirmar que todos los requerimientos se cumplen.

#### Tareas:

```
[ ] 6.3.1 - Matriz de trazabilidad
    RF01-RF27: Cada uno mapeado a código + tests

[ ] 6.3.2 - RNF (No-Funcionales)
    RNF01-RNF08: Verificar cumplimiento
    ├─ Monitores tiempo inactividad ✓
    ├─ Aplica deterioro automáticamente ✓
    ├─ Restaura a calidad original ✓
    ├─ Interfaz clara ✓
    ├─ Integridad de archivos originales ✓
    ├─ Multiplataforma ✓
    ├─ Contraseñas hasheadas ✓
    └─ Aislamiento de sesiones ✓

[ ] 6.3.3 - Casos de uso (14)
    CU01-CU14: Todos implementados ✓
```

---

### 6.4 Limpieza Final

**Objetivo:** Preparar código para producción.

#### Tareas:

```
[ ] 6.4.1 - Code review
    - Revisar estilo (PEP 8)
    - Revisar lógica
    - Revisar seguridad
    - Revisar documentación

[ ] 6.4.2 - Linting
    pylint src/ --min-similarity-lines=7
    pytest --flake8

[ ] 6.4.3 - Cleanup
    ├─ Remover código comentado
    ├─ Remover print() de debug
    ├─ Remover imports no usados
    ├─ Consistent naming conventions

[ ] 6.4.4 - Merge a main
    git checkout main
    git merge refactor/architecture-alignment
    git tag v2.0.0
```

---

## FASE 7: DOCUMENTACIÓN FINAL (1 semana)

### 7.1 Documentación Técnica

```
[ ] 7.1.1 - README.md completo
    ├─ Descripción proyecto
    ├─ Stack tecnológico
    ├─ Instrucciones instalación
    ├─ Cómo correr (dev + producción)
    ├─ Tests
    ├─ Documentación links
    └─ Créditos

[ ] 7.1.2 - ARCHITECTURE.md
    ├─ Diagrama general
    ├─ Descripción de capas
    ├─ Patrones de diseño
    ├─ Flujos principales
    └─ Decisiones arquitectónicas

[ ] 7.1.3 - API.md
    ├─ Listar métodos públicos
    ├─ Parámetros + tipos
    ├─ Retornos esperados
    ├─ Códigos de error
    └─ Ejemplos

[ ] 7.1.4 - DEVELOPMENT.md
    ├─ Setup de entorno
    ├─ Estructura de proyecto
    ├─ Cómo agregar features
    ├─ Testing
    ├─ Naming conventions
    └─ Git workflow

[ ] 7.1.5 - DEPLOYMENT.md
    ├─ Requisitos
    ├─ Instalación
    ├─ Configuración
    ├─ Backup + Restore
    └─ Troubleshooting
```

### 7.2 Documentación de Cambios

```
[ ] 7.2.1 - CHANGELOG.md
    - v2.0.0 (Refactorización)
      ├─ Motor de erosión completamente implementado
      ├─ Papelera funcional
      ├─ Scheduler de tareas periódicas
      ├─ Seguridad con bcrypt
      ├─ >80% test coverage
      └─ Arquitectura OOP con patrones

[ ] 7.2.2 - MIGRATION.md
    - Guía para migrar de v1.0 a v2.0
    ├─ Cambios en API
    ├─ Cambios en BD (schema)
    ├─ Cambios en frontend
    └─ Scripts de migración
```

---

## ESTIMACIÓN FINAL

```
┌───────────────────────────────────────────────┐
│         CRONOGRAMA DE REFACTORIZACIÓN         │
├──────────────────┬──────────┬─────────────────┤
│ FASE             │ DURACIÓN │ HORAS ESTIMADAS │
├──────────────────┼──────────┼─────────────────┤
│ 0: Preparación   │ 1 semana │ 20-24h          │
│ 1: Arquitectura  │ 2 semanas│ 50-60h          │
│ 2: Erosión       │ 1 semana │ 30-40h          │
│ 3: Papelera      │ 1 semana │ 25-35h          │
│ 4: Dashboard     │ 1 semana │ 15-20h          │
│ 5: Seguridad     │ 1 semana │ 20-25h          │
│ 6: Testing E2E   │ 1 semana │ 20-25h          │
│ 7: Documentación │ 1 semana │ 15-20h          │
├──────────────────┼──────────┼─────────────────┤
│ TOTAL            │ 5 semanas│ 195-249 horas   │
│ Equipos:         │          │ 2-3 developers  │
│ Vel. esperada:   │          │ 40h/semana      │
└──────────────────┴──────────┴─────────────────┘
```

---

## MÉTRICAS DE ÉXITO

```
Cobertura Arquitectónica:
  Inicio:  33% (MVP actual)
  Meta:    75%+ (arquitectura consistente)
  Target:  85%+ (producción ready)

Test Coverage:
  Inicio:  ~5% (sin tests)
  Target:  80%+ (código nuevo)
  Meta:    >85% (crítico)

Cobertura de Requerimientos:
  Inicio:  RF: 37% | CU: 29%
  Target:  RF: 90%+ | CU: 100% (14/14)

Performance:
  Subir 50 fotos: < 30 segundos
  Aplicar deterioro (100 fotos): < 60 segundos
  Memoria base: < 150 MB

Seguridad:
  ✅ Contraseñas hasheadas
  ✅ Validación entrada
  ✅ Sesiones aisladas
  ✅ No vulnerabilidades conocidas
```

---

## ENTREGABLES FINALES

```
Código:
  ├─ src/ con arquitectura completa
  ├─ tests/ con >80% coverage
  ├─ requirements.txt actualizado
  └─ .gitignore + .env.example

Documentación:
  ├─ README.md
  ├─ ARCHITECTURE.md
  ├─ API.md
  ├─ DEVELOPMENT.md
  ├─ DEPLOYMENT.md
  ├─ CHANGELOG.md
  └─ inline docstrings (100%)

Tests:
  ├─ Unit tests (>500)
  ├─ Integration tests (>20)
  ├─ E2E tests (>10)
  └─ Coverage report (>80%)

Calidad:
  ├─ Linting passed (PEP 8)
  ├─ Code review completado
  ├─ Security audit passed
  └─ Performance benchmarked
```

---

## PRÓXIMOS PASOS DESPUÉS DE REFACTORIZACIÓN

Una vez completada la refactorización, el proyecto estará listo para:

1. **Agregar nuevas features** (basadas en documentación)
   - Búsqueda de fotos
   - Categorización automática
   - Compartir fotos
   - Export de datos

2. **Escalar** a múltiples plataformas
   - Web (Flask/Django backend)
   - Mobile (React Native)
   - Cloud deployment

3. **Mejorar UX/UI**
   - Diseño profesional
   - Animaciones
   - Temas personalizables

4. **Monetización**
   - Plan freemium
   - Integración cloud
   - API comercial
**Documento completado:** Abril 6, 2026
**Versión:** 1.0
**Estado:** Listo para implementación
