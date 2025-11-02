import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// mock API
vi.mock('../../api/campaigns', () => ({
    getCampaignDetail: async (id: string) => ({
        id: 1,
        name: 'Campaña Prueba',
        tipo_campania: 'mensual',
        fecha_inicio: '2023-01-01',
        fecha_fin: '2023-01-31',
        impacto_personas: 100,
        impacto_vehiculos: 200,
        impacto: 300,
        impacto_mensual: 150,
        impacto_sites: 50,
        impacto_periods: 40,
        impacto_total: 500,
        impacto_promedio: 10,
        impacto_promedio_sites: 5,
        impacto_promedio_periods: 4,
        impacto_mediana: 2,
        impacto_desviacion: 1,
        universo_zona_metro: 10000,
        impacto_personas_por_municipio: [],
        periods: [],
        sites: [],
    } as any),
}));

import CampaignDetail from '../CampaignDetail';

describe('CampaignDetail', () => {
    it('renders data from API', async () => {
        render(<CampaignDetail campaignId="1" />);
        await waitFor(() => expect(screen.getByText('Campaña Prueba')).toBeDefined());
        expect(screen.getByText(/Resumen de campaña/i)).toBeDefined();
    });
});
