import React, { createContext, useContext, useEffect, useState } from 'react';
import api from '../api/client';
import { login as apiLogin, me as apiMe, register as apiRegister } from '../api/auth';

type User = {
    id: number;
    email: string;
    company_id?: number;
    role?: string;
};

type AuthContextType = {
    user: User | null;
    loading: boolean;
    sessionExpired: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    register: (email: string, password: string, companyName?: string) => Promise<void>;
    clearSessionExpired: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [sessionExpired, setSessionExpired] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            apiMe()
                .then((u) => setUser(u))
                .catch(() => setUser(null))
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    // Listen for global auth expiry events dispatched by the API client.
    useEffect(() => {
        const onExpired = () => {
            try {
                localStorage.removeItem('access_token');
            } catch (e) {
                // ignore
            }
            setUser(null);
            setSessionExpired(true);
        };
        window.addEventListener('auth:expired', onExpired as EventListener);
        return () => window.removeEventListener('auth:expired', onExpired as EventListener);
    }, []);

    const login = async (email: string, password: string) => {
        const data = await apiLogin(email, password);
        localStorage.setItem('access_token', data.access_token);
        setSessionExpired(false);
        const u = await apiMe();
        setUser(u);
    };

    const register = async (email: string, password: string, companyName?: string) => {
        const u = await apiRegister(email, password, companyName);
        // Optionally auto-login after register
        await login(email, password);
        return u;
    };

    const logout = async () => {
        // tell backend to revoke refresh cookie and clear client state
        try {
            await api.post('/auth/logout');
        } catch (e) {
            // ignore network errors but proceed to clear local session
        }

        try {
            localStorage.removeItem('access_token');
        } catch (e) {}
        setUser(null);
        setSessionExpired(false);
    };

    const clearSessionExpired = () => setSessionExpired(false);

    const handleGoToLogin = () => {
        // Ensure token is cleared and user is logged out, then hide modal.
        try {
            localStorage.removeItem('access_token');
        } catch (e) {}
        setUser(null);
        setSessionExpired(false);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, register, sessionExpired, clearSessionExpired }}>
            {children}

            {sessionExpired && (
                <div className="modal-overlay" role="dialog" aria-modal="true">
                    <div className="modal animate-fade-slide">
                        <h3 className="modal-title">Sesión expirada</h3>
                        <div className="modal-body">Tu sesión ha expirado o tus credenciales ya no son válidas. Por seguridad, debes iniciar sesión de nuevo.</div>
                        <div className="modal-actions">
                            <button className="btn-secondary" onClick={() => clearSessionExpired()}>Cerrar</button>
                            <button className="btn-primary" onClick={() => handleGoToLogin()}>Ir al login</button>
                        </div>
                    </div>
                </div>
            )}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
};
