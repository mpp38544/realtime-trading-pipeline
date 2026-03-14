import { useState, useEffect } from 'react'
import axios from 'axios'

function Trades() {

    const [trades, setTrades] = useState([])

    useEffect(() => {
        const fetchTrades = async () => {
            const response = await axios.get("http://localhost:8000/trades")
            setTrades(response.data)
        }

        fetchTrades()
        const interval = setInterval(fetchTrades, 5000)
        return () => clearInterval(interval)
    }, [])

return (
    <div>
        <h2>Recent Trades</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
                <tr>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Symbol</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Side</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Price</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Quantity</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {trades.map((trade, index) => (
                    <tr key={index}>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{trade.symbol}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{trade.side}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{trade.price}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{trade.quantity}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{trade.timestamp}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
)
}

export default Trades