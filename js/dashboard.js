// DashboardService - Módulo de Panel de Control
import { getEstadisticas, getFotografiasActivas } from './storage.js';
import { getSession } from './auth.js';

// Formateo de bytes a GB
const formatBytesToGB = (bytes) => (bytes / (1024 * 1024 * 1024)).toFixed(1);

// DashboardService.obtenerEstadisticas()
export const renderizarDashboard = () => {
    const session = getSession();
    if (!session) return;

    // Métricas globales del seed
    const estadisticas = getEstadisticas(session.usuarioId);

    // Cálculos dinámicos desde sesión para las categorías de erosión
    const fotosActivas = getFotografiasActivas(session.usuarioId);
    const conteos = {
        'DETERIORO_LEVE': 0, 'DETERIORO_MENOR': 0, 'DETERIORO_MAYOR': 0, 'DETERIORO_CRITICO': 0
    };
    fotosActivas.forEach(f => { conteos[f.estadoErosion]++; });

    // Actualizar UI - Stats fijos
    document.getElementById('statDeleted').innerText = `${estadisticas.totalEliminadasSistema.toLocaleString()} items`;
    document.getElementById('statFreed').innerText = `${formatBytesToGB(estadisticas.bytesLiberados)} GB`;

    // Actualizar UI - Conteos dinámicos
    document.getElementById('countLight').innerText = `${conteos['DETERIORO_LEVE']} Photos`;
    document.getElementById('countMinor').innerText = `${conteos['DETERIORO_MENOR']} Photos`;
    document.getElementById('countMajor').innerText = `${conteos['DETERIORO_MAYOR']} Photos`;
    document.getElementById('countCritical').innerText = `${conteos['DETERIORO_CRITICO']} Photos`;
};