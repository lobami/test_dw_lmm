import api from './client';
import { Campaign, CampaignDetail } from '../types/campaign';

export const getCampaigns = async (
    page: number,
    pageSize: number,
    tipoCampania?: string,
    startDate?: string,
    endDate?: string
): Promise<{ data: Campaign[]; total: number }> => {
    const skip = page * pageSize;
    const params = new URLSearchParams({
        skip: skip.toString(),
        limit: pageSize.toString(),
        ...(tipoCampania && { tipo_campania: tipoCampania }),
        ...(startDate && { start_date: startDate }),
        ...(endDate && { end_date: endDate }),
    });

    const response = await api.get(`/campaigns/?${params}`);
    return response.data;
};

export const getCampaignDetail = async (campaignId: string): Promise<CampaignDetail> => {
    const response = await api.get(`/campaigns/${campaignId}`);
    return response.data;
};

export const searchCampaignsByDate = async (
    startDate: string,
    endDate: string
): Promise<Campaign[]> => {
    const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
    });

    const response = await api.get(`/campaigns/search-by-date/?${params}`);
    return response.data;
};
