import React, { useState, useEffect } from 'react';
import { Cpu, Plus, Trash2, Zap, Star, Clock, CheckCircle2, Sparkles } from 'lucide-react';
import { api } from '../api/client';

const COMMON_APPLIANCES = [
  { type: '1.5 Ton Split AC (3-Star)', wattage: 1500, defaultHours: 8, star: 3 },
  { type: '1.5 Ton Inverter AC (5-Star)', wattage: 1050, defaultHours: 8, star: 5 },
  { type: 'Double Door Refrigerator', wattage: 250, defaultHours: 24, star: 4 },
  { type: 'Single Door Refrigerator', wattage: 150, defaultHours: 24, star: 3 },
  { type: 'Ceiling Fan (BLDC 5-Star)', wattage: 28, defaultHours: 12, star: 5 },
  { type: 'Ceiling Fan (Standard)', wattage: 75, defaultHours: 12, star: 2 },
  { type: 'Storage Geyser (Water Heater)', wattage: 2000, defaultHours: 1.5, star: 3 },
  { type: 'Front Load Washing Machine', wattage: 600, defaultHours: 1, star: 5 },
  { type: 'Top Load Washing Machine', wattage: 450, defaultHours: 1, star: 4 },
  { type: '55-inch 4K LED Television', wattage: 110, defaultHours: 5, star: 4 },
  { type: 'Microwave Oven', wattage: 1200, defaultHours: 0.5, star: 3 },
  { type: 'RO Water Purifier', wattage: 60, defaultHours: 3, star: 4 },
  { type: 'LED Bulbs & Battens (Set of 6)', wattage: 60, defaultHours: 6, star: 5 },
];

