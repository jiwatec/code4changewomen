const API_BASE_URL = 'http://localhost:8000/api';

async function request(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    ...options.headers,
  } as any;

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  // Artisan Auth
  requestOTP: (phone: string) => 
    request('/users/request-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone }),
    }),
  
  verifyOTP: (phone: string, otp: string) =>
    request('/users/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, otp }),
    }),

  // Validator Auth
  login: (username: string, password: string) =>
    request('/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    }),

  // Artisan Actions
  getProfile: () => request('/users/profile'),
  
  submitSkill: (trade: string, file: File) => {
    const formData = new FormData();
    formData.append('trade', trade);
    formData.append('file', file);
    return request('/users/submit', {
      method: 'POST',
      body: formData,
    });
  },

  getSubmissions: () => request('/users/submissions'),

  // Validator Actions
  getPendingSubmissions: () => request('/admin/submissions/pending'),
  
  approveSubmission: (id: string, skillScore: number, professionalismScore: number) =>
    request(`/admin/submissions/${id}/approve?skillScore=${skillScore}&professionalismScore=${professionalismScore}`, {
      method: 'POST',
    }),

  rejectSubmission: (id: string) =>
    request(`/admin/submissions/${id}/reject`, {
      method: 'POST',
    }),

  // Public
  verifyCertificate: (code: string) => request(`/public/verify/${code}`),
};
