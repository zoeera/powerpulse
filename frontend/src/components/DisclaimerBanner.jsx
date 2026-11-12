import React from 'react';
import { Info } from 'lucide-react';

export default function DisclaimerBanner({ asOfDate = 'Today' }) {
  return (
    <div className="emerald-subpanel border border-emerald-500/25 rounded-xl p-3 text-xs text-emerald-200/80 flex items-start space-x-2.5">
      <Info className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
      <div>
        <span className="font-bold text-white mr-1.5">💡 Helpful Note:</span>
        These numbers are estimates based on your past usage and seasonal weather changes. Actual electricity board bills may vary slightly based on your state's latest official rates.
      </div>
    </div>
  );
}

