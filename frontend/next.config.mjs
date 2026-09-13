/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // All backend URLs come from env vars — never hardcode hosts here.
  env: {
    NEXT_PUBLIC_APP_NAME: "NuroFlow"
  }
};

export default nextConfig;
