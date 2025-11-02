import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export const Register: React.FC = () => {
    const { register } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [company, setCompany] = useState('');
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setError(null);
            await register(email, password, company || undefined);
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Register failed');
        }
    };

    return (
        <div className="login-center">
            <div className="login-card animate-fade-slide">
                <div className="login-header">
                    <div className="avatar">R</div>
                    <div>
                        <h2 className="login-title">Crear cuenta</h2>
                        <p className="login-hint">Registra una nueva cuenta y compañía</p>
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
                        <label className="form-group">Compañía (opcional)</label>
                        <input
                            value={company}
                            onChange={e => setCompany(e.target.value)}
                            className="input"
                            placeholder="Nombre de tu compañía"
                        />
                    </div>
                    <div>
                        <button className="btn-primary">Registrar</button>
                    </div>
                </form>

                <div className="small-muted">
                    ¿Ya tienes cuenta? <a href="/" className="link-blue">Inicia sesión</a>
                </div>
            </div>
        </div>
    );
};

export default Register;
