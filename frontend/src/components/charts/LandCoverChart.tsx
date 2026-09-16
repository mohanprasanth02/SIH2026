import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import type { ClassStatistic } from '../../services/api';
import { rgbToCSS, formatArea } from '../../utils/cn';

interface Props {
  stats: ClassStatistic[];
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ name: string; value: number; payload: ClassStatistic }> }) => {
  if (!active || !payload?.length) return null;
  const cls = payload[0].payload;
  return (
    <div className="glass-darker px-3 py-2 rounded-lg text-xs shadow-xl">
      <p className="font-semibold text-white">{cls.label}</p>
      <p className="text-slate-300">{cls.percentage.toFixed(2)}%</p>
      {cls.area_km2 != null && (
        <p className="text-slate-400">{formatArea(cls.area_km2)}</p>
      )}
      <p className="text-slate-500 mt-1">
        {cls.pixel_count.toLocaleString()} pixels
      </p>
    </div>
  );
};

export function LandCoverChart({ stats }: Props) {
  // Filter out classes with 0 pixels for the chart
  const data = stats
    .filter((s) => s.pixel_count > 0)
    .sort((a, b) => b.percentage - a.percentage);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
        No classification data
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Donut chart */}
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={2}
              dataKey="percentage"
              nameKey="label"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={rgbToCSS(entry.color)}
                  stroke="rgba(0,0,0,0.2)"
                  strokeWidth={1}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Stats table */}
      <div className="space-y-2">
        {data.map((s) => (
          <div key={s.class_id} className="flex items-center gap-3">
            {/* Color swatch */}
            <div
              className="w-3 h-3 rounded-sm shrink-0"
              style={{ background: rgbToCSS(s.color) }}
            />
            {/* Label */}
            <span className="text-xs text-slate-300 flex-1 truncate">{s.label}</span>
            {/* Bar */}
            <div className="w-24 h-1.5 rounded-full bg-dark-700 overflow-hidden shrink-0">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${s.percentage}%`,
                  background: rgbToCSS(s.color),
                }}
              />
            </div>
            {/* Percentage */}
            <span className="text-xs font-mono text-white w-12 text-right shrink-0">
              {s.percentage.toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
