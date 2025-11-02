import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import CampaignDetail from '../components/CampaignDetail';

// Mock the API module used by CampaignDetail
vi.mock('../api/campaigns', () => ({
  getCampaignDetail: async (id: string) => ({
    name: id,
    tipo_campania: 'mensual',
    fecha_inicio: '2023-01-01',
    fecha_fin: '2023-01-31',
    universo_zona_metro: 0,
    impactos_personas: 100,
    impactos_vehiculos: 50,
    frecuencia_calculada: 1,
    frecuencia_promedio: 1,
    alcance: 10,
    nse_ab: 0,
    nse_c: 0,
    nse_cmas: 0,
    nse_d: 0,
    nse_dmas: 0,
    nse_e: 0,
    edad_0a14: 0,
    edad_15a19: 0,
    edad_20a24: 0,
    edad_25a34: 0,
    edad_35a44: 0,
    edad_45a64: 0,
    edad_65mas: 0,
    hombres: 0,
    mujeres: 0,
    periods: [
      { id: 1, campaign_name: id, period: 'P1', impactos_periodo_personas: 10, impactos_periodo_vehiculos: 5 }
    ],
    sites: [
      { id: 1, campaign_name: id, codigo_del_sitio: 'S1', tipo_de_mueble: 'M', tipo_de_anuncio: 'A', estado: 'E', municipio: 'Mcp', zm: 'Z', frecuencia_catorcenal: 0, frecuencia_mensual: 0, impactos_catorcenal: 0, impactos_mensuales: 0, alcance_mensual: 0 }
    ]
  })
}));

describe('CampaignDetail', () => {
  it('renders campaign detail after fetching', async () => {
    render(<CampaignDetail campaignId="campania_test" />);

    // Wait for the campaign name to appear
    const nameElem = await screen.findByText('campania_test');
    expect(nameElem).toBeInTheDocument();

    // Period and site should be present
    expect(screen.getByText('Períodos')).toBeInTheDocument();
    expect(screen.getByText('Sitios')).toBeInTheDocument();
    expect(screen.getByText('P1')).toBeInTheDocument();
    expect(screen.getByText('S1')).toBeInTheDocument();
  });
});
