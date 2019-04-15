module.exports = {
    publicPath: "/frontend",
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
                proxyTimeout: 5 * 60 * 1000,
                onProxyReq: (proxyReq, req, res) => req.setTimeout(5 * 60 * 1000)
            },
            '/data': {
                target: 'http://localhost:5000',
                ws: true,
                changeOrigin: true,
                proxyTimeout: 5 * 60 * 1000,
                onProxyReq: (proxyReq, req, res) => req.setTimeout(5 * 60 * 1000)
            },
        },
    }
}