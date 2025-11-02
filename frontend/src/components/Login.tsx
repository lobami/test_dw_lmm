import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export const Login: React.FC = () => {
    const { login, sessionExpired, clearSessionExpired } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setError(null);
            await login(email, password);
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Login failed');
        }
    };

    return (
        <div className="login-center">
            <div className="login-card animate-fade-slide">
                <div className="login-header">
                    <div className="avatar">A</div>
                    <div>
                        <h2 className="login-title">Inicia sesión</h2>
                        <p className="login-hint">Accede al Análisis de Campañas</p>
                    </div>
                </div>


                {error && <div className="error" style={{ marginBottom: 12 }}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div>
                        <label className="form-group">Correo electrónico</label>
                        <input
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            className="input"
                            placeholder="tu@correo.com"
                            type="email"
                            required
                        />
                    </div>
                    <div>
                        <label className="form-group">Contraseña</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            className="input"
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    <div>
                        <button className="btn-primary">Entrar</button>
                    </div>
                </form>

                <div className="small-muted">
                    ¿No tienes cuenta? <a href="/register" className="link-blue">Regístrate</a>
                </div>
            </div>
        </div>
    );
};
