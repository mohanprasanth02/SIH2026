// ─── Orbital Command Shared UI Primitives ──────────────────────────────────
// Professional Satellite Earth-Observation & Geospatial Intelligence System
// Light, Minimal, Scientific Aesthetic (Inspired by Earth As The Interface)

import { type ReactNode, type HTMLAttributes, type ButtonHTMLAttributes, useState, useEffect } from 'react';
import { cn } from '../../utils/cn';
import { Activity, AlertTriangle, Crosshair } from 'lucide-react';

// ─── GlassCard / OrbitalPanel (Pure White Surface with Crisp Border) ───────
interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hover?: boolean;
  glow?: 'blue' | 'indigo' | 'cyan' | 'violet' | 'teal' | 'amber' | 'emerald' | 'none';
  padding?: 'sm' | 'md' | 'lg' | 'none';
  neon?: boolean;
}

export function GlassCard({
  children, className, hover = false, glow = 'none', padding = 'md', neon = false, ...props
}: GlassCardProps) {
  const paddingMap = { sm: 'p-3', md: 'p-4', lg: 'p-5', none: '' };
  const glowBorder = glow === 'amber' ? 'border-[#D8893D]/40' : (glow === 'none' ? 'border-[#DDE1DD]' : 'border-[#0C7C72]/30');

  return (
    <div
      className={cn(
        'bg-white rounded-lg border shadow-sm transition-all duration-150',
        glowBorder,
        paddingMap[padding],
        hover && 'hover:border-[#0C7C72]/40 hover:shadow-md cursor-default',
        neon && 'border-[#0C7C72]/40 shadow-sm',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// ─── FloatingPanel ──────────────────────────────────────────────────────────
export function FloatingPanel({ children, className, ...props }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div className={cn('bg-white/95 backdrop-blur-md border border-[#DDE1DD] rounded-lg p-4 shadow-[0_4px_20px_rgba(0,0,0,0.06)]', className)} {...props}>
      {children}
    </div>
  );
}

// ─── GlowButton ─────────────────────────────────────────────────────────────
interface GlowButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function GlowButton({
  children, className, variant = 'primary', size = 'md', ...props
}: GlowButtonProps) {
  const variantMap: Record<string, string> = {
    primary:   'btn-primary',
    secondary: 'btn-secondary',
    ghost:     'btn-ghost',
    danger:    'inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md font-mono text-xs font-semibold text-[#C84B4B] bg-[#C84B4B]/10 border border-[#C84B4B]/30 hover:bg-[#C84B4B]/15 transition-all cursor-pointer',
  };
  const sizeMap: Record<string, string> = { sm: '!px-2.5 !py-1 !text-xs', md: '', lg: '!px-5 !py-2.5 !text-sm' };

  return (
    <button className={cn(variantMap[variant], sizeMap[size], className)} {...props}>
      {children}
    </button>
  );
}

// ─── SectionHeader ──────────────────────────────────────────────────────────
interface SectionHeaderProps {
  icon?: ReactNode;
  title: string;
  subtitle?: string;
  iconBg?: string;
  iconColor?: string;
  action?: ReactNode;
  className?: string;
  badge?: string;
}

export function SectionHeader({
  icon, title, subtitle, iconColor = 'text-[#0C7C72]', action, className, badge,
}: SectionHeaderProps) {
  return (
    <div className={cn('flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-[#DDE1DD] pb-3.5 mb-5', className)}>
      <div className="flex items-center gap-2.5 min-w-0">
        {icon && (
          <div className={cn('w-7 h-7 rounded-md bg-[#EEF0EC] border border-[#DDE1DD] flex items-center justify-center shrink-0', iconColor)}>
            {icon}
          </div>
        )}
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="font-heading font-semibold text-base sm:text-lg text-[#111516] tracking-tight truncate">
              {title}
            </h1>
            {badge && (
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-[#0C7C72]/10 text-[#0C7C72] border border-[#0C7C72]/20 tracking-wide uppercase">
                {badge}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-[#687277] font-sans truncate mt-0.5">{subtitle}</p>
          )}
        </div>
      </div>
      {action && <div className="flex items-center gap-2 shrink-0">{action}</div>}
    </div>
  );
}

// ─── StatusBadge ────────────────────────────────────────────────────────────
export function StatusBadge({ status, className }: { status: string; className?: string }) {
  const s = status.toLowerCase();
  let badgeCls = 'badge-gray';
  let dotCls = 'bg-[#687277]';
  let label = status.toUpperCase();

  if (s === 'completed' || s === 'available' || s === 'ready' || s === 'loaded') {
    badgeCls = 'badge-green';
    dotCls = 'bg-[#258A65]';
    label = s === 'completed' ? 'READY / COMPLETED' : label;
  } else if (s === 'running' || s === 'processing') {
    badgeCls = 'badge-cyan';
    dotCls = 'bg-[#0C7C72] animate-pulse';
    label = 'RUNNING';
  } else if (s === 'pending' || s === 'beta' || s === 'starting') {
    badgeCls = 'badge-amber';
    dotCls = 'bg-[#D8893D] animate-pulse';
    label = 'STANDBY';
  } else if (s === 'failed' || s === 'error') {
    badgeCls = 'badge-red';
    dotCls = 'bg-[#C84B4B]';
    label = 'ALERT / FAILED';
  }

  return (
    <span className={cn('badge', badgeCls, className)}>
      <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', dotCls)} />
      {label}
    </span>
  );
}

// ─── AnimatedMetric ─────────────────────────────────────────────────────────
interface AnimatedMetricProps {
  value: string | number | null;
  label: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: ReactNode;
  accentColor?: string;
  loading?: boolean;
  className?: string;
}

export function AnimatedMetric({
  value, label, trend, trendValue, icon, accentColor = '#0C7C72', loading = false, className,
}: AnimatedMetricProps) {
  return (
    <div className={cn('bg-white border border-[#DDE1DD] rounded-lg p-3 relative flex flex-col justify-between shadow-xs', className)}>
      <div className="flex items-center justify-between text-[#687277] mb-1">
        <span className="font-sans text-[11px] font-medium tracking-wide uppercase text-[#687277]">
          {label}
        </span>
        {icon && <span style={{ color: accentColor }} className="opacity-80">{icon}</span>}
      </div>

      <div className="flex items-baseline gap-2 mt-0.5">
        {loading ? (
          <div className="h-6 w-20 shimmer rounded" />
        ) : (
          <span className="font-mono text-xl font-bold tracking-tight text-[#111516]">
            {value ?? '—'}
          </span>
        )}
        {trendValue && (
          <span className={cn(
            'text-[10px] font-mono font-medium',
            trend === 'up' ? 'text-[#258A65]' : trend === 'down' ? 'text-[#C84B4B]' : 'text-[#687277]'
          )}>
            {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '■'} {trendValue}
          </span>
        )}
      </div>
    </div>
  );
}

// ─── AIIndicator ─────────────────────────────────────────────────────────────
interface AIIndicatorProps {
  active?: boolean;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  stage?: string;
}

export function AIIndicator({ active = true, size = 'md', label, stage }: AIIndicatorProps) {
  const px = { sm: 28, md: 44, lg: 56 }[size];

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative flex items-center justify-center" style={{ width: px, height: px }}>
        <div
          className="absolute inset-0 rounded-full border border-[#0C7C72]/30"
          style={{
            animation: active ? 'spin 4s linear infinite' : 'none',
          }}
        />
        <Crosshair className={cn('text-[#0C7C72]', active && 'animate-pulse')} style={{ width: px * 0.55, height: px * 0.55 }} />
      </div>

      {(label || stage) && (
        <div className="text-center font-mono">
          {label && <p className="text-xs font-semibold text-[#111516] tracking-wide">{label}</p>}
          {stage && <p className="text-[10px] text-[#0C7C72] mt-0.5">{stage}</p>}
        </div>
      )}
    </div>
  );
}

// ─── EmptyStateCanvas ────────────────────────────────────────────────────────
interface EmptyStateCanvasProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyStateCanvas({ icon, title, description, action, className }: EmptyStateCanvasProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16 px-6 text-center bg-white border border-dashed border-[#DDE1DD] rounded-lg m-2', className)}>
      <div className="w-12 h-12 rounded-lg bg-[#EEF0EC] border border-[#DDE1DD] flex items-center justify-center text-[#0C7C72] mb-3">
        {icon}
      </div>
      <h3 className="font-heading text-sm font-semibold tracking-tight text-[#111516] mb-1.5">
        {title}
      </h3>
      <p className="text-xs text-[#687277] max-w-md leading-relaxed mb-4 font-sans">
        {description}
      </p>
      {action}
    </div>
  );
}

// ─── ErrorState ──────────────────────────────────────────────────────────────
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex items-start gap-3 p-3.5 rounded-lg bg-[#C84B4B]/10 border border-[#C84B4B]/30 text-xs">
      <AlertTriangle className="w-4 h-4 text-[#C84B4B] shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0 font-mono">
        <p className="font-bold text-[#C84B4B] uppercase tracking-wide mb-0.5">Telemetry / Inference Alert</p>
        <p className="text-[#111516]/90 leading-relaxed break-words">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="shrink-0 text-[11px] font-mono text-[#C84B4B] hover:bg-[#C84B4B]/20 border border-[#C84B4B]/30 px-2 py-1 rounded transition-colors cursor-pointer"
        >
          RETRY
        </button>
      )}
    </div>
  );
}

// ─── LoadingPulse ─────────────────────────────────────────────────────────────
export function LoadingPulse({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="shimmer rounded h-3.5"
          style={{ width: i === 0 ? '75%' : i === 1 ? '90%' : '60%' }}
        />
      ))}
    </div>
  );
}

