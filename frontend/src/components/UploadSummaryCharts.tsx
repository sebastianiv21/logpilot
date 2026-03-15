import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { UploadResult } from '../lib/schemas';

const BAR_COLORS = { Processed: 'hsl(var(--su))', Skipped: 'hsl(var(--wa))', Parsed: 'hsl(var(--su))', Rejected: 'hsl(var(--er))' };

export function UploadSummaryCharts({ result }: { result: UploadResult | null }) {
  if (!result || result.status === 'failed') return null;

  const filesData = [
    { name: 'Files', Processed: result.files_processed, Skipped: result.files_skipped },
  ];
  const linesData = [
    { name: 'Lines', Parsed: result.lines_parsed, Rejected: result.lines_rejected },
  ];
  const totalLines = result.lines_parsed + result.lines_rejected;
  const coveragePct = totalLines > 0
    ? Math.round((result.lines_parsed / totalLines) * 100)
    : 0;

  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3"
      role="img"
      aria-label={`Upload summary: ${result.files_processed} files processed, ${result.files_skipped} skipped; ${result.lines_parsed} lines parsed, ${result.lines_rejected} rejected; ${coveragePct}% parsed coverage`}
    >
      <div>
        <p className="text-sm font-medium text-base-content/80 mb-1">Files</p>
        <ResponsiveContainer width="100%" height={80}>
          <BarChart data={filesData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip
              formatter={(value) => [value ?? 0, '']}
              contentStyle={{ fontSize: 12 }}
            />
            <Bar dataKey="Processed" stackId="a" fill={BAR_COLORS.Processed} name="Processed" />
            <Bar dataKey="Skipped" stackId="a" fill={BAR_COLORS.Skipped} name="Skipped" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div>
        <p className="text-sm font-medium text-base-content/80 mb-1">Lines</p>
        <ResponsiveContainer width="100%" height={80}>
          <BarChart data={linesData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip
              formatter={(value) => [value ?? 0, '']}
              contentStyle={{ fontSize: 12 }}
            />
            <Bar dataKey="Parsed" stackId="b" fill={BAR_COLORS.Parsed} name="Parsed" />
            <Bar dataKey="Rejected" stackId="b" fill={BAR_COLORS.Rejected} name="Rejected" />
          </BarChart>
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
