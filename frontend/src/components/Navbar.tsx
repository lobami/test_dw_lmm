import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
    const { user, logout } = useAuth();
    const isDetail = typeof window !== 'undefined' && window.location.pathname.startsWith('/campaigns/');

    return (
        <nav className="flex items-center justify-between p-4 bg-white shadow">
            <div className="text-lg font-semibold">Análisis de campañas</div>
            <div className="flex items-center space-x-4">
                {user && <div className="text-sm">{user.email}</div>}
                {user && user.role === 'owner' && (
                    <button
                        onClick={() => {
                            const newPath = '/manage-users';
                            window.history.pushState({}, '', newPath);
                            window.dispatchEvent(new PopStateEvent('popstate'));
                        }}
                        className="px-3 py-1 bg-green-600 text-white rounded text-sm"
                    >
                        Gestión usuarios
                    </button>
                )}
                <button
                    onClick={() => logout()}
                    className="px-3 py-1 bg-red-500 text-white rounded text-sm"
                >
                    Cerrar sesión
                </button>
                {isDetail && (
                    <button
                        onClick={() => window.history.back()}
                        className="px-3 py-1 bg-blue-600 text-white rounded text-sm"
                        aria-label="Cerrar detalle"
                    >
                        Cerrar
                    </button>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
