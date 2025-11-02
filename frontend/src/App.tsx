import { useState, useEffect } from 'react';
import { CampaignTable } from './components/CampaignTable';
import { DateRangeForm } from './components/DateRangeForm';
import { Campaign } from './types/campaign';
import { getCampaigns, searchCampaignsByDate } from './api/campaigns';
import CampaignDetail from './components/CampaignDetail';
import OwnerUserCreate from './components/OwnerUserCreate';
import { useAuth } from './contexts/AuthContext';
import { Login } from './components/Login';
import Register from './components/Register';
import Navbar from './components/Navbar';

function App() {
    const [campaigns, setCampaigns] = useState<Campaign[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(0);
    const [pageSize] = useState(5);
    const [tipoCampania, setTipoCampania] = useState<string | undefined>();
    const [startDate, setStartDate] = useState<string | undefined>();
    const [endDate, setEndDate] = useState<string | undefined>();
    const [routePath, setRoutePath] = useState<string>(window.location.pathname);
    const { user, loading: authLoading } = useAuth();

    useEffect(() => {
        // Don't attempt to load campaigns when there's no authenticated user.
        if (!user) return;
        loadCampaigns();
    }, [page, pageSize, tipoCampania, user]);

    // Keep React in sync with history API changes (back/forward buttons)
    useEffect(() => {
        const handler = () => setRoutePath(window.location.pathname);
        window.addEventListener('popstate', handler);
        return () => window.removeEventListener('popstate', handler);
    }, []);
    

    const loadCampaigns = async () => {
        try {
            setLoading(true);
            setError(null); // Clear any previous errors
            const response = await getCampaigns(page, pageSize, tipoCampania, startDate, endDate);
            
            if (Array.isArray(response.data)) {
                setCampaigns(response.data);
            } else {
                console.error('Invalid response format:', response);
                setError('Invalid data format received from server');
            }
        } catch (err) {
            console.error('Error in loadCampaigns:', err);
            setError(err instanceof Error ? err.message : 'Error loading campaigns');
            setCampaigns([]); // Reset campaigns on error
        } finally {
            setLoading(false);
        }
    };

    const handleDateRangeSubmit = async (startDate: string, endDate: string) => {
        // Use the paginated API with date filters and reset to page 0
        setStartDate(startDate);
        setEndDate(endDate);
        setPage(0);
        // loadCampaigns will run via the effect
    };

    const handleTipoCampaniaChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const value = event.target.value;
        setTipoCampania(value === '' ? undefined : value);
        setPage(0);
    };

    // Authentication state takes priority: show loading or login first.
    if (authLoading) return <div>Loading...</div>;

    // Simple route handling: if path is /register, show Register page
    if (routePath === '/register') {
        return <Register />;
    }

    if (!user) return <Login />;

    // If the route is a campaign detail, render it as a separate full page
    if (routePath.startsWith('/campaigns/')) {
        const parts = routePath.split('/');
        const campaignId = decodeURIComponent(parts[2] || '');
        if (!campaignId) return <div>Invalid campaign id</div>;
        return (
            <div className="app-container">
                <Navbar />
                <CampaignDetail campaignId={campaignId} />
            </div>
        );
    }

    if (routePath === '/manage-users') {
        return (
            <div className="app-container">
                <Navbar />
                <OwnerUserCreate />
            </div>
        );
    }

    // Only show API errors once the user is authenticated (or attempting to be).
    if (error) {
        return <div className="text-red-600">{error}</div>;
    }

    return (
        <div className="app-container">
            <Navbar />
            <h1 className="app-title">Análisis de campañas</h1>

            <div className="section">
                <h2 className="section-title">Buscar por rango de fechas</h2>
                <DateRangeForm onSubmit={handleDateRangeSubmit} />
            </div>

            <div className="form-group">
                <label htmlFor="tipoCampania">
                    Tipo de campaña
                </label>
                <select
                    id="tipoCampania"
                    value={tipoCampania || ''}
                    onChange={handleTipoCampaniaChange}
                >
                    <option value="">Todos</option>
                    <option value="mensual">Mensual</option>
                    <option value="catorcenal">Catorcenal</option>
                </select>
            </div>

            {loading ? (
                <div>Loading...</div>
            ) : (
                <>
                    <CampaignTable
                        data={campaigns}
                        onRowClick={(campaign) => {
                            // Navigate to a dedicated campaign detail view
                            const id = encodeURIComponent(campaign.name);
                            const newPath = `/campaigns/${id}`;
                            window.history.pushState({}, '', newPath);
                            setRoutePath(newPath);
                        }}
                    />
                    <div className="mt-4 flex justify-between">
                        <button
                            onClick={() => setPage(p => Math.max(0, p - 1))}
                            disabled={page === 0}
                            className="px-4 py-2 border rounded disabled:opacity-50"
                        >
                            Anterior
                        </button>
                        <button
                            onClick={() => setPage(p => p + 1)}
                            disabled={campaigns.length < pageSize}
                            className="px-4 py-2 border rounded disabled:opacity-50"
                        >
                            Siguiente
                        </button>
                    </div>
                </>
            )}
            {/* route-based detail view is rendered as a full page above */}
        </div>
    );
}

export default App;
