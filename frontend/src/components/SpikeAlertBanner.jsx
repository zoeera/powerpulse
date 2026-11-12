import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export default function SpikeAlertBanner({ spikes = [], onResolve }) {
  const unresolved = spikes.filter(s => !s.is_resolved);
  if (!unresolved || unresolved.length === 0) return null;

  return (
    <div className="space-y-3 mb-6">
      {unresolved.map((spike) => (
        <div
          key={spike.id}
          className="bg-rose-950/40 border border-rose-500/50 rounded-2xl p-4 shadow-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
        >
          <div className="flex items-start space-x-3">
            <div className="p-2 rounded-xl bg-rose-500/20 text-rose-300 mt-0.5 border border-rose-500/30">
              <AlertCircle className="w-5 h-5 text-rose-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  {spike.spike_type === 'hourly' ? 'High Power Usage' : 'Unexpected Bill Jump'}
                </span>
                <span className="text-xs font-bold text-rose-300">
                  +{spike.deviation_pct}% Higher Than Usual
                </span>
              </div>
              <p className="text-sm font-semibold text-white mt-1">{spike.message}</p>
              <p className="text-xs text-rose-200/70 mt-0.5">
                Normal usage is around {spike.threshold_kwh} units (kWh), but {spike.actual_kwh} units were used.
              </p>
            </div>
          </div>
          <button
            onClick={() => onResolve(spike.id)}
            className="whitespace-nowrap px-3.5 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-400/40 text-rose-200 text-xs font-bold shadow-xs flex items-center transition"
          >
            <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-rose-300" />
            Dismiss Alert
          </button>
        </div>
      ))}
    </div>
  );
}

