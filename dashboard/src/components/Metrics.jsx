import { useState, useEffect } from 'react'
import axios from 'axios'

function Metrics() {
    const [metrics, setMetrics] = useState(null)

    useEffect(() => {
        const fetchMetrics = async () => {
            const response = await axios.get("http://localhost:8000/metrics")
            setMetrics(response.data)
        }

        fetchMetrics()
        const interval = setInterval(fetchMetrics, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div>
            <h1>Metrics</h1>
            <h2 style={{ fontWeight: 'normal' }}>Sharpe Ratio: {metrics ? metrics.sharpe_ratio ?? "Calculating..." : "Loading..."}</h2>
            <h2 style={{ fontWeight: 'normal' }}>Max Drawdown: {metrics ? (metrics.max_drawdown * 100).toFixed(2)  + "%" ?? "Calculating..." : "Loading..."}</h2>
        </div>
    )
}

export default Metrics