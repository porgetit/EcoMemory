// FotografiaService - Módulo de Galería
import { initStorage, getFotografiasActivas, sincronizarDB, apiPickAndUpload } from './storage.js';
import { getSession, logout } from './auth.js';
import { getLabelEstado, getColorBadge, getTextColorClass } from './erosion.js';
import { renderizarDashboard } from './dashboard.js';

// FotografiaService.obtenerGaleria()
const renderizarGaleria = () => {
    const session = getSession();
    const fotos = getFotografiasActivas(session.usuarioId);
    const galleryGrid = document.getElementById('galleryGrid');

    galleryGrid.innerHTML = '';

    fotos.forEach(foto => {
        const pctDecay = Math.round(foto.nivelDeterioro * 100);
        const colDiv = document.createElement('div');
        colDiv.className = 'col';

        colDiv.innerHTML = `
            <div class="card gallery-card h-100">
                <img src="${foto.rutaOriginal}" class="gallery-img card-img-top" alt="${foto.nombre}">
                <span class="badge badge-decay ${getColorBadge(foto.estadoErosion)}">${pctDecay}% DECAY</span>
                <div class="card-body p-3 bg-surface">
                    <h6 class="card-title text-truncate mb-1 text-white fw-bold" title="${foto.nombre}">${foto.nombre}</h6>
                    <div class="d-flex justify-content-between text-muted-custom" style="font-size: 0.8rem;">
                        <span class="${getTextColorClass(foto.estadoErosion)} fw-bold">${getLabelEstado(foto.estadoErosion)} <span class="text-muted-custom fw-normal">• ${(foto.tamanoBytes / (1024 * 1024)).toFixed(1)}MB</span></span>
                    </div>
                </div>
            </div>
        `;
        galleryGrid.appendChild(colDiv);
    });

    renderizarDashboard();
};

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

    // Render inicial
    renderizarGaleria();
});
