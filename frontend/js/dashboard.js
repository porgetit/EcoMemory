import { apiGetDashboardStats, getFotografiasActivas } from './storage.js';
import { getSession } from './auth.js';

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

const formatBytes = (bytes) => {
    if (bytes === 0)           return '0 B';
    if (bytes < 1024)          return `${bytes} B`;
    if (bytes < 1024 ** 2)     return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 ** 3)     return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
    return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
};

// ──────────────────────────────────────────────────────────────────────────────
// Render principal
// ──────────────────────────────────────────────────────────────────────────────

export const renderizarDashboard = async () => {
    const session = getSession();
    if (!session) return;

    const res = await apiGetDashboardStats(session.usuarioId);
    if (!res || !res.success) return;

    const { stats } = res;
    const conteos   = stats.conteoPorEstado;

    // Métricas globales
    document.getElementById('statDeleted').innerText =
        `${stats.totalEliminadasSistema.toLocaleString()} elementos`;
    document.getElementById('statFreed').innerText =
        formatBytes(stats.bytesLiberados);

    // Conteos por estado
    document.getElementById('countLight').innerText    = `${conteos['DETERIORO_LEVE']} fotos`;
    document.getElementById('countMinor').innerText    = `${conteos['DETERIORO_MENOR']} fotos`;
    document.getElementById('countMajor').innerText    = `${conteos['DETERIORO_MAYOR']} fotos`;
    document.getElementById('countCritical').innerText = `${conteos['DETERIORO_CRITICO']} fotos`;
};