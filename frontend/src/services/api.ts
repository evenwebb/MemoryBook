import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
})

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status, error.response.data)
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error: No response from server')
    } else {
      // Error setting up request
      console.error('Request Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export interface Image {
  id: number
  filename: string
  original_filename: string
  file_path: string
  thumbnail_path: string | null
  file_size: number
  mime_type: string
  upload_date: string
  exif_data: any
  ocr_text: string | null
  ocr_processed: string | null
  notes: string | null
  rotation: number
  width: number | null
  height: number | null
  tags: Tag[]
  categories: Category[]
}

export interface Tag {
  id: number
  name: string
  tag_type: string | null
  created_at: string
}

export interface Category {
  id: number
  name: string
  description: string | null
  color: string | null
  created_at: string
}

export interface SearchRequest {
  query?: string
  category_ids?: number[]
  tag_ids?: number[]
  date_from?: string
  date_to?: string
  limit?: number
  offset?: number
}

export const imageApi = {
  uploadImages: async (files: File[]): Promise<any> => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    const response = await api.post('/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 second timeout for large files
      onUploadProgress: (progressEvent) => {
        // Progress tracking can be added here if needed
      }
    })
    return response.data
  },

  getImages: async (skip = 0, limit = 50, categoryId?: number, tagId?: number): Promise<Image[]> => {
    const params: any = { skip, limit }
    if (categoryId) params.category_id = categoryId
    if (tagId) params.tag_id = tagId
    const response = await api.get('/images', { params })
    return response.data
  },

  getImage: async (id: number): Promise<Image> => {
    const response = await api.get(`/images/${id}`)
    return response.data
  },

  deleteImage: async (id: number): Promise<void> => {
    await api.delete(`/images/${id}`)
  },

  addTagsToImage: async (imageId: number, tagIds: number[]): Promise<Image> => {
    const response = await api.post(`/images/${imageId}/tags`, tagIds)
    return response.data
  },

  removeTagFromImage: async (imageId: number, tagId: number): Promise<Image> => {
    const response = await api.delete(`/images/${imageId}/tags/${tagId}`)
    return response.data
  },

  addCategoriesToImage: async (imageId: number, categoryIds: number[]): Promise<Image> => {
    const response = await api.post(`/images/${imageId}/categories`, categoryIds)
    return response.data
  },

  removeCategoryFromImage: async (imageId: number, categoryId: number): Promise<Image> => {
    const response = await api.delete(`/images/${imageId}/categories/${categoryId}`)
    return response.data
  },

  updateNotes: async (imageId: number, notes: string): Promise<Image> => {
    const response = await api.put(`/images/${imageId}/notes`, { notes })
    return response.data
  },

  rotateImage: async (imageId: number, degrees: number): Promise<Image> => {
    const response = await api.put(`/images/${imageId}/rotate?degrees=${degrees}`)
    return response.data
  },

  processOCR: async (imageId: number): Promise<Image> => {
    const response = await api.post(`/images/${imageId}/process-ocr`)
    return response.data
  },
}

export const categoryApi = {
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/categories')
    return response.data
  },

  createCategory: async (category: { name: string; description?: string; color?: string }): Promise<Category> => {
    const response = await api.post('/categories', category)
    return response.data
  },

  deleteCategory: async (id: number): Promise<void> => {
    await api.delete(`/categories/${id}`)
  },
}

export const tagApi = {
  getTags: async (tagType?: string): Promise<Tag[]> => {
    const params = tagType ? { tag_type: tagType } : {}
    const response = await api.get('/tags', { params })
    return response.data
  },

  createTag: async (tag: { name: string; tag_type?: string }): Promise<Tag> => {
    const response = await api.post('/tags', tag)
    return response.data
  },

  deleteTag: async (id: number): Promise<void> => {
    await api.delete(`/tags/${id}`)
  },
}

export const searchApi = {
  search: async (searchRequest: SearchRequest): Promise<Image[]> => {
    const response = await api.post('/search', searchRequest)
    return response.data
  },

  getSuggestions: async (query: string): Promise<any> => {
    const response = await api.get('/search/suggestions', { params: { q: query } })
    return response.data
  },
}

export default api

