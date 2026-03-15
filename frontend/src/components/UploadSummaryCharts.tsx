import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { UploadResult } from '../lib/schemas';

/** Explicit colors that stay visible in both light and dark theme (DaisyUI --su/--wa/--er are too dark in dark mode). */
const COLORS = {
  Processed: 'hsl(142, 76%, 46%)',   // green
  Skipped: 'hsl(38, 92%, 50%)',     // amber
  Parsed: 'hsl(142, 76%, 46%)',     // green
  Rejected: 'hsl(0, 84%, 60%)',     // red
} as const;

/** Theme-aware tooltip so label and value are readable in light and dark mode */
function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="bg-base-200 text-base-content border border-base-300 rounded-lg px-3 py-2 shadow-lg text-sm"
      role="tooltip"
    >
      {label && <p className="font-medium mb-1">{label}</p>}
      <ul className="space-y-0.5">
        {payload.map((entry) => (
          <li key={entry.name} className="flex items-center gap-2">
            <span
              className="inline-block w-2 h-2 rounded-full shrink-0"
              style={{ backgroundColor: entry.color }}
              aria-hidden
            />
            <span>{entry.name}:</span>
            <span className="font-medium tabular-nums">{entry.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function UploadSummaryCharts({ result }: { result: UploadResult | null }) {
  if (!result || result.status === 'failed') return null;

  const filesData = [
    { name: 'Processed', value: result.files_processed, color: COLORS.Processed },
    { name: 'Skipped', value: result.files_skipped, color: COLORS.Skipped },
  ].filter((d) => d.value > 0);

  const linesData = [
    { name: 'Parsed', value: result.lines_parsed, color: COLORS.Parsed },
    { name: 'Rejected', value: result.lines_rejected, color: COLORS.Rejected },
  ].filter((d) => d.value > 0);

  const totalLines = result.lines_parsed + result.lines_rejected;
  const coveragePct =
    totalLines > 0 ? Math.round((result.lines_parsed / totalLines) * 100) : 0;

  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3"
      role="img"
      aria-label={`Upload summary: ${result.files_processed} files processed, ${result.files_skipped} skipped; ${result.lines_parsed} lines parsed, ${result.lines_rejected} rejected; ${coveragePct}% parsed coverage`}
    >
      <div>
        <p className="text-sm font-medium text-base-content/80 mb-1">Files</p>
        <ResponsiveContainer width="100%" height={160}>
          <PieChart>
            <Pie
              data={filesData.length ? filesData : [{ name: 'None', value: 1, color: 'hsl(var(--b3))' }]}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={60}
              paddingAngle={2}
              dataKey="value"
              nameKey="name"
            >
              {filesData.length
                ? filesData.map((entry, i) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))
                : <Cell fill="hsl(var(--b3))" />}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12 }}
              formatter={(value, entry) => (
                <span className="text-base-content">{value}</span>
              )}
              iconType="circle"
              iconSize={8}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div>
        <p className="text-sm font-medium text-base-content/80 mb-1">Lines</p>
        <ResponsiveContainer width="100%" height={160}>
          <PieChart>
            <Pie
              data={linesData.length ? linesData : [{ name: 'None', value: 1, color: 'hsl(var(--b3))' }]}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={60}
              paddingAngle={2}
              dataKey="value"
              nameKey="name"
            >
              {linesData.length
                ? linesData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))
                : <Cell fill="hsl(var(--b3))" />}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12 }}
              formatter={(value) => (
                <span className="text-base-content">{value}</span>
              )}
              iconType="circle"
              iconSize={8}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="sm:col-span-2">
        <p className="text-sm font-medium text-base-content/80 mb-1">Parsed coverage</p>
        <div className="flex items-center gap-2">
          <div
            className="flex-1 h-6 rounded-full bg-base-300 overflow-hidden"
            role="progressbar"
            aria-valuenow={coveragePct}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Parsed coverage ${coveragePct}%`}
          >
            <div
              className="h-full bg-success transition-all duration-300"
              style={{ width: `${coveragePct}%` }}
            />
          </div>
          <span className="text-sm font-medium tabular-nums">{coveragePct}%</span>
        </div>
      </div>
    </div>
  );
}
