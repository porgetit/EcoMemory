// AuthService - Módulo de Autenticación (Registro / Login)
import { initStorage, buscarPorCorreo, apiRegister } from './storage.js';

const SESSION_KEY = 'ecomemory_session';

// AuthService.iniciarSesion()
export const login = (correo, contrasena) => {
    const usuario = buscarPorCorreo(correo);
    if (usuario && usuario.contrasena === contrasena) {
        sessionStorage.setItem(SESSION_KEY, JSON.stringify({
            usuarioId: usuario.id,
            nombre: usuario.nombre,
            correo: usuario.correo
        }));
        return true;
    }
    return false;
};

// AuthService.registrarUsuario() — async: delega en api.py via PyWebView
export const registrar = async (nombre, apellido, correo, contrasena) => {
    return await apiRegister(`${nombre} ${apellido}`, correo, contrasena);
};

export const getSession = () => JSON.parse(sessionStorage.getItem(SESSION_KEY));
export const logout = () => { sessionStorage.removeItem(SESSION_KEY); window.location.href = 'index.html'; };

document.addEventListener('DOMContentLoaded', async () => {
    await initStorage();

    // Redirecciones de seguridad
    const session = getSession();
    const isAuthPage = window.location.pathname.includes('index.html')
        || window.location.pathname.includes('register.html')
        || window.location.pathname === '/';

    if (session && isAuthPage) window.location.href = 'gallery.html';

    // UI Events para index.html (Login)
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('emailLogin').value;
            const pass = document.getElementById('passLogin').value;

            if (login(email, pass)) {
                window.location.href = 'gallery.html';
            } else {
                document.getElementById('authAlerts').innerHTML =
                    `<div class="alert alert-danger mt-3 py-2" role="alert">Credenciales inválidas</div>`;
            }
        });
    }

    // UI Events para register.html (Register)
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fName = document.getElementById('fName').value;
            const lName = document.getElementById('lName').value;
            const email = document.getElementById('emailReg').value;
            const pass = document.getElementById('passReg').value;

            if (fName && lName && email && pass) {
                const resultado = await registrar(fName, lName, email, pass);
                if (resultado.success) {
                    window.location.href = 'index.html';
                } else {
                    document.getElementById('authAlerts').innerHTML =
                        `<div class="alert alert-danger mt-3 py-2" role="alert">El email ya está registrado</div>`;
                }
            }
        });
    }

    // Toggle visibilidad contraseña
    const togglePass = document.getElementById('togglePass');
    if (togglePass) {
        togglePass.addEventListener('click', () => {
            const passReg = document.getElementById('passReg');
            const passLogin = document.getElementById('passLogin');
            const input = passReg || passLogin;
            const icon = togglePass.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    }
});
