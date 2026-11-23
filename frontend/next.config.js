/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/output/:path*",
        destination: "http://127.0.0.1:8000/output/:path*",
      },
      {
        source: "/cache/:path*",
        destination: "http://127.0.0.1:8000/cache/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
