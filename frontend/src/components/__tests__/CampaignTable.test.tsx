import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CampaignTable } from '../CampaignTable';
import { Campaign } from '../../types/campaign';

describe('CampaignTable', () => {
    const sample: Campaign[] = [
        {
            id: 1,
            name: 'Campaña A',
            tipo_campania: 'mensual',
            fecha_inicio: '2023-01-01',
            fecha_fin: '2023-01-31',
            impactos_personas: 1000,
            impactos_vehiculos: 2000,
            alcance: 800,
        } as any,
    ];

    it('renders headers and rows', () => {
        render(<CampaignTable data={sample} />);
        expect(screen.getByText('Nombre')).toBeDefined();
        expect(screen.getByText('Campaña A')).toBeDefined();
        expect(screen.getByText('mensual')).toBeDefined();
    });

    it('calls onRowClick when a row is clicked', () => {
        const onRowClick = vi.fn();
        render(<CampaignTable data={sample} onRowClick={onRowClick} />);
        const row = screen.getByText('Campaña A').closest('tr') as HTMLElement;
        fireEvent.click(row);
        expect(onRowClick).toHaveBeenCalledTimes(1);
        expect(onRowClick).toHaveBeenCalledWith(expect.objectContaining({ name: 'Campaña A' }));
    });
});
