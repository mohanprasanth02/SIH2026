import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Search, Wifi, WifiOff, Satellite, Zap, ChevronRight } from 'lucide-react';

const PAGE_META: Record<string, { label: string; subtitle: string; color: string; icon: string }> = {
  '/dashboard':        { label: 'Mission Control',   subtitle: 'Real-time satellite telemetry & AI analytics',          color: '#6366f1', icon: '🛰️' },
  '/analysis':         { label: 'AI Analysis',        subtitle: 'Intelligent image interpretation powered by Gemini',    color: '#a78bfa', icon: '🔍' },
  '/land-cover':       { label: 'Land Cover',          subtitle: 'SegFormer semantic segmentation · Pixel classification', color: '#2dd4bf', icon: '🗺️' },
  '/change-detection': { label: 'Change Detection',   subtitle: 'Temporal change quantification & mapping',              color: '#f59e0b', icon: '⚡' },
  '/optical-sar':      { label: 'Optical + SAR Fusion', subtitle: 'Multimodal sensor fusion analysis',                  color: '#22d3ee', icon: '📡' },
  '/reports':          { label: 'Reports',             subtitle: 'Analysis artifacts & export management',               color: '#34d399', icon: '📊' },
  '/models':           { label: 'AI Models',           subtitle: 'Model registry & compute environment',                  color: '#f472b6', icon: '🤖' },
  '/settings':         { label: 'Settings',            subtitle: 'System configuration & API management',                color: '#94a3b8', icon: '⚙️' },
};

function MissionClock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const hh = time.getHours().toString().padStart(2, '0');
  const mm = time.getMinutes().toString().padStart(2, '0');
  const ss = time.getSeconds().toString().padStart(2, '0');

  return (
    <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl"
      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}>
      <Satellite className="w-3 h-3 text-indigo-400 shrink-0" />
      <span className="font-mono text-xs text-slate-300 tracking-wider">
        {hh}<span className="text-indigo-400 animate-pulse mx-0.5">:</span>{mm}<span className="text-indigo-400 animate-pulse mx-0.5">:</span>{ss}
      </span>
      <span className="text-[9px] text-slate-600 font-medium">IST</span>
    </div>
  );
}

