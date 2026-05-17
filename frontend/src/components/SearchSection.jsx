import { useState } from 'react'
import { Search, Loader2, ImageOff } from 'lucide-react'

function resolveImageUrl(imageId) {
  if (imageId.startsWith('http')) return imageId
  return `/uploads/${imageId}`
}

export default function SearchSection({ uid }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState('')

  const doSearch = async () => {
    const q = query.trim()
    if (!q) return

    setLoading(true)
    setError('')
    setSearched(true)

    try {
      const res = await fetch('/api/v1/recommend/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid, query: q, top_k: 12 }),
      })
      const data = await res.json()
      if (res.ok) {
        setResults(data.results || [])
      } else {
        setError(data.detail || '搜索失败')
      }
    } catch {
      setError('网络错误，请检查后端服务是否启动')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') doSearch()
  }

  return (
    <div className="flex flex-col items-center gap-6 mt-8">
      <h2 className="text-xl font-semibold text-gray-200">智能检索</h2>

      <div className="w-full max-w-2xl relative">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入搜索词，如：温暖的午后、科技感城市..."
          className="w-full bg-gray-900 border border-gray-700 rounded-xl px-5 py-4 pr-14 text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-colors text-lg"
        />
        <button
          onClick={doSearch}
          disabled={loading}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-emerald-400 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            <Search className="w-6 h-6" />
          )}
        </button>
      </div>

      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      {searched && !loading && !error && results.length === 0 && (
        <div className="flex flex-col items-center gap-3 mt-16 text-gray-600">
          <ImageOff className="w-16 h-16" />
          <p className="text-lg">未找到匹配的图片</p>
          <p className="text-sm">尝试使用更宽泛的关键词搜索</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 w-full mt-2">
          {results.map((imageId, i) => (
            <a
              key={i}
              href={resolveImageUrl(imageId)}
              target="_blank"
              rel="noreferrer"
              className="group relative aspect-square rounded-xl overflow-hidden bg-gray-900 border border-gray-800 hover:border-emerald-500/50 transition-all"
            >
              <img
                src={resolveImageUrl(imageId)}
                alt={`result-${i}`}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                loading="lazy"
                onError={(e) => {
                  e.target.src = ''
                  e.target.parentNode.classList.add('bg-gray-800')
                }}
              />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                <span className="text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity truncate px-2 max-w-full">
                  {imageId}
                </span>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
