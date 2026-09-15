import axios from "axios";

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
  // eslint-disable-next-line no-console
  console.error(
    "NEXT_PUBLIC_API_BASE_URL is not set. Copy .env.example to .env.local."
  );
}

export const apiClient = axios.create({
  baseURL,
  withCredentials: true
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