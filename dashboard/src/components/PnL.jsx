import { useState, useEffect } from 'react'
import axios from 'axios'

function PnL() {
    const [summary, setSummary] = useState(null)

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_URL}/summary`)
                setSummary(response.data)
            } catch (error) {
                console.error("Fetch error:", error)
            }
        }

        fetchSummary()
        const interval = setInterval(fetchSummary, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div>
            <h3 style={{ fontWeight: 'normal' }}>Portfolio PnL: ${summary ? summary.portfolio_pnl.toFixed(2) : "Loading..."}</h3>
            <h3 style={{ fontWeight: 'normal' }}>Unrealised PnL: ${summary ? summary.unrealised.toFixed(2) : "Loading..."}</h3>
            <h3 style={{ fontWeight: 'normal' }}>Realised PnL: ${summary ? summary.realised.toFixed(2) : "Loading..."}</h3>
        </div>
    )
}

export default PnL
