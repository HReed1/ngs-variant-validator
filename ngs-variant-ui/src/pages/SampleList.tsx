import { Link } from 'react-router-dom';
import { useSamples } from '../hooks/useSamples';

export default function SampleList() {
    const { data: samples, isLoading, isError } = useSamples();

    if (isLoading) return <div className="p-4 text-gray-500">Loading pipeline data...</div>;
    if (isError) return <div className="p-4 text-red-600">Failed to securely fetch data from API.</div>;

    return (
        <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl">
            <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Sample ID</th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Patient Hash (De-identified)</th>
                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Runs</th>
                        <th className="relative py-3.5 pl-3 pr-4"><span className="sr-only">View</span></th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                    {samples?.map((sample) => (
                        <tr key={sample.sample_id} className="hover:bg-gray-50">
                            <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900">
                                {sample.sample_id}
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500 font-mono">
                                {sample.patient_hash.substring(0, 12)}...
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                <div className="flex gap-2">
                                    {sample.runs.map((run) => (
                                        <span key={run.run_id} className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                                            {run.assay_type}
                                        </span>
                                    ))}
                                </div>
                            </td>
                            <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium">
                                <Link to={`/samples/${sample.sample_id}`} className="text-blue-600 hover:text-blue-900">
                                    View Analysis<span className="sr-only">, {sample.sample_id}</span>
                                </Link>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}