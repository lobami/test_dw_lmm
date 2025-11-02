import api from './client';

export interface CreateUserPayload {
    email: string;
    password: string;
    role?: 'admin' | 'viewer';
}

export const createUser = async (payload: CreateUserPayload) => {
    const res = await api.post('/auth/create_user', payload);
    return res.data;
};

export default { createUser };
