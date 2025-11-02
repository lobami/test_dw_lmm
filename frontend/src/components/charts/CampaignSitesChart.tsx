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
import { CampaignSite } from '../../types/campaign';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

interface CampaignSitesChartProps {
    sites: CampaignSite[];
}

export const CampaignSitesChart: React.FC<CampaignSitesChartProps> = ({ sites }) => {
    if (!sites || sites.length === 0) {
        return (
            <div className="bg-white p-8 rounded-lg border shadow-sm text-center">
                <p className="text-gray-500">No hay datos de sitios para mostrar gráficas.</p>
            </div>
        );
    }

    // Agregar datos por tipo de mueble
    const muebleStats = sites.reduce((acc, site) => {
        if (!acc[site.tipo_de_mueble]) {
            acc[site.tipo_de_mueble] = {
                count: 0,
                impactos: 0,
                alcance: 0,
            };
        }
        acc[site.tipo_de_mueble].count += 1;
        acc[site.tipo_de_mueble].impactos += site.impactos_mensuales;
        acc[site.tipo_de_mueble].alcance += site.alcance_mensual;
        return acc;
    }, {} as Record<string, { count: number; impactos: number; alcance: number }>);

    // Agregar datos por estado
    const estadoStats = sites.reduce((acc, site) => {
        if (!acc[site.estado]) {
            acc[site.estado] = {
                count: 0,
                impactos: 0,
            };
        }
        acc[site.estado].count += 1;
        acc[site.estado].impactos += site.impactos_mensuales;
        return acc;
    }, {} as Record<string, { count: number; impactos: number }>);

    // Datos para gráfica de impactos por tipo de mueble
    const muebleLabels = Object.keys(muebleStats);
    const muebleImpactData = {
        labels: muebleLabels,
        datasets: [
            {
                label: 'Impactos Mensuales',
                data: muebleLabels.map(label => muebleStats[label].impactos),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(6, 182, 212, 0.8)',
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(16, 185, 129)',
                    'rgb(245, 158, 11)',
                    'rgb(239, 68, 68)',
                    'rgb(139, 92, 246)',
                    'rgb(6, 182, 212)',
                ],
                borderWidth: 1,
            },
        ],
    };

    const muebleOptions = {
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: true,
                text: 'Impactos por Tipo de Mueble',
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

    // Datos para gráfica de distribución por estado
    const estadoLabels = Object.keys(estadoStats);
    const estadoData = {
        labels: estadoLabels.slice(0, 8), // Mostrar solo los primeros 8 estados
        datasets: [
            {
                data: estadoLabels.slice(0, 8).map(label => estadoStats[label].count),
                backgroundColor: [
                    '#8B5CF6',
                    '#06B6D4',
                    '#10B981',
                    '#F59E0B',
                    '#EF4444',
                    '#6B7280',
                    '#EC4899',
                    '#14B8A6',
                ],
                borderWidth: 2,
                borderColor: '#fff',
            },
        ],
    };

    const estadoOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom' as const,
            },
            title: {
                display: true,
                text: 'Distribución de Sitios por Estado',
            },
        },
    };

    // Top 10 sitios por impactos
    const topSites = [...sites]
        .sort((a, b) => b.impactos_mensuales - a.impactos_mensuales)
        .slice(0, 10);

    const topSitesData = {
        labels: topSites.map(site => site.codigo_del_sitio),
        datasets: [
            {
                label: 'Impactos Mensuales',
                data: topSites.map(site => site.impactos_mensuales),
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderColor: 'rgb(16, 185, 129)',
                borderWidth: 1,
            },
        ],
    };

    const topSitesOptions = {
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: true,
                text: 'Top 10 Sitios por Impactos Mensuales',
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
        indexAxis: 'y' as const,
    };

    return (
        <div className="space-y-6">
            {/* Gráfica de impactos por tipo de mueble */}
            <div className="bg-white p-4 rounded-lg border shadow-sm">
                <Bar data={muebleImpactData} options={muebleOptions} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Distribución por estado */}
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <Doughnut data={estadoData} options={estadoOptions} />
                </div>

                {/* Top sitios */}
                <div className="bg-white p-4 rounded-lg border shadow-sm">
                    <Bar data={topSitesData} options={topSitesOptions} />
                </div>
            </div>
        </div>
    );
};