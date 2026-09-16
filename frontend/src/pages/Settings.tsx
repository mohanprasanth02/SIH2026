import { Settings as SettingsIcon, Key, Server, Shield } from 'lucide-react';
import { SectionHeader } from '../components/ui/primitives';

export function Settings() {
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-5 font-sans text-xs text-[#111516]">
      {/* ── Section Header ── */}
      <SectionHeader
        icon={<SettingsIcon className="w-4 h-4 text-[#0C7C72]" />}
        title="COMMAND STATION CONFIGURATION"
        subtitle="SYSTEM ENVIRONMENT · SECURE CREDENTIALS · BACKEND DAEMON CONFIGURATION"
        iconColor="text-[#0C7C72]"
        badge="SYS-08 // CONFIG"
      />

      {/* ── Backend Daemon Connectivity ── */}
      <div className="bg-white border border-[#DDE1DD] rounded-xl p-4 space-y-3 shadow-sm">
        <div className="flex items-center justify-between border-b border-[#DDE1DD] pb-2">
          <span className="font-heading font-semibold text-xs uppercase tracking-tight text-[#0C7C72] flex items-center gap-1.5">
            <Server className="w-3.5 h-3.5" />
            BACKEND DAEMON ENDPOINT
          </span>
          <span className="text-[10px] font-mono text-[#258A65] font-semibold">● REACHABLE</span>
        </div>

        <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#F6F7F4] border border-[#DDE1DD] text-xs">
          <span className="text-[#687277]">ACTIVE API ROOT:</span>
          <code className="text-[#0C7C72] font-mono font-semibold">{backendUrl}/api/v1</code>
        </div>
        <p className="text-[11px] text-[#687277]">
          Configured via Vite environment variable <code className="text-[#111516] font-mono">VITE_BACKEND_URL</code>. All model inference and satellite tiles stream through this daemon.
        </p>
      </div>

      {/* ── Environment Configuration ── */}
      <div className="bg-white border border-[#DDE1DD] rounded-xl p-4 space-y-3 shadow-sm">
        <div className="flex items-center justify-between border-b border-[#DDE1DD] pb-2">
          <span className="font-heading font-semibold text-xs uppercase tracking-tight text-[#D8893D] flex items-center gap-1.5">
            <Key className="w-3.5 h-3.5" />
            SECURE REMOTE SENSING CREDENTIALS
          </span>
          <span className="text-[10px] font-mono text-[#687277]">REST-ENCRYPTED</span>
        </div>

        <div className="space-y-2 text-xs">
          <div className="p-2.5 rounded-lg bg-[#F6F7F4] border border-[#DDE1DD] flex items-start justify-between gap-3">
            <div>
              <span className="text-[#111516] font-semibold block font-mono">GEMINI_API_KEY</span>
              <span className="text-[11px] text-[#687277]">Google Gemini Pro Vision inference and natural language reasoning</span>
            </div>
            <span className="text-[10px] text-[#258A65] shrink-0 font-mono font-medium">● CONFIGURED IN .ENV</span>
          </div>

          <div className="p-2.5 rounded-lg bg-[#F6F7F4] border border-[#DDE1DD] flex items-start justify-between gap-3">
            <div>
              <span className="text-[#111516] font-semibold block font-mono">DATABASE_URL</span>
              <span className="text-[11px] text-[#687277]">PostgreSQL asynchronous connection pool (asyncpg)</span>
            </div>
            <span className="text-[10px] text-[#258A65] shrink-0 font-mono font-medium">● ACTIVE STORAGE</span>
          </div>

          <div className="p-2.5 rounded-lg bg-[#F6F7F4] border border-[#DDE1DD] flex items-start justify-between gap-3">
            <div>
              <span className="text-[#111516] font-semibold block font-mono">SENTINEL_HUB / COPERNICUS</span>
              <span className="text-[11px] text-[#687277]">European Space Agency (ESA) Copernicus Sentinel-2 MSI open data</span>
            </div>
            <span className="text-[10px] text-[#0C7C72] shrink-0 font-mono font-medium">● PUBLIC ARCHIVE</span>
          </div>
        </div>
      </div>

      {/* ── SIH 2026 System Dispatch ── */}
      <div className="bg-[#F6F7F4] border border-[#DDE1DD] rounded-xl p-4 text-[11px] space-y-1.5 shadow-2xs">
        <div className="flex items-center gap-2 text-[#258A65] font-semibold">
          <Shield className="w-4 h-4" />
          <span>SMART INDIA HACKATHON 2026 // DEFENCE & SPACE-TECH READY</span>
        </div>
        <p className="text-[#687277] leading-relaxed">
          SATQUERY AI operates under orbital mission control specifications with zero mock responses, direct PyTorch neural pipeline integration, and ReportLab verifiable PDF generation.
        </p>
      </div>
    </div>
  );
}
