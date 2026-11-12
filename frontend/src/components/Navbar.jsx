import React, { useRef, useEffect } from 'react';
import { Zap, LayoutDashboard, UploadCloud, Cpu, LineChart, Sun, FileText, LogOut } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, user, onLogout }) {
  const navItems = [
    { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
    { id: 'bills', label: 'Upload Bill', icon: UploadCloud },
    { id: 'appliances', label: 'Appliances', icon: Cpu },
    { id: 'forecasts', label: 'Future Bills', icon: LineChart },
    { id: 'eco', label: 'Solar & Savings', icon: Sun },
    { id: 'reports', label: 'Settings & PDF', icon: FileText },
  ];

  const mobileStripRef = useRef(null);

  useEffect(() => {
    if (mobileStripRef.current) {
      const activeBtn = mobileStripRef.current.querySelector('[data-active="true"]');
      if (activeBtn) {
        activeBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }, [activeTab]);

  return (
    <header className="sticky top-0 z-50 bg-[#061411]/95 backdrop-blur-xl border-b border-emerald-500/25 shadow-lg shadow-emerald-950/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo */}
          <div 
            className="flex items-center space-x-3 cursor-pointer group"
            onClick={() => setActiveTab('dashboard')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-400 via-teal-400 to-cyan-400 flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-emerald-500/35 group-hover:scale-105 transition-transform duration-200">
              <Zap className="w-5 h-5 fill-slate-950 stroke-slate-950 stroke-2" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-black tracking-tight text-white">
                  Power<span className="text-emerald-400 text-glow-emerald">Pulse</span>
                </span>
                <span className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                  Smart Energy
                </span>
              </div>
              <div className="flex items-center space-x-1.5 text-xs text-emerald-200/70">
                <span className="font-bold text-emerald-400">{user?.utility || 'TGSPDCL'}</span>
                <span>•</span>
                <span>{user?.city || 'Hyderabad'}</span>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1 p-1 rounded-xl bg-[#091a15] border border-emerald-500/20">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`relative flex items-center whitespace-nowrap shrink-0 px-3 py-1.5 rounded-lg text-xs xl:text-sm font-bold transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-400 to-teal-400 text-slate-950 shadow-md shadow-emerald-500/40 font-extrabold'
                      : 'text-emerald-200/75 hover:text-white hover:bg-emerald-900/30'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 mr-1.5 shrink-0 ${isActive ? 'text-slate-950 stroke-[2.5]' : 'text-emerald-400'}`} />
                  <span>{item.label}</span>
                  {item.id === 'eco' && (
                    <span className="ml-1.5 flex h-2 w-2 relative shrink-0">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-400"></span>
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* User profile & Action */}
          <div className="flex items-center space-x-2.5 shrink-0">
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-[#091a15] border border-emerald-500/20 text-xs whitespace-nowrap">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.9)] animate-pulse shrink-0"></span>
              <div>
                <span className="font-bold text-white">{user?.full_name || 'Consumer'}</span>
                <span className="text-emerald-300/70 ml-1.5">({user?.tariff_category || 'LT-I(A)'})</span>
              </div>
            </div>

            <button
              onClick={onLogout}
              title="Sign Out"
              className="p-2 rounded-xl bg-[#091a15] hover:bg-rose-950/40 text-emerald-300 hover:text-rose-400 border border-emerald-500/20 hover:border-rose-700/50 transition-colors shrink-0"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Compact / Tablet & Mobile Navigation Strip */}
        <div ref={mobileStripRef} className="lg:hidden flex overflow-x-auto py-2.5 space-x-1.5 border-t border-emerald-950/80">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                data-active={isActive ? 'true' : 'false'}
                onClick={() => setActiveTab(item.id)}
                className={`flex-shrink-0 flex items-center px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-400 to-teal-400 text-slate-950 font-extrabold'
                    : 'bg-[#091a15] text-emerald-200/75'
                }`}
              >
                <Icon className="w-3.5 h-3.5 mr-1" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
