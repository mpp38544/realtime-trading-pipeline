import { useState, useEffect } from 'react'
import axios from 'axios'

function PnL() {
    const [portfolio, setPortfolio] = useState(null)

    useEffect(() => {
        const fetchPortfolio = async () => {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_URL}/portfolio`)
                setPortfolio(response.data)
            } catch (error) {
                console.error("Fetch error:", error)
            }
        }

        fetchPortfolio()
        const interval = setInterval(fetchPortfolio, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div>
            <h3 style={{ fontWeight: 'normal' }}>Portfolio PnL: ${portfolio ? portfolio.portfolio_pnl.toFixed(2) : "Loading..."}</h3>
            <h3 style={{ fontWeight: 'normal' }}>Unrealised PnL: ${portfolio ? portfolio.unrealised.toFixed(2) : "Loading..."}</h3>
            <h3 style={{ fontWeight: 'normal' }}>Realised PnL: ${portfolio ? portfolio.realised.toFixed(2) : "Loading..."}</h3>
        </div>
    )
}

export default PnL
