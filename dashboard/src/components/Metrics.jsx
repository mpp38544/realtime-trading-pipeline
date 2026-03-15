import { useState, useEffect } from 'react'
import axios from 'axios'

function Metrics() {
    const [metrics, setMetrics] = useState(null)

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_URL}/metrics`)
                setMetrics(response.data)
            } catch (error) {
                console.error("Fetch error:", error)
            }
        }

        fetchMetrics()
        const interval = setInterval(fetchMetrics, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div>
            <h2>Metrics</h2>
            <h3 style={{ fontWeight: 'normal' }}>Sharpe Ratio: {metrics ? metrics.sharpe_ratio ?? "Calculating..." : "Loading..."}</h3>
            <h3 style={{ fontWeight: 'normal' }}>Max Drawdown: {metrics ? (metrics.max_drawdown * 100).toFixed(2)  + "%" ?? "Calculating..." : "Loading..."}</h3>
        </div>
    )
}

export default Metrics
