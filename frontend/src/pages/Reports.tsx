import { useState, useEffect } from 'react';
import {
  FileBarChart2, Download, RefreshCw,
  Eye, Copy, Check, X, Shield, FileText,
  AlertCircle
} from 'lucide-react';
import {
  listJobs, type JobSummaryItem,
  triggerReportDownload, getReportHtmlUrl
} from '../services/api';
import { SectionHeader } from '../components/ui/primitives';

export function Reports() {
  const [jobs, setJobs] = useState<JobSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [customJobId, setCustomJobId] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewJobId, setPreviewJobId] = useState<string | null>(null);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const data = await listJobs();
      setJobs(data || []);
    } catch (err) {
      console.error('Failed to load jobs list:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleCopy = (id: string) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getTaskBadge = (task?: string) => {
    switch (task) {
      case 'change_detection':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#D8893D]/10 text-[#D8893D] border border-[#D8893D]/20">BI-TEMPORAL CHANGE</span>;
      case 'optical_sar':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#0C7C72]/10 text-[#0C7C72] border border-[#0C7C72]/20">OPTICAL + SAR FUSION</span>;
      case 'grounding':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#258A65]/10 text-[#258A65] border border-[#258A65]/20">VRSBENCH GROUNDING</span>;
      case 'area':
      case 'land_cover':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#258A65]/10 text-[#258A65] border border-[#258A65]/20">SEGFORMER LULC</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#F6F7F4] text-[#687277] border border-[#DDE1DD]">EO INTELLIGENCE</span>;
    }
  };

  return (
    <div className="pt-24 px-6 pb-12 max-w-7xl mx-auto space-y-5 font-sans text-xs text-[#111516]">
      {/* ── Header ── */}
      <SectionHeader
        icon={<FileBarChart2 className="w-4 h-4 text-[#0C7C72]" />}
        title="GEOSPATIAL INTELLIGENCE REPORT REGISTRY"
        subtitle="REPORTLAB CERTIFIED ARTIFACTS · INTERACTIVE HTML AUDIT DISPATCHES"
        iconColor="text-[#0C7C72]"
        badge="SYS-07 // REPORTS"
        action={
          <button
            type="button"
            onClick={fetchJobs}
            disabled={loading}
            className="btn-secondary py-1.5 px-3 text-xs flex items-center gap-1.5 cursor-pointer shadow-xs font-medium"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#0C7C72] ${loading ? 'animate-spin' : ''}`} />
            <span>REFRESH REGISTRY</span>
          </button>
        }
      />

      {/* ── Direct Dispatch Lookup ── */}
      <div className="bg-white border border-[#DDE1DD] rounded-xl p-4 shadow-sm space-y-2">
        <span className="font-heading font-semibold text-xs text-[#0C7C72] uppercase tracking-tight flex items-center gap-1.5">
          <Download className="w-3.5 h-3.5" />
          DIRECT REPORT DISPATCH BY JOB ID
        </span>
        <p className="text-[#687277] text-xs">
          Enter any active or past Analysis Job UUID to compile an official geospatial report or open the interactive dispatch preview.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-2 pt-1.5">
          <input
            type="text"
            value={customJobId}
            onChange={(e) => setCustomJobId(e.target.value.trim())}
            placeholder="Paste Job UUID (e.g. 7c32e0bf-1234-4567-890a-bcdef0123456)..."
            className="input-primary flex-1 font-mono text-xs py-2"
          />
          <button
            type="button"
            disabled={!customJobId}
            onClick={() => triggerReportDownload(customJobId)}
            className="btn-primary py-2 px-3.5 text-xs font-heading font-semibold uppercase tracking-wider flex items-center gap-1.5 shrink-0 shadow-xs cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>EXPORT PDF</span>
          </button>
          <button
            type="button"
            disabled={!customJobId}
            onClick={() => {
              setPreviewJobId(customJobId);
              setPreviewUrl(getReportHtmlUrl(customJobId));
            }}
            className="btn-secondary py-2 px-3.5 text-xs font-heading font-semibold uppercase tracking-wider flex items-center gap-1.5 shrink-0 shadow-xs cursor-pointer"
          >
            <Eye className="w-3.5 h-3.5 text-[#0C7C72]" />
            <span>VIEW PREVIEW</span>
          </button>
        </div>
      </div>

      {/* ── Official Report Table ── */}
      <div className="bg-white border border-[#DDE1DD] rounded-xl overflow-hidden shadow-sm">
        <div className="px-4 py-3 bg-[#F6F7F4] border-b border-[#DDE1DD] flex items-center justify-between">
          <span className="font-heading font-semibold text-xs uppercase tracking-tight text-[#111516] flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-[#258A65]" />
            ARCHIVED GEOSPATIAL INTELLIGENCE REPORTS ({jobs.length})
          </span>
          <span className="text-[10px] font-mono text-[#687277] uppercase font-medium">REST ENCRYPTED</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-[#687277] space-y-2">
            <RefreshCw className="w-6 h-6 mx-auto animate-spin text-[#0C7C72]" />
            <p className="text-xs">Scanning registry for completed intelligence jobs…</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-[#687277] space-y-2">
            <AlertCircle className="w-6 h-6 mx-auto opacity-50" />
            <p className="text-xs">No compiled reports found in active registry session.</p>
            <p className="text-[11px] text-[#8B9AA3]">Execute an analysis workflow in the Workstation to generate official dispatches.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-[#F6F7F4] text-[#687277] border-b border-[#DDE1DD] text-[10px] font-mono uppercase">
                <tr>
                  <th className="p-3">REPORT / JOB ID</th>
                  <th className="p-3">TARGET AOI</th>
                  <th className="p-3">ACQUISITION TIMESTAMP</th>
                  <th className="p-3">SATELLITE SENSOR</th>
                  <th className="p-3">ANALYSIS TYPE</th>
                  <th className="p-3">STATUS</th>
                  <th className="p-3 text-right">DISPATCH ACTIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DDE1DD]">
                {jobs.map((job) => (
                  <tr key={job.job_id} className="hover:bg-[#F6F7F4] transition-colors">
                    <td className="p-3 font-mono font-semibold text-[#111516]">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[#0C7C72]">{job.job_id.slice(0, 8)}</span>
                        <button
                          type="button"
                          onClick={() => handleCopy(job.job_id)}
                          className="text-[#687277] hover:text-[#111516] cursor-pointer"
                          title="Copy Full UUID"
                        >
                          {copiedId === job.job_id ? <Check className="w-3 h-3 text-[#258A65]" /> : <Copy className="w-3 h-3" />}
                        </button>
                      </div>
                    </td>
                    <td className="p-3 text-[#111516] truncate max-w-[180px]">
                      {job.query || 'Delhi Urban / Custom AOI'}
                    </td>
                    <td className="p-3 text-[#687277] font-mono text-[11px]">
                      {job.created_at ? new Date(job.created_at).toLocaleString('en-GB', { hour12: false }) : '—'}
                    </td>
                    <td className="p-3 text-[#D8893D] font-mono">
                      Sentinel-2 MSI
                    </td>
                    <td className="p-3">
                      {getTaskBadge(job.task)}
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium ${
                        job.status === 'completed'
                          ? 'bg-[#258A65]/10 text-[#258A65] border border-[#258A65]/20'
                          : job.status === 'running'
                          ? 'bg-[#0C7C72]/10 text-[#0C7C72] border border-[#0C7C72]/20 animate-pulse'
                          : 'bg-[#C84B4B]/10 text-[#C84B4B] border border-[#C84B4B]/20'
                      }`}>
                        ● {job.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          type="button"
                          onClick={() => {
                            setPreviewJobId(job.job_id);
                            setPreviewUrl(getReportHtmlUrl(job.job_id));
                          }}
                          className="px-2.5 py-1 rounded-md bg-[#F6F7F4] hover:bg-[#EEF0EC] border border-[#DDE1DD] text-[#687277] hover:text-[#111516] flex items-center gap-1 text-[11px] font-medium transition-colors cursor-pointer"
                          title="View Official Interactive Report"
                        >
                          <Eye className="w-3 h-3" />
                          <span>PREVIEW</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => triggerReportDownload(job.job_id)}
                          className="px-2.5 py-1 rounded-md bg-[#0C7C72] hover:bg-[#09635B] text-white flex items-center gap-1 text-[11px] font-medium shadow-2xs transition-colors cursor-pointer"
                          title="Export PDF Document"
                        >
                          <Download className="w-3 h-3" />
                          <span>PDF</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Official Report Preview Modal / Drawer ── */}
      {previewUrl && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-[#DDE1DD] rounded-xl w-full max-w-5xl h-[85vh] flex flex-col overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="h-11 bg-[#F6F7F4] border-b border-[#DDE1DD] px-4 flex items-center justify-between text-xs shrink-0">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#258A65]" />
                <span className="font-heading font-semibold text-xs uppercase tracking-tight text-[#111516]">
                  OFFICIAL GEOSPATIAL INTELLIGENCE REPORT DISPATCH · {previewJobId?.slice(0, 8)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                {previewJobId && (
                  <button
                    type="button"
                    onClick={() => triggerReportDownload(previewJobId)}
                    className="btn-primary py-1 px-3 text-xs flex items-center gap-1 font-semibold uppercase cursor-pointer"
                  >
                    <Download className="w-3 h-3" />
                    <span>EXPORT PDF</span>
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setPreviewUrl(null)}
                  className="p-1 rounded-md text-[#687277] hover:text-[#111516] hover:bg-white/80 transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Iframe Viewport */}
            <div className="flex-1 bg-white">
              <iframe
                src={previewUrl}
                title="Geospatial Intelligence Report"
                className="w-full h-full border-none"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
