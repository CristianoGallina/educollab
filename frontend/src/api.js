export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function apiFetch(url, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { ...options.headers };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Remove o cabeçalho antigo se estiver presente
  if (headers['x-tipo-usuario']) {
    delete headers['x-tipo-usuario'];
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    // Dispara evento para o App.jsx deslogar o usuário
    window.dispatchEvent(new Event('unauthorized'));
  }

  return response;
}
