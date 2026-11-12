import React from 'react';
import { ShieldCheck, AlertCircle, HelpCircle } from 'lucide-react';

export default function ConfidenceBadge({ tier, score, showScore = true }) {
  if (tier === 'HIGH' || (score !== undefined && score >= 0.90)) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/40">
        <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-400" />
        Very Accurate {showScore && score !== undefined && `(${Math.round(score * 100)}%)`}
      </span>
    );
  }

  if (tier === 'LOW' || (score !== undefined && score >= 0.70)) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-yellow-500/20 text-yellow-300 border border-yellow-400/40">
        <AlertCircle className="w-3.5 h-3.5 mr-1 text-yellow-400" />
        Fair Estimate {showScore && score !== undefined && `(${Math.round(score * 100)}%)`}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-500/20 text-teal-300 border border-teal-400/40">
      <HelpCircle className="w-3.5 h-3.5 mr-1 text-teal-400" />
      General Estimate
    </span>
  );
}

