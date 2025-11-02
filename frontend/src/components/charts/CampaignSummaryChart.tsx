import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Campaign } from '../../types/campaign';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

interface CampaignSummaryChartProps {
    campaign: Campaign;
}

export const CampaignSummaryChart: React.FC<CampaignSummaryChartProps> = ({ campaign }) => {
    // Gráfica de barras para impactos y alcance
    const impactData = {
        labels: ['Impactos Personas', 'Impactos Vehículos', 'Alcance'],
        datasets: [
            {
                label: 'Métricas de Campaña',
                data: [campaign.impactos_personas, campaign.impactos_vehiculos, campaign.alcance],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)', 
                    'rgba(245, 158, 11, 0.8)',
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(16, 185, 129)',
                    'rgb(245, 158, 11)',
                ],
                borderWidth: 1,
            },
        ],
    };

    const impactOptions = {
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: true,
                text: 'Resumen de Impactos y Alcance',
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

    // Gráfica de dona para distribución demográfica por NSE
    const nseData = {
        labels: ['NSE AB', 'NSE C', 'NSE C+', 'NSE D', 'NSE D+', 'NSE E'],
        datasets: [
            {
                data: [
                    campaign.nse_ab,
                    campaign.nse_c,
                    campaign.nse_cmas,
                    campaign.nse_d,
                    campaign.nse_dmas,
                    campaign.nse_e,
                ],
                backgroundColor: [
                    '#8B5CF6',
                    '#06B6D4',
                    '#10B981',
                    '#F59E0B',
                    '#EF4444',
                    '#6B7280',
                ],
                borderWidth: 2,
                borderColor: '#fff',
            },
        ],
    };

    const nseOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom' as const,
            },
            title: {
                display: true,
                text: 'Distribución por Nivel Socioeconómico',
            },
        },
    };

    // Gráfica de dona para distribución por género
    const genderData = {
        labels: ['Hombres', 'Mujeres'],
        datasets: [
            {
                data: [campaign.hombres, campaign.mujeres],
                backgroundColor: ['#3B82F6', '#EC4899'],
                borderWidth: 2,
                borderColor: '#fff',
            },
        ],
    };

    const genderOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom' as const,
            },
            title: {
                display: true,
                text: 'Distribución por Género',
            },
        },
    };

    return (
        <div className="space-y-6">
            {/* Gráfica de impactos */}
            <div className="bg-white p-4 rounded-lg border shadow-sm">
                <Bar data={impactData} options={impactOptions} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Gráfica de NSE */}
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <Doughnut data={nseData} options={nseOptions} />
                </div>

                {/* Gráfica de género */}
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <Doughnut data={genderData} options={genderOptions} />
                </div>
            </div>
        </div>
    );
};