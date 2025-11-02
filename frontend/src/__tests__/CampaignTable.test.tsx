import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CampaignTable } from '../components/CampaignTable';
import { Campaign } from '../types/campaign';

describe('CampaignTable', () => {
  it('renders rows and calls onRowClick when a row is clicked', () => {
    const data: Campaign[] = [
      {
        name: 'campania_test',
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
      }
    ];

    const onRowClick = vi.fn();

    render(<CampaignTable data={data} onRowClick={onRowClick} />);

    // The campaign name should be visible
    expect(screen.getByText('campania_test')).toBeInTheDocument();

    // Click the row (click the cell text will bubble up to row)
    fireEvent.click(screen.getByText('campania_test'));

    expect(onRowClick).toHaveBeenCalledTimes(1);
    expect(onRowClick).toHaveBeenCalledWith(expect.objectContaining({ name: 'campania_test' }));
  });
});