// ─── CounterMetric ────────────────────────────────────────────────────────────
interface CounterMetricProps {
  end: number;
  duration?: number;
  suffix?: string;
  prefix?: string;
  label: string;
  color?: string;
  icon?: ReactNode;
}

export function CounterMetric({ end, duration = 1000, suffix = '', prefix = '', label, color = '#0C7C72', icon }: CounterMetricProps) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const step = end / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= end) { setCount(end); clearInterval(timer); }
      else setCount(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [end, duration]);

  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-1.5 text-[11px] font-sans text-[#687277] uppercase tracking-wide mb-1">
        {icon && <span style={{ color }}>{icon}</span>}
        <span>{label}</span>
      </div>
      <div className="font-mono text-xl font-bold tracking-tight" style={{ color }}>
        {prefix}{count.toLocaleString()}{suffix}
      </div>
    </div>
  );
}

// ─── PipelineProgress ────────────────────────────────────────────────────────
interface PipelineStage {
  id: string;
  label: string;
  status: 'done' | 'active' | 'pending';
}

export function PipelineProgress({ stages }: { stages: PipelineStage[] }) {
  return (
    <div className="space-y-1.5 font-mono">
      {stages.map((s, i) => (
        <div key={s.id} className={cn('pipeline-stage', s.status)}>
          <div className="w-3.5 h-3.5 rounded-sm flex items-center justify-center shrink-0 text-[9px] font-bold border border-current">
            {s.status === 'done' ? '✓' : i + 1}
          </div>
          <span className="text-[11px] truncate">{s.label}</span>
          {s.status === 'active' && (
            <Activity className="w-3 h-3 ml-auto animate-pulse text-[#0C7C72] shrink-0" />
          )}
        </div>
      ))}
    </div>
  );
}
