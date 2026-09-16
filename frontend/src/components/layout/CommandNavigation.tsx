import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanSearch,
  GitCompare,
  Layers3,
  Map,
  FileBarChart2,
  Cpu,
  Settings,
  ChevronLeft,
  ChevronRight,
  Radio,
} from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';
import { cn } from '../../utils/cn';

const NAV_ITEMS = [
  {
    to: '/dashboard',
    icon: LayoutDashboard,
    label: 'OVERVIEW',
    code: '01',
    description: 'Mission Control & Geospatial Map',
  },
  {
    to: '/analysis',
    icon: ScanSearch,
    label: 'ANALYSIS',
    code: '02',
    description: 'EO Analysis Workstation',
  },
  {
    to: '/change-detection',
    icon: GitCompare,
    label: 'CHANGE DETECTION',
    code: '03',
    description: 'Bi-Temporal Comparison',
  },
  {
    to: '/optical-sar',
    icon: Layers3,
    label: 'OPTICAL + SAR',
    code: '04',
    description: 'Multimodal Sensor Fusion',
  },
  {
    to: '/land-cover',
    icon: Map,
    label: 'LAND COVER',
    code: '05',
    description: 'SegFormer Classification',
  },
  {
    to: '/models',
    icon: Cpu,
    label: 'AI MODELS',
    code: '06',
    description: 'Model Registry & Compute',
  },
  {
    to: '/reports',
    icon: FileBarChart2,
    label: 'REPORTS',
    code: '07',
    description: 'Intelligence Reports & Exports',
  },
  {
    to: '/settings',
    icon: Settings,
    label: 'SETTINGS',
    code: '08',
    description: 'Station Configuration',
  },
];

export function CommandNavigation() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();

  return (
    <nav
      className={cn(
        'shrink-0 h-full bg-white border-r border-[#DDE1DD] flex flex-col justify-between select-none transition-all duration-200 z-20 shadow-xs',
        sidebarCollapsed ? 'w-14' : 'w-56'
      )}
    >
      {/* ── Nav Rail Header ── */}
      <div className="flex flex-col">
        <div className="h-10 flex items-center justify-between px-3.5 border-b border-[#DDE1DD] text-[10px] font-mono text-[#687277]">
          {!sidebarCollapsed && <span className="uppercase tracking-wider font-medium">OPERATIONAL MODULES</span>}
          <button
            type="button"
            onClick={toggleSidebar}
            className="p-1 rounded text-[#687277] hover:text-[#111516] hover:bg-[#F6F7F4] transition-colors ml-auto cursor-pointer"
            title={sidebarCollapsed ? 'Expand Navigation' : 'Collapse Navigation'}
          >
            {sidebarCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* ── Nav Items ── */}
        <div className="py-2 space-y-1 px-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                title={sidebarCollapsed ? `${item.label} (${item.description})` : undefined}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-all relative group',
                    isActive
                      ? 'bg-[#EEF0EC] text-[#0C7C72] font-semibold shadow-2xs'
                      : 'text-[#687277] hover:text-[#111516] hover:bg-[#F6F7F4]'
                  )
                }
              >
                <Icon className="w-4 h-4 shrink-0 transition-colors" />
                {!sidebarCollapsed && (
                  <div className="flex items-center justify-between w-full min-w-0">
                    <span className="font-heading tracking-wide truncate text-[11px]">
                      {item.label}
                    </span>
                    <span className="font-mono text-[10px] text-[#8B9AA3] group-hover:text-[#687277]">
                      {item.code}
                    </span>
                  </div>
                )}
              </NavLink>
            );
          })}
        </div>
      </div>

      {/* ── Nav Rail Footer: Station / SIH 2026 Telemetry ── */}
      <div className="p-2.5 border-t border-[#DDE1DD] font-mono text-[10px]">
        {!sidebarCollapsed ? (
          <div className="bg-[#F6F7F4] p-2.5 rounded-lg border border-[#DDE1DD] space-y-1">
            <div className="flex items-center justify-between text-[#687277]">
              <span className="flex items-center gap-1.5 font-medium text-[10px] text-[#111516]">
                <Radio className="w-3 h-3 text-[#258A65]" />
                TELEMETRY
              </span>
              <span className="text-[#258A65] font-semibold text-[9px]">ONLINE</span>
            </div>
            <div className="text-[9px] text-[#687277] truncate">
              SIH 2026 // EO-PLATFORM
            </div>
          </div>
        ) : (
          <div className="flex justify-center" title="SIH 2026 Remote Sensing Telemetry Online">
            <span className="w-2 h-2 rounded-full bg-[#258A65]" />
          </div>
        )}
      </div>
    </nav>
  );
}
