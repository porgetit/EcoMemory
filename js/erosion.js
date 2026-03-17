// ErosionService
// 5. Motor de Erosión Digital

// 5.1 calcularNivelDeterioro(foto)
export const calcularNivelDeterioro = (foto) => {
    if (foto && foto.nivelDeterioro !== undefined && foto.nivelDeterioro !== null) {
        return foto.nivelDeterioro;
    }
    return Math.random(); // Float entre 0 y 1
};

// 5.2 determinarEstado(nivelDeterioro)
export const determinarEstado = (nivelDeterioro) => {
    if (nivelDeterioro < 0.25) return 'DETERIORO_LEVE';
    if (nivelDeterioro < 0.50) return 'DETERIORO_MENOR';
    if (nivelDeterioro < 0.75) return 'DETERIORO_MAYOR';
    return 'DETERIORO_CRITICO';
};

// 5.3 Funciones adicionales
export const superaUmbralCritico = (nivelDeterioro) => nivelDeterioro > 0.75;

export const calcularDiasInactividad = (foto) => {
    const ahora = Date.now();
    const ultimoAcceso = new Date(foto.fechaUltimoAcceso).getTime();
    return Math.floor((ahora - ultimoAcceso) / (1000 * 60 * 60 * 24));
};

export const getLabelEstado = (estadoErosion) => {
    const labels = {
        'DETERIORO_LEVE': 'Light',
        'DETERIORO_MENOR': 'Minor',
        'DETERIORO_MAYOR': 'Major',
        'DETERIORO_CRITICO': 'Critical'
    };
    return labels[estadoErosion] || 'Unknown';
};

export const getColorBadge = (estadoErosion) => {
    const classes = {
        'DETERIORO_LEVE': 'bg-light-decay',
        'DETERIORO_MENOR': 'bg-minor-decay',
        'DETERIORO_MAYOR': 'bg-major-decay',
        'DETERIORO_CRITICO': 'bg-critical-decay'
    };
    return classes[estadoErosion] || 'bg-secondary';
};

export const getTextColorClass = (estadoErosion) => {
    const classes = {
        'DETERIORO_LEVE': 'text-light-decay',
        'DETERIORO_MENOR': 'text-minor-decay',
        'DETERIORO_MAYOR': 'text-major-decay',
        'DETERIORO_CRITICO': 'text-critical-decay'
    };
    return classes[estadoErosion] || 'text-secondary';
};