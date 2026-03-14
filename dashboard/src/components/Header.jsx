import { useState, useEffect } from 'react'
import axios from 'axios'

function Header() {
    const [portfolio, setPortfolio] = useState(null)

    useEffect(() => {
        const fetchPortfolio = async () => {
            const response = await axios.get("http://localhost:8000/portfolio")
            setPortfolio(response.data)
        }

        fetchPortfolio()
        const interval = setInterval(fetchPortfolio, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div>
            <h1><strong>Trading Dashboard</strong></h1>
            <h2 style={{ fontWeight: 'normal' }}>Portfolio PnL: ${portfolio ? portfolio.portfolio_pnl.toFixed(2) : "Loading..."}</h2>
        </div>
    )
}

export default Header