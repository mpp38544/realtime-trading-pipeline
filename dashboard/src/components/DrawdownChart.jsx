import { useState, useEffect } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

function DrawdownChart() {

    const [drawdown, setDrawdown] = useState([])

    useEffect(() => {
        const fetchDrawdown = async () => {
            const response = await axios.get(`${import.meta.env.VITE_API_URL}/drawdown`)
            setDrawdown(response.data)
        }

        fetchDrawdown()
        const interval = setInterval(fetchDrawdown, 5000)
        return () => clearInterval(interval)
    }, [])

return (  
    <div>
        <h2>Drawdown</h2>
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={drawdown}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" tickFormatter={(t) => new Date(t).toLocaleTimeString()} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="drawdown" stroke="#ff0000" dot={false} />
        </LineChart>
        </ResponsiveContainer>
    </div>
)
}

export default DrawdownChart
