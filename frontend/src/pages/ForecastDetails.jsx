import React, { useState, useEffect } from 'react';
import { LineChart, UploadCloud, Sparkles, RefreshCw } from 'lucide-react';
import { api } from '../api/client';
import ConfidenceBadge from '../components/ConfidenceBadge';
import DisclaimerBanner from '../components/DisclaimerBanner';

export default function ForecastDetails({ onNavigate }) {
  const [monthlyForecast, setMonthlyForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadForecasts();
  }, []);

  const loadForecasts = async () => {
    setLoading(true);
    try {
      const m = await api.getMonthlyForecast();
      setMonthlyForecast(m);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const hasBills = monthlyForecast && monthlyForecast.bill_count_used > 0;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <div className="rounded-2xl p-6 sm:p-7 bg-gradient-emerald-hero">
        <div className="inline-flex items-center space-x-2 text-xs font-bold text-yellow-300 uppercase tracking-wider mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Smart Bill Predictor</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Future Electricity Bills
        </h1>
        <p className="text-sm text-emerald-100 mt-1 max-w-2xl">
          See your expected units and bill amounts for the next 3 months based on your saved bills, local rates, and seasons.
        </p>
      </div>

      {loading ? (
        <div className="card-emerald p-8 flex items-center justify-center space-x-2 text-sm text-emerald-200">
          <RefreshCw className="w-4 h-4 animate-spin text-yellow-400" />
          <span>Calculating your upcoming bills...</span>
        </div>
      ) : !hasBills ? (
        <div className="card-emerald p-8 text-center space-y-4">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center text-yellow-400">
            <LineChart className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h2 className="text-lg font-bold text-white">No Bills Uploaded Yet</h2>
            <p className="text-xs text-emerald-300/80 max-w-md mx-auto">
              Upload or enter at least one electricity bill on the Home page to see your upcoming bill predictions.
            </p>
          </div>
          {onNavigate && (
            <button
              type="button"
              onClick={() => onNavigate('dashboard')}
              className="btn-yellow-contrast inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Go to Home &amp; Upload Bill</span>
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="card-emerald p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div className="flex items-center space-x-3">
              <ConfidenceBadge tier={monthlyForecast.confidence_tier} />
              <span className="text-xs text-emerald-200">
                Predicted from your <strong className="text-white">{monthlyForecast.bill_count_used}</strong> saved{' '}
                {monthlyForecast.bill_count_used === 1 ? 'bill' : 'bills'} &amp; seasonal weather trends
              </span>
            </div>
            <span className="text-xs text-emerald-300/75">
              Plan: {monthlyForecast.tariff_slab_applied || 'Domestic'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {(monthlyForecast.forecast_timeline || []).map((item, idx) => {
              const kwh = Number(item.kwh) || 0;
              const inr = Number(item.inr) || 0;
              const subsidy = Number(item.subsidy_inr) || 0;
              return (
                <div key={idx} className="card-emerald card-emerald-hover p-6 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">{item.month}</span>
                      <span className="text-[11px] font-semibold text-emerald-300/70">
                        {idx === 0 ? 'Next Month' : `Month +${idx + 1}`}
                      </span>
                    </div>
                    <div className="text-3xl font-black text-white mt-2">
                      {kwh.toFixed(1)} <span className="text-sm font-normal text-emerald-300/80">kWh</span>
                    </div>
                    <div className="text-lg font-bold text-yellow-300 mt-1">
                      ₹{Math.round(inr).toLocaleString('en-IN')}
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <span className="inline-block text-[11px] font-bold text-emerald-300 bg-[#071713] border border-emerald-500/30 px-2.5 py-1 rounded-md">
                      Plan: {item.tariff_slab || monthlyForecast.tariff_slab_applied || 'Domestic'}
                    </span>
                    {subsidy > 0 && (
                      <span className="inline-block text-[11px] font-bold text-yellow-300 bg-yellow-500/15 border border-yellow-400/30 px-2.5 py-1 rounded-md">
                        Govt Subsidy: ₹{Math.round(subsidy).toLocaleString('en-IN')}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <DisclaimerBanner source={monthlyForecast?.model_used} />
        </>
      )}
    </div>
  );
}
