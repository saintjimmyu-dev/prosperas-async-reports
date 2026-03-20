const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, { status, code, details } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status ?? 500;
    this.code = code ?? "HTTP_ERROR";
    this.details = details ?? {};
  }
}

async function parseJsonSafely(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

async function request(path, { method = "GET", token, body, signal } = {}) {
  const headers = {
    Accept: "application/json",
  };

  if (body) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });

  const data = await parseJsonSafely(response);

  if (!response.ok) {
    const errorPayload = data?.error ?? {};
    throw new ApiError(errorPayload.message ?? "La API respondio con error.", {
      status: response.status,
      code: errorPayload.code,
      details: errorPayload.details,
    });
  }

  return data;
}

export function login(username, password) {
  return request("/auth/login", {
    method: "POST",
    body: { username, password },
  });
}

export function createJob(token, payload) {
  return request("/jobs", {
    method: "POST",
    token,
    body: payload,
  });
}

export function listJobs(token, { pageSize = 20, cursor } = {}) {
  const params = new URLSearchParams({ page_size: String(pageSize) });

  if (cursor) {
    params.set("cursor", cursor);
  }

  return request(`/jobs?${params.toString()}`, {
    token,
  });
}
