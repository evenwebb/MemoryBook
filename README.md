# MemoryBook

A beautiful, self-hostable image gallery application for organising life memories. Upload receipts from memorable trips, certificates from school, school photos, and more - all organised with smart tags, categories, and OCR-powered search.

## Features

- 📸 **Beautiful Gallery UI** - Modern, responsive design with smooth loading
- 🚀 **Batch Upload** - Drag-and-drop multiple images with multi-threaded uploads
- 🔍 **Smart Search** - Full-text search across OCR-extracted text, tags, and categories
- 🏷️ **Tag Management** - Organise with tags for people, events, anniversaries, birthdays
- 📁 **Categories** - Pre-defined categories: Receipts, Certificates, School Photos, Others
- 🤖 **OCR Integration** - Automatic text extraction with Tesseract OCR
- 💡 **Smart Suggestions** - Automatic tag and category suggestions based on OCR text
- 🖼️ **Image Viewer** - Full-screen viewer with zoom, pan, and image details
- 🐳 **Docker Ready** - Complete Docker Compose setup for easy deployment

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL
- **Cache**: Redis
- **OCR**: Tesseract OCR
- **Image Processing**: Pillow

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 2GB of free disk space

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MemoryBook
```

2. Create environment file (optional, defaults are provided):
```bash
cp .env.example .env
# Edit .env if needed
```

3. Start the application:
```bash
docker-compose up -d
```

4. Initialize the database with default categories:
```bash
docker-compose exec backend python -m app.core.init_db
```

5. Access the application:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Backend API: http://localhost:8000

### First Steps

1. Navigate to http://localhost:3000/upload
2. Drag and drop your images or click to select
3. Images will be automatically processed with OCR
4. Review suggested tags and categories in the gallery
5. Search and filter your memories!

## Project Structure

```
MemoryBook/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Configuration and database
│   │   ├── models/      # Database models and schemas
│   │   └── services/    # Business logic (OCR, image processing, etc.)
│   └── Dockerfile
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/   # API client
│   └── Dockerfile
├── storage/             # Image storage (created on first run)
│   ├── images/         # Original images
│   └── thumbnails/     # Generated thumbnails
├── docker-compose.yml   # Docker Compose configuration
└── README.md
```

## API Endpoints

### Images
- `POST /api/v1/images/upload` - Upload multiple images
- `GET /api/v1/images` - List images with filters
- `GET /api/v1/images/{id}` - Get image details
- `DELETE /api/v1/images/{id}` - Delete image
- `POST /api/v1/images/{id}/tags` - Add tags to image
- `POST /api/v1/images/{id}/categories` - Add categories to image
- `POST /api/v1/images/{id}/process-ocr` - Manually trigger OCR

### Categories
- `GET /api/v1/categories` - List all categories
- `POST /api/v1/categories` - Create category
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### Tags
- `GET /api/v1/tags` - List all tags
- `POST /api/v1/tags` - Create tag
- `PUT /api/v1/tags/{id}` - Update tag
- `DELETE /api/v1/tags/{id}` - Delete tag

### Search
- `POST /api/v1/search` - Advanced search
- `GET /api/v1/search/suggestions` - Get search suggestions

Full API documentation available at http://localhost:8000/docs

## Configuration

Environment variables can be set in `.env` file:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `UPLOAD_DIR` - Directory for storing images
- `THUMBNAIL_DIR` - Directory for storing thumbnails
- `MAX_UPLOAD_SIZE` - Maximum file size in bytes (default: 50MB)
- `TESSERACT_CMD` - Path to Tesseract executable (auto-detected if not set)
- `OCR_LANGUAGES` - OCR languages (default: "eng")

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Features in Detail

### OCR Processing
- Automatic text extraction from images
- Extracts dates, names, and other structured data
- Suggests tags based on extracted content
- Suggests categories based on keywords

### Tag Suggestions
The system automatically suggests tags for:
- People's names (extracted from text)
- Dates (anniversaries, birthdays)
- Events (based on keywords)
- Years mentioned in documents

### Category Suggestions
Categories are suggested based on keywords:
- **Receipts**: receipt, total, payment, invoice
- **Certificates**: certificate, award, diploma, degree
- **School Photos**: school, class, student, teacher

### Image Processing
- Automatic thumbnail generation (300x300px)
- Image optimization for large files
- EXIF data extraction
- Duplicate detection (via file hash)

## Troubleshooting

### Images not loading
- Check that storage directories exist and have proper permissions
- Verify Docker volumes are mounted correctly

### OCR not working
- Ensure Tesseract is installed in the Docker container
- Check OCR language settings match your documents

### Database connection errors
- Verify PostgreSQL container is running: `docker-compose ps`
- Check database credentials in `.env`

## Security Notes

- Change `SECRET_KEY` in production
- Configure proper CORS origins
- Set up authentication if exposing publicly
- Regularly backup your database and storage

## Backup

To backup your data:

```bash
# Backup database
docker-compose exec postgres pg_dump -U memorybook memorybook > backup.sql

# Backup images
tar -czf images_backup.tar.gz storage/
```

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Future Enhancements

- Face recognition for auto-tagging people
- Machine learning for better categorization
- Mobile app support
- Cloud storage integration
- Multi-user support with permissions
- Advanced analytics and insights
