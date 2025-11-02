import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { CampaignPeriod } from '../../types/campaign';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend
);

interface CampaignPeriodsChartProps {
    periods: CampaignPeriod[];
}

export const CampaignPeriodsChart: React.FC<CampaignPeriodsChartProps> = ({ periods }) => {
    if (!periods || periods.length === 0) {
        return (
            <div className="bg-white p-8 rounded-lg border shadow-sm text-center">
                <p className="text-gray-500">No hay datos de períodos para mostrar gráficas.</p>
            </div>
        );
    }

    // Ordenar períodos por nombre para mostrar cronológicamente
    const sortedPeriods = [...periods].sort((a, b) => a.period.localeCompare(b.period));

    // Gráfica de barras comparativa
    const barData = {
        labels: sortedPeriods.map(p => p.period),
        datasets: [
            {
                label: 'Impactos Personas',
                data: sortedPeriods.map(p => p.impactos_periodo_personas),
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: 'rgb(59, 130, 246)',
                borderWidth: 1,
            },
            {
                label: 'Impactos Vehículos',
                data: sortedPeriods.map(p => p.impactos_periodo_vehiculos),
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderColor: 'rgb(16, 185, 129)',
                borderWidth: 1,
            },
        ],
    };

    const barOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: true,
                text: 'Impactos por Período',
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value: any) {
                        return new Intl.NumberFormat().format(value);
                    }
                }
            },
        },
    };

    // Gráfica de líneas para tendencias
    const lineData = {
        labels: sortedPeriods.map(p => p.period),
        datasets: [
            {
                label: 'Impactos Personas',
                data: sortedPeriods.map(p => p.impactos_periodo_personas),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                tension: 0.1,
            },
            {
                label: 'Impactos Vehículos',
                data: sortedPeriods.map(p => p.impactos_periodo_vehiculos),
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                tension: 0.1,
            },
        ],
    };

    const lineOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: true,
                text: 'Tendencia de Impactos a lo Largo del Tiempo',
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value: any) {
                        return new Intl.NumberFormat().format(value);
                    }
                }
            },
        },
    };

    return (
        <div className="space-y-6">
            {/* Gráfica de barras */}
            <div className="bg-white p-4 rounded-lg border shadow-sm">
                <Bar data={barData} options={barOptions} />
            </div>

            {/* Gráfica de líneas */}
            <div className="bg-white p-4 rounded-lg border shadow-sm">
                <Line data={lineData} options={lineOptions} />
            </div>
        </div>
    );
};