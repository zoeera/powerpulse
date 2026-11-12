import React, { useState } from 'react';
import { 
  UploadCloud, FileText, CheckCircle2, AlertTriangle, 
  Edit3, Save, IndianRupee, ShieldCheck, RefreshCw, FileCode, Sparkles 
} from 'lucide-react';
import { api } from '../api/client';
import ConfidenceBadge from '../components/ConfidenceBadge';

const BILL_FIELDS = [
  { label: 'Electricity Provider (e.g. TGSPDCL)', key: 'provider', required: true },
  { label: 'State', key: 'state', required: true },
  { label: 'Tariff / Plan Category', key: 'tariff_category', required: true },
  { label: 'Bill From Date', key: 'from_date', type: 'date', required: true },
  { label: 'Bill To Date', key: 'to_date', type: 'date', required: true },
  { label: 'Billing Days', key: 'billing_days', type: 'number', manualOnly: true, required: true },
  { label: 'Units Used (kWh)', key: 'units_consumed_kwh', type: 'number', required: true },
  { label: 'Energy Charges (₹)', key: 'energy_charges', type: 'number' },
  { label: 'Fixed Monthly Charges (₹)', key: 'fixed_charges', type: 'number' },
  { label: 'Customer / Service Charges (₹)', key: 'customer_charges', type: 'number' },
  { label: 'Electricity Tax / Duty (₹)', key: 'electricity_duty', type: 'number' },
  { label: 'Govt Subsidy / Discount (₹)', key: 'subsidy_amount', type: 'number' },
  { label: 'Govt Scheme (e.g. Gruha Jyothi)', key: 'subsidy_scheme' },
  { label: 'Total Amount to Pay (₹)', key: 'net_payable', type: 'number' },
  { label: 'Meter Number', key: 'meter_number' },
];

const EMPTY_MANUAL_FORM = {
  provider: '',
  state: '',
  tariff_category: '',
  from_date: '',
  to_date: '',
  billing_days: 0,
  units_consumed_kwh: 0,
  energy_charges: 0,
  fixed_charges: 0,
  customer_charges: 0,
  electricity_duty: 0,
  subsidy_amount: 0,
  subsidy_scheme: '',
  net_payable: 0,
  meter_number: '',
  consumer_number: '',
  manual_review_required: false,
  confidence_score: 1.0,
};

function BillFieldsGrid({ fields, values, onChange, enforceRequired = false }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
      {fields.map((f) => (
        <div key={f.key}>
          <label className="block text-xs font-bold text-emerald-200 mb-1.5">{f.label}</label>
          <input
            type={f.type || 'text'}
            step={f.type === 'number' ? (f.key === 'billing_days' ? '1' : 'any') : undefined}
            required={enforceRequired && f.required}
            value={values[f.key] ?? ''}
            onChange={(e) => onChange(f.key, f.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value)}
            className="w-full bg-[#071713] border border-emerald-700/60 focus:border-yellow-400 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none"
          />
        </div>
      ))}
    </div>
  );
}

