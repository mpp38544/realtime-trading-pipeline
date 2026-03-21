import { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

function PnLChart() {

    const [pnl, setPnl] = useState([])

    useEffect(() => {
        const fetchPnl = async () => {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_URL}/pnl`)
                setPnl(response.data)
            } catch (error) {
                console.error("Fetch error:", error)
            }
        }

        fetchPnl()
        const interval = setInterval(fetchPnl, 5000)
        return () => clearInterval(interval)
    }, [])

return (
    <div>
        <h2>PnL</h2>
        <ResponsiveContainer width="100%" height={300}>
            <LineChart width={800} height={300} data={pnl}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
                dataKey="timestamp" 
                tickFormatter={(t) => {
                    const date = new Date(t)
                    return `${date.getMonth()+1}/${date.getDate()}`
                }}
                tick={{ fontSize: 11 }}
                interval="preserveStartEnd"
            />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="portfolio_pnl" stroke="#00ff88" dot={false} />
        </LineChart>
        </ResponsiveContainer>
    </div>
)
}

export default PnLChart
