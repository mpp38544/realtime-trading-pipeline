import Header from './components/Header'
import PnlChart from './components/PnLChart'
import Positions from './components/Positions'
import Trades from './components/Trades'
import PositionBarChart from './components/PositionBarChart'
import Metrics from './components/Metrics'
import DrawdownChart from './components/DrawdownChart'
import ActivityFeed from './components/ActivityFeed'

function App() {
  return (
    <div style={{ 
        width: '100%',
        padding: '20px',
        color: 'white',
        fontFamily: 'monospace',
        boxSizing: 'border-box',
        overflowY: 'hidden'
    }}>

      <div style={{ display: 'flex', gap: '20px', overflowY: 'hidden' }}>
        <div style={{ flex: 1 }}>
          <Header />
        </div>
        <div style={{ flex: 1 }}>
          <Metrics />
        </div>
      </div>


      {/* Main two-column layout */}
      <div style={{ display: 'flex', gap: '20px'}}>
      
        {/* Left column - main content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          
          {/* Row 2 - PnL and Drawdown charts */}
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1 }}>
              <PnlChart />
            </div>
            <div style={{ flex: 1 }}>
              <DrawdownChart />
            </div>
          </div>

          {/* Row 3 - Positions and Trades tables */}
          <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
            <div style={{ flex: 1 }}>
                        <PositionBarChart />
            </div>
            <div style={{ flex: 1 }}>
              <Trades />
            </div>
          </div>

          <Positions />

        </div>

        {/* Right sidebar */}
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

      </div>

    </div>
  )
}

export default App