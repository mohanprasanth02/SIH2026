import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format bytes to human-readable size */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

/** Format milliseconds to human-readable duration */
export function formatMs(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`;
  const m = Math.floor(ms / 60_000);
  const s = Math.floor((ms % 60_000) / 1000);
  return `${m}m ${s}s`;
}

/** Format a number with commas */
export function formatNumber(n: number): string {
  return n.toLocaleString();
}

/** Format area in km² or ha depending on size */
export function formatArea(km2: number | null | undefined): string {
  if (km2 == null) return 'N/A';
  if (km2 >= 1) return `${km2.toFixed(2)} km²`;
  if (km2 >= 0.01) return `${(km2 * 100).toFixed(2)} ha`;
  return `${(km2 * 1_000_000).toFixed(0)} m²`;
}

/** Convert [R, G, B] to CSS rgb() string */
export function rgbToCSS(rgb: [number, number, number]): string {
  return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
}

/** Get status color class */
export function statusColor(status: string): string {
  const map: Record<string, string> = {
    completed: 'text-emerald-400',
    running:   'text-brand-400',
    failed:    'text-red-400',
    cancelled: 'text-slate-500',
    pending:   'text-amber-400',
  };
  return map[status] || 'text-slate-400';
}

/** Get status badge class */
export function statusBadge(status: string): string {
  const map: Record<string, string> = {
    completed: 'badge-green',
    running:   'badge-blue',
    failed:    'badge-red',
    pending:   'badge-amber',
    cancelled: 'badge-gray',
  };
  return map[status] || 'badge-gray';
}
