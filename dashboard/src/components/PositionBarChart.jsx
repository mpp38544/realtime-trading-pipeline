import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

function PositionBarChart() {

    const [pnl, setPnl] = useState([])

    useEffect(() => {
        const fetchPnl = async () => {
            const response = await axios.get("http://localhost:8000/pnl")
            setPnl(response.data)
        }

        fetchPnl()
        const interval = setInterval(fetchPnl, 5000)

        return () => clearInterval(interval)
    }, [])

    const latest = {}
        pnl.forEach(row => {
            latest[row.symbol] = row.total
        })
        const chartData = Object.entries(latest).map(([symbol, total]) => ({ symbol, total }))

return (
    <div>
        <h2>PNL</h2>
        <ResponsiveContainer width="100%" height={300}>
            <BarChart width={600} height={300} data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="symbol" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="total" fill="#00ff88" />
        </BarChart>
        </ResponsiveContainer>
    </div>
)
}

export default PositionBarChart