# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- 2GB+ free disk space

## Installation Steps

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to start** (about 30-60 seconds):
   ```bash
   docker-compose logs -f
   ```
   Press Ctrl+C when you see "Application startup complete"

3. **Initialize database** (creates default categories):
   ```bash
   docker-compose exec backend python -m app.core.init_db
   ```

4. **Access the application:**
   - **Gallery**: http://localhost:3000
   - **Upload Page**: http://localhost:3000/upload
   - **API Docs**: http://localhost:8000/docs

## First Upload

1. Go to http://localhost:3000/upload
2. Drag and drop images or click to select files
3. Click "Upload" - images will be processed automatically
4. OCR will extract text and suggest tags/categories
5. View your images in the gallery at http://localhost:3000

## Default Categories

The system comes with these categories:
- **Receipts** - For receipts from trips and purchases
- **Certificates** - For certificates and awards
- **School Photos** - For school photos and yearbooks
- **Others** - For everything else

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Clean everything (removes data!)
docker-compose down -v
```

## Troubleshooting

**Images not loading?**
- Check storage permissions: `ls -la storage/`
- Verify volumes are mounted: `docker-compose ps`

**OCR not working?**
- Check backend logs: `docker-compose logs backend`
- Verify Tesseract is installed in container

**Database errors?**
- Check PostgreSQL is running: `docker-compose ps postgres`
- View database logs: `docker-compose logs postgres`

## Next Steps

- Upload your first batch of images
- Review OCR suggestions and add tags
- Organize images into categories
- Use search to find specific memories
- Explore the API at http://localhost:8000/docs

Enjoy organizing your memories! 📸