export default function BillUpload({ onBillSaved }) {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'manual'
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [parsedBill, setParsedBill] = useState(null);
  const [editableFields, setEditableFields] = useState({});
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState('');

  const [manualForm, setManualForm] = useState({
    provider: 'TGSPDCL',
    state: 'Telangana',
    tariff_category: 'LT-I(A)',
    from_date: '2024-02-07',
    to_date: '2024-03-01',
    billing_days: 23,
    units_consumed_kwh: 148,
    energy_charges: 599.80,
    fixed_charges: 16.60,
    customer_charges: 90.00,
    electricity_duty: 8.88,
    subsidy_amount: 715.00,
    subsidy_scheme: 'GJS',
    net_payable: 0.00,
    meter_number: '29443604',
    consumer_number: '',
    manual_review_required: false,
    confidence_score: 1.0,
  });

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      selectFile(e.dataTransfer.files[0]);
    }
  };

  const selectFile = (selected) => {
    if (selected.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10 MB limit.');
      return;
    }
    setFile(selected);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    setSavedSuccess(false);

    try {
      const res = await api.uploadBill(file);
      setParsedBill(res);
      setEditableFields({
        provider: res.provider,
        state: res.state,
        tariff_category: res.tariff_category,
        from_date: res.from_date,
        to_date: res.to_date,
        billing_days: res.billing_days,
        units_consumed_kwh: res.units_consumed_kwh,
        energy_charges: res.energy_charges,
        fixed_charges: res.fixed_charges,
        customer_charges: res.customer_charges,
        electricity_duty: res.electricity_duty,
        subsidy_amount: res.subsidy_amount,
        subsidy_scheme: res.subsidy_scheme,
        net_payable: res.net_payable,
        meter_number: res.meter_number,
        consumer_number: res.consumer_number,
      });
      if (onBillSaved) onBillSaved(res);
    } catch (err) {
      setError(err.message || 'Error uploading or parsing bill');
    } finally {
      setUploading(false);
    }
  };

  const handleFieldChange = (key, value) => {
    setEditableFields(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveEdits = async () => {
    if (!parsedBill || !parsedBill.id) return;
    try {
      const updated = await api.updateBill(parsedBill.id, editableFields);
      setParsedBill(updated);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 4000);
      if (onBillSaved) onBillSaved(updated);
    } catch (err) {
      setError(err.message || 'Could not save modifications');
    }
  };

  const handleManualFieldChange = (key, value) => {
    setManualForm(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.createBillManual(manualForm);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 5000);
      if (onBillSaved) onBillSaved(res);
      setManualForm({ ...EMPTY_MANUAL_FORM });
    } catch (err) {
      setError(err.message || 'Could not save manual bill');
    }
  };

  const switchTab = (tab) => {
    setActiveTab(tab);
    setSavedSuccess(false);
    setError('');
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Radiant Gradient Emerald Header */}
      <div className="relative overflow-hidden rounded-3xl p-7 sm:p-8 bg-gradient-emerald-hero shadow-2xl">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md border border-white/25 mb-3">
          <UploadCloud className="w-3.5 h-3.5 text-yellow-300" />
          <span>Smart Bill Scanner (TGSPDCL, UPPCL, MPWZ, BSES & more)</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Upload Electricity Bill
        </h1>
        <p className="text-sm text-emerald-100 mt-1 max-w-2xl font-medium">
          Take a photo of your paper bill or upload a PDF. We automatically read your units, rates, and government discounts.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-emerald-900/60">
        <button
          onClick={() => switchTab('upload')}
          className={`pb-3 px-5 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'upload'
              ? 'border-yellow-400 text-yellow-300 text-glow-yellow'
              : 'border-transparent text-emerald-200/60 hover:text-white'
          }`}
        >
          Upload Bill Photo / PDF
        </button>
        <button
          onClick={() => switchTab('manual')}
          className={`pb-3 px-5 text-sm font-bold border-b-2 transition-all ${
            activeTab === 'manual'
              ? 'border-yellow-400 text-yellow-300 text-glow-yellow'
              : 'border-transparent text-emerald-200/60 hover:text-white'
          }`}
        >
          Enter Details Manually
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-sm flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {activeTab === 'upload' ? (
        <div className="space-y-6">
          {/* Drag & Drop Area */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            className="border-2 border-dashed border-emerald-400/40 hover:border-yellow-400 rounded-3xl p-10 text-center card-emerald hover:bg-[#0e2720] transition cursor-pointer shadow-md"
            onClick={() => document.getElementById('bill-file-input').click()}
          >
            <input
              id="bill-file-input"
              type="file"
              accept=".pdf,image/png,image/jpeg,image/jpg"
              className="hidden"
              onChange={(e) => e.target.files && selectFile(e.target.files[0])}
            />
            <div className="w-16 h-16 mx-auto rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 flex items-center justify-center mb-3">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-white">
              {file ? file.name : 'Click to select or drag your bill here'}
            </h3>
            <p className="text-xs text-emerald-300/70 mt-1 max-w-md mx-auto">
              Supports photos and PDFs from TGSPDCL, UPPCL, MPWZ, BSES & all major providers (up to 10 MB)
            </p>
            {file && (
              <span className="inline-block mt-3 text-xs font-bold px-3 py-1 rounded-full bg-yellow-400/20 text-yellow-300 border border-yellow-400/30">
                {(file.size / (1024 * 1024)).toFixed(2)} MB Selected
              </span>
            )}
          </div>

          {file && (
            <div className="flex justify-end">
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="btn-yellow-contrast px-6 py-2.5 rounded-xl text-sm flex items-center space-x-2 transition disabled:opacity-50"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Reading your bill...</span>
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4" />
                    <span>Scan & Read Bill</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Extracted Fields Editor */}
          {parsedBill && (
            <div className="card-emerald p-6 sm:p-7 space-y-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-emerald-900/60 pb-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-bold text-white">Details Found on Your Bill</h2>
                    <ConfidenceBadge score={parsedBill.confidence_score} />
                  </div>
                  <p className="text-xs text-emerald-300/70 mt-0.5">
                    Please review these values. You can edit any numbers if needed.
                  </p>
                </div>
                {parsedBill.manual_review_required && (
                  <span className="text-xs font-bold px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
                    ⚠️ Please double check numbers
                  </span>
                )}
              </div>

              {/* Form Grid */}
              <BillFieldsGrid
                fields={BILL_FIELDS.filter(f => !f.manualOnly)}
                values={editableFields}
                onChange={handleFieldChange}
              />

              <div className="flex justify-between items-center pt-4 border-t border-emerald-900/60">
                {savedSuccess ? (
                  <span className="text-xs font-bold text-yellow-300 flex items-center">
                    <CheckCircle2 className="w-4 h-4 mr-1.5 text-yellow-400" />
                    Bill saved successfully!
                  </span>
                ) : <span></span>}

                <button
                  onClick={handleSaveEdits}
                  className="btn-yellow-contrast px-5 py-2.5 rounded-xl text-xs flex items-center space-x-2 transition"
                >
                  <Save className="w-4 h-4" />
                  <span>Save Bill</span>
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Manual Form */
        <form onSubmit={handleManualSubmit} className="card-emerald p-6 sm:p-7 space-y-6">
          <h2 className="text-lg font-bold text-white mb-2">Direct Bill Entry</h2>
          <BillFieldsGrid
            fields={BILL_FIELDS}
            values={manualForm}
            onChange={handleManualFieldChange}
            enforceRequired
          />
          <div className="flex justify-between items-center pt-4 border-t border-emerald-900/60">
            {savedSuccess ? (
              <span className="text-xs font-bold text-emerald-300 bg-emerald-500/15 border border-emerald-400/40 px-3.5 py-2 rounded-xl flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-400" />
                Manual bill recorded successfully!
              </span>
            ) : <span></span>}
            <button
              type="submit"
              className="btn-yellow-contrast px-6 py-2.5 rounded-xl text-sm transition"
            >
              Record Bill
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
