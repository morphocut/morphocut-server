module.exports = {
    baseUrl: "/frontend",
    assetsDir: "static",
    devServer: {
        proxy: {
            '/static': {
                target: 'http://localhost:5000',
                ws: true,
                changeOrigin: true,
                proxyTimeout: 5 * 60 * 1000,
                onProxyReq: (proxyReq, req, res) => req.setTimeout(5 * 60 * 1000)
            },
            '/api': {
                target: 'http://localhost:5000',
                ws: true,
                changeOrigin: true,
                proxyTimeout: 30 * 60 * 1000, // set proxy timeout to 30 minutes due to long running requests (=> processing)
                onProxyReq: (proxyReq, req, res) => req.setTimeout(30 * 60 * 1000)
            },
        },
    }
}