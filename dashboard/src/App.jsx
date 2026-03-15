import PnL from './components/PnL'
import PnlChart from './components/PnLChart'
import Positions from './components/Positions'
import Trades from './components/Trades'
import PositionBarChart from './components/PositionBarChart'
import Metrics from './components/Metrics'
import DrawdownChart from './components/DrawdownChart'
import ActivityFeed from './components/ActivityFeed'
import { useState, useEffect } from 'react'

function App() {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div style={{ 
        width: '100%',
        padding: '20px',
        color: 'white',
        fontFamily: 'monospace',
        boxSizing: 'border-box',
        overflowY: 'hidden'
    }}>
      
      {/* Header Row */}
      <div style={{ 
        display: 'flex', 
        flexDirection: isMobile ? 'column' : 'row',
        gap: '20px', overflowY: 'hidden' 
      }}>
        <div style={{ flex: 1 }}>
          <h1 style={{marginTop: isMobile ? '10px': '30px'}}><strong>Trading Dashboard (Avellaneda-Stoikov Model)</strong></h1>
        </div>
        <div style={{ flex: 1, marginTop: isMobile ? '10px' : '20px' }}>
            <div style={{ display: 'flex', gap: '20px'}}>
              <div style={{ flex: 1}}><Metrics /></div>
              <div style={{ flex: 1}}><PnL /></div>
            </div>
        </div>
      </div>


      {/* Main two-column layout */}
      <div style={{ display: 'flex', gap: '20px', flexDirection: isMobile ? 'column' : 'row'}}>
      
        {/* Left column - main content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          
          {/* Row 2 - PnL and Drawdown charts */}
          <div style={{ display: 'flex', gap: '20px', flexDirection: isMobile ? 'column' : 'row'}}>
            <div style={{ flex: 1 }}><PnlChart /></div>
            <div style={{ flex: 1 }}><DrawdownChart /></div>
          </div>

          {/* Row 3 - Positions and Trades tables */}
          <div style={{ display: 'flex', gap: '20px', marginTop: '20px',  flexDirection: isMobile ? 'column' : 'row'}}>
            <div style={{ flex: 1 }}><PositionBarChart /></div>
            <div style={{ flex: 1 }}><Trades /></div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <Positions />
          </div>

        </div>

        {/* Right sidebar */}
        {isMobile && (
          <div style={{ 
            width: '400px', 
            flexShrink: 0,
            position: 'sticky',
            top: '20px',
            height: 'calc(100vh - 150px)',
            overflowX: 'hidden',
            overflowY: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
        }}>
          <ActivityFeed />
        </div>
        )}
        
      </div>

    </div>
  )
}

export default App