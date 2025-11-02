import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('../../contexts/AuthContext', () => ({
    useAuth: () => ({
        user: { id: 1, email: 'owner@x.com', role: 'owner' },
        logout: vi.fn(),
    }),
}));

import Navbar from '../Navbar';

describe('Navbar', () => {
    it('renders owner controls and close when on detail', () => {
        // simulate detail path
        Object.defineProperty(window, 'location', {
            value: { pathname: '/campaigns/1' },
            writable: true,
        });

    render(<Navbar />);
    expect(screen.getByText('Gestión usuarios')).toBeDefined();
    // the detail close button has aria-label 'Cerrar detalle'
    expect(screen.getByRole('button', { name: /Cerrar detalle/i })).toBeDefined();
    });

    it('does not show detail close on non-detail path', () => {
        Object.defineProperty(window, 'location', {
            value: { pathname: '/' },
            writable: true,
        });
    render(<Navbar />);
    expect(screen.queryByRole('button', { name: /Cerrar detalle/i })).toBeNull();
    });
});
