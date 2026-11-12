import React, { useEffect, useState } from 'react';
import {
  Zap, IndianRupee, Sun, TrendingUp, UploadCloud, ChevronRight,
  Cpu, FileText, LineChart, Receipt, CheckCircle2, Info
} from 'lucide-react';
import {
  ResponsiveContainer, LineChart as ReLineChart, Line, XAxis, YAxis,
  Tooltip, CartesianGrid, Legend
} from 'recharts';
import { api } from '../api/client';
import BillUpload from './BillUpload';
import SpikeAlertBanner from '../components/SpikeAlertBanner';
import ConfidenceBadge from '../components/ConfidenceBadge';

function formatBillDate(dateStr) {
  if (!dateStr) return '—';
  const dt = new Date(dateStr);
  if (Number.isNaN(dt.getTime())) return String(dateStr);
  return dt.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' });
}

export default function Dashboard({ user, onNavigate, onBillSaved }) {
  const [bills, setBills] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [spikes, setSpikes] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [billsData, forecastData, spikesData] = await Promise.all([
        api.getBills().catch(() => []),
        api.getMonthlyForecast().catch(() => null),
        api.getSpikes(true).catch(() => []),
      ]);
      setBills(billsData || []);
      setForecast(forecastData);
      setSpikes(spikesData || []);
    } catch (e) {
      console.error('Error loading home data', e);
    }
  };

  const handleBillUploadedOrSaved = async (savedBill) => {
    if (onBillSaved) onBillSaved(savedBill);
    await loadDashboardData();
  };

  const handleResolveSpike = async (spikeId) => {
    try {
      await api.resolveSpike(spikeId);
      setSpikes(spikes.filter(s => s.id !== spikeId));
    } catch (e) {
      console.error(e);
    }
  };

  const sortedBills = [...bills].sort((a, b) => new Date(a.to_date) - new Date(b.to_date));
  const hasRealBills = sortedBills.length > 0;
  const hasModelForecast = hasRealBills && forecast && forecast.bill_count_used > 0;

  // Build trend chart ONLY when actual bills exist (zero mock/fake values)
  const chartData = [];
  if (hasRealBills) {
    sortedBills.slice(-6).forEach(b => {
      const d = new Date(b.to_date);
      const label = Number.isNaN(d.getTime())
        ? String(b.to_date)
        : d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
      chartData.push({
        name: label,
        Actual_kWh: Number(b.units_consumed_kwh) || 0,
        Forecast_kWh: null,
      });
    });

    if (hasModelForecast && forecast.forecast_timeline?.length) {
      forecast.forecast_timeline.forEach(pt => {
        chartData.push({
          name: pt.month,
          Actual_kWh: null,
          Forecast_kWh: Number(pt.kwh) || 0,
        });
      });
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* 1. Brief Introduction & How PowerPulse Works */}
      <section className="rounded-2xl p-6 sm:p-7 bg-gradient-emerald-hero space-y-5">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="space-y-1.5">
            <span className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-yellow-300">
              <Zap className="w-3.5 h-3.5" />
              <span>Welcome to PowerPulse India</span>
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Your Smart Home Electricity Helper
            </h1>
            <p className="text-sm text-emerald-50/90 max-w-3xl leading-relaxed">
              PowerPulse makes it easy to read your electricity bill, check if you qualify for free government power,
              see which home appliances cost you the most, estimate your upcoming bills, and find out how much you can save with rooftop solar.
            </p>
          </div>
        </div>

        {/* Simple 3-Step Guide */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-2">
          <div className="rounded-xl bg-[#062b20]/70 border border-white/15 p-4">
            <div className="text-xs font-extrabold text-yellow-300 uppercase tracking-wider mb-1">
              Step 1 • Add Your Bill
            </div>
            <p className="text-xs text-emerald-50/85 leading-relaxed">
              Take a photo or upload a PDF of your bill below, or type the details by hand.
            </p>
          </div>
          <div className="rounded-xl bg-[#062b20]/70 border border-white/15 p-4">
            <div className="text-xs font-extrabold text-yellow-300 uppercase tracking-wider mb-1">
              Step 2 • See Upcoming Bills
            </div>
            <p className="text-xs text-emerald-50/85 leading-relaxed">
              Right after saving, see what your next 3 electricity bills are likely to be.
            </p>
          </div>
          <div className="rounded-xl bg-[#062b20]/70 border border-white/15 p-4">
            <div className="text-xs font-extrabold text-yellow-300 uppercase tracking-wider mb-1">
              Step 3 • Save Money
            </div>
            <p className="text-xs text-emerald-50/85 leading-relaxed">
              Check Appliance costs, Solar Savings, or download a clean PDF summary from the menu above.
            </p>
          </div>
        </div>
      </section>

      {/* Spike Alerts (only when real spikes exist) */}
      <SpikeAlertBanner spikes={spikes} onResolve={handleResolveSpike} />

      {/* 2. Upload Bill Section & Instant Predictions Right on Home */}
      <section className="card-emerald p-6 sm:p-7">
        <BillUpload
          embedded
          onBillSaved={handleBillUploadedOrSaved}
          onNavigate={onNavigate}
        />
      </section>

      {/* 3. Saved Bills & Current Model Summary (ONLY shown when at least 1 real bill is saved) */}
      {hasRealBills ? (
        <section className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Latest Saved Bill */}
            {(() => {
              const lb = sortedBills[sortedBills.length - 1];
              return (
                <div className="card-emerald p-5 flex flex-col justify-between">
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Latest Saved Bill</span>
                    <Receipt className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="mt-3">
                    <div className="text-3xl font-black text-white">
                      {Number(lb.units_consumed_kwh || 0)} <span className="text-sm font-normal text-emerald-300/80">kWh</span>
                    </div>
                    <div className="text-sm font-bold text-yellow-300 mt-1">
                      Paid: ₹{(Number(lb.net_payable) || 0).toLocaleString('en-IN')}
                    </div>
                    <p className="text-xs text-emerald-300/70 mt-2">
                      {lb.provider || user?.utility} • {formatBillDate(lb.from_date)} – {formatBillDate(lb.to_date)}
                    </p>
                  </div>
                </div>
              );
            })()}

            {/* Next Month Bill Prediction */}
            {hasModelForecast && (
              <div className="card-emerald p-5 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Expected Next Month</span>
                  <TrendingUp className="w-4 h-4 text-yellow-400" />
                </div>
                <div className="mt-3">
                  <div className="text-3xl font-black text-white">
                    {Number(forecast.predicted_kwh || 0).toFixed(1)} <span className="text-sm font-normal text-emerald-300/80">Units</span>
                  </div>
                  <div className="text-sm font-bold text-yellow-300 mt-1">
                    Estimated Bill: ₹{Math.round(Number(forecast.estimated_cost_inr) || 0).toLocaleString('en-IN')}
                  </div>
                  <div className="mt-2 flex items-center justify-between gap-2">
                    <ConfidenceBadge tier={forecast.confidence_tier} />
                  </div>
                </div>
              </div>
            )}

            {/* Plan & Total Bills */}
            <div className="card-emerald p-5 flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Tariff &amp; History</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="mt-3">
                <div className="text-2xl font-black text-white">
                  {forecast?.tariff_slab_applied || user?.tariff_category || 'Domestic'}
                </div>
                <p className="text-xs text-emerald-300/80 mt-1">
                  {sortedBills.length} saved {sortedBills.length === 1 ? 'bill' : 'bills'} in your account
                </p>
                <button
                  type="button"
                  onClick={() => onNavigate('forecasts')}
                  className="mt-3 text-xs font-bold text-yellow-300 hover:text-yellow-200 inline-flex items-center"
                >
                  <span>View Full 3-Month Forecast</span>
                  <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Usage & Forecast Chart (real bills only) */}
          {chartData.length > 0 && (
            <div className="card-emerald p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-2">
                <div>
                  <h2 className="text-base font-bold text-white">Your Past Bills &amp; Upcoming Forecast</h2>
                  <p className="text-xs text-emerald-300/70">Units used in your saved bills compared to expected upcoming months</p>
                </div>
                <button
                  type="button"
                  onClick={() => onNavigate('reports')}
                  className="text-xs font-bold text-yellow-300 hover:text-yellow-200 inline-flex items-center"
                >
                  <span>View All Bills &amp; PDF</span>
                  <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                </button>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ReLineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#0a2a22" />
                    <XAxis dataKey="name" stroke="#6ee7b7" fontSize={12} tickLine={false} />
                    <YAxis stroke="#6ee7b7" fontSize={12} tickLine={false} unit=" Units" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#071713', borderRadius: '12px', border: '1px solid #10b981', color: '#ffffff' }}
                      formatter={(val, name) => [`${val} Units`, name]}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="Actual_kWh"
                      stroke="#10b981"
                      strokeWidth={3}
                      dot={{ r: 5, fill: '#10b981' }}
                      name="Your Saved Bills"
                    />
                    <Line
                      type="monotone"
                      dataKey="Forecast_kWh"
                      stroke="#facc15"
                      strokeWidth={3}
                      strokeDasharray="5 5"
                      dot={{ r: 5, fill: '#facc15' }}
                      name="Predicted Next Bills"
                    />
                  </ReLineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </section>
      ) : (
        <div className="card-emerald p-5 flex items-center space-x-3 text-xs text-emerald-200/80">
          <Info className="w-4 h-4 text-yellow-400 shrink-0" />
          <span>
            No bills added yet — upload a bill photo/PDF or use <strong>Enter Details Manually</strong> above to see your upcoming bill predictions right here.
          </span>
        </div>
      )}

      {/* 4. Quick Navigation Cards */}
      <section className="space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-emerald-300">Explore More Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            type="button"
            onClick={() => onNavigate('forecasts')}
            className="card-emerald card-emerald-hover p-4 text-left flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-2">
              <LineChart className="w-5 h-5 text-yellow-400" />
              <ChevronRight className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">Future Bills</div>
              <p className="text-xs text-emerald-300/75 mt-0.5">See what your next 3 bills may cost</p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate('appliances')}
            className="card-emerald card-emerald-hover p-4 text-left flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-2">
              <Cpu className="w-5 h-5 text-emerald-400" />
              <ChevronRight className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">Appliances</div>
              <p className="text-xs text-emerald-300/75 mt-0.5">See which home devices cost you the most</p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate('eco')}
            className="card-emerald card-emerald-hover p-4 text-left flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-2">
              <Sun className="w-5 h-5 text-yellow-400" />
              <ChevronRight className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">Solar &amp; Savings</div>
              <p className="text-xs text-emerald-300/75 mt-0.5">Calculate rooftop solar &amp; PM Surya Ghar subsidy</p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate('reports')}
            className="card-emerald card-emerald-hover p-4 text-left flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-2">
              <FileText className="w-5 h-5 text-emerald-400" />
              <ChevronRight className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <div className="text-sm font-bold text-white">History &amp; PDF</div>
              <p className="text-xs text-emerald-300/75 mt-0.5">View saved bills &amp; download PDF report</p>
            </div>
          </button>
        </div>
      </section>
    </div>
  );
}
