import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
// Add the 'type' keyword here
import type { Sample } from '../types/api';

interface FetchSamplesParams {
    skip?: number;
    limit?: number;
    assay_type?: string;
}

export const useSamples = (params: FetchSamplesParams = { skip: 0, limit: 50 }) => {
    return useQuery({
        queryKey: ['samples', params],
        queryFn: async (): Promise<Sample[]> => {
            const { data } = await apiClient.get('/samples/', { params });
            return data;
        },
        refetchInterval: 10000,
    });
};

export const useSampleDetail = (sampleId: string) => {
    return useQuery({
        queryKey: ['sample', sampleId],
        queryFn: async (): Promise<Sample> => {
            const { data } = await apiClient.get(`/samples/${sampleId}`);
            return data;
        },
        enabled: !!sampleId,
    });
};