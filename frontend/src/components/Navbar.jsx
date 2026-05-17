import { Image } from 'lucide-react'

export default function Navbar({ activeTab, onTabChange, uid, onUidChange }) {
  return (
    <nav className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
      <div className="flex items-center gap-2 text-emerald-400 font-semibold text-lg">
        <Image className="w-6 h-6" />
        <span>Image RAG Engine</span>
      </div>

      <div className="flex gap-1 bg-gray-800 rounded-lg p-1">
        <button
          onClick={() => onTabChange('upload')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'upload'
              ? 'bg-gray-700 text-white shadow'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          图片入库
        </button>
        <button
          onClick={() => onTabChange('search')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'search'
              ? 'bg-gray-700 text-white shadow'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          智能检索
        </button>
      </div>

      <div className="flex items-center gap-2 text-sm">
        <label className="text-gray-500">UID:</label>
        <input
          value={uid}
          onChange={(e) => onUidChange(e.target.value)}
          className="w-28 bg-gray-800 border border-gray-700 rounded-md px-2 py-1 text-white text-sm focus:outline-none focus:border-emerald-500 transition-colors"
        />
      </div>
    </nav>
  )
}
