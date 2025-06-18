import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  experimental: {
    ppr: true,
  },
  images: {
    remotePatterns: [
      {
        hostname: 'avatar.vercel.sh',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/agents/:path*',
        destination: 'http://localhost:8000/api/agents/:path*',
      },
    ];
  },
};

export default nextConfig;
