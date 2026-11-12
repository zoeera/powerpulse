const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/+$/, '');
const BACKEND_ORIGIN = API_BASE.replace(/\/api\/v1$/, '');

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('powerpulse_token') || null;
  }

  getFileUrl(relativeUrl) {
    if (!relativeUrl) return '';
    if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
      return relativeUrl;
    }
    return `${BACKEND_ORIGIN}${relativeUrl.startsWith('/') ? '' : '/'}${relativeUrl}`;
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('powerpulse_token', token);
    } else {
      localStorage.removeItem('powerpulse_token');
    }
  }

  async request(endpoint, options = {}, retriesLeft = 1) {
    const url = `${API_BASE}${endpoint}`;
    const headers = { ...(options.headers || {}) };

    const activeToken = this.token || 'demo_token';
    if (!headers['Authorization']) {
      headers['Authorization'] = `Bearer ${activeToken}`;
    }

    const isFormData = options.body instanceof FormData;
    if (!headers['Content-Type'] && !isFormData) {
      headers['Content-Type'] = 'application/json';
    }

    const timeoutMs = isFormData ? 55000 : 35000;
    const controller = new AbortController();
    const timerId = setTimeout(() => controller.abort(), timeoutMs);

    let response;
    try {
      response = await fetch(url, { ...options, headers, signal: controller.signal });
    } catch (err) {
      clearTimeout(timerId);
      if (err.name === 'AbortError') {
        throw new Error('Request timed out while waiting for the server. Please try again in a few seconds (or use Enter Details Manually).');
      }
      if (retriesLeft > 0 && !isFormData) {
        await new Promise((r) => setTimeout(r, 3000));
        return this.request(endpoint, options, retriesLeft - 1);
      }
      throw new Error('Server is waking up or temporarily unreachable. Please wait 15–30 seconds and try again.');
    } finally {
      clearTimeout(timerId);
    }

    if ((response.status === 502 || response.status === 503) && retriesLeft > 0 && !isFormData) {
      await new Promise((r) => setTimeout(r, 3000));
      return this.request(endpoint, options, retriesLeft - 1);
    }

    if (response.status === 401 && this.token) {
      this.setToken(null);
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      if (response.status === 502 || response.status === 503) {
        throw new Error('Server is waking up from sleep. Please wait 20–30 seconds and try again.');
      }
      throw new Error(data.detail || data.message || `API error: ${response.status}`);
    }

    return data;
  }

  // Auth
  async register(payload) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (data.access_token) this.setToken(data.access_token);
    return data;
  }

  async login(payload, optionalPassword) {
    let body = payload;
    if (typeof payload === 'string') {
      body = { email: payload, password: optionalPassword };
    }
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (data.access_token) this.setToken(data.access_token);
    return data;
  }

  async getProfile() {
    return this.request('/users/me');
  }

  async deleteMyData() {
    const res = await this.request('/users/me', { method: 'DELETE' });
    this.setToken(null);
    return res;
  }

  // Bills
  async uploadBill(file) {
    const formData = new FormData();
    formData.append('file', file);
    const idempotencyKey = `idemp_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    return this.request('/bills/upload', {
      method: 'POST',
      headers: {
        'Idempotency-Key': idempotencyKey,
      },
      body: formData,
    });
  }

  async createBillManual(billData) {
    return this.request('/bills/manual', {
      method: 'POST',
      body: JSON.stringify(billData),
    });
  }

  createManualBill(billData) {
    return this.createBillManual(billData);
  }

  async getBills() {
    return this.request('/bills');
  }

  async updateBill(id, updateData) {
    return this.request(`/bills/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  }

  // Smart Meter
  async uploadMeterCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('/meter/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async getMeterReadings() {
    return this.request('/meter/readings');
  }

  // Appliances
  async getAppliances() {
    return this.request('/appliances');
  }

  async addAppliance(appliance) {
    return this.request('/appliances', {
      method: 'POST',
      body: JSON.stringify(appliance),
    });
  }

  async deleteAppliance(id) {
    return this.request('/appliances/' + id, { method: 'DELETE' });
  }

  // Forecasts
  async getMonthlyForecast(month, year) {
    const params = new URLSearchParams();
    if (month) params.append('target_month', month);
    if (year) params.append('target_year', year);
    return this.request(`/forecasts/monthly?${params.toString()}`);
  }

  async getDailyForecast(days = 7) {
    return this.request(`/forecasts/daily?days=${days}`);
  }

  async getBillForecast() {
    return this.request('/forecasts/bill');
  }

  // Spikes
  async getSpikes(unresolvedOnly = false) {
    return this.request(`/spikes?unresolved_only=${unresolvedOnly}`);
  }

  async resolveSpike(id) {
    return this.request(`/spikes/${id}/resolve`, {
      method: 'PATCH',
      body: JSON.stringify({ is_resolved: true }),
    });
  }

  // Recommendations
  async getRecommendations() {
    return this.request('/recommendations');
  }

  async calculateSolarRoi(params) {
    return this.request('/recommendations/solar', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Reports
  async generateReport(period = 'Last 12 Months') {
    return this.request('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ report_period: period }),
    });
  }
}

export const api = new ApiClient();

