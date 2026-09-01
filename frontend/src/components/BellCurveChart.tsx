'use client';

import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendingUp, User } from 'lucide-react';

interface BellCurveChartProps {
  diseaseName: string;
  userPercentile: number;
  userZScore: number;
}

export const BellCurveChart: React.FC<BellCurveChartProps> = ({
  diseaseName,
  userPercentile,
  userZScore,
}) => {
  // Generate Gaussian normal distribution points from -3.5 to +3.5 SD
  const data = React.useMemo(() => {
    const points = [];
    for (let z = -3.5; z <= 3.5; z += 0.1) {
      // Normal probability density: (1 / sqrt(2pi)) * exp(-z^2 / 2)
      const density = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * z * z);
      // Approximate percentile
      const p = 50 * (1 + Math.sign(z) * Math.sqrt(1 - Math.exp(-2 * z * z / Math.PI)));
      points.push({
        zScore: parseFloat(z.toFixed(1)),
        density: parseFloat(density.toFixed(4)),
        percentile: parseFloat(p.toFixed(1)),
      });
    }
    return points;
  }, []);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4 text-brand-600" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800">
              Population Risk Distribution — {diseaseName}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Analytic normal CDF relative to reference population.
          </p>
        </div>

        <div className="flex items-center space-x-2 rounded-xl bg-brand-50 border border-brand-200 px-3 py-1.5 self-start sm:self-auto">
          <User className="h-4 w-4 text-brand-600" />
          <div className="text-xs font-bold text-brand-900">
            Your Position:{' '}
            <span className="text-brand-600 font-extrabold">{userPercentile.toFixed(1)}th</span> %ile{' '}
            <span className="text-[11px] text-slate-500 font-medium">(Z = {userZScore > 0 ? `+${userZScore}` : userZScore})</span>
          </div>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="bellGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="zScore"
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              tick={{ fontSize: 11, fill: '#64748b' }}
              tickFormatter={(v) => (v === 0 ? 'Mean (50%)' : `${v > 0 ? '+' : ''}${v} SD`)}
            />
            <YAxis hide domain={[0, 0.45]} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const pt = payload[0].payload;
                  return (
                    <div className="rounded-lg border border-slate-200 bg-white p-2 text-xs shadow-md">
                      <p className="font-bold text-slate-800">Z-score: {pt.zScore} SD</p>
                      <p className="text-slate-600">Approx. {pt.percentile}th Percentile</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area
              type="monotone"
              dataKey="density"
              stroke="#2563eb"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#bellGradient)"
            />
            {/* User marker reference line */}
            <ReferenceLine
              x={userZScore}
              stroke="#e11d48"
              strokeWidth={2.5}
              strokeDasharray="3 3"
              label={{
                value: `You (${userPercentile.toFixed(0)}%)`,
                position: 'top',
                fill: '#e11d48',
                fontSize: 11,
                fontWeight: 'bold',
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="flex justify-between items-center text-[11px] font-semibold text-slate-500 px-2 mt-2">
        <span className="text-emerald-600">Lower Genetic Risk (&lt; 20%)</span>
        <span>Average Risk (50%)</span>
        <span className="text-rose-600">Elevated Genetic Risk (&gt; 80%)</span>
      </div>
    </div>
  );
};
