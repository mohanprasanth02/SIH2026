import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Satellite, Wifi, WifiOff,
  SlidersHorizontal
} from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';
import { cn } from '../../utils/cn';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Overview' },
  { to: '/analysis', label: 'Analysis' },
  { to: '/change-detection', label: 'Change' },
  { to: '/land-cover', label: 'Land Cover' },
  { to: '/optical-sar', label: 'Sensors' },
  { to: '/reports', label: 'Reports' },
];

export function TopCommandBar() {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [utcTime, setUtcTime] = useState('');
  const { primaryImage } = useAppStore();

  useEffect(() => {
    const updateClocks = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().slice(17, 22) + ' UTC');
    };
    updateClocks();
    const id = setInterval(updateClocks, 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/api/v1/health`);
        setBackendOnline(res.ok);
      } catch {
        setBackendOnline(false);
      }
    };
    check();
    const id = setInterval(check, 15_000);
    return () => clearInterval(id);
  }, []);

  const activeAoi = primaryImage?.metadata?.is_georeferenced
    ? (primaryImage.metadata.bounds_wgs84
        ? `${primaryImage.metadata.bounds_wgs84.lat_min.toFixed(2)}°N, ${primaryImage.metadata.bounds_wgs84.lon_min.toFixed(2)}°E`
        : primaryImage.original_filename)
    : 'Delhi Urban · 28.614°N';

  return (
    <header className="absolute top-4 left-0 right-0 z-40 px-6 pointer-events-none">
      <div className="max-w-7xl mx-auto flex items-center justify-between pointer-events-auto">
        
        {/* Left: Brand Identity in Floating Capsule */}
        <div className="flex items-center gap-3 bg-white/90 backdrop-blur-md px-4 py-2 rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-white/60">
          <NavLink to="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-7 h-7 rounded-xl bg-[#16877F] text-white flex items-center justify-center shadow-xs transition-transform group-hover:scale-105">
              <Satellite className="w-4 h-4" />
            </div>
            <span className="font-heading font-semibold text-sm tracking-tight text-[#151918]">
              SATQUERY
            </span>
          </NavLink>

          <span className="h-3 w-px bg-[#DDE1DD] mx-1" />

          <div className="hidden sm:flex items-center gap-1.5 text-[11px] font-sans text-[#737B78]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#258A65]" />
            <span className="font-mono text-[#151918]">{activeAoi}</span>
          </div>
        </div>

        {/* Center: Minimal Floating Navigation with Generous Whitespace */}
        <nav className="hidden md:flex items-center gap-1 bg-white/90 backdrop-blur-md px-2 py-1.5 rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-white/60">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'px-3.5 py-1.5 rounded-xl text-xs font-sans transition-all',
                  isActive
                    ? 'font-semibold text-[#151918] bg-[#F7F8F5] shadow-2xs'
                    : 'text-[#737B78] hover:text-[#151918] hover:bg-black/[0.02]'
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Right: Telemetry & Controls */}
        <div className="flex items-center gap-2.5 bg-white/90 backdrop-blur-md px-3.5 py-2 rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-white/60 text-xs">
          <span className="font-mono text-[11px] text-[#737B78] hidden sm:inline">
            {utcTime}
          </span>

          <div
            className="flex items-center gap-1 text-[11px] font-sans"
            title={backendOnline ? 'Telemetry online' : 'Offline'}
          >
            {backendOnline ? (
              <span className="flex items-center gap-1 text-[#16877F] font-medium">
                <Wifi className="w-3 h-3" />
                <span className="hidden lg:inline text-[10px]">ONLINE</span>
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[#C84B4B] font-medium">
                <WifiOff className="w-3 h-3" />
                <span className="hidden lg:inline text-[10px]">STANDBY</span>
              </span>
            )}
          </div>

          <NavLink
            to="/settings"
            className="p-1 text-[#737B78] hover:text-[#151918] hover:bg-black/[0.03] rounded-lg transition-colors"
            title="Station Settings"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
          </NavLink>
        </div>

      </div>
    </header>
  );
}
