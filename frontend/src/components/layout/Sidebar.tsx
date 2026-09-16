import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, ScanSearch, GitCompare, Layers3, Map,
  FileBarChart2, Cpu, Settings, Satellite,
  ChevronLeft, ChevronRight, Activity,
} from 'lucide-react';
import { useAppStore } from '../../stores/useAppStore';
import { cn } from '../../utils/cn';

const navItems = [
  {
    to: '/dashboard',
    icon: LayoutDashboard,
    label: 'Dashboard',
    color: '#6366f1',
    glow: 'rgba(99,102,241,0.4)',
    bg: 'rgba(99,102,241,0.12)',
    border: 'rgba(99,102,241,0.25)',
  },
  {
    to: '/analysis',
    icon: ScanSearch,
    label: 'AI Analysis',
    color: '#a78bfa',
    glow: 'rgba(139,92,246,0.4)',
    bg: 'rgba(139,92,246,0.12)',
    border: 'rgba(139,92,246,0.25)',
  },
  {
    to: '/land-cover',
    icon: Map,
    label: 'Land Cover',
    color: '#2dd4bf',
    glow: 'rgba(45,212,191,0.4)',
    bg: 'rgba(45,212,191,0.12)',
    border: 'rgba(45,212,191,0.25)',
  },
  {
    to: '/change-detection',
    icon: GitCompare,
    label: 'Change Detection',
    color: '#f59e0b',
    glow: 'rgba(245,158,11,0.35)',
    bg: 'rgba(245,158,11,0.10)',
    border: 'rgba(245,158,11,0.22)',
  },
  {
    to: '/optical-sar',
    icon: Layers3,
    label: 'Optical + SAR',
    color: '#22d3ee',
    glow: 'rgba(34,211,238,0.35)',
    bg: 'rgba(34,211,238,0.10)',
    border: 'rgba(34,211,238,0.22)',
  },
  {
    to: '/reports',
    icon: FileBarChart2,
    label: 'Reports',
    color: '#34d399',
    glow: 'rgba(52,211,153,0.35)',
    bg: 'rgba(52,211,153,0.10)',
    border: 'rgba(52,211,153,0.22)',
  },
  {
    to: '/models',
    icon: Cpu,
    label: 'AI Models',
    color: '#f472b6',
    glow: 'rgba(244,114,182,0.35)',
    bg: 'rgba(244,114,182,0.10)',
    border: 'rgba(244,114,182,0.22)',
  },
  {
    to: '/settings',
    icon: Settings,
    label: 'Settings',
    color: '#94a3b8',
    glow: 'rgba(100,116,139,0.3)',
    bg: 'rgba(100,116,139,0.10)',
    border: 'rgba(100,116,139,0.20)',
  },
];

