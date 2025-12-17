import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { imageApi, categoryApi, Category } from '../../services/api'
import './ImageUploader.css'

interface UploadProgress {
  filename: string
  progress: number
  status: 'uploading' | 'success' | 'error'
  error?: string
  imageId?: number
  suggestedCategory?: string
  suggestedTags?: string[]
}

const ImageUploader = () => {
  const [files, setFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<Map<string, UploadProgress>>(new Map())
  const [isUploading, setIsUploading] = useState(false)
  const [uploadComplete, setUploadComplete] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])

  // Load categories on mount
  useEffect(() => {
    categoryApi.getCategories().then(setCategories).catch(console.error)
  }, [])

  const handleUpload = useCallback(async (filesToUpload: File[]) => {
    if (filesToUpload.length === 0) return

    setIsUploading(true)
    setUploadComplete(false)

    // Initialize progress for all files
    const newProgress = new Map(uploadProgress)
    filesToUpload.forEach(file => {
      newProgress.set(file.name, {
        filename: file.name,
        progress: 0,
        status: 'uploading'
      })
    })
    setUploadProgress(newProgress)

    try {
      const result = await imageApi.uploadImages(filesToUpload)
      
      // Update progress with suggestions
      const updatedProgress = new Map(uploadProgress)
      result.images.forEach((img: any) => {
        updatedProgress.set(img.filename, {
          filename: img.filename,
          progress: 100,
          status: img.status === 'success' ? 'success' : 'error',
          error: img.message,
          imageId: img.id,
          suggestedCategory: img.exif_data?.suggested_category,
          suggestedTags: img.exif_data?.suggested_tags || []
        })
      })
      setUploadProgress(updatedProgress)
      setUploadComplete(true)

      // Clear files after successful upload
      setTimeout(() => {
        setFiles([])
        setUploadProgress(new Map())
        setIsUploading(false)
        setUploadComplete(false)
      }, 3000)
    } catch (error: any) {
      console.error('Upload error:', error)
      // Mark all as error
      const updatedProgress = new Map(uploadProgress)
      filesToUpload.forEach(file => {
        updatedProgress.set(file.name, {
          filename: file.name,
          progress: 0,
          status: 'error',
          error: error.response?.data?.detail || error.message || 'Upload failed'
        })
      })
      setUploadProgress(updatedProgress)
      setIsUploading(false)
    }
  }, [uploadProgress])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles])
    // Auto-upload immediately
    handleUpload(acceptedFiles)
  }, [handleUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.heif']
    },
    multiple: true
  })

  const handleManualUpload = async () => {
    if (files.length === 0) return
    await handleUpload(files)
  }

  const removeFile = (filename: string) => {
    setFiles(prev => prev.filter(f => f.name !== filename))
    const updatedProgress = new Map(uploadProgress)
    updatedProgress.delete(filename)
    setUploadProgress(updatedProgress)
  }

  const applyCategory = async (filename: string, categoryName: string) => {
    const progress = uploadProgress.get(filename)
    if (!progress?.imageId) return

    const category = categories.find(c => c.name === categoryName)
    if (!category) return

    try {
      await imageApi.addCategoriesToImage(progress.imageId, [category.id])
      
      // Update progress to remove suggestion
      const updatedProgress = new Map(uploadProgress)
      const item = updatedProgress.get(filename)
      if (item) {
        item.suggestedCategory = undefined
        updatedProgress.set(filename, item)
        setUploadProgress(updatedProgress)
      }
    } catch (error) {
      console.error('Failed to apply category:', error)
    }
  }

  return (
    <div className="uploader-container">
      <h2>Upload Images</h2>
      
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p>
            {isDragActive
              ? 'Drop the files here...'
              : 'Drag & drop images here, or click to select'}
          </p>
          <p className="dropzone-hint">Supports: JPG, PNG, GIF, WebP, BMP, TIFF, HEIC</p>
        </div>
      </div>

      {files.length > 0 && (
        <div className="files-list">
          <h3>Selected Files ({files.length})</h3>
          <div className="files-grid">
            {files.map(file => (
              <div key={file.name} className="file-item">
                <div className="file-preview">
                  {file.type.startsWith('image/') && (
                    <img
                      src={URL.createObjectURL(file)}
                      alt={file.name}
                      onLoad={(e) => URL.revokeObjectURL((e.target as HTMLImageElement).src)}
                    />
                  )}
                </div>
                <div className="file-info">
                  <p className="file-name">{file.name}</p>
                  <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  {uploadProgress.has(file.name) && (
                    <div className="upload-status">
                      {uploadProgress.get(file.name)?.status === 'uploading' && (
                        <div className="progress-bar">
                          <div className="progress-fill" style={{ width: `${uploadProgress.get(file.name)?.progress}%` }} />
                        </div>
                      )}
                      {uploadProgress.get(file.name)?.status === 'success' && (
                        <>
                          <span className="status-success">✓ Uploaded</span>
                          {uploadProgress.get(file.name)?.suggestedCategory && (
                            <div className="suggestions">
                              <div className="suggestion-label">Suggested:</div>
                              <button
                                className="suggestion-chip category-chip"
                                onClick={() => applyCategory(file.name, uploadProgress.get(file.name)!.suggestedCategory!)}
                                title="Click to apply this category"
                              >
                                + {uploadProgress.get(file.name)?.suggestedCategory}
                              </button>
                            </div>
                          )}
                        </>
                      )}
                      {uploadProgress.get(file.name)?.status === 'error' && (
                        <span className="status-error">✗ {uploadProgress.get(file.name)?.error}</span>
                      )}
                    </div>
                  )}
                </div>
                <button
                  className="remove-file"
                  onClick={() => removeFile(file.name)}
                  disabled={isUploading}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          <div className="upload-actions">
            {!isUploading && !uploadComplete && (
              <button
                className="btn-upload"
                onClick={handleManualUpload}
                disabled={files.length === 0}
              >
                Upload {files.length} Image{files.length > 1 ? 's' : ''} Again
              </button>
            )}
            {isUploading && (
              <div className="upload-status-message">Uploading {files.length} image{files.length > 1 ? 's' : ''}...</div>
            )}
            {uploadComplete && (
              <a href="/" className="btn-view-gallery">
                View Gallery
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ImageUploader

