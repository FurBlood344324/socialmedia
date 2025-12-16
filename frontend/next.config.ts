import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  allowedDevOrigins: [
    "http://192.168.*.*:3000",
    "http://10.*.*.*:3000",
    "http://172.16.*.*:3000",
    "http://localhost:3000",
  ],
}

export default nextConfig
