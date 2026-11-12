import React, { useState, useEffect } from 'react';
import { 
  Sun, Battery, IndianRupee, Leaf, Clock, TrendingDown, 
  Lightbulb, Wind, Flame, CheckCircle2, Sliders, Sparkles, ShieldCheck 
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { api } from '../api/client';

export default function EcoAlternatives() {
  const [panelKw, setPanelKw] = useState(3.0);
  const [batteryKwh, setBatteryKwh] = useState(0.0);
  const [city, setCity] = useState('Hyderabad');
  const [occupants, setOccupants] = useState(4);
  const [solarRoi, setSolarRoi] = useState(null);
  const [ecoRecs, setEcoRecs] = useState([]);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  useEffect(() => {
    runSolarCalculation();
  }, [panelKw, batteryKwh, city, occupants]);

  const fetchRecommendations = async () => {
    try {
      const recs = await api.getRecommendations();
      setEcoRecs(recs.filter(r => r.category !== 'solar') || []);
    } catch (e) {
      console.error(e);
    }
  };

  const runSolarCalculation = async () => {
    setCalculating(true);
    try {
      const res = await api.calculateSolarRoi({
        panel_kw: parseFloat(panelKw),
        battery_kwh: parseFloat(batteryKwh),
        city,
        occupants: parseInt(occupants),
      });
      setSolarRoi(res);
    } catch (e) {
      console.error(e);
    } finally {
      setCalculating(false);
    }
  };

  const solarHourlyData = [];
  if (solarRoi && solarRoi.hourly_generation_profile) {
    Object.entries(solarRoi.hourly_generation_profile).forEach(([hour, val]) => {
      solarHourlyData.push({ hour, Generation_kWh: val });
    });
  }

  const getEcoIcon = (cat) => {
    switch (cat) {
      case 'led': return <Lightbulb className="w-5 h-5 text-yellow-400" />;
      case 'inverter_ac': return <Wind className="w-5 h-5 text-emerald-400" />;
      case 'swh': return <Flame className="w-5 h-5 text-amber-400" />;
      case 'battery': return <Battery className="w-5 h-5 text-teal-400" />;
      default: return <Leaf className="w-5 h-5 text-emerald-400" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Radiant Gradient Emerald Header */}
      <div className="relative overflow-hidden rounded-3xl p-7 sm:p-8 bg-gradient-emerald-hero shadow-2xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md border border-white/25 mb-3">
              <Sun className="w-3.5 h-3.5 text-yellow-300" />
              <span>Government Rooftop Solar Scheme</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Solar & Energy Savings Calculator
            </h1>
            <p className="text-sm text-emerald-100 mt-1 max-w-2xl font-medium">
              See how much money you can save by installing rooftop solar panels with government subsidies, and explore energy-saving home upgrades.
            </p>
          </div>
          <div className="px-4 py-2.5 rounded-2xl bg-white/15 border border-white/25 backdrop-blur-md text-right">
            <span className="text-[10px] uppercase tracking-wider text-yellow-300 block font-bold">Your Location</span>
            <span className="text-sm font-black text-white">{city}, India</span>
          </div>
        </div>
      </div>

      {/* Interactive Solar Simulator Card */}
      <div className="card-emerald p-6 sm:p-7 space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-emerald-900/60 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-2xl emerald-subpanel text-yellow-400 border border-yellow-400/30">
              <Sun className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Rooftop Solar Estimator</h2>
              <p className="text-xs text-emerald-300/70">Calculated using your local sunlight levels and government subsidy rates</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 px-3.5 py-1 rounded-full bg-yellow-400/20 border border-yellow-400/40 text-yellow-300 text-xs font-bold shadow-xs">
            <ShieldCheck className="w-4 h-4 text-yellow-400" />
            <span>Govt Subsidy: ₹{solarRoi?.subsidy_amount_inr?.toLocaleString('en-IN') || '78,000'} Off</span>
          </div>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 emerald-subpanel p-5 rounded-2xl">
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-bold text-emerald-200">Solar System Size</label>
              <span className="text-xs font-bold text-yellow-300 bg-yellow-500/20 px-2 py-0.5 rounded border border-yellow-500/30">{panelKw} kW</span>
            </div>
            <input
              type="range"
              min="1.0"
              max="10.0"
              step="0.5"
              value={panelKw}
              onChange={(e) => setPanelKw(parseFloat(e.target.value))}
              className="w-full accent-yellow-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-emerald-300/60 mt-1">
              <span>1 kW</span>
              <span>3 kW (Typical)</span>
              <span>10 kW</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-bold text-emerald-200">Battery Backup</label>
              <span className="text-xs font-bold text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/30">{batteryKwh} kWh</span>
            </div>
            <input
              type="range"
              min="0"
              max="15"
              step="1"
              value={batteryKwh}
              onChange={(e) => setBatteryKwh(parseFloat(e.target.value))}
              className="w-full accent-emerald-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-emerald-300/60 mt-1">
              <span>No Battery</span>
              <span>5 kWh</span>
              <span>15 kWh</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-bold text-emerald-200">Your City</label>
            </div>
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full bg-[#061914] border border-emerald-700/60 text-white text-xs rounded-xl p-2.5 focus:border-yellow-400 focus:outline-none"
            >
              <option value="Hyderabad">Hyderabad (Telangana)</option>
              <option value="Lucknow">Lucknow (UP)</option>
              <option value="Indore">Indore (MP)</option>
              <option value="Delhi">Delhi (NCR)</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-bold text-emerald-200">Family Members in Home</label>
              <span className="text-xs font-bold text-yellow-300 bg-yellow-500/20 px-2 py-0.5 rounded border border-yellow-500/30">{occupants} People</span>
            </div>
            <input
              type="range"
              min="1"
              max="8"
              step="1"
              value={occupants}
              onChange={(e) => setOccupants(parseInt(e.target.value))}
              className="w-full accent-yellow-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-emerald-300/60 mt-1">
              <span>1</span>
              <span>4</span>
              <span>8</span>
            </div>
          </div>
        </div>

        {/* Solar ROI Metrics */}
        {solarRoi && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="emerald-subpanel p-4 rounded-2xl">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300/70">Expected Monthly Power</span>
              <div className="text-2xl font-black text-white mt-1">
                {Math.round(solarRoi.monthly_generation_kwh)} <span className="text-sm font-normal text-emerald-300/80">Units</span>
              </div>
              <span className="text-xs text-emerald-300/60 mt-1 block">~{Math.round(solarRoi.annual_generation_kwh)} Units / year</span>
            </div>

            <div className="emerald-subpanel p-4 rounded-2xl border-yellow-400/40">
              <span className="text-[11px] font-bold uppercase tracking-wider text-yellow-400">Yearly Savings</span>
              <div className="text-2xl font-black text-yellow-300 mt-1 text-glow-yellow">
                ₹{Math.round(solarRoi.annual_savings_inr).toLocaleString('en-IN')}
              </div>
              <span className="text-xs text-yellow-300/90 mt-1 block">₹{Math.round(solarRoi.monthly_savings_inr).toLocaleString('en-IN')} / month</span>
            </div>

            <div className="emerald-subpanel p-4 rounded-2xl">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300/70">Net Cost (After Subsidy)</span>
              <div className="text-2xl font-black text-white mt-1">
                ₹{Math.round(solarRoi.net_cost_inr).toLocaleString('en-IN')}
              </div>
              <span className="text-xs text-emerald-300/60 mt-1 block">Full Price: ₹{Math.round(solarRoi.estimated_system_cost_inr).toLocaleString('en-IN')}</span>
            </div>

            <div className="emerald-subpanel p-4 rounded-2xl border-emerald-400/40">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-300">Pays For Itself In</span>
              <div className="text-2xl font-black text-emerald-300 mt-1">
                {solarRoi.payback_period_years} <span className="text-sm font-normal text-emerald-300/80">Years</span>
              </div>
              <span className="text-xs text-emerald-300/90 mt-1 block">Free clean electricity for 20+ years</span>
            </div>
          </div>
        )}

        {/* 24-Hour Solar Generation Profile Chart */}
        {solarHourlyData.length > 0 && (
          <div className="pt-2">
            <h3 className="text-sm font-bold text-white mb-1">Expected Daily Sunlight & Power Output</h3>
            <p className="text-xs text-emerald-300/70 mb-4">How much electricity your solar panels produce throughout the day</p>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={solarHourlyData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="solarGradEmerald" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#facc15" stopOpacity={0.45}/>
                      <stop offset="95%" stopColor="#facc15" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#0a2a22" vertical={false} />
                  <XAxis dataKey="hour" stroke="#6ee7b7" fontSize={11} tickLine={false} />
                  <YAxis stroke="#6ee7b7" fontSize={11} tickLine={false} unit=" kWh" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#071713', borderRadius: '12px', border: '1px solid #facc15', color: '#ffffff' }}
                    formatter={(val) => [`${val} Units`, 'Solar Generation']}
                  />
                  <Area type="monotone" dataKey="Generation_kWh" stroke="#facc15" strokeWidth={2.5} fillOpacity={1} fill="url(#solarGradEmerald)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* BEE 5-Star Upgrades */}
      <div>
        <h2 className="text-xl font-bold text-white mb-1">Energy-Saving Home Upgrades</h2>
        <p className="text-xs text-emerald-300/70 mb-6">Compare purchase cost vs how much you will save on your electricity bills</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {ecoRecs.map((rec) => (
            <div key={rec.id || rec.recommendation_type} className="card-emerald card-emerald-hover p-5 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-3">
                  <div className="p-2.5 rounded-xl emerald-subpanel">
                    {getEcoIcon(rec.recommendation_type)}
                  </div>
                  <span className="text-[11px] font-bold text-yellow-300 bg-yellow-500/20 border border-yellow-500/30 px-2 py-0.5 rounded-md">
                    Pays off in {rec.payback_period_years} yrs
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white mb-1">{rec.title}</h3>
                <p className="text-xs text-emerald-200/80 leading-relaxed mb-4">{rec.description}</p>
              </div>

              <div className="border-t border-emerald-900/60 pt-3 space-y-1.5 text-xs">
                <div className="flex justify-between text-emerald-300/80">
                  <span>Equipment Price:</span>
                  <span className="font-semibold text-white">₹{Math.round(rec.estimated_cost_inr).toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between text-emerald-300/80">
                  <span>Yearly Savings:</span>
                  <span className="font-bold text-yellow-300">₹{Math.round(rec.annual_savings_inr).toLocaleString('en-IN')}/yr</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
