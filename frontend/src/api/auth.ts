import api from './client';

interface TokenResponse {
    access_token: string;
    token_type: string;
    refresh_token?: string;
}

export const login = async (email: string, password: string): Promise<TokenResponse> => {
    // OAuth2 form-encoded
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const res = await api.post('/auth/token', params);
    return res.data;
};

export const register = async (email: string, password: string, companyName?: string) => {
    const payload: any = { email, password };
    if (companyName) payload.company_name = companyName;
    const res = await api.post('/auth/register', payload);
    return res.data;
};

export const me = async () => {
    const res = await api.get('/auth/me');
    return res.data;
};
