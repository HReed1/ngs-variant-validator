import ReactECharts from 'echarts-for-react';

interface RunQualityChartProps {
    coverageData?: number[];
    qualityData?: number[];
}

export default function RunQualityChart({ coverageData = [], qualityData = [] }: RunQualityChartProps) {
    if (!coverageData.length) {
        return <div className="flex h-full items-center justify-center text-gray-400">No chart data available</div>;
    }

    // Create the X-axis array (e.g., representing genomic windows or time)
    const xAxisData = Array.from({ length: coverageData.length }, (_, i) => i + 1);

    const option = {
        tooltip: {
            trigger: 'axis',
        },
        legend: {
            data: ['Depth of Coverage (x)', 'Phred Quality Score'],
            bottom: 0,
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            top: '10%',
            containLabel: true,
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: xAxisData,
        },
        yAxis: [
            {
                type: 'value',
                name: 'Coverage',
                position: 'left',
            },
            {
                type: 'value',
                name: 'Quality',
                position: 'right',
                max: 40, // Standard max Phred score
            }
        ],
        series: [
            {
                name: 'Depth of Coverage (x)',
                type: 'line',
                data: coverageData,
                smooth: true,
                itemStyle: { color: '#3b82f6' }, // Blue
                areaStyle: { color: 'rgba(59, 130, 246, 0.1)' },
            },
            {
                name: 'Phred Quality Score',
                type: 'line',
                yAxisIndex: 1,
                data: qualityData,
                smooth: true,
                itemStyle: { color: '#10b981' }, // Green
            },
        ],
    };

    return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />;
}