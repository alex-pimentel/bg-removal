import { useCallback, useRef, useState } from "react"
import { Upload } from "lucide-react"

interface Props {
  onUpload: (file: File) => void
}

export default function ImageUploader({ onUpload }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith("image/")) return
      if (file.size > 10 * 1024 * 1024) {
        alert("File too large. Maximum size is 10MB.")
        return
      }
      onUpload(file)
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
  )
}
