// Capa de Acceso a Datos / IFileStorageService
const DB_KEY = 'ecomemory_db';

// Espera a que la API de PyWebView esté lista
const waitForPyWebView = () => new Promise((resolve) => {
    if (window.pywebview && window.pywebview.api) {
        resolve();
    } else {
        window.addEventListener('pywebviewready', resolve, { once: true });
    }
});

// 7.4 Inicialización — lee db.json desde Python y lo cachea en localStorage
export const initStorage = async () => {
    await waitForPyWebView();
    try {
        const data = await window.pywebview.api.get_db();
        localStorage.setItem(DB_KEY, JSON.stringify(data));
    } catch (e) {
        console.error('Error cargando DB desde Python:', e);
        if (!localStorage.getItem(DB_KEY)) {
            localStorage.setItem(DB_KEY, JSON.stringify({ usuarios: [], fotografias: [], registrosEliminacion: [], estadisticas: {} }));
        }
    }
};

// Fuerza una re-sincronización desde db.json (útil tras escrituras)
export const sincronizarDB = async () => {
    await waitForPyWebView();
    const data = await window.pywebview.api.get_db();
    localStorage.setItem(DB_KEY, JSON.stringify(data));
};

const getDB = () => JSON.parse(localStorage.getItem(DB_KEY) || '{}');

// 7.1 IUsuarioRepository
export const getUsuarios = () => getDB().usuarios || [];
export const buscarPorCorreo = (correo) => getUsuarios().find(u => u.correo === correo);

// 7.2 IFotografiaRepository
export const getFotografias = (usuarioId) => (getDB().fotografias || []).filter(f => f.usuarioId === usuarioId);
export const getFotografiasActivas = (usuarioId) => getFotografias(usuarioId).filter(f => !f.enPapelera);

// 7.3 IRegistroEliminacionRepository (y Estadísticas)
export const getEstadisticas = () => {
    const db = getDB();
    return db.estadisticas || { totalEliminadasSistema: 0, bytesLiberados: 0, fotosPorEstado: {} };
};

// ──────────────────────────────────────────────────────────────────────────────
// API Bridge — puentes hacia Python via PyWebView
// ──────────────────────────────────────────────────────────────────────────────

// Registra un nuevo usuario (escribe en db.json)
// Retorna: { success: bool, error?: 'EMAIL_EXISTS' }
export const apiRegister = async (nombre, correo, contrasena) => {
    await waitForPyWebView();
    return await window.pywebview.api.register_user(nombre, correo, contrasena);
};

// Abre el diálogo nativo del SO, copia imágenes y actualiza db.json
// Retorna: { success: bool, fotos: [...] }
export const apiPickAndUpload = async (usuarioId) => {
    await waitForPyWebView();
    return await window.pywebview.api.pick_and_upload(usuarioId);
};