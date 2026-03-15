import { useState, useEffect } from 'react'
import axios from 'axios'

function ActivityFeed() {

    const [logs, setLog] = useState([])

    useEffect(() => {
        const fetchLog = async () => {
            const response = await axios.get(`${import.meta.env.VITE_API_URL}/logs`)
            setLog(response.data)
        }

        fetchLog()
        const interval = setInterval(fetchLog, 5000)
        return () => clearInterval(interval)
    }, [])

    const serviceColor = (service) => {
        if (service === 'producer') return '#4488ff'
        if (service === 'processor') return '#ffcc00'
        if (service === 'executor') return '#00ff88'
        return 'white'
    }

return (  
    <div>
        <h2>Activity Feed</h2>
        <div style={{ height: 'calc(100vh - 200px)', maxHeight: '100%', overflowX: 'hidden', overflowY: 'auto'}}>
            <table style={{ width: '100%', borderCollapse: 'collapse', tableLayout: 'fixed' }}>
                <thead>
                    <tr>
                        <th style={{ width: '20%', padding: '6px', borderBottom: '1px solid #333', textAlign: 'left' }}>Service</th>
                                <th style={{ width: '50%', padding: '6px', borderBottom: '1px solid #333', textAlign: 'left' }}>Message</th>
                                <th style={{ width: '30%', padding: '6px', borderBottom: '1px solid #333', textAlign: 'left' }}>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {logs.map((log, index) => (
                        <tr key={index}>
                            <td style={{ padding: '8px', borderBottom: '1px solid #333', color: serviceColor(log.service)}}>{log.service}</td>
                            <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{log.message}</td>
                           <td style={{ padding: '6px', borderBottom: '1px solid #333', fontSize: '11px' }}>
    {new Date(log.timestamp).toLocaleTimeString()}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
    )
} 

export default ActivityFeed
