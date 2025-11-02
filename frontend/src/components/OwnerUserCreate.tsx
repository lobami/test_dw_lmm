import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { createUser } from '../api/users';

const OwnerUserCreate: React.FC = () => {
    const { user } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState<'admin' | 'viewer'>('viewer');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);

    if (!user || user.role !== 'owner') {
        return <div className="p-6">Acceso denegado. Solo los owners pueden crear usuarios.</div>;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        try {
            await createUser({ email, password, role });
            setMessage('Usuario creado correctamente');
            setEmail('');
            setPassword('');
            setRole('viewer');
        } catch (err: any) {
            setMessage(err?.response?.data?.detail || 'Error creando usuario');
        } finally {
            setLoading(false);
        }
    };

    const goBack = () => {
        // Try graceful SPA navigation first: go back in history.
        try {
            window.history.back();
            // If going back didn't change the path (user landed directly here), fallback to full navigation.
            setTimeout(() => {
                if (window.location.pathname === '/manage-users') {
                    window.location.href = '/';
                }
            }, 150);
        } catch (e) {
            window.location.href = '/';
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-semibold">Crear usuario (admin / viewer)</h2>
                <button
                    onClick={goBack}
                    className="ml-4 px-3 py-1 bg-blue-600 text-white rounded text-sm"
                    aria-label="Cerrar"
                >
                    Cerrar
                </button>
            </div>
            {message && <div className="mb-4 text-sm text-gray-700">{message}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="owner-email" className="block text-sm font-medium text-gray-700">Correo</label>
                    <input id="owner-email" value={email} onChange={e => setEmail(e.target.value)} type="email" required className="mt-1 block w-full rounded-md border-gray-300" />
                </div>
                <div>
                    <label htmlFor="owner-password" className="block text-sm font-medium text-gray-700">Contraseña</label>
                    <input id="owner-password" value={password} onChange={e => setPassword(e.target.value)} type="password" required className="mt-1 block w-full rounded-md border-gray-300" />
                </div>
                <div>
                    <label htmlFor="owner-role" className="block text-sm font-medium text-gray-700">Rol</label>
                    <select id="owner-role" value={role} onChange={e => setRole(e.target.value as any)} className="mt-1 block w-full rounded-md border-gray-300">
                        <option value="viewer">Viewer</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                <div>
                    <button disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? 'Creando...' : 'Crear usuario'}</button>
                </div>
            </form>
        </div>
    );
};

export default OwnerUserCreate;
