import { Category } from '../../services/api'
import './CategoryFilter.css'

interface CategoryFilterProps {
  categories: Category[]
  selectedCategory: number | null
  onCategoryChange: (categoryId: number | null) => void
}

const CategoryFilter = ({ categories, selectedCategory, onCategoryChange }: CategoryFilterProps) => {
  return (
    <div className="category-filter">
      <button
        className={`category-button ${selectedCategory === null ? 'active' : ''}`}
        onClick={() => onCategoryChange(null)}
      >
        All
      </button>
      {categories.map(category => (
        <button
          key={category.id}
          className={`category-button ${selectedCategory === category.id ? 'active' : ''}`}
          onClick={() => onCategoryChange(category.id)}
          style={{
            borderColor: category.color || '#667eea',
          }}
        >
          {category.name}
        </button>
      ))}
    </div>
  )
}

export default CategoryFilter