export function GlassTopbar() {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [searchFocused, setSearchFocused] = useState(false);
  const [searchVal, setSearchVal] = useState('');
  const location = useLocation();

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

  const pageInfo = PAGE_META[location.pathname] ?? { label: 'SatQuery AI', subtitle: '', color: '#6366f1', icon: '🛰️' };

  // Build breadcrumb
  const crumbs = location.pathname.split('/').filter(Boolean);

  return (
    <header
      className="h-14 shrink-0 flex items-center justify-between px-5 gap-4 relative"
      style={{
        background: 'rgba(4, 6, 18, 0.88)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        zIndex: 40,
      }}
    >
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-px"
        style={{ background: 'linear-gradient(90deg, transparent 0%, rgba(99,102,241,0.3) 30%, rgba(34,211,238,0.2) 70%, transparent 100%)' }}
      />

      {/* ── Left: breadcrumb + page title ── */}
      <div className="flex items-center gap-3 min-w-0">
        {/* Breadcrumb */}
        <div className="hidden sm:flex items-center gap-1 text-[11px] text-slate-600">
          <span className="text-slate-500">SatQuery</span>
          {crumbs.map((c, i) => (
            <span key={i} className="flex items-center gap-1">
              <ChevronRight className="w-3 h-3" />
              <span style={{ color: i === crumbs.length - 1 ? pageInfo.color : undefined }}
                className="capitalize">
                {c.replace('-', ' ')}
              </span>
            </span>
          ))}
        </div>

        {/* Divider */}
        <div className="hidden sm:block w-px h-4" style={{ background: 'rgba(255,255,255,0.08)' }} />

        {/* Page title */}
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 6 }}
            transition={{ duration: 0.2 }}
            className="flex items-center gap-2 min-w-0"
          >
            <span className="text-sm shrink-0">{pageInfo.icon}</span>
            <div className="min-w-0">
              <h2 className="text-sm font-bold text-white truncate leading-none" style={{ fontFamily: 'Outfit, sans-serif' }}>
                {pageInfo.label}
              </h2>
              <p className="text-[10px] text-slate-500 truncate hidden md:block mt-0.5 leading-none">
                {pageInfo.subtitle}
              </p>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* ── Center: Search ── */}
      <div className="flex-1 max-w-sm hidden md:flex items-center">
        <div className="relative w-full">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder="Search analyses… (⌘K)"
            value={searchVal}
            onChange={e => setSearchVal(e.target.value)}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            className="w-full h-8 pl-9 pr-4 text-xs text-white placeholder-slate-500 outline-none transition-all duration-250 rounded-xl"
            style={{
              background: searchFocused ? 'rgba(8,12,28,0.9)' : 'rgba(255,255,255,0.04)',
              border: searchFocused
                ? '1px solid rgba(99,102,241,0.5)'
                : '1px solid rgba(255,255,255,0.07)',
              boxShadow: searchFocused ? '0 0 0 3px rgba(99,102,241,0.12)' : 'none',
            }}
          />
        </div>
      </div>

      {/* ── Right: status + actions ── */}
      <div className="flex items-center gap-2 shrink-0">
        <MissionClock />

        {/* Backend connectivity */}
        <motion.div
          animate={backendOnline === true ? {
            boxShadow: ['0 0 0 0 rgba(16,185,129,0.4)', '0 0 0 6px rgba(16,185,129,0)', '0 0 0 0 rgba(16,185,129,0)']
          } : {}}
          transition={{ repeat: Infinity, duration: 2 }}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-medium"
          style={{
            background: backendOnline === true
              ? 'rgba(16,185,129,0.08)'
              : backendOnline === false
              ? 'rgba(244,63,94,0.08)'
              : 'rgba(100,116,139,0.08)',
            border: backendOnline === true
              ? '1px solid rgba(16,185,129,0.25)'
              : backendOnline === false
              ? '1px solid rgba(244,63,94,0.25)'
              : '1px solid rgba(100,116,139,0.15)',
            color: backendOnline === true ? '#34d399' : backendOnline === false ? '#fb7185' : '#64748b',
          }}
          title={backendOnline === true ? 'Backend online' : 'Backend offline'}
        >
          {backendOnline === false
            ? <WifiOff className="w-3 h-3" />
            : <Wifi className="w-3 h-3" />
          }
          <span className="hidden sm:inline text-[11px]">
            {backendOnline === null ? 'Connecting…' : backendOnline ? 'API Online' : 'API Offline'}
          </span>
          {backendOnline === true && (
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          )}
        </motion.div>

        {/* AI active badge */}
        <div
          className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl"
          style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)' }}
        >
          <Zap className="w-3 h-3 text-indigo-400" />
          <span className="text-[11px] text-indigo-300 font-medium">Gemini Pro</span>
        </div>

        {/* Notifications */}
        <motion.button
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.95 }}
          className="relative w-8 h-8 rounded-xl flex items-center justify-center text-slate-400 hover:text-white transition-colors duration-150"
          style={{ border: '1px solid rgba(255,255,255,0.08)' }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.07)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = ''; }}
        >
          <Bell className="w-4 h-4" />
          <span
            className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full animate-pulse"
            style={{ background: '#6366f1', boxShadow: '0 0 6px rgba(99,102,241,0.8)' }}
          />
        </motion.button>

        {/* User avatar */}
        <div className="flex items-center gap-2 pl-2"
          style={{ borderLeft: '1px solid rgba(255,255,255,0.07)' }}>
          <motion.div
            whileHover={{ scale: 1.08 }}
            className="w-7 h-7 rounded-xl flex items-center justify-center text-[10px] font-bold text-white shrink-0 cursor-pointer"
            style={{
              background: 'linear-gradient(135deg, #4f46e5, #6366f1, #22d3ee)',
              boxShadow: '0 0 14px rgba(99,102,241,0.4)',
              fontFamily: 'Outfit, sans-serif',
            }}
          >
            SQ
          </motion.div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-white leading-none" style={{ fontFamily: 'Outfit, sans-serif' }}>Analyst</div>
            <div className="text-[10px] text-slate-500 mt-0.5">SIH 2026</div>
          </div>
        </div>
      </div>
    </header>
  );
}