export function GlassSidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();
  const location = useLocation();

  return (
    <motion.aside
      initial={false}
      animate={{ width: sidebarCollapsed ? 72 : 248 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="relative flex flex-col h-full shrink-0 select-none overflow-hidden"
      style={{
        background: 'rgba(4, 6, 18, 0.92)',
        backdropFilter: 'blur(32px)',
        WebkitBackdropFilter: 'blur(32px)',
        borderRight: '1px solid rgba(255,255,255,0.06)',
        zIndex: 50,
      }}
    >
      {/* Top gradient accent line */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.5), rgba(34,211,238,0.3), transparent)' }}
      />

      {/* Ambient glow top */}
      <div className="absolute top-0 left-0 right-0 h-40 pointer-events-none"
        style={{ background: 'linear-gradient(180deg, rgba(99,102,241,0.05) 0%, transparent 100%)' }}
      />

      {/* ── Logo ──────────────────────────────────────────────────────── */}
      <div
        className={cn(
          'flex items-center gap-3 shrink-0 transition-all duration-300',
          sidebarCollapsed ? 'px-[18px] py-5 justify-center' : 'px-5 py-5'
        )}
        style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
      >
        {/* Animated satellite logo */}
        <motion.div
          whileHover={{ rotate: 15, scale: 1.05 }}
          transition={{ type: 'spring', stiffness: 400 }}
          className="relative w-9 h-9 rounded-2xl flex items-center justify-center shrink-0"
          style={{
            background: 'linear-gradient(135deg, #4f46e5, #6366f1, #22d3ee)',
            boxShadow: '0 0 20px rgba(99,102,241,0.5), 0 0 40px rgba(99,102,241,0.2)',
          }}
        >
          <Satellite className="w-4.5 h-4.5 text-white" />
          {/* Pulsing orbit ring */}
          <div
            className="absolute inset-[-4px] rounded-full border border-indigo-400/30 animate-ping"
            style={{ animationDuration: '2.5s' }}
          />
        </motion.div>

        <AnimatePresence mode="wait">
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden min-w-0"
            >
              <div className="text-sm font-bold text-white whitespace-nowrap tracking-wide"
                style={{ fontFamily: 'Outfit, sans-serif' }}>
                SatQuery <span style={{ color: '#a5b4fc' }}>AI</span>
              </div>
              <div className="text-[10px] text-slate-500 whitespace-nowrap mt-0.5 font-mono">
                Remote Sensing Intelligence
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ── Navigation ────────────────────────────────────────────────── */}
      <nav
        className={cn(
          'flex-1 py-3 overflow-y-auto space-y-0.5',
          sidebarCollapsed ? 'px-2' : 'px-3'
        )}
      >
        {navItems.map(({ to, icon: Icon, label, color, glow, bg, border }, idx) => {
          const isActive = location.pathname.startsWith(to);

          return (
            <motion.div
              key={to}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04, duration: 0.3, ease: 'easeOut' }}
            >
              <NavLink to={to} className="block" title={sidebarCollapsed ? label : undefined}>
                <div
                  className={cn(
                    'group flex items-center gap-3 rounded-2xl transition-all duration-250 cursor-pointer relative',
                    sidebarCollapsed ? 'p-2.5 justify-center' : 'px-3 py-2.5',
                    isActive ? 'text-white' : 'text-slate-500 hover:text-slate-200'
                  )}
                  style={isActive ? {
                    background: bg,
                    border: `1px solid ${border}`,
                    boxShadow: `0 0 24px ${glow}, inset 0 1px 0 rgba(255,255,255,0.08)`,
                  } : {
                    border: '1px solid transparent',
                  }}
                  onMouseEnter={e => {
                    if (!isActive) (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.05)';
                  }}
                  onMouseLeave={e => {
                    if (!isActive) (e.currentTarget as HTMLElement).style.background = '';
                  }}
                >
                  {/* Active left bar */}
                  {isActive && !sidebarCollapsed && (
                    <motion.div
                      layoutId="nav-pill"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full"
                      style={{ background: color, boxShadow: `0 0 8px ${glow}` }}
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    />
                  )}

                  <motion.div
                    whileHover={{ scale: isActive ? 1 : 1.12 }}
                    transition={{ type: 'spring', stiffness: 400 }}
                  >
                    <Icon
                      className={cn('shrink-0 transition-all duration-200', sidebarCollapsed ? 'w-5 h-5' : 'w-4 h-4')}
                      style={{ color: isActive ? color : undefined, filter: isActive ? `drop-shadow(0 0 6px ${glow})` : undefined }}
                    />
                  </motion.div>

                  <AnimatePresence mode="wait">
                    {!sidebarCollapsed && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="text-sm font-medium truncate"
                        style={{ fontFamily: 'Inter, sans-serif' }}
                      >
                        {label}
                      </motion.span>
                    )}
                  </AnimatePresence>

                  {/* Tooltip on collapsed */}
                  {sidebarCollapsed && (
                    <div
                      className="absolute left-full ml-3 px-3 py-1.5 rounded-xl text-xs font-medium text-white opacity-0 group-hover:opacity-100 pointer-events-none transition-all duration-150 whitespace-nowrap z-50"
                      style={{
                        background: 'rgba(4,6,18,0.97)',
                        border: `1px solid ${border}`,
                        backdropFilter: 'blur(16px)',
                        boxShadow: `0 8px 32px rgba(0,0,0,0.7), 0 0 12px ${glow}`,
                      }}
                    >
                      {label}
                    </div>
                  )}
                </div>
              </NavLink>
            </motion.div>
          );
        })}
      </nav>

      {/* ── Bottom Status + Collapse ───────────────────────────────────── */}
      <div
        className={cn('shrink-0 space-y-1 p-2', sidebarCollapsed ? 'px-2' : 'px-3')}
        style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
      >
        {/* Live system status */}
        {!sidebarCollapsed && (
          <div
            className="flex items-center gap-2 px-3 py-2 rounded-xl mb-1"
            style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.15)' }}
          >
            <Activity className="w-3 h-3 text-emerald-400 shrink-0" />
            <span className="text-[10px] text-emerald-400 font-medium">System Online</span>
            <span className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
          </div>
        )}

        {/* Version */}
        {!sidebarCollapsed && (
          <div className="px-2 py-1 text-[10px] text-slate-600 font-mono">
            v2.0.0 · SIH 2026
          </div>
        )}

        {/* Collapse toggle */}
        <motion.button
          onClick={toggleSidebar}
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.97 }}
          className={cn(
            'flex items-center justify-center w-full py-2 rounded-xl transition-all duration-150 text-slate-500 hover:text-white',
            !sidebarCollapsed && 'gap-2'
          )}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.06)'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = ''; }}
          title={sidebarCollapsed ? 'Expand' : 'Collapse'}
        >
          {sidebarCollapsed
            ? <ChevronRight className="w-4 h-4" />
            : <><ChevronLeft className="w-4 h-4" /><span className="text-xs font-medium">Collapse</span></>
          }
        </motion.button>
      </div>
    </motion.aside>
  );
}