export default function ApplianceQuestionnaire() {
  const [userAppliances, setUserAppliances] = useState([]);
  const [loading, setLoading] = useState(true);

  // New appliance state
  const [selectedPreset, setSelectedPreset] = useState('');
  const [applianceType, setApplianceType] = useState('1.5 Ton Split AC (3-Star)');
  const [count, setCount] = useState(1);
  const [wattage, setWattage] = useState(1500);
  const [starRating, setStarRating] = useState(3);
  const [dailyHours, setDailyHours] = useState(8);

  useEffect(() => {
    loadAppliances();
  }, []);

  const loadAppliances = async () => {
    try {
      const data = await api.getAppliances();
      setUserAppliances(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handlePresetSelect = (name) => {
    const preset = COMMON_APPLIANCES.find(a => a.type === name);
    if (preset) {
      setSelectedPreset(name);
      setApplianceType(preset.type);
      setWattage(preset.wattage);
      setStarRating(preset.star);
      setDailyHours(preset.defaultHours);
    }
  };

  const handleAddAppliance = async (e) => {
    e.preventDefault();
    try {
      const res = await api.addAppliance({
        appliance_type: applianceType,
        count: parseInt(count),
        wattage_watts: parseFloat(wattage),
        star_rating: parseInt(starRating),
        daily_hours: parseFloat(dailyHours),
      });
      setUserAppliances([...userAppliances, res]);
    } catch (err) {
      alert(err.message || 'Error adding appliance');
    }
  };

  const handleDeleteAppliance = async (appliance, index) => {
    try {
      await api.deleteAppliance(appliance.id);
      setUserAppliances(prev =>
        prev.filter((item, idx) => (appliance.id ? item.id !== appliance.id : idx !== index))
      );
    } catch (err) {
      alert(err.message || 'Error removing appliance');
    }
  };

  const totalMonthlyKwh = userAppliances.reduce((acc, a) => acc + (a.estimated_monthly_kwh || 0), 0);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Radiant Gradient Emerald Header */}
      <div className="relative overflow-hidden rounded-3xl p-7 sm:p-8 bg-gradient-emerald-hero shadow-2xl">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md border border-white/25 mb-3">
          <Cpu className="w-3.5 h-3.5 text-yellow-300" />
          <span>Home Energy Breakdown</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          My Home Appliances
        </h1>
        <p className="text-sm text-emerald-100 mt-1 max-w-2xl font-medium">
          Add your daily appliances to see which devices use the most electricity and contribute most to your monthly bill.
        </p>
      </div>

      {/* Aggregate summary banner */}
      <div className="card-emerald p-6 sm:p-7 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 border-emerald-400/40 bg-[#08241d]">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider text-yellow-300">Estimated Monthly Running Power</span>
          <div className="text-3xl font-black text-white mt-1">
            {totalMonthlyKwh.toFixed(1)} <span className="text-sm font-normal text-emerald-300/80">Units / month</span>
          </div>
          <p className="text-xs text-emerald-300/70 mt-1">
            Calculated across {userAppliances.length} appliances in your home
          </p>
        </div>

        <div className="text-right bg-[#051712] p-4 rounded-2xl border border-yellow-400/30">
          <div className="text-xs text-yellow-200/70">Estimated Monthly Running Cost</div>
          <div className="text-2xl font-black text-yellow-300 mt-0.5 text-glow-yellow">₹{Math.round(totalMonthlyKwh * 7.50).toLocaleString('en-IN')}</div>
        </div>
      </div>

      {/* Add New Appliance Card */}
      <div className="card-emerald p-6 sm:p-7 space-y-6">
        <h2 className="text-lg font-bold text-white flex items-center">
          <Plus className="w-5 h-5 mr-2 text-yellow-400" />
          Add An Appliance
        </h2>

        <div>
          <label className="block text-xs font-bold text-emerald-200 mb-2">Quick Add: Common Home Appliances</label>
          <div className="flex flex-wrap gap-2">
            {COMMON_APPLIANCES.map(preset => (
              <button
                type="button"
                key={preset.type}
                onClick={() => handlePresetSelect(preset.type)}
                className={`text-xs px-3 py-1.5 rounded-xl border transition-all ${
                  selectedPreset === preset.type
                    ? 'bg-yellow-400/25 border-yellow-400 text-yellow-300 font-bold shadow-xs'
                    : 'emerald-subpanel hover:border-emerald-400/50 text-emerald-200/80'
                }`}
              >
                {preset.type}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleAddAppliance} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end pt-2">
          <div className="lg:col-span-2">
            <label className="block text-xs font-bold text-emerald-200 mb-1.5">Appliance Name</label>
            <input
              type="text"
              required
              value={applianceType}
              onChange={(e) => setApplianceType(e.target.value)}
              className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-emerald-200 mb-1.5">Quantity</label>
            <input
              type="number"
              min="1"
              max="20"
              value={count}
              onChange={(e) => setCount(e.target.value)}
              className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-emerald-200 mb-1.5">Power Usage (Watts)</label>
            <input
              type="number"
              value={wattage}
              onChange={(e) => setWattage(e.target.value)}
              className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none"
            />
          </div>

          <div>
            <button
              type="submit"
              className="btn-yellow-contrast w-full py-2.5 rounded-xl text-sm transition-all"
            >
              Add Appliance
            </button>
          </div>
        </form>
      </div>

      {/* Cataloged appliances table */}
      <div className="card-emerald p-6 sm:p-7">
        <h2 className="text-lg font-bold text-white mb-4">Your Added Appliances</h2>
        {userAppliances.length === 0 ? (
          <p className="text-xs text-emerald-300/70">No appliances added yet. Click one of the quick buttons above to get started!</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-emerald-300/70 border-b border-emerald-900/60 uppercase font-mono">
                <tr>
                  <th className="py-2.5 px-3">Appliance</th>
                  <th className="py-2.5 px-3">Quantity</th>
                  <th className="py-2.5 px-3">Power Usage (Watts)</th>
                  <th className="py-2.5 px-3">Used Per Day (hours)</th>
                  <th className="py-2.5 px-3">Monthly Usage</th>
                  <th className="py-2.5 px-3">Remove</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-950/80">
                {userAppliances.map((a, i) => (
                  <tr key={a.id ?? i} className="hover:bg-[#071d18]/60 text-emerald-100">
                    <td className="py-3 px-3 font-semibold text-white">{a.appliance_type}</td>
                    <td className="py-3 px-3">{a.count}</td>
                    <td className="py-3 px-3">{a.wattage_watts} W</td>
                    <td className="py-3 px-3">{a.daily_hours} hrs/day</td>
                    <td className="py-3 px-3 font-black text-yellow-300">{a.estimated_monthly_kwh} Units</td>
                    <td className="py-3 px-3">
                      <button
                        type="button"
                        onClick={() => handleDeleteAppliance(a, i)}
                        className="p-1.5 rounded-lg bg-red-500/15 hover:bg-red-500/30 border border-red-500/30 text-red-400 hover:text-red-200 transition"
                        title="Remove appliance"
                        aria-label={`Remove ${a.appliance_type}`}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
