import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DateRangeForm } from '../DateRangeForm';

describe('DateRangeForm', () => {
    it('submits start and end dates', async () => {
        const onSubmit = vi.fn();
        const { container } = render(<DateRangeForm onSubmit={onSubmit} />);

        const start = screen.getByLabelText(/Fecha inicio/i) as HTMLInputElement;
        const end = screen.getByLabelText(/Fecha fin/i) as HTMLInputElement;

    // use 'input' event which works more reliably with date inputs in jsdom
    fireEvent.input(start, { target: { value: '2023-01-01' } });
    fireEvent.input(end, { target: { value: '2023-01-10' } });
    // submit the form directly to avoid date input quirks in jsdom
    const form = container.querySelector('form') as HTMLFormElement;
    fireEvent.submit(form);

    // resolver is async; wait for handler to be called
    await new Promise((r) => setTimeout(r, 0));
    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith('2023-01-01', '2023-01-10');
    });

    it('shows validation error when end < start', async () => {
        const onSubmit = vi.fn();
        const { container } = render(<DateRangeForm onSubmit={onSubmit} />);

        const start = screen.getByLabelText(/Fecha inicio/i) as HTMLInputElement;
        const end = screen.getByLabelText(/Fecha fin/i) as HTMLInputElement;

        fireEvent.change(start, { target: { value: '2023-01-10' } });
        fireEvent.change(end, { target: { value: '2023-01-01' } });
        const form = container.querySelector('form') as HTMLFormElement;
        fireEvent.submit(form);

        // validation runs and should show the error
        await screen.findByText(/La fecha de fin/);
        expect(onSubmit).not.toHaveBeenCalled();
    });
});
