import React, { useEffect, useState } from 'react';
import { 
  Zap, IndianRupee, Sun, AlertOctagon, TrendingUp, Calendar, 
  ArrowUpRight, ShieldCheck, PieChart as PieIcon, UploadCloud, ChevronRight,
  CheckCircle2, Sparkles, HelpCircle, Receipt, Landmark
} from 'lucide-react';
import { 
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, 
  Tooltip, CartesianGrid, Legend, PieChart, Pie, Cell 
} from 'recharts';
import { api } from '../api/client';
import SpikeAlertBanner from '../components/SpikeAlertBanner';
import ConfidenceBadge from '../components/ConfidenceBadge';
import DisclaimerBanner from '../components/DisclaimerBanner';

const PIE_COLORS = ['#10b981', '#facc15', '#34d399', '#38bdf8', '#059669', '#f59e0b'];

function formatBillDate(dateStr) {
  if (!dateStr) return '—';
  const dt = new Date(dateStr);
  if (Number.isNaN(dt.getTime())) return String(dateStr);
  return dt.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' });
}

export default function Dashboard({ user, onNavigate }) {
  const [loading, setLoading] = useState(true);
  const [bills, setBills] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [spikes, setSpikes] = useState([]);
  const [appliances, setAppliances] = useState([]);
  const [solarData, setSolarData] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [billsData, forecastData, spikesData, appData, recData] = await Promise.all([
        api.getBills().catch(() => []),
        api.getMonthlyForecast().catch(() => null),
        api.getSpikes(true).catch(() => []),
        api.getAppliances().catch(() => []),
        api.getRecommendations().catch(() => []),
      ]);

      setBills(billsData || []);
      setForecast(forecastData);
      setSpikes(spikesData || []);
      setAppliances(appData || []);
      
      const solar = (recData || []).find(r => r.category === 'solar');
      setSolarData(solar);
    } catch (e) {
      console.error('Error loading dashboard data', e);
    } finally {
      setLoading(false);
    }
  };

  const handleResolveSpike = async (spikeId) => {
    try {
      await api.resolveSpike(spikeId);
      setSpikes(spikes.filter(s => s.id !== spikeId));
    } catch (e) {
      console.error(e);
    }
  };

  // Build chart history + forecast series
  const chartData = [];
  const sortedBills = [...bills].sort((a, b) => new Date(a.to_date) - new Date(b.to_date));
  
  if (sortedBills.length > 0) {
    sortedBills.slice(-6).forEach(b => {
      const d = new Date(b.to_date);
      const label = d.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
      chartData.push({
        name: label,
        Actual_kWh: b.units_consumed_kwh,
        Forecast_kWh: null,
        Net_Bill_INR: b.net_payable,
      });
    });
  } else {
    chartData.push(
      { name: 'Aug', Actual_kWh: 145, Forecast_kWh: null, Net_Bill_INR: 0 },
      { name: 'Sep', Actual_kWh: 160, Forecast_kWh: null, Net_Bill_INR: 0 },
      { name: 'Oct', Actual_kWh: 152, Forecast_kWh: null, Net_Bill_INR: 0 },
      { name: 'Nov', Actual_kWh: 148, Forecast_kWh: null, Net_Bill_INR: 0 }
    );
  }

  // Append next month forecast
  if (forecast) {
    const d = new Date(forecast.target_date);
    const label = `${d.toLocaleDateString('en-IN', { month: 'short' })} (Est.)`;
    chartData.push({
      name: label,
      Actual_kWh: null,
      Forecast_kWh: forecast.predicted_kwh,
      Net_Bill_INR: forecast.estimated_cost_inr,
    });
  }

  // Appliance breakdown pie
  const pieData = appliances.length > 0 ? appliances.map(a => ({
    name: a.appliance_type,
    value: a.estimated_monthly_kwh
  })) : [
    { name: 'Air Conditioning', value: 75 },
    { name: 'Refrigerator', value: 36 },
    { name: 'Fans & Ventilation', value: 25 },
    { name: 'Lighting & TVs', value: 18 },
    { name: 'Water Geyser', value: 14 },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Radiant Gradient Emerald Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl p-7 sm:p-8 bg-gradient-emerald-hero shadow-2xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-white/10 blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md border border-white/25 mb-3">
              <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
              <span>Electricity & Solar Dashboard</span>
            </div>
            
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Welcome, <span className="text-yellow-300 text-glow-yellow">{user?.full_name || 'Consumer'}</span>
            </h1>
            
            <p className="text-sm text-emerald-100 mt-1 max-w-2xl font-medium">
              Provider: <strong className="text-white font-bold">{user?.utility || 'TGSPDCL'}</strong> • 
              Plan: <strong className="text-white font-bold">{user?.tariff_category || 'LT-I(A)'}</strong>
              {user?.utility === 'TGSPDCL' && ' • Gruha Jyothi (Under 200 units ₹0 Bill)'}
            </p>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <button
              onClick={() => onNavigate('bills')}
              className="btn-yellow-contrast flex-1 sm:flex-none px-5 py-2.5 rounded-xl text-sm flex items-center justify-center space-x-2 transition-transform active:scale-95"
            >
              <UploadCloud className="w-4 h-4 stroke-[2.5]" />
              <span>Upload Bill</span>
            </button>
            <button
              onClick={() => onNavigate('eco')}
              className="bg-white/15 hover:bg-white/25 text-white border border-white/30 backdrop-blur-md flex-1 sm:flex-none px-5 py-2.5 rounded-xl font-bold text-sm flex items-center justify-center space-x-2 transition"
            >
              <Sun className="w-4 h-4 text-yellow-300" />
              <span>Solar Savings</span>
            </button>
          </div>
        </div>
      </div>

      {/* Spike Alert Banner */}
      <SpikeAlertBanner spikes={spikes} onResolve={handleResolveSpike} />

      {/* KPI Cards — flex-wrap so 5-6 cards still flow cleanly */}
      <div className="flex flex-wrap gap-5">
        
        {/* Next Month Estimated Bill */}
        <div className="card-emerald card-emerald-hover p-5 flex flex-col justify-between min-w-[220px] flex-1">
          <div className="flex justify-between items-start">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Expected Next Bill</span>
            <div className="p-2.5 rounded-xl emerald-subpanel text-yellow-400 border border-yellow-400/30">
              <IndianRupee className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-white">
              ₹{forecast ? forecast.estimated_cost_inr.toLocaleString('en-IN') : '0.00'}
            </div>
            <div className="flex items-center mt-2.5">
              <ConfidenceBadge tier={forecast?.confidence_tier} />
            </div>
            {user?.utility === 'TGSPDCL' && (forecast?.predicted_kwh || 148) <= 200 && (
              <div className="mt-3 flex items-center text-xs font-bold text-yellow-300 bg-yellow-500/15 border border-yellow-400/30 rounded-lg px-2.5 py-1">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 flex-shrink-0 text-yellow-400" />
                <span>🎉 Free Electricity Qualified (Under 200 units)</span>
              </div>
            )}
          </div>
        </div>

        {/* Forecast Usage */}
        <div className="card-emerald card-emerald-hover p-5 flex flex-col justify-between min-w-[220px] flex-1">
          <div className="flex justify-between items-start">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Expected Usage</span>
            <div className="p-2.5 rounded-xl emerald-subpanel text-emerald-400 border border-emerald-400/30">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-white">
              {forecast ? `${forecast.predicted_kwh}` : '148.0'}{' '}
              <span className="text-base font-normal text-emerald-300/80">Units (kWh)</span>
            </div>
            <p className="text-xs text-emerald-300/70 mt-2">
              Based on {forecast?.bill_count_used || bills.length} past bills & seasons
            </p>
          </div>
        </div>

        {/* Solar Savings Potential */}
        <div className="card-emerald card-emerald-hover p-5 flex flex-col justify-between min-w-[220px] flex-1">
          <div className="flex justify-between items-start">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Solar Savings</span>
            <div className="p-2.5 rounded-xl emerald-subpanel text-yellow-400 border border-yellow-400/30">
              <Sun className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-yellow-300 text-glow-yellow">
              ₹{solarData ? Math.round(solarData.monthly_savings_inr).toLocaleString('en-IN') : '2,250'}
              <span className="text-sm font-normal text-emerald-300/80">/mo</span>
            </div>
            <p className="text-xs text-emerald-300/70 mt-2">
              Save up to ₹78,000 with Govt Subsidy
            </p>
          </div>
        </div>

        {/* Tariff Category */}
        <div className="card-emerald card-emerald-hover p-5 flex flex-col justify-between min-w-[220px] flex-1">
          <div className="flex justify-between items-start">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Electricity Plan</span>
            <div className="p-2.5 rounded-xl emerald-subpanel text-emerald-400 border border-emerald-400/30">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-bold text-white">
              {forecast?.tariff_slab_applied || 'Domestic LT-I(A)'}
            </div>
            <p className="text-xs text-emerald-300/70 mt-1">
              State: {user?.state || 'Telangana'}
            </p>
            <div className="mt-2 text-xs font-bold text-emerald-300 bg-[#071713] px-2.5 py-1 rounded-md inline-block border border-emerald-500/30">
              {bills.length} bills saved
            </div>
          </div>
        </div>

        {/* Last Bill KPI */}
        {sortedBills.length > 0 && (() => {
          const lb = sortedBills[sortedBills.length - 1];
          return (
            <div className="card-emerald card-emerald-hover p-5 flex flex-col justify-between min-w-[220px] flex-1">
              <div className="flex justify-between items-start">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Last Bill</span>
                <div className="p-2.5 rounded-xl emerald-subpanel text-emerald-400 border border-emerald-400/30">
                  <Receipt className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-white">
                  ₹{lb.net_payable != null ? Number(lb.net_payable).toLocaleString('en-IN') : '—'}
                </div>
                <p className="text-xs text-emerald-300/70 mt-1">
                  {formatBillDate(lb.from_date)} – {formatBillDate(lb.to_date)}
                </p>
                <p className="text-xs text-emerald-300/70 mt-0.5">
                  {lb.units_consumed_kwh ?? 0} kWh
                </p>
              </div>
            </div>
          );
        })()}

        {/* Govt Savings KPI — only if any bill has subsidy */}
        {(() => {
          const subsidizedBills = bills.filter(b => (Number(b.subsidy_amount) || 0) > 0);
          const totalSubsidy = subsidizedBills.reduce((sum, b) => sum + (Number(b.subsidy_amount) || 0), 0);
          if (totalSubsidy <= 0) return null;
          return (
            <div className="card-emerald card-emerald-hover p-5 flex flex-col justify-between min-w-[220px] flex-1">
              <div className="flex justify-between items-start">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">Govt Savings</span>
                <div className="p-2.5 rounded-xl emerald-subpanel text-yellow-400 border border-yellow-400/30">
                  <Landmark className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-3xl font-black text-yellow-300 text-glow-yellow">
                  ₹{totalSubsidy.toLocaleString('en-IN')}
                </div>
                <p className="text-xs text-emerald-300/70 mt-2">
                  Total subsidy across {subsidizedBills.length} bill(s)
                </p>
              </div>
            </div>
          );
        })()}
      </div>

      {/* Main Charts: Line Chart + Donut Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Trend & Forecast Chart */}
        <div className="lg:col-span-2 card-emerald p-6 sm:p-7">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-2">
            <div>
              <h2 className="text-lg font-bold text-white">Monthly Electricity Usage & Next Bill</h2>
              <p className="text-xs text-emerald-300/70 mt-0.5">Track your monthly units and estimated upcoming bill</p>
            </div>
            <button
              onClick={() => onNavigate('forecasts')}
              className="text-xs font-bold text-yellow-300 hover:text-yellow-200 flex items-center transition"
            >
              <span>View Future Bills</span>
              <ChevronRight className="w-3.5 h-3.5 ml-1" />
            </button>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#0a2a22" />
                <XAxis dataKey="name" stroke="#6ee7b7" fontSize={12} tickLine={false} />
                <YAxis stroke="#6ee7b7" fontSize={12} tickLine={false} unit=" kWh" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#071713', borderRadius: '12px', border: '1px solid #10b981', color: '#ffffff' }}
                  formatter={(val, name) => [`${val} Units`, name === 'Actual_kWh' ? 'Actual Usage' : 'Estimated Usage']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="Actual_kWh"
                  stroke="#10b981"
                  strokeWidth={3}
                  dot={{ r: 5, fill: '#10b981' }}
                  activeDot={{ r: 7 }}
                  name="Past Usage (Units)"
                />
                <Line
                  type="monotone"
                  dataKey="Forecast_kWh"
                  stroke="#facc15"
                  strokeWidth={3}
                  strokeDasharray="5 5"
                  dot={{ r: 6, fill: '#facc15' }}
                  name="Estimated Next Usage"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4">
            <DisclaimerBanner />
          </div>
        </div>

        {/* Appliance Breakdown Donut Chart */}
        <div className="card-emerald p-6 sm:p-7 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-lg font-bold text-white">Where Your Power Goes</h2>
              <button
                onClick={() => onNavigate('appliances')}
                className="text-xs font-bold text-yellow-300 hover:text-yellow-200 transition"
              >
                Edit
              </button>
            </div>
            <p className="text-xs text-emerald-300/70 mb-4">Estimated units used per month by your home appliances</p>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#071713', borderRadius: '12px', border: '1px solid #10b981', color: '#ffffff' }}
                    formatter={(val) => [`${val} Units/mo`, 'Estimated']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-2.5 mt-2">
              {pieData.slice(0, 4).map((p, idx) => (
                <div key={p.name} className="flex justify-between items-center text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[idx % PIE_COLORS.length] }}></span>
                    <span className="text-emerald-100 truncate max-w-[150px]">{p.name}</span>
                  </div>
                  <span className="font-bold text-white">{p.value} Units</span>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => onNavigate('appliances')}
            className="w-full mt-5 py-2.5 px-3 text-xs font-bold rounded-xl emerald-subpanel text-white hover:border-emerald-400 transition text-center"
          >
            Manage My Appliances
          </button>
        </div>
      </div>

      {/* Recent Bills Table */}
      <div className="card-emerald p-6 sm:p-7">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-lg font-bold text-white">Recent Bills</h2>
            <p className="text-xs text-emerald-300/70 mt-0.5">
              {sortedBills.length > 0
                ? `Your last ${Math.min(sortedBills.length, 5)} electricity bills`
                : 'No bills uploaded yet'}
            </p>
          </div>
          <button
            onClick={() => onNavigate('reports')}
            className="text-xs font-bold text-yellow-300 hover:text-yellow-200 flex items-center transition"
          >
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5 ml-1" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-emerald-800/60">
                <th className="text-left text-xs font-bold uppercase tracking-wider text-emerald-400 pb-3 pr-4">Period</th>
                <th className="text-right text-xs font-bold uppercase tracking-wider text-emerald-400 pb-3 pr-4">Units (kWh)</th>
                <th className="text-right text-xs font-bold uppercase tracking-wider text-emerald-400 pb-3">Amount Paid</th>
              </tr>
            </thead>
            <tbody>
              {sortedBills.length === 0 ? (
                <tr>
                  <td colSpan={3} className="py-6 text-center text-xs text-emerald-300/60">
                    Upload your first electricity bill to view recent billing history.
                  </td>
                </tr>
              ) : (
                [...sortedBills].reverse().slice(0, 5).map((b, i) => (
                  <tr key={b.id || i} className="border-b border-emerald-900/40 hover:bg-emerald-900/20 transition">
                    <td className="py-3 pr-4 text-emerald-100 whitespace-nowrap">
                      {formatBillDate(b.from_date)} – {formatBillDate(b.to_date)}
                    </td>
                    <td className="py-3 pr-4 text-right font-bold text-white">{b.units_consumed_kwh ?? 0}</td>
                    <td className="py-3 text-right font-black text-yellow-300">
                      ₹{(Number(b.net_payable) || 0).toLocaleString('en-IN')}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
