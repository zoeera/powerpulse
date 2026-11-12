import React, { useState } from 'react';
import { Zap, ShieldCheck, MapPin, Building, CheckCircle2, ArrowRight } from 'lucide-react';
import { api } from '../api/client';

export default function Onboarding({ onComplete }) {
  const [mode, setMode] = useState('register'); // register or login
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('Homeowner');
  const [state, setState] = useState('Telangana');
  const [city, setCity] = useState('Hyderabad');
  const [utility, setUtility] = useState('TGSPDCL');
  const [consentGranted, setConsentGranted] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const utilitiesByState = {
    'Telangana': [
      { code: 'TGSPDCL', name: 'TGSPDCL (Telangana Southern - Hyderabad & Secunderabad)' },
      { code: 'TGNPDCL', name: 'TGNPDCL (Telangana Northern)' },
    ],
    'Uttar Pradesh': [
      { code: 'UPPCL', name: 'UPPCL (Urban Domestic LMV-1 - Lucknow, Noida, Kanpur)' },
    ],
    'Madhya Pradesh': [
      { code: 'MPWZ', name: 'MPWZ / MPPKVVCL (Madhya Pradesh West - Indore, Ujjain)' },
    ],
    'Delhi': [
      { code: 'BSES Delhi', name: 'BSES Rajdhani Power Limited (BRPL / BYPL)' },
    ],
  };

  const handleStateChange = (newState) => {
    setState(newState);
    const available = utilitiesByState[newState];
    if (available && available.length > 0) {
      setUtility(available[0].code);
    }
    if (newState === 'Telangana') setCity('Hyderabad');
    if (newState === 'Uttar Pradesh') setCity('Lucknow');
    if (newState === 'Madhya Pradesh') setCity('Indore');
    if (newState === 'Delhi') setCity('Delhi');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'register') {
        if (!consentGranted) {
          setError('You must grant data consent to continue.');
          setLoading(false);
          return;
        }
        const res = await api.register({
          email,
          password,
          full_name: fullName,
          state,
          city,
          utility,
          tariff_category: 'LT-I(A)',
          consent_granted: consentGranted,
        });
        if (onComplete) onComplete(res);
      } else {
        const res = await api.login(email, password);
        if (onComplete) onComplete(res);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto px-4 py-12">
      <div className="card-emerald p-8 shadow-2xl">
        <div className="text-center mb-8">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-emerald-400 via-teal-400 to-cyan-400 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-emerald-500/35 mb-4">
            <Zap className="w-8 h-8 fill-slate-950 stroke-slate-950 stroke-2" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">
            Power<span className="text-emerald-400 text-glow-emerald">Pulse</span> India
          </h1>
          <p className="text-xs text-emerald-200/70 mt-1">
            Smart Electricity & Solar Savings Platform
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex rounded-xl p-1 emerald-subpanel mb-6">
          <button
            type="button"
            onClick={() => setMode('register')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
              mode === 'register'
                ? 'btn-yellow-contrast text-slate-950 shadow-xs'
                : 'text-emerald-200/70 hover:text-white'
            }`}
          >
            Create Account
          </button>
          <button
            type="button"
            onClick={() => setMode('login')}
            className={`flex-1 py-2 text-xs font-bold rounded-lg transition ${
              mode === 'login'
                ? 'btn-yellow-contrast text-slate-950 shadow-xs'
                : 'text-emerald-200/70 hover:text-white'
            }`}
          >
            Sign In
          </button>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs mb-5">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-xs font-bold text-emerald-200 mb-1.5">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Ramesh Kumar"
                className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-emerald-200 mb-1.5">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="consumer@example.com"
              className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-emerald-200 mb-1.5">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none"
            />
          </div>

          {mode === 'register' && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-emerald-200 mb-1.5">State</label>
                  <select
                    value={state}
                    onChange={(e) => handleStateChange(e.target.value)}
                    className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
                  >
                    <option value="Telangana">Telangana</option>
                    <option value="Uttar Pradesh">Uttar Pradesh</option>
                    <option value="Madhya Pradesh">Madhya Pradesh</option>
                    <option value="Delhi">Delhi</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-emerald-200 mb-1.5">City</label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-emerald-200 mb-1.5">Electricity Provider</label>
                <select
                  value={utility}
                  onChange={(e) => setUtility(e.target.value)}
                  className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3 py-2 text-xs text-white focus:outline-none"
                >
                  {(utilitiesByState[state] || []).map((u) => (
                    <option key={u.code} value={u.code}>
                      {u.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Data Consent Checkbox */}
              <div className="pt-2">
                <label className="flex items-start space-x-2.5 cursor-pointer text-xs text-emerald-200/80">
                  <input
                    type="checkbox"
                    checked={consentGranted}
                    onChange={(e) => setConsentGranted(e.target.checked)}
                    className="mt-0.5 accent-yellow-400 rounded"
                  />
                  <span>
                    I agree to let PowerPulse read my bills to calculate usage and government savings.
                  </span>
                </label>
              </div>
            </>
          )}

          <div className="pt-3 space-y-3">
            <button
              type="submit"
              disabled={loading}
              className="btn-yellow-contrast w-full py-3 rounded-xl text-sm flex items-center justify-center space-x-2 transition disabled:opacity-50"
            >
              <span>{mode === 'register' ? 'Get Started Free' : 'Sign In'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => {
                if (onComplete) {
                  onComplete({
                    user_id: 'user_default',
                    full_name: 'Consumer',
                    email: 'consumer@powerpulse.in',
                    state: 'Telangana',
                    city: 'Hyderabad',
                    utility: 'TGSPDCL',
                    tariff_category: 'LT-I(A)',
                  });
                }
              }}
              className="w-full py-2.5 rounded-xl border border-emerald-500/40 hover:border-emerald-400 emerald-subpanel text-emerald-200 hover:text-white text-xs font-bold transition flex items-center justify-center space-x-2"
            >
              <span>⚡ Try Instant Demo (Skip Sign In)</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
