import { useState } from 'react'
import KeywordSearch from './KeywordSearch';
import './App.css';

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className="App">
         <KeywordSearch />
      </div>
    </>
  )
}

export default App
