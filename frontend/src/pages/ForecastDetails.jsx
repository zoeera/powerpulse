import React, { useState, useEffect } from 'react';
import { LineChart, Calendar, ShieldCheck, IndianRupee, Zap, Info, ChevronRight, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import ConfidenceBadge from '../components/ConfidenceBadge';
import DisclaimerBanner from '../components/DisclaimerBanner';

export default function ForecastDetails() {
  const [monthlyForecast, setMonthlyForecast] = useState(null);
  const [dailyForecast, setDailyForecast] = useState(null);
  const [billForecast, setBillForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadForecasts();
  }, []);

  const loadForecasts = async () => {
    setLoading(true);
    try {
      const [m, d, b] = await Promise.all([
        api.getMonthlyForecast(),
        api.getDailyForecast(7),
        api.getBillForecast(),
      ]);
      setMonthlyForecast(m);
      setDailyForecast(d);
      setBillForecast(b);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Radiant Gradient Emerald Header */}
      <div className="relative overflow-hidden rounded-3xl p-7 sm:p-8 bg-gradient-emerald-hero shadow-2xl">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md border border-white/25 mb-3">
          <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
          <span>Smart Bill Predictor</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Future Electricity Bills & Estimates
        </h1>
        <p className="text-sm text-emerald-100 mt-1 max-w-2xl font-medium">
          See what you can expect to pay over the coming months based on seasonal usage patterns and your government subsidy eligibility.
        </p>
      </div>

      {/* Model Confidence Tier Overview */}
      <div className="card-emerald p-6 sm:p-7 space-y-5">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-emerald-900/60 pb-4">
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-bold text-white">Estimate Accuracy Level</h2>
            <ConfidenceBadge tier={monthlyForecast?.confidence_tier} />
          </div>
          <span className="text-xs text-yellow-300 font-medium">
            Smart Seasonal Trend Forecast
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className={`p-4 rounded-xl border ${monthlyForecast?.confidence_tier === 'HIGH' ? 'bg-[#0e3b2e] border-emerald-400/50' : 'emerald-subpanel border-emerald-900/60'}`}>
            <span className="font-bold text-emerald-300 block mb-1">High Accuracy (12+ bills saved)</span>
            <span className="text-emerald-200/70">Accounts for full seasonal weather cycles, summer cooling spikes, and winter dips.</span>
          </div>
          <div className={`p-4 rounded-xl border ${monthlyForecast?.confidence_tier === 'LOW' ? 'bg-yellow-950/40 border-yellow-500/50' : 'emerald-subpanel border-emerald-900/60'}`}>
            <span className="font-bold text-yellow-300 block mb-1">Fair Accuracy (6–11 bills saved)</span>
            <span className="text-emerald-200/70">Good estimates based on recent months. Adding 12 bills unlocks maximum accuracy.</span>
          </div>
          <div className={`p-4 rounded-xl border ${monthlyForecast?.confidence_tier === 'ESTIMATE' ? 'bg-teal-950/40 border-teal-500/50' : 'emerald-subpanel border-emerald-900/60'}`}>
            <span className="font-bold text-teal-300 block mb-1">General Average (&lt; 6 bills saved)</span>
            <span className="text-emerald-200/70">Based on standard home power usage in your state. Upload bills to personalize.</span>
          </div>
        </div>
      </div>

      {/* 3-Month Projection Cards */}
      {monthlyForecast && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {(monthlyForecast.forecast_timeline && monthlyForecast.forecast_timeline.length > 0
            ? monthlyForecast.forecast_timeline
            : [
                {
                  month: 'Next Month',
                  kwh: monthlyForecast.predicted_kwh ?? 0,
                  inr: monthlyForecast.estimated_cost_inr ?? 0,
                  tariff_slab: monthlyForecast.tariff_slab_applied,
                  subsidy_inr: monthlyForecast.subsidy_applied_inr ?? 0,
                },
              ]
          ).map((item, idx) => {
            const kwh = Number(item.kwh) || 0;
            const inr = Number(item.inr) || 0;
            const subsidy = Number(item.subsidy_inr) || 0;
            return (
              <div key={idx} className="card-emerald card-emerald-hover p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">{item.month}</span>
                    <span className="text-[11px] font-semibold text-emerald-300/70">
                      {idx === 0 ? 'Upcoming' : `Month +${idx + 1}`}
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
      )}

      {/* Disclaimer */}
      <DisclaimerBanner source={monthlyForecast?.model_used} />
    </div>
  );
}
