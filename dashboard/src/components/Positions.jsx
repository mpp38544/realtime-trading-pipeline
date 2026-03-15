import { useState, useEffect } from 'react'
import axios from 'axios'

function Positions() {

    const [positions, setPositions] = useState([])

    useEffect(() => {
        const fetchPositions = async () => {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_URL}/positions`)
                setPositions(response.data)
            } catch (error) {
                console.error("Fetch error:", error)
            }
        }

        fetchPositions()
        const interval = setInterval(fetchPositions, 5000)
        return () => clearInterval(interval)
    }, [])

return (
    <div>
        <h2>Current Positions</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
                <tr>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Symbol</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Inventory</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Cash Balance</th>
                    <th style={{ padding: '8px', borderBottom: '1px solid #333' }}>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {positions.map((position, index) => (
                    <tr key={index}>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333', textAlign: 'center' }}>{position.symbol}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333', textAlign: 'center' }}>{position.inventory.toFixed(6)}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333', textAlign: 'center' }}>{position.cash_balance}</td>
                        <td style={{ padding: '8px', borderBottom: '1px solid #333', textAlign: 'center' }}>{position.timestamp}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
)
}

export default Positions
