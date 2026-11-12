import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import BillUpload from './pages/BillUpload';
import ApplianceQuestionnaire from './pages/ApplianceQuestionnaire';
import ForecastDetails from './pages/ForecastDetails';
import EcoAlternatives from './pages/EcoAlternatives';
import ReportsAndSettings from './pages/ReportsAndSettings';
import { api } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState({
    id: 'user_default',
    full_name: 'Consumer',
    email: 'consumer@powerpulse.in',
    state: 'Telangana',
    city: 'Hyderabad',
    utility: 'TGSPDCL',
    tariff_category: 'LT-I(A)',
  });
  const [isAuth, setIsAuth] = useState(true);

  useEffect(() => {
    api.getProfile()
      .then(data => {
        if (data && data.full_name) {
          setUser(data);
          setIsAuth(true);
        }
        // Chain a bills fetch to sync tariff_category & provider from the most recent bill
        return api.getBills().catch(() => []);
      })
      .then(bills => {
        if (!Array.isArray(bills) || bills.length === 0) return;
        const sorted = [...bills].sort((a, b) => new Date(b.to_date) - new Date(a.to_date));
        const latest = sorted[0];
        setUser(prev => ({
          ...prev,
          ...(latest.tariff_category ? { tariff_category: latest.tariff_category } : {}),
          ...(latest.provider ? { utility: latest.provider } : {}),
        }));
      })
      .catch(() => {});
  }, []);

  const handleAuthComplete = (authData) => {
    setUser({
      id: authData.user_id,
      full_name: authData.full_name || 'Consumer',
      email: authData.email,
      state: authData.state || 'Telangana',
      city: authData.city || 'Hyderabad',
      utility: authData.utility || 'TGSPDCL',
      tariff_category: authData.tariff_category || 'LT-I(A)',
    });
    setIsAuth(true);
    setActiveTab('dashboard');
  };

  const handleLogout = () => {
    api.setToken(null);
    setIsAuth(false);
    setUser({
      id: '',
      full_name: 'Guest User',
      email: '',
      state: 'Telangana',
      city: 'Hyderabad',
      utility: 'TGSPDCL',
      tariff_category: 'LT-I(A)',
    });
    setActiveTab('onboarding');
  };

  return (
    <div className="min-h-screen bg-[#091210] text-white flex flex-col font-sans selection:bg-emerald-400 selection:text-slate-950">
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        user={user} 
        onLogout={handleLogout}
      />

      <main className="flex-1 pb-16">
        {activeTab === 'onboarding' && (
          <Onboarding onComplete={handleAuthComplete} />
        )}
        {activeTab === 'dashboard' && (
          <Dashboard
            user={user}
            onNavigate={setActiveTab}
            onBillSaved={(savedBill) => {
              if (!savedBill) return;
              setUser(prev => ({
                ...prev,
                ...(savedBill.provider ? { utility: savedBill.provider } : {}),
                ...(savedBill.state ? { state: savedBill.state } : {}),
                ...(savedBill.tariff_category ? { tariff_category: savedBill.tariff_category } : {}),
              }));
            }}
          />
        )}
        {activeTab === 'bills' && (
          <BillUpload
            onNavigate={setActiveTab}
            onBillSaved={(savedBill) => {
              if (!savedBill) return;
              setUser(prev => ({
                ...prev,
                ...(savedBill.provider ? { utility: savedBill.provider } : {}),
                ...(savedBill.state ? { state: savedBill.state } : {}),
                ...(savedBill.tariff_category ? { tariff_category: savedBill.tariff_category } : {}),
              }));
            }}
          />
        )}
        {activeTab === 'appliances' && (
          <ApplianceQuestionnaire />
        )}
        {activeTab === 'forecasts' && (
          <ForecastDetails onNavigate={setActiveTab} />
        )}
        {activeTab === 'eco' && (
          <EcoAlternatives />
        )}
        {activeTab === 'reports' && (
          <ReportsAndSettings user={user} onDataDeleted={handleLogout} />
        )}
      </main>

      <footer className="bg-[#050d0b] border-t border-emerald-950/80 py-6 text-center text-xs text-emerald-200/60">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-3">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span>
            <span className="font-bold text-white">PowerPulse India</span>
            <span>• AI Electricity Forecasting & Rooftop Solar Optimizer</span>
          </div>
          <div className="text-emerald-300/50">
            DISCOM Support: TGSPDCL, UPPCL, MPWZ, BSES Delhi • Gruha Jyothi & PM Surya Ghar Compliant
          </div>
        </div>
      </footer>
    </div>
  );
}
