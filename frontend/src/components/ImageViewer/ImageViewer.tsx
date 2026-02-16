import { useState, useEffect } from 'react'
import { Image, Tag, Category } from '../../services/api'
import { imageApi } from '../../services/api'
import './ImageViewer.css'

interface ImageViewerProps {
  image: Image
  onClose: (updatedImage?: Image) => void
  onTagToggle: (tagId: number) => void
  selectedTags: number[]
  tags: Tag[]
  categories: Category[]
}

const ImageViewer = ({
  image,
  onClose,
  onTagToggle,
  selectedTags,
  tags,
  categories,
}: ImageViewerProps) => {
  const [currentImage, setCurrentImage] = useState(image)
  const [zoom, setZoom] = useState(1)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [newTagName, setNewTagName] = useState('')
  const [notes, setNotes] = useState(image.notes || '')
  const [isEditingNotes, setIsEditingNotes] = useState(false)

  useEffect(() => {
    setCurrentImage(image)
    setZoom(1)
    setPosition({ x: 0, y: 0 })
    setNotes(image.notes || '')
  }, [image])

  const getImageUrl = (img: Image) => {
    return `/storage${img.file_path.replace(/^.*\/storage/, '')}`
  }

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    setZoom(prev => Math.max(0.5, Math.min(3, prev + delta)))
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom > 1) {
      setIsDragging(true)
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y })
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && zoom > 1) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      })
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleAddTag = async (tagName?: string) => {
    const nameToAdd = tagName || newTagName.trim()
    if (!nameToAdd) return

    try {
      // Create tag if it doesn't exist
      const existingTag = tags.find(t => t.name.toLowerCase() === nameToAdd.toLowerCase())
      let tagId = existingTag?.id

      if (!tagId) {
        const { tagApi } = await import('../../services/api')
        const newTag = await tagApi.createTag({ name: nameToAdd })
        tagId = newTag.id
      }

      // Add tag to image
      const updatedImage = await imageApi.addTagsToImage(currentImage.id, [tagId])
      setCurrentImage(updatedImage)
      setNewTagName('')
    } catch (error) {
      console.error('Error adding tag:', error)
    }
  }

  const handleRemoveTag = async (tagId: number) => {
    try {
      const updatedImage = await imageApi.removeTagFromImage(currentImage.id, tagId)
      setCurrentImage(updatedImage)
    } catch (error) {
      console.error('Error removing tag:', error)
    }
  }

  const handleAddCategory = async (categoryId: number) => {
    try {
      const updatedImage = await imageApi.addCategoriesToImage(currentImage.id, [categoryId])
      setCurrentImage(updatedImage)
    } catch (error) {
      console.error('Error adding category:', error)
    }
  }

  const handleRemoveCategory = async (categoryId: number) => {
    try {
      const updatedImage = await imageApi.removeCategoryFromImage(currentImage.id, categoryId)
      setCurrentImage(updatedImage)
    } catch (error) {
      console.error('Error removing category:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const handleSaveNotes = async () => {
    try {
      const updatedImage = await imageApi.updateNotes(currentImage.id, notes)
      setCurrentImage(updatedImage)
      setIsEditingNotes(false)
    } catch (error) {
      console.error('Error saving notes:', error)
    }
  }

  const handleRotate = async (degrees: number) => {
    try {
      const updatedImage = await imageApi.rotateImage(currentImage.id, degrees)
      setCurrentImage(updatedImage)
    } catch (error) {
      console.error('Error rotating image:', error)
    }
  }

  return (
    <div className="image-viewer-overlay" onClick={() => onClose(currentImage)}>
      <div className="image-viewer-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={() => onClose(currentImage)}>
          ×
        </button>

        <div className="image-viewer-main">
          <div
            className="image-container"
            onWheel={handleWheel}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            <img
              src={getImageUrl(currentImage)}
              alt={currentImage.original_filename}
              style={{
                transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px) rotate(${currentImage.rotation || 0}deg)`,
                cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'zoom-in',
              }}
            />
          </div>

          <div className="image-details">
            <h3>{currentImage.original_filename}</h3>
            <p className="upload-date">Uploaded {formatDate(currentImage.upload_date)}</p>
            
            <div className="image-controls">
              <button onClick={() => handleRotate(90)} title="Rotate 90°">↻</button>
              <button onClick={() => handleRotate(-90)} title="Rotate -90°">↺</button>
            </div>

            {currentImage.exif_data?.suggested_tags && currentImage.exif_data.suggested_tags.length > 0 && (
              <div className="suggestions-section">
                <h4>Suggested Tags</h4>
                <div className="suggested-tags">
                  {currentImage.exif_data.suggested_tags.map((tagName: string, idx: number) => (
                    <button
                      key={idx}
                      className="suggestion-tag"
                      onClick={() => handleAddTag(tagName)}
                    >
                      + {tagName}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="tags-section">
              <h4>Tags</h4>
              <div className="tags-list">
                {currentImage.tags.map(tag => (
                  <span key={tag.id} className="tag-item">
                    {tag.name}
                    <button 
                      className="remove-btn" 
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRemoveTag(tag.id)
                      }}
                      title="Remove tag"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <div className="add-tag-input">
                <input
                  type="text"
                  placeholder="Add tag..."
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                />
                <button onClick={handleAddTag}>Add</button>
              </div>
            </div>

            <div className="categories-section">
              <h4>Categories</h4>
              <div className="categories-list">
                {currentImage.categories.map(cat => (
                  <span key={cat.id} className="category-item">
                    {cat.name}
                    <button 
                      className="remove-btn" 
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRemoveCategory(cat.id)
                      }}
                      title="Remove category"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <div className="add-category-buttons">
                {categories
                  .filter(cat => !currentImage.categories.find(c => c.id === cat.id))
                  .map(cat => (
                    <button
                      key={cat.id}
                      className="category-button"
                      onClick={() => handleAddCategory(cat.id)}
                    >
                      + {cat.name}
                    </button>
                  ))}
              </div>
            </div>

            <div className="notes-section">
              <h4>Notes</h4>
              {isEditingNotes ? (
                <div>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add notes about this image..."
                    rows={4}
                  />
                  <div className="notes-actions">
                    <button onClick={handleSaveNotes}>Save</button>
                    <button onClick={() => {
                      setNotes(currentImage.notes || '')
                      setIsEditingNotes(false)
                    }}>Cancel</button>
                  </div>
                </div>
              ) : (
                <div>
                  <p className="notes-text">{notes || 'No notes yet'}</p>
                  <button onClick={() => setIsEditingNotes(true)}>
                    {notes ? 'Edit' : 'Add Notes'}
                  </button>
                </div>
              )}
            </div>

            {currentImage.exif_data && Object.keys(currentImage.exif_data).length > 0 && (
              <div className="exif-section">
                <h4>Image Information</h4>
                <div className="exif-data">
                  {currentImage.exif_data.DateTime && (
                    <div><strong>Taken:</strong> {currentImage.exif_data.DateTime}</div>
                  )}
                  {currentImage.exif_data.Make && (
                    <div><strong>Camera:</strong> {currentImage.exif_data.Make} {currentImage.exif_data.Model}</div>
                  )}
                  {currentImage.width && currentImage.height && (
                    <div><strong>Dimensions:</strong> {currentImage.width} × {currentImage.height}</div>
                  )}
                  {currentImage.file_size && (
                    <div><strong>Size:</strong> {(currentImage.file_size / 1024 / 1024).toFixed(2)} MB</div>
                  )}
                </div>
              </div>
            )}

            {currentImage.ocr_text && (
              <div className="ocr-section">
                <h4>Extracted Text</h4>
                <div className="ocr-text">{currentImage.ocr_text}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ImageViewer

