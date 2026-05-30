// FotografiaService - Módulo de Galería
import { initStorage, getFotografiasActivas, sincronizarDB, apiPickAndUpload, apiDeletePhoto, apiGetConfig, apiStartSession } from './storage.js';
import { getSession, logout } from './auth.js';
import { getLabelEstado, getTextColorClass } from './erosion.js';
import { renderizarDashboard } from './dashboard.js';

// ──────────────────────────────────────────────────────────────────────────────
// Constantes
// ──────────────────────────────────────────────────────────────────────────────
const CANVAS_W = 320;              // Resolución lógica del canvas
const CANVAS_H = 200;

// ──────────────────────────────────────────────────────────────────────────────
// Algoritmo de Pixelado con doble dibujo en <canvas>
// ──────────────────────────────────────────────────────────────────────────────

/**
 * Aplica un efecto de pixelado proporcional al nivel de deterioro.
 * nivelDeterioro = 0.0 → imagen nítida.  nivelDeterioro = 1.0 → bloques gigantes.
 */
const aplicarPixelado = (canvas, imageSrc, nivelDeterioro) => {
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.src = imageSrc;

    const render = () => {
        canvas.width  = CANVAS_W;
        canvas.height = CANVAS_H;

        // Factor: 1.0 = resolución completa, ~0.02 = mínima (bloques enormes)
        const factor = Math.max(1 - nivelDeterioro, 0.02);
        const w = Math.ceil(CANVAS_W * factor);
        const h = Math.ceil(CANVAS_H * factor);

        // Desactivar suavizado para obtener bloques cuadrados
        ctx.imageSmoothingEnabled = false;

        // Paso 1: dibujar la imagen reducida
        ctx.drawImage(img, 0, 0, w, h);

        // Paso 2: escalar de vuelta al tamaño completo
        ctx.drawImage(canvas, 0, 0, w, h, 0, 0, CANVAS_W, CANVAS_H);
    };

    if (img.complete && img.naturalWidth > 0) {
        render();
    } else {
        img.onload = render;
    }
};

// ──────────────────────────────────────────────────────────────────────────────
// Renderizado de la galería
// ──────────────────────────────────────────────────────────────────────────────

const renderizarGaleria = () => {
    const session = getSession();
    const fotos = getFotografiasActivas(session.usuarioId);
    const galleryGrid = document.getElementById('galleryGrid');

    galleryGrid.innerHTML = '';

    fotos.forEach(foto => {
        const colDiv = document.createElement('div');
        colDiv.className = 'col';

        colDiv.innerHTML = `
            <div class="card gallery-card h-100">
                <div class="gallery-canvas-wrapper">
                    <canvas class="gallery-canvas" data-foto-id="${foto.id}"></canvas>
                    <button class="btn btn-delete-overlay" title="Eliminar foto" data-foto-id="${foto.id}">
                        <i class="bi bi-trash3-fill"></i>
                    </button>
                </div>
                <div class="card-body p-3 bg-surface">
                    <h6 class="card-title text-truncate mb-1 text-white fw-bold" title="${foto.nombre}">${foto.nombre}</h6>
                    <div class="d-flex justify-content-between text-muted-custom" style="font-size: 0.8rem;">
                        <span class="${getTextColorClass(foto.estadoErosion)} fw-bold">${getLabelEstado(foto.estadoErosion)} <span class="text-muted-custom fw-normal">• ${(foto.tamanoBytes / (1024 * 1024)).toFixed(1)}MB</span></span>
                    </div>
                </div>
            </div>
        `;
        galleryGrid.appendChild(colDiv);

        // Renderizar pixelado en el canvas recién insertado
        const canvas = colDiv.querySelector('canvas');
        aplicarPixelado(canvas, foto.rutaOriginal, foto.nivelDeterioro);

        // Event listener del botón de eliminar
        const btnDelete = colDiv.querySelector('.btn-delete-overlay');
        btnDelete.addEventListener('click', async (e) => {
            e.stopPropagation();
            const confirmar = confirm(`¿Eliminar "${foto.nombre}"?`);
            if (!confirmar) return;

            const result = await apiDeletePhoto(foto.id, session.usuarioId);
            if (result && result.success) {
                await sincronizarDB();
                renderizarGaleria();
            }
        });

        const card = colDiv.querySelector('.gallery-card');
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => {
            localStorage.setItem('ecomemory_foto_actual', foto.id);
            window.location.href = 'photo.html';
        });
    });

    renderizarDashboard();
};

// ──────────────────────────────────────────────────────────────────────────────
// Polling para reflejar la erosión en tiempo real
// ──────────────────────────────────────────────────────────────────────────────

let pollingTimer = null;

const iniciarPolling = (intervalMs) => {
    if (pollingTimer) return;
    pollingTimer = setInterval(async () => {
        const scrollY = window.scrollY;
        await sincronizarDB();
        renderizarGaleria();
        window.scrollTo(0, scrollY);
    }, intervalMs);
};

// ──────────────────────────────────────────────────────────────────────────────
// Init
// ──────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    await initStorage();

    const session = getSession();
    if (!session) {
        window.location.href = 'index.html';
        return;
    }

    // Mostrar nombre del usuario en la navbar
    document.querySelectorAll('.user-name-display').forEach(el => el.innerText = session.nombre);

    document.getElementById('btnLogout').addEventListener('click', logout);

    // Upload Photo → abre el diálogo nativo del SO via Python (JPG/PNG filtrado)
    document.getElementById('btnUpload').addEventListener('click', async () => {
        const result = await apiPickAndUpload(session.usuarioId);
        if (result && result.success && result.fotos && result.fotos.length > 0) {
            // Re-sincronizar el caché local con el db.json actualizado por Python
            await sincronizarDB();
            renderizarGaleria();
        }
    });

    // Arrancar el daemon de erosión para este usuario
    await apiStartSession(session.usuarioId);

    // Obtener intervalo de polling dinámico desde el backend
    const config = await apiGetConfig();
    const pollingMs = (config && config.pollingIntervalMs) ? config.pollingIntervalMs : 5000;

    // Render inicial
    renderizarGaleria();

    // Arrancar auto-refresh con intervalo dinámico
    iniciarPolling(pollingMs);
});
