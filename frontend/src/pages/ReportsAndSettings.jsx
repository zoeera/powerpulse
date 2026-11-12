import React, { useState, useEffect } from 'react';
import { 
  FileText, Download, Trash2, ShieldAlert, CheckCircle2, 
  ExternalLink, Calendar, RefreshCw, Edit3, Save 
} from 'lucide-react';
import { api } from '../api/client';
import ConfidenceBadge from '../components/ConfidenceBadge';

const EDITABLE_BILL_FIELDS = [
  { key: 'energy_charges', label: 'Energy Charges (₹)' },
  { key: 'fixed_charges', label: 'Fixed Charges (₹)' },
  { key: 'customer_charges', label: 'Customer Charges (₹)' },
  { key: 'electricity_duty', label: 'Electricity Duty (₹)' },
  { key: 'subsidy_amount', label: 'Govt Subsidy (₹)' },
  { key: 'net_payable', label: 'Net Payable (₹)' },
];

export default function ReportsAndSettings({ user, onDataDeleted }) {
  const [bills, setBills] = useState([]);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [reportUrl, setReportUrl] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [message, setMessage] = useState('');
  const [editingBillId, setEditingBillId] = useState(null);
  const [editFields, setEditFields] = useState({});
  const [savingBill, setSavingBill] = useState(false);

  useEffect(() => {
    loadBills();
  }, []);

  const loadBills = async () => {
    try {
      const data = await api.getBills();
      setBills(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateReport = async () => {
    setGeneratingPdf(true);
    setMessage('');
    try {
      const rep = await api.generateReport('Last 12 Months');
      setReportUrl(rep.download_url);
      setMessage('PDF Report generated successfully! Click download below.');
    } catch (e) {
      setMessage('Could not generate report: ' + e.message);
    } finally {
      setGeneratingPdf(false);
    }
  };

  const handleDeleteData = async () => {
    setDeleting(true);
    try {
      await api.deleteMyData();
      if (onDataDeleted) onDataDeleted();
    } catch (e) {
      setMessage('Error deleting data: ' + e.message);
    } finally {
      setDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const handleEditBill = (bill) => {
    setEditingBillId(bill.id);
    setEditFields({
      energy_charges: bill.energy_charges ?? 0,
      fixed_charges: bill.fixed_charges ?? 0,
      customer_charges: bill.customer_charges ?? 0,
      electricity_duty: bill.electricity_duty ?? 0,
      subsidy_amount: bill.subsidy_amount ?? 0,
      net_payable: bill.net_payable ?? 0,
    });
  };

  const handleCancelEdit = () => {
    setEditingBillId(null);
    setEditFields({});
  };

  const handleSaveBillEdit = async (billId) => {
    setSavingBill(true);
    try {
      const changes = Object.fromEntries(
        EDITABLE_BILL_FIELDS.map(({ key }) => {
          const parsed = Number(editFields[key]);
          return [key, Number.isFinite(parsed) ? parsed : 0];
        })
      );
      await api.updateBill(billId, changes);
      setEditingBillId(null);
      setEditFields({});
      await loadBills();
    } catch (e) {
      setMessage('Error saving bill: ' + e.message);
    } finally {
      setSavingBill(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Radiant Gradient Emerald Header */}
      <div className="relative overflow-hidden rounded-3xl p-7 sm:p-8 bg-gradient-emerald-hero shadow-2xl">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md border border-white/25 mb-3">
          <FileText className="w-3.5 h-3.5 text-yellow-300" />
          <span>Statements & Account</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Reports & Account Settings
        </h1>
        <p className="text-sm text-emerald-100 mt-1 max-w-2xl font-medium">
          Download your complete electricity and solar report as a PDF, view your past bill records, or delete your account anytime.
        </p>
      </div>

      {/* PDF Export Section */}
      <div className="card-emerald p-6 sm:p-7 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-bold text-white">Download Full Bill & Solar Summary</h2>
            <p className="text-xs text-emerald-300/70 mt-0.5">
              Includes your monthly usage, appliance power breakdown, and solar savings estimates
            </p>
          </div>

          <button
            onClick={handleGenerateReport}
            disabled={generatingPdf}
            className="btn-yellow-contrast px-5 py-2.5 rounded-xl text-xs flex items-center space-x-2 transition disabled:opacity-50"
          >
            {generatingPdf ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Preparing PDF...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Download PDF Statement</span>
              </>
            )}
          </button>
        </div>

        {message && (
          <div className="p-4 rounded-xl bg-yellow-400/15 border border-yellow-400/30 text-yellow-200 text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-yellow-400 shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {reportUrl && (
          <div className="pt-2">
            <a
              href={api.getFileUrl(reportUrl)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center space-x-2 text-xs font-bold text-yellow-300 hover:underline"
            >
              <span>Click to Open / Download PDF File</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        )}
      </div>

      {/* Bill History Table */}
      <div className="card-emerald p-6 sm:p-7">
        <h2 className="text-lg font-bold text-white mb-1">Past Recorded Bills</h2>
        <p className="text-xs text-emerald-300/70 mb-4">History of all bills saved to your account</p>

        {bills.length === 0 ? (
          <p className="text-xs text-emerald-300/70 py-4">No bills recorded yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-emerald-300/70 border-b border-emerald-900/60 uppercase font-mono">
                <tr>
                  <th className="py-2.5 px-3">Billing Period</th>
                  <th className="py-2.5 px-3">Electricity Provider</th>
                  <th className="py-2.5 px-3">Units Used</th>
                  <th className="py-2.5 px-3">Energy Charges (₹)</th>
                  <th className="py-2.5 px-3">Govt Discount (₹)</th>
                  <th className="py-2.5 px-3">Amount Paid (₹)</th>
                  <th className="py-2.5 px-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-950/80">
                {bills.map((b) => (
                  <React.Fragment key={b.id}>
                    <tr className="hover:bg-[#071d18]/60 text-emerald-100">
                      <td className="py-3 px-3 font-semibold text-white">
                        <span className="whitespace-nowrap">{b.from_date} → {b.to_date}</span>
                      </td>
                      <td className="py-3 px-3">{b.provider}</td>
                      <td className="py-3 px-3 font-bold text-white">{b.units_consumed_kwh} Units</td>
                      <td className="py-3 px-3">₹{b.energy_charges}</td>
                      <td className="py-3 px-3 text-yellow-300 font-semibold">
                        {b.subsidy_amount > 0 ? `₹${b.subsidy_amount}` : '₹0'}
                      </td>
                      <td className="py-3 px-3 font-bold text-white">₹{b.net_payable}</td>
                      <td className="py-3 px-3">
                        <button
                          type="button"
                          onClick={() => (editingBillId === b.id ? handleCancelEdit() : handleEditBill(b))}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-emerald-900/40 hover:bg-emerald-800/60 border border-emerald-700/50 text-emerald-200 text-xs font-semibold transition"
                        >
                          <Edit3 className="w-3 h-3" />
                          <span>{editingBillId === b.id ? 'Close' : 'Edit'}</span>
                        </button>
                      </td>
                    </tr>
                    {editingBillId === b.id && (
                      <tr className="bg-[#071713]">
                        <td colSpan={7} className="p-4 border-t border-emerald-800/40">
                          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                            {EDITABLE_BILL_FIELDS.map((field) => (
                              <div key={field.key}>
                                <label className="block text-[11px] font-bold text-emerald-200 mb-1">
                                  {field.label}
                                </label>
                                <input
                                  type="number"
                                  step="any"
                                  value={editFields[field.key] ?? ''}
                                  onChange={(e) =>
                                    setEditFields((prev) => ({
                                      ...prev,
                                      [field.key]: e.target.value,
                                    }))
                                  }
                                  className="w-full bg-[#091c17] border border-emerald-700/60 focus:border-yellow-400 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none"
                                />
                              </div>
                            ))}
                          </div>
                          <div className="flex justify-end space-x-2 mt-4">
                            <button
                              type="button"
                              onClick={handleCancelEdit}
                              className="px-3.5 py-1.5 rounded-lg border border-emerald-800 text-emerald-200 text-xs font-semibold hover:bg-emerald-900/40 transition"
                            >
                              Cancel
                            </button>
                            <button
                              type="button"
                              onClick={() => handleSaveBillEdit(b.id)}
                              disabled={savingBill}
                              className="btn-yellow-contrast px-3.5 py-1.5 rounded-lg text-xs inline-flex items-center space-x-1.5 transition disabled:opacity-50"
                            >
                              <Save className="w-3.5 h-3.5" />
                              <span>{savingBill ? 'Saving...' : 'Save'}</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Privacy: Delete My Data */}
      <div className="card-emerald p-6 border-rose-800/60 bg-rose-950/20">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h2 className="text-lg font-bold text-rose-300 flex items-center">
              <ShieldAlert className="w-5 h-5 mr-1.5 text-rose-400" />
              Delete Account & All Bills
            </h2>
            <p className="text-xs text-rose-300/80 mt-0.5">
              Permanently delete all your uploaded bills, appliance data, and account information.
            </p>
          </div>

          <button
            onClick={() => setShowDeleteModal(true)}
            className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-md transition"
          >
            Delete Account & Data
          </button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="emerald-subpanel border border-yellow-400/30 p-6 rounded-2xl max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Confirm Account & Data Deletion</h3>
            <p className="text-xs text-emerald-200/80 leading-relaxed">
              This will permanently delete all your bills and data. This cannot be undone.
            </p>
            <div className="flex justify-end space-x-3 pt-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 rounded-lg border border-emerald-800 text-emerald-200 text-xs font-semibold hover:bg-emerald-900/40 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteData}
                disabled={deleting}
                className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition"
              >
                {deleting ? 'Deleting...' : 'Yes, Delete Everything'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
