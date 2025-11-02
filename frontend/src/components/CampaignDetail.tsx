import React, { useEffect, useState } from 'react';
import { getCampaignDetail } from '../api/campaigns';
import { CampaignDetail as CampaignDetailType } from '../types/campaign';
import { CampaignSummaryChart, CampaignPeriodsChart, CampaignSitesChart } from './charts';

interface Props {
    campaignId: string;
    onClose?: () => void;
}

const StatCard: React.FC<{ label: string; value: string | number | null }> = ({ label, value }) => (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
        <p className="text-xs text-gray-500">{label}</p>
        <p className="mt-2 text-2xl font-semibold text-gray-800">{value ?? '-'}</p>
    </div>
);

const CampaignDetail: React.FC<Props> = ({ campaignId, onClose }) => {
    const [data, setData] = useState<CampaignDetailType | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState<'tables' | 'charts'>('tables');

    useEffect(() => {
        let mounted = true;
        const load = async () => {
            setLoading(true);
            setError(null);
            try {
                const resp = await getCampaignDetail(campaignId);
                if (!mounted) return;
                setData(resp);
            } catch (e: any) {
                setError(e?.message || 'Error loading campaign detail');
            } finally {
                if (mounted) setLoading(false);
            }
        };
        load();
        return () => { mounted = false; };
    }, [campaignId]);

    if (loading) return <div className="p-6">Loading campaign detail...</div>;
    if (error) return <div className="p-6 text-red-600">{error}</div>;
    if (!data) return <div className="p-6">No detail available</div>;

    const fmt = (n?: number) => (typeof n === 'number' ? n.toLocaleString() : '-');

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="bg-white shadow rounded-lg p-6 relative">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
                    <div>
                        <h1 className="text-3xl font-extrabold text-gray-900">{data.name}</h1>
                        <p className="text-sm text-gray-600 mt-1">{data.tipo_campania} · {new Date(data.fecha_inicio).toLocaleDateString()} — {new Date(data.fecha_fin).toLocaleDateString()}</p>
                    </div>
                    
                    {/* Botones para alternar vista */}
                    <div className="flex bg-gray-100 rounded-lg p-1">
                        <button
                            onClick={() => setViewMode('tables')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                                viewMode === 'tables'
                                    ? 'bg-white text-gray-900 shadow-sm'
                                    : 'text-gray-600 hover:text-gray-900'
                            }`}
                        >
                            Tablas
                        </button>
                        <button
                            onClick={() => setViewMode('charts')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                                viewMode === 'charts'
                                    ? 'bg-white text-gray-900 shadow-sm'
                                    : 'text-gray-600 hover:text-gray-900'
                            }`}
                        >
                            Gráficas
                        </button>
                    </div>
                </div>

                {/* Close button is rendered in Navbar for consistent placement */}

                {/* Summary table (compact) */}
                <div className="mb-6">
                    <div className="bg-white border rounded-lg overflow-hidden">
                        <div className="px-4 py-3 border-b bg-gray-50">
                            <h2 className="text-lg font-semibold text-gray-800">Resumen de campaña</h2>
                        </div>
                        <div className="p-4">
                            <table className="w-full text-sm text-left">
                                <tbody>
                                    <tr className="border-b">
                                        <td className="py-3 text-gray-600 w-1/2">Impactos (Personas)</td>
                                        <td className="py-3 text-gray-900 font-medium text-right">{fmt(data.impactos_personas)}</td>
                                    </tr>
                                    <tr className="border-b">
                                        <td className="py-3 text-gray-600">Impactos (Vehículos)</td>
                                        <td className="py-3 text-gray-900 font-medium text-right">{fmt(data.impactos_vehiculos)}</td>
                                    </tr>
                                    <tr className="border-b">
                                        <td className="py-3 text-gray-600">Alcance</td>
                                        <td className="py-3 text-gray-900 font-medium text-right">{fmt(data.alcance)}</td>
                                    </tr>
                                    <tr>
                                        <td className="py-3 text-gray-600">Frecuencia promedio</td>
                                        <td className="py-3 text-gray-900 font-medium text-right">{data.frecuencia_promedio ?? '-'}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main content */}
                    <div className="lg:col-span-2 space-y-6">
                        {viewMode === 'tables' ? (
                            <>
                                <section className="bg-gray-50 rounded-lg p-4">
                                    <h2 className="text-lg font-semibold text-gray-800 mb-3">Resumen</h2>
                                    <p className="text-sm text-gray-600">Resumen general de la campaña y métricas agregadas por período y sitio.</p>
                                </section>

                                <section>
                                    <h3 className="text-xl font-semibold mb-4">Períodos</h3>
                                    {data.periods && data.periods.length > 0 ? (
                                        <div className="overflow-x-auto rounded-lg border">
                                            <table className="min-w-full divide-y divide-gray-200">
                                                <thead className="bg-gray-100">
                                                    <tr>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Periodo</th>
                                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Impactos Personas</th>
                                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Impactos Vehículos</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="bg-white divide-y divide-gray-100">
                                                    {data.periods.map(p => (
                                                        <tr key={p.id} className="hover:bg-gray-50">
                                                            <td className="px-6 py-3 text-sm text-gray-800">{p.period}</td>
                                                            <td className="px-6 py-3 text-sm text-right text-gray-800">{fmt(p.impactos_periodo_personas)}</td>
                                                            <td className="px-6 py-3 text-sm text-right text-gray-800">{fmt(p.impactos_periodo_vehiculos)}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500">No hay datos de períodos.</p>
                                    )}
                                </section>

                                <section>
                                    <h3 className="text-xl font-semibold mb-4">Sitios</h3>
                                    {data.sites && data.sites.length > 0 ? (
                                        <div className="overflow-x-auto rounded-lg border">
                                            <table className="min-w-full divide-y divide-gray-200">
                                                <thead className="bg-gray-100">
                                                    <tr>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Código</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Tipo mueble</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Tipo anuncio</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Municipio</th>
                                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Impactos mensuales</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="bg-white divide-y divide-gray-100">
                                                    {data.sites.map(s => (
                                                        <tr key={s.id} className="hover:bg-gray-50">
                                                            <td className="px-6 py-3 text-sm text-gray-800">{s.codigo_del_sitio}</td>
                                                            <td className="px-6 py-3 text-sm text-gray-800">{s.tipo_de_mueble}</td>
                                                            <td className="px-6 py-3 text-sm text-gray-800">{s.tipo_de_anuncio}</td>
                                                            <td className="px-6 py-3 text-sm text-gray-800">{s.municipio}</td>
                                                            <td className="px-6 py-3 text-sm text-right text-gray-800">{fmt(s.impactos_mensuales)}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500">No hay datos de sitios.</p>
                                    )}
                                </section>
                            </>
                        ) : (
                            <>
                                <section>
                                    <h3 className="text-xl font-semibold mb-4">Resumen General de Campaña</h3>
                                    <CampaignSummaryChart campaign={data} />
                                </section>

                                <section>
                                    <h3 className="text-xl font-semibold mb-4">Análisis por Períodos</h3>
                                    <CampaignPeriodsChart periods={data.periods} />
                                </section>

                                <section>
                                    <h3 className="text-xl font-semibold mb-4">Análisis de Sitios</h3>
                                    <CampaignSitesChart sites={data.sites} />
                                </section>
                            </>
                        )}
                    </div>

                    {/* Sidebar */}
                    <aside className="space-y-4">
                        <div className="bg-white border rounded-lg p-4 shadow-sm">
                            <h4 className="text-sm font-semibold text-gray-700">Metadatos</h4>
                            <dl className="mt-3 text-sm text-gray-600 space-y-2">
                                <div className="flex justify-between"><dt className="text-gray-500">Universo</dt><dd className="font-medium">{fmt(data.universo_zona_metro)}</dd></div>
                                <div className="flex justify-between"><dt className="text-gray-500">Tipo</dt><dd className="font-medium">{data.tipo_campania}</dd></div>
                                <div className="flex justify-between"><dt className="text-gray-500">Fechas</dt><dd className="font-medium">{new Date(data.fecha_inicio).toLocaleDateString()} — {new Date(data.fecha_fin).toLocaleDateString()}</dd></div>
                            </dl>
                        </div>

                        <div className="bg-white border rounded-lg p-4 shadow-sm">
                            <h4 className="text-sm font-semibold text-gray-700">Acciones</h4>
                            <div className="mt-3 flex flex-col gap-2">
                                <button onClick={() => window.print()} className="w-full text-left px-3 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">Imprimir</button>
                                <a href="#" className="w-full text-left px-3 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">Exportar CSV</a>
                            </div>
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    );
};

export default CampaignDetail;
