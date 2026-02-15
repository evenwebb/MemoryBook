import { useState, useEffect, useCallback, useMemo, useRef, memo } from 'react'
import { Link } from 'react-router-dom'
import InfiniteScroll from 'react-infinite-scroll-component'
import { imageApi, categoryApi, tagApi, searchApi, Image, Category, Tag } from '../../services/api'
import SearchBar from '../SearchBar/SearchBar'
import CategoryFilter from '../CategoryFilter/CategoryFilter'
import ImageViewer from '../ImageViewer/ImageViewer'
import './Gallery.css'

// Memoized image card component
const ImageCard = memo(({ image, onClick }: { image: Image, onClick: () => void }) => {
  const getImageUrl = useMemo(() => {
    if (image.thumbnail_path) {
      return `/storage${image.thumbnail_path.replace(/^.*\/storage/, '')}`
    }
    return `/storage${image.file_path.replace(/^.*\/storage/, '')}`
  }, [image.thumbnail_path, image.file_path])

  const cardClass = useMemo(() => {
    if (!image.width || !image.height) return 'image-card'
    const aspectRatio = image.width / image.height
    return aspectRatio > 2 ? 'image-card panoramic' : 'image-card'
  }, [image.width, image.height])

  return (
    <div className={cardClass} onClick={onClick}>
      <div className="image-wrapper">
        <img
          src={getImageUrl}
          alt={image.original_filename}
          loading="lazy"
          style={{
            transform: `rotate(${image.rotation || 0}deg)`
          }}
        />
        <div className="image-overlay">
          <div className="image-info">
            <p className="image-filename">{image.original_filename}</p>
            {image.categories.length > 0 && (
              <div className="image-categories">
                {image.categories.map(cat => (
                  <span key={cat.id} className="category-badge">
                    {cat.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
})

ImageCard.displayName = 'ImageCard'

const Gallery = () => {
  const [images, setImages] = useState<Image[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)
  const [hasMore, setHasMore] = useState(true)
  const [selectedImage, setSelectedImage] = useState<Image | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)
  const [selectedTags, setSelectedTags] = useState<number[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'date_desc' | 'date_asc' | 'name'>('date_desc')

  // Use ref for offset to avoid stale closure issues
  const offsetRef = useRef(0)
  const abortControllerRef = useRef<AbortController | null>(null)

  const loadImages = useCallback(async (reset = false) => {
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    abortControllerRef.current = new AbortController()

    try {
      const currentOffset = reset ? 0 : offsetRef.current
      let newImages: Image[]

      if (searchQuery || selectedCategory || selectedTags.length > 0) {
        const searchResult = await searchApi.search({
          query: searchQuery || undefined,
          category_ids: selectedCategory ? [selectedCategory] : undefined,
          tag_ids: selectedTags.length > 0 ? selectedTags : undefined,
          limit: 50,
          offset: currentOffset,
        })
        newImages = searchResult
      } else {
        newImages = await imageApi.getImages(
          currentOffset,
          50,
          selectedCategory || undefined,
          selectedTags.length === 1 ? selectedTags[0] : undefined
        )
      }

      // Apply sorting
      if (sortBy === 'date_desc') {
        newImages.sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime())
      } else if (sortBy === 'date_asc') {
        newImages.sort((a, b) => new Date(a.upload_date).getTime() - new Date(b.upload_date).getTime())
      } else if (sortBy === 'name') {
        newImages.sort((a, b) => a.original_filename.localeCompare(b.original_filename))
      }

      if (reset) {
        setImages(newImages)
        offsetRef.current = newImages.length
      } else {
        setImages(prev => [...prev, ...newImages])
        offsetRef.current += newImages.length
      }

      setHasMore(newImages.length === 50)
      setLoading(false)
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') return
      console.error('Error loading images:', error)
      setLoading(false)
    }
  }, [searchQuery, selectedCategory, selectedTags, sortBy])

  // Load initial data once on mount
  useEffect(() => {
    let cancelled = false
    const fetchInitialData = async () => {
      setLoading(true)
      try {
        const [cats, tagsData] = await Promise.all([
          categoryApi.getCategories(),
          tagApi.getTags(),
        ])
        if (!cancelled) {
          setCategories(cats)
          setTags(tagsData)
        }
      } catch (error) {
        console.error('Error loading initial data:', error)
      }
      if (!cancelled) {
        await loadImages(true)
      }
    }
    fetchInitialData()
    return () => { cancelled = true }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Reload when filters change
  useEffect(() => {
    loadImages(true)
  }, [searchQuery, selectedCategory, selectedTags, sortBy]) // eslint-disable-line react-hooks/exhaustive-deps

  // Cleanup abort controller on unmount
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort()
    }
  }, [])

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query)
  }, [])

  const handleCategoryChange = useCallback((categoryId: number | null) => {
    setSelectedCategory(categoryId)
  }, [])

  const handleTagToggle = useCallback((tagId: number) => {
    setSelectedTags(prev =>
      prev.includes(tagId) ? prev.filter(id => id !== tagId) : [...prev, tagId]
    )
  }, [])

  const handleImageClick = useCallback((image: Image) => {
    setSelectedImage(image)
  }, [])

  const handleCloseViewer = useCallback((updatedImage?: Image) => {
    if (updatedImage) {
      setImages(prevImages =>
        prevImages.map(img =>
          img.id === updatedImage.id ? updatedImage : img
        )
      )
    }
    setSelectedImage(null)
  }, [])

  return (
    <div className="gallery-container">
      <div className="gallery-header">
        <h2>Your Memories</h2>
        <div className="gallery-filters">
          <SearchBar onSearch={handleSearch} />
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onCategoryChange={handleCategoryChange}
          />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date_desc' | 'date_asc' | 'name')}
            className="sort-select"
          >
            <option value="date_desc">Newest First</option>
            <option value="date_asc">Oldest First</option>
            <option value="name">Name (A-Z)</option>
          </select>
        </div>
      </div>

      {loading && images.length === 0 ? (
        <div className="loading">Loading images...</div>
      ) : images.length === 0 ? (
        <div className="empty-state">
          <p>No images found. Start by uploading some memories!</p>
          <Link to="/upload" className="btn-upload-link">Upload Images</Link>
        </div>
      ) : (
        <InfiniteScroll
          dataLength={images.length}
          next={loadImages}
          hasMore={hasMore}
          loader={<div className="loading">Loading more images...</div>}
          className="images-grid"
        >
          {images.map(image => (
            <ImageCard
              key={image.id}
              image={image}
              onClick={() => handleImageClick(image)}
            />
          ))}
        </InfiniteScroll>
      )}

      {selectedImage && (
        <ImageViewer
          image={selectedImage}
          onClose={handleCloseViewer}
          onTagToggle={handleTagToggle}
          selectedTags={selectedTags}
          tags={tags}
          categories={categories}
        />
      )}
    </div>
  )
}

export default Gallery
