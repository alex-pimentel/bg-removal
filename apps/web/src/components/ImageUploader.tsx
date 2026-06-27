import { useCallback, useRef, useState } from "react"
import { Info, Upload } from "lucide-react"

const MAX_DIMENSION = 1200

function resizeImage(file: File, maxDim: number): Promise<File> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      let { width, height } = img
      if (width <= maxDim && height <= maxDim) {
        resolve(file)
        return
      }
      const ratio = Math.min(maxDim / width, maxDim / height)
      width = Math.round(width * ratio)
      height = Math.round(height * ratio)

      const canvas = document.createElement("canvas")
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext("2d")
      if (!ctx) {
        reject(new Error("Failed to get canvas context"))
        return
      }
      ctx.drawImage(img, 0, 0, width, height)

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(new Error("Failed to create blob"))
            return
          }
          const resizedFile = new File([blob], file.name, { type: file.type })
          resolve(resizedFile)
        },
        file.type,
      )
    }
    img.onerror = () => reject(new Error("Failed to load image"))
    img.src = URL.createObjectURL(file)
  })
}

interface Props {
  onUpload: (file: File) => void
}

export default function ImageUploader({ onUpload }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.type.startsWith("image/")) return
      if (file.size > 10 * 1024 * 1024) {
        alert("File too large. Maximum size is 10MB.")
        return
      }
      try {
        const resizedFile = await resizeImage(file, MAX_DIMENSION)
        onUpload(resizedFile)
      } catch {
        alert("Failed to process image. Please try another file.")
      }
    },
    [onUpload],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  return (
    <>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click()
        }}
        role="button"
        tabIndex={0}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-16 transition-colors ${
          dragging
            ? "border-blue-500 bg-blue-50"
            : "border-slate-300 hover:border-slate-400 hover:bg-slate-50"
        }`}
      >
        <Upload className="mb-4 h-12 w-12 text-slate-400" />
        <p className="text-lg font-medium text-slate-700">
          Drop an image here
        </p>
        <p className="mt-1 text-sm text-slate-500">or click to browse</p>
        <p className="mt-2 text-xs text-slate-400">PNG, JPG, WEBP up to 10MB</p>
        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          onChange={handleChange}
          className="hidden"
        />
      </div>
      <div className="mt-4 flex items-center justify-center gap-1.5 text-xs text-slate-400">
        <Info className="h-3.5 w-3.5 shrink-0" />
        <span>
          Output limited to {MAX_DIMENSION}&times;{MAX_DIMENSION}px. Need higher resolution?{" "}
          <a
            href="mailto:alex@agenteresolve.com.br"
            className="text-blue-500 hover:text-blue-600 underline"
          >
            Contact us
          </a>
        </span>
      </div>
    </>
  )
}
