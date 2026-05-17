import { useState } from 'react'
import Navbar from './components/Navbar.jsx'
import UploadSection from './components/UploadSection.jsx'
import SearchSection from './components/SearchSection.jsx'

export default function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uid, setUid] = useState('user_001')

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        uid={uid}
        onUidChange={setUid}
      />
      <main className="flex-1 px-6 py-8 max-w-5xl mx-auto w-full">
        {activeTab === 'upload' ? (
          <UploadSection uid={uid} />
        ) : (
          <SearchSection uid={uid} />
        )}
      </main>
    </div>
  )
}
