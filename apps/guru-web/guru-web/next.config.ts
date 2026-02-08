import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 🔒 STEP 7: REMOVE STRICT MODE DUPLICATION (DEV ONLY)
  // This stops double execution and duplicate logs in development
  reactStrictMode: false,
  // Use Turbopack (Next.js 16 default) with empty config
  turbopack: {},
};

export default nextConfig;
