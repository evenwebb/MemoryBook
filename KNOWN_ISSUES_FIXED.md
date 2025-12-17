# Known Issues Fixed

## Issue 1: Rotation Not Working
**Problem**: Image rotation endpoint was returning 404 even though routes were registered.

**Root Cause**: Old backend server process wasn't being killed properly, so code changes weren't taking effect.

**Solution**: 
- Properly kill all backend processes before restarting: `lsof -ti:8001 | xargs kill -9`
- Changed rotation endpoint from PATCH to PUT for consistency
- Added query parameter for degrees: `PUT /api/v1/images/{image_id}/rotate?degrees=90`

**Files Changed**:
- `backend/app/api/routes/images.py` - Changed @router.patch to @router.put
- `frontend/src/services/api.ts` - Updated API call to use PUT with query parameter

## Issue 2: Rotation Not Visible in Gallery
**Problem**: Rotated images didn't appear rotated on the homepage/gallery.

**Root Cause**: Gallery component wasn't applying CSS rotation transform to thumbnails.

**Solution**: Added rotation transform to gallery image cards.

**Files Changed**:
- `frontend/src/components/Gallery/Gallery.tsx` - Added `style={{ transform: rotate(...) }}` to img tags

## Issue 3: Deprecated Pydantic Methods
**Problem**: Using deprecated `.dict()` method instead of `.model_dump()` in Pydantic v2.

**Root Cause**: Code was written for Pydantic v1 but project uses Pydantic v2.

**Solution**: 
- Replaced `category.dict()` with `category.model_dump()` in categories route
- Replaced `tag.dict()` with `tag.model_dump()` in tags route
- Added cache invalidation when updating categories/tags

**Files Changed**:
- `backend/app/api/routes/categories.py`
- `backend/app/api/routes/tags.py`

## Issue 4: Missing Fields in API Responses
**Problem**: `notes` and `rotation` fields weren't being returned in API responses.

**Root Cause**: Old server process was running code without the new schema fields.

**Solution**: Proper server restart resolved the issue once the model changes were loaded.

## Prevention Tips

1. **Always kill old processes**: Use `lsof -ti:PORT | xargs kill -9` before restarting
2. **Check running processes**: Use `ps aux | grep python` to verify no old processes
3. **Verify API routes**: Check `/docs` endpoint to see registered routes
4. **Test after changes**: Always test endpoints after code changes to verify they're working
5. **Use Pydantic v2 methods**: Always use `.model_dump()` instead of `.dict()`

## Testing Checklist

- [ ] Backend starts without errors
- [ ] All routes appear in `/docs`
- [ ] Test rotation endpoint: `curl -X PUT "http://localhost:8001/api/v1/images/1/rotate?degrees=90"`
- [ ] Verify fields in response: `curl http://localhost:8001/api/v1/images/1 | grep rotation`
- [ ] Check frontend applies rotation in gallery
- [ ] Test notes update endpoint
- [ ] Verify cache invalidation works for categories/tags

