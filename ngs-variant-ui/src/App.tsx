import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SampleList from './pages/SampleList';
import RunDetail from './pages/RunDetail';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 text-slate-900 font-sans">
        <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
          <h1 className="text-xl font-bold tracking-tight text-blue-900">
            NGS Variant Validator
          </h1>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/samples" element={<SampleList />} />
            <Route path="/samples/:sampleId" element={<RunDetail />} />
            <Route path="*" element={<Navigate to="/samples" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}