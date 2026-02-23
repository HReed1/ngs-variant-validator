import RunQualityChart from '../components/RunQualityChart';
import { useParams, Link } from 'react-router-dom';
import { useSampleDetail } from '../hooks/useSamples';
// import ReactECharts from 'echarts-for-react'; // Uncomment when ready to build the chart

export default function RunDetail() {
    const { sampleId } = useParams<{ sampleId: string }>();
    const { data: sample, isLoading, isError } = useSampleDetail(sampleId!);

    if (isLoading) return <div className="p-4 text-gray-500">Fetching run details...</div>;
    if (isError || !sample) return <div className="p-4 text-red-600">Failed to load run details.</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4">
                <Link to="/samples" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                    &larr; Back to Samples
                </Link>
                <h2 className="text-2xl font-bold tracking-tight text-gray-900">
                    Analysis: {sample.sample_id}
                </h2>
            </div>

            {sample.runs.map((run) => (
                <div key={run.run_id} className="overflow-hidden bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl">
                    <div className="border-b border-gray-200 bg-gray-50 px-4 py-5 sm:px-6 flex justify-between items-center">
                        <h3 className="text-base font-semibold leading-6 text-gray-900">
                            Run: {run.run_id}
                        </h3>
                        <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                            {run.assay_type}
                        </span>
                    </div>

                    <div className="px-4 py-5 sm:p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Metadata Section (1/3 Width) */}
                        <div className="lg:col-span-1">
                            <h4 className="text-sm font-medium text-gray-500 mb-4">Run Metadata</h4>
                            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2 lg:grid-cols-1">
                                {Object.entries(run.metadata_col)
                                    // Explicitly filter out the visualization arrays so they don't render as text
                                    .filter(([key]) => key !== 'coverage_profile' && key !== 'quality_profile')
                                    .map(([key, value]) => (
                                        <div key={key} className="sm:col-span-1">
                                            <dt className="text-sm font-medium text-gray-500 capitalize">{key.replace('_', ' ')}</dt>
                                            <dd className="mt-1 text-sm text-gray-900 break-words">{String(value)}</dd>
                                        </div>
                                    ))}
                            </dl>
                        </div>

                        {/* Visualization Component (2/3 Width) */}
                        <div className="lg:col-span-2 lg:border-l lg:border-gray-200 lg:pl-6">
                            <h4 className="text-sm font-medium text-gray-500 mb-4">Quality Metrics</h4>
                            <div className="h-80 w-full bg-white rounded flex items-center justify-center">
                                <RunQualityChart
                                    coverageData={run.metadata_col?.coverage_profile}
                                    qualityData={run.metadata_col?.quality_profile}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}