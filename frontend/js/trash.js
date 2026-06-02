import { apiGetTrash, apiRestorePhoto, apiPermanentDelete } from './storage.js';
import { getSession, logout } from './auth.js';

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

const formatTiempoRestante = (diasRestantes) => {
    if (diasRestantes <= 0)  return 'Eliminación inminente';
    if (diasRestantes === 1) return '1 día restante';
    return `${diasRestantes} días restantes`;
};

const getUrgencyClass = (diasRestantes) => {
    if (diasRestantes <= 7)  return 'urgent';
    if (diasRestantes <= 14) return 'warning';
    return 'safe';
};

// Aplica pixelado al 100% en el canvas (todas las fotos en papelera
// se muestran completamente degradadas)
const renderCanvas = (canvas, rutaOriginal, nivelDeterioro) => {
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.src = rutaOriginal;

    const draw = () => {
        const w = canvas.offsetWidth  || 200;
        const h = canvas.offsetHeight || 190;
        canvas.width  = w;
        canvas.height = h;

        if (nivelDeterioro <= 0) {
            // Sin deterioro: mostrar imagen nítida
            ctx.imageSmoothingEnabled = true;
            ctx.drawImage(img, 0, 0, w, h);
            return;
        }

        const factor = Math.max(1 - nivelDeterioro, 0.02);
        const pw = Math.max(1, Math.ceil(w * factor));
        const ph = Math.max(1, Math.ceil(h * factor));

        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img, 0, 0, pw, ph);
        ctx.drawImage(canvas, 0, 0, pw, ph, 0, 0, w, h);
    };

    if (img.complete && img.naturalWidth > 0) {
        draw();
    } else {
        img.onload = draw;
    }
};

// ──────────────────────────────────────────────────────────────────────────────
// Render de una tarjeta
// ──────────────────────────────────────────────────────────────────────────────

const crearTarjeta = (foto, onRestore, onPurge) => {
    const col = document.createElement('div');
    col.className = 'col';
    col.dataset.fotoId = foto.id;

    const urgency = getUrgencyClass(foto.diasRestantes);
    const tiempoLabel = formatTiempoRestante(foto.diasRestantes);

    col.innerHTML = `
        <div class="trash-card">
            <div class="trash-canvas-wrapper">
                <canvas class="trash-canvas"></canvas>

                <!-- Overlay hover con botones -->
                <div class="trash-card-overlay">
                    <button class="btn-overlay-restore">
                        <i class="bi bi-arrow-counterclockwise"></i> Restaurar
                    </button>
                    <button class="btn-overlay-purge">
                        <i class="bi bi-trash3-fill"></i> Eliminar
                    </button>
                </div>

                <!-- Badge de tiempo restante -->
                <div class="badge-time ${urgency}">
                    <i class="bi bi-clock"></i>
                    ${tiempoLabel}
                </div>
            </div>
        </div>
    `;

    // Renderizar canvas con pixelado máximo
    const canvas = col.querySelector('.trash-canvas');
    requestAnimationFrame(() => renderCanvas(canvas, foto.rutaOriginal, foto.nivelDeterioro));

    // Listeners de botones
    col.querySelector('.btn-overlay-restore').addEventListener('click', (e) => {
        e.stopPropagation();
        onRestore(foto);
    });

    col.querySelector('.btn-overlay-purge').addEventListener('click', (e) => {
        e.stopPropagation();
        onPurge(foto);
    });

    return col;
};

// ──────────────────────────────────────────────────────────────────────────────
// Render del grid completo
// ──────────────────────────────────────────────────────────────────────────────

const renderGrid = (fotos, session) => {
    const grid       = document.getElementById('trashGrid');
    const emptyState = document.getElementById('emptyState');
    const actions    = document.getElementById('trashActions');

    grid.innerHTML = '';

    if (!fotos || fotos.length === 0) {
        emptyState.classList.remove('d-none');
        actions.classList.add('d-none');
        return;
    }

    emptyState.classList.add('d-none');
    actions.classList.remove('d-none');

    fotos.forEach(foto => {
        const tarjeta = crearTarjeta(
            foto,
            // onRestore
            async (f) => {
                const ok = confirm(`¿Restaurar "${f.nombre}" en tu galería?`);
                if (!ok) return;
                const res = await apiRestorePhoto(f.id, session.usuarioId);
                if (res && res.success) {
                    document.querySelector(`[data-foto-id="${f.id}"]`)?.remove();
                    // Si ya no quedan fotos, mostrar estado vacío
                    if (grid.children.length === 0) {
                        emptyState.classList.remove('d-none');
                        actions.classList.add('d-none');
                    }
                }
            },
            // onPurge
            async (f) => {
                const ok = confirm(
                    `¿Eliminar permanentemente "${f.nombre}"?\n\nEsta acción es irreversible y no se puede deshacer.`
                );
                if (!ok) return;
                const res = await apiPermanentDelete(f.id, session.usuarioId);
                if (res && res.success) {
                    document.querySelector(`[data-foto-id="${f.id}"]`)?.remove();
                    if (grid.children.length === 0) {
                        emptyState.classList.remove('d-none');
                        actions.classList.add('d-none');
                    }
                }
            }
        );
        grid.appendChild(tarjeta);
    });
};

// ──────────────────────────────────────────────────────────────────────────────
// Init
// ──────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    const session = getSession();
    if (!session) {
        window.location.href = 'index.html';
        return;
    }

    // Nombre de usuario en navbar
    document.querySelectorAll('.user-name-display')
        .forEach(el => el.textContent = session.nombre || 'Usuario');

    // Cargar papelera
    const res = await apiGetTrash(session.usuarioId);
    if (res && res.success) {
        renderGrid(res.fotos, session);
    }

    // ── Restore All ──
    document.getElementById('btnRestoreAll').addEventListener('click', async () => {
        const res = await apiGetTrash(session.usuarioId);
        if (!res?.fotos?.length) return;

        const ok = confirm(`¿Restaurar las ${res.fotos.length} fotos a tu galería?`);
        if (!ok) return;

        for (const foto of res.fotos) {
            await apiRestorePhoto(foto.id, session.usuarioId);
        }
        renderGrid([], session);
    });

    // ── Empty Trash ──
    document.getElementById('btnEmptyTrash').addEventListener('click', async () => {
        const res = await apiGetTrash(session.usuarioId);
        if (!res?.fotos?.length) return;

        const ok = confirm(
            `¿Eliminar permanentemente las ${res.fotos.length} fotos?\n\nEsta acción es irreversible y no se puede deshacer.`
        );
        if (!ok) return;

        for (const foto of res.fotos) {
            await apiPermanentDelete(foto.id, session.usuarioId);
        }
        renderGrid([], session);
    });

    // ── Back to Gallery ──
    document.getElementById('btnBackToGallery').addEventListener('click', () => {
        window.location.href = 'gallery.html';
    });

    const btnBackEmpty = document.getElementById('btnBackEmpty');
    if (btnBackEmpty) {
        btnBackEmpty.addEventListener('click', () => {
            window.location.href = 'gallery.html';
        });
    }

    // ── Logout ──
    document.getElementById('btnLogout').addEventListener('click', () => {
        logout();
        window.location.href = 'index.html';
    });
});
