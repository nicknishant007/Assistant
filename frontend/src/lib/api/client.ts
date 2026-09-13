import axios from "axios";

/**
 * Single Axios instance for the whole app.
 *
 * - Base URL comes from env, never hardcoded.
 * - `withCredentials: true` because the real backend (Backend/api/routes/auth.py)
 *   sets an httpOnly `access_token` cookie on /api/auth/callback/google and
 *   reads it via Depends(get_current_user) — there is no bearer token to
 *   attach manually.
 * - A response interceptor normalizes FastAPI's error shape
 *   ({ detail: string }) into a single `ApiError` so UI code never has to
 *   know about Axios or FastAPI specifics.
 */
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!baseURL && typeof window !== "undefined") {
  // Fail loudly in dev rather than silently hitting the wrong host.
  // eslint-disable-next-line no-console
  console.error(
    "NEXT_PUBLIC_API_BASE_URL is not set. Copy .env.example to .env.local."
  );
}

export const apiClient = axios.create({
  baseURL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json"
  }
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status ?? 0;
    const message =
      error?.response?.data?.detail ??
      error?.message ??
      "Something went wrong talking to NuroFlow's backend.";

    return Promise.reject(new ApiError(status, message));
  }
);
