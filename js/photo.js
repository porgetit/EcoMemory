import { apiViewPhoto, apiDeletePhoto } from './storage.js';
import { getSession } from './auth.js';

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

const getLabelEstado = (estadoErosion) => {
    const labels = {
        'DETERIORO_LEVE':   'Light decay',
        'DETERIORO_MENOR':  'Minor decay',
        'DETERIORO_MAYOR':  'Major decay',
        'DETERIORO_CRITICO':'Critical decay',
    };
    return labels[estadoErosion] || 'Unknown';
};

const getBarColor = (nivel) => {
    if (nivel < 0.25) return '#28a745';
    if (nivel < 0.50) return '#ffc107';
    if (nivel < 0.75) return '#fd7e14';
    return '#dc3545';
};

// ──────────────────────────────────────────────────────────────────────────────
// Renderizado del canvas de fondo con pixelado proporcional al nivel PREVIO
// ──────────────────────────────────────────────────────────────────────────────

const renderBackground = (rutaOriginal, nivelDeterioro) => {
    const canvas = document.getElementById('photoBackground');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.src = rutaOriginal;

    const render = () => {
        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;

        const factor = Math.max(1 - nivelDeterioro, 0.02);
        const w = Math.ceil(canvas.width  * factor);
        const h = Math.ceil(canvas.height * factor);

        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img, 0, 0, w, h);
        ctx.drawImage(canvas, 0, 0, w, h, 0, 0, canvas.width, canvas.height);
    };

    if (img.complete && img.naturalWidth > 0) {
        render();
    } else {
        img.onload = render;
    }

    // Re-renderizar si cambia el tamaño de ventana
    window.addEventListener('resize', render);
};

// ──────────────────────────────────────────────────────────────────────────────
// Rellena el panel inferior con los datos de erosión previa
// ──────────────────────────────────────────────────────────────────────────────

const renderPanel = (foto, nivelPrevio) => {
    const pct = Math.round(nivelPrevio * 100);

    // Título con porcentaje previo
    document.getElementById('erosionTitle').textContent = `Erosion: ${pct}%`;

    // Barra de progreso con color según nivel
    const bar = document.getElementById('erosionBarFill');
    bar.style.width    = `${pct}%`;
    bar.style.background = getBarColor(nivelPrevio);

    // Estado textual
    const estadoLabel = getLabelEstado(foto.estadoErosion);
    document.getElementById('panelStatus').textContent =
        nivelPrevio > 0 ? 'Degradation cycle active' : 'Optimal state';

    // Nombre del archivo en navbar
    document.getElementById('photoFilename').textContent = foto.nombre;

    // Mensaje según si había deterioro o no
    if (nivelPrevio > 0) {
        document.getElementById('panelMessage').textContent =
            `You have interacted with this photo. The erosion will restart after closing this view.`;
    } else {
        document.getElementById('panelMessage').textContent =
            `This photo is in optimal state. Keep interacting with it to prevent erosion.`;
    }
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

    // Leer fotoId guardado por gallery.js en localStorage
    const fotoId = parseInt(localStorage.getItem('ecomemory_foto_actual'));
    if (!fotoId) {
        window.location.href = 'gallery.html';
        return;
    }

    // Llamar view_photo: resetea deterioro y retorna nivel previo
    const res = await apiViewPhoto(fotoId, session.usuarioId);

    if (!res || !res.success) {
        window.location.href = 'gallery.html';
        return;
    }

    const { foto, nivelPrevio } = res;

    // Renderizar fondo con el nivel PREVIO (así el usuario ve cómo estaba)
    renderBackground(foto.rutaOriginal, nivelPrevio);

    // Rellenar panel
    renderPanel(foto, nivelPrevio);

    // Ocultar pantalla de carga
    document.getElementById('loadingState').classList.add('hidden');

    // ── Botón Protect / Back: vuelve a galería (foto ya fue reseteada) ──
    document.getElementById('btnProtect').addEventListener('click', () => {
        window.location.href = 'gallery.html';
    });

    document.getElementById('btnBack').addEventListener('click', () => {
        window.location.href = 'gallery.html';
    });

    // ── Botón Move to Trash ──
    document.getElementById('btnTrash').addEventListener('click', async () => {
        const confirmar = confirm(`Move "${foto.nombre}" to trash?`);
        if (!confirmar) return;

        const result = await apiDeletePhoto(fotoId, session.usuarioId);
        if (result && result.success) {
            window.location.href = 'gallery.html';
        }
    });
});
