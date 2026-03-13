import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import RunQualityChart from '../RunQualityChart';

describe('RunQualityChart', () => {
    it('renders the fallback text when no data is provided', () => {
        render(<RunQualityChart coverageData={[]} qualityData={[]} />);
        expect(screen.getByText('No chart data available')).toBeInTheDocument();
    });

    it('renders the ECharts canvas when data is provided', () => {
        const { container } = render(
            <RunQualityChart coverageData={[30, 32]} qualityData={[35, 36]} />
        );
        // ReactECharts renders an echarts-for-react class wrapper
        expect(container.querySelector('.echarts-for-react')).toBeInTheDocument();
    });
});