import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock useAuth so the component thinks an owner is logged in
vi.mock('../../contexts/AuthContext', () => ({
    useAuth: () => ({
        user: { id: 1, email: 'owner@x.com', role: 'owner' },
        logout: vi.fn(),
    }),
}));

import OwnerUserCreate from '../OwnerUserCreate';

describe('OwnerUserCreate', () => {
    it('renders form fields and close button', () => {
        render(<OwnerUserCreate />);
        expect(screen.getByLabelText(/Correo/i)).toBeDefined();
        expect(screen.getByLabelText(/Contraseña/i)).toBeDefined();
        expect(screen.getByLabelText(/Rol/i)).toBeDefined();
        expect(screen.getByRole('button', { name: /Cerrar/i })).toBeDefined();
    });

    it('calls history.back when close is clicked', () => {
        const backSpy = vi.spyOn(window.history, 'back');
        render(<OwnerUserCreate />);
        const btn = screen.getByRole('button', { name: /Cerrar/i });
        fireEvent.click(btn);
        expect(backSpy).toHaveBeenCalled();
        backSpy.mockRestore();
    });
});
