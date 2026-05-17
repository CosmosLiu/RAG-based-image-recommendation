import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, CheckCircle, XCircle, Loader2, FileImage } from 'lucide-react'

export default function UploadSection({ uid }) {
  const [status, setStatus] = useState('idle') // idle | uploading | success | error
  const [preview, setPreview] = useState(null)
  const [message, setMessage] = useState('')

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    setPreview(URL.createObjectURL(file))
    setStatus('uploading')
    setMessage('')

    const formData = new FormData()
    formData.append('uid', uid)
    formData.append('file', file)

    try {
      const res = await fetch('/api/v1/images/upload', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (res.ok) {
        setStatus('success')
        setMessage(data.image_url)
      } else {
        setStatus('error')
        setMessage(data.detail || '上传失败')
      }
    } catch {
      setStatus('error')
      setMessage('网络错误，请检查后端服务是否启动')
    }
  }, [uid])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'] },
    maxFiles: 1,
    disabled: status === 'uploading',
  })

  const reset = () => {
    setStatus('idle')
    setPreview(null)
    setMessage('')
  }

  return (
    <div className="flex flex-col items-center gap-6 mt-12">
      <h2 className="text-xl font-semibold text-gray-200">图片入库</h2>
      <p className="text-gray-500 text-sm -mt-4">
        点击选择图片或直接将图片拖入下方区域
      </p>

      {status === 'success' ? (
        <div className="flex flex-col items-center gap-4 mt-4">
          <CheckCircle className="w-16 h-16 text-emerald-400" />
          <p className="text-emerald-400 text-lg font-medium">入库成功</p>
          {message && (
            <code className="text-sm text-gray-400 bg-gray-800 px-3 py-1 rounded">
              {message}
            </code>
          )}
          <button
            onClick={reset}
            className="mt-2 px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            继续上传
          </button>
        </div>
      ) : status === 'error' ? (
        <div className="flex flex-col items-center gap-4 mt-4">
          <XCircle className="w-16 h-16 text-red-400" />
          <p className="text-red-400 text-lg font-medium">上传失败</p>
          <p className="text-gray-500 text-sm">{message}</p>
          <button
            onClick={reset}
            className="mt-2 px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
          >
            重试
          </button>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`w-full max-w-xl h-64 border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-3 cursor-pointer transition-all
            ${isDragActive
              ? 'border-emerald-400 bg-emerald-400/10 scale-[1.02]'
              : 'border-gray-600 hover:border-gray-500 bg-gray-900/50'
            }
            ${status === 'uploading' ? 'pointer-events-none opacity-60' : ''}
          `}
        >
          <input {...getInputProps()} />
          {status === 'uploading' ? (
            <>
              {preview && (
                <img
                  src={preview}
                  alt="preview"
                  className="w-24 h-24 object-cover rounded-lg shadow-lg"
                />
              )}
              <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
              <p className="text-gray-400 text-sm">正在上传并分析图片...</p>
            </>
          ) : isDragActive ? (
            <>
              <Upload className="w-12 h-12 text-emerald-400" />
              <p className="text-emerald-400 text-lg font-medium">释放以上传图片</p>
            </>
          ) : (
            <>
              <FileImage className="w-12 h-12 text-gray-500" />
              <div className="text-center">
                <p className="text-gray-400">
                  <span className="text-emerald-400 font-medium">点击选择</span>
                  {' '}或拖曳图片至此
                </p>
                <p className="text-gray-600 text-xs mt-1">
                  支持 JPG、PNG、GIF、WebP、BMP
                </p>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
