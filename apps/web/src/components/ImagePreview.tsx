import { Download, Info, RotateCcw } from "lucide-react"

const MAX_DIMENSION = 1200

interface Props {
  original: string
  resultUrl: string
  onReset: () => void
}

export default function ImagePreview({ original, resultUrl, onReset }: Props) {
  const handleDownload = async () => {
    try {
      const response = await fetch(resultUrl)
      if (!response.ok) throw new Error("Download failed")

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)

      const anchor = document.createElement("a")
      anchor.href = url
      anchor.download = "bg-removed.png"
      document.body.appendChild(anchor)
      anchor.click()
      document.body.removeChild(anchor)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error("Download error:", err)
    }
  }

  return (
    <div>
      <div className="grid grid-cols-2 gap-8">
        <div>
          <h3 className="mb-2 text-sm font-medium text-slate-500">Original</h3>
          <img
            src={original}
            alt="Original"
            className="w-full rounded-lg border border-slate-200 object-contain"
          />
        </div>
        <div>
          <h3 className="mb-2 text-sm font-medium text-slate-500">Result</h3>
          <img
            src={resultUrl}
            alt="Result"
            className="w-full rounded-lg border border-slate-200 object-contain"
          />
        </div>
      </div>

      <div className="mt-8 flex justify-center gap-4">
        <button
          onClick={handleDownload}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <Download className="h-5 w-5" />
          Download PNG
        </button>
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-6 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
        >
          <RotateCcw className="h-5 w-5" />
          Remove another
        </button>
      </div>

      <div className="mt-6 text-center text-xs text-slate-400">
        <Info className="mr-1 inline-block h-3.5 w-3.5" />
        Max resolution: {MAX_DIMENSION}&times;{MAX_DIMENSION}px &middot;{" "}
        <a
          href="mailto:alex@agenteresolve.com.br"
          className="text-blue-500 hover:text-blue-600 underline"
        >
          Contact us
        </a>{" "}
        for unlimited version
      </div>
    </div>
  )
}
