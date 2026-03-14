import Header from './components/Header'
import PnlChart from './components/PnLChart'
import Positions from './components/Positions'
import Trades from './components/Trades'
import PositionBarChart from './components/PositionBarChart'
import Metrics from './components/Metrics'
import DrawdownChart from './components/DrawdownChart'

function App() {
  return (
    <div style={{ 
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '20px',
        color: 'white',
        fontFamily: 'monospace'
    }}>
      
      <Header />
      <Metrics />

    <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
      <div style={{ flex: 1 }}>
        <PnlChart />
      </div>
      <div style={{ flex: 1 }}>
        <DrawdownChart />
      </div>
      <div style={{ flex: 1 }}>
        <PositionBarChart />
      </div>
    </div>
      
      <div style={{display: 'flex', gap: '20px', marginTop: '20px' }}>
        <div style={{ flex: 1 }}>
          <Positions />
        </div>
        <div style={{ flex: 1 }}>
          <Trades />
        </div>
      </div>

    </div>
  )
}

export default App