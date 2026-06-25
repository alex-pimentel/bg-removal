import { Download, RotateCcw } from "lucide-react"

interface Props {
  original: string
  resultUrl: string
  onReset: () => void
}

export default function ImagePreview({ original, resultUrl, onReset }: Props) {
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
        <a
          href={resultUrl}
          download="bg-removed.png"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <Download className="h-5 w-5" />
          Download PNG
        </a>
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-6 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
        >
          <RotateCcw className="h-5 w-5" />
          Remove another
        </button>
      </div>
    </div>
  )
}
