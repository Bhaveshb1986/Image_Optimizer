# TODO: Replace imghdr with mimetypes in routes.py

- [x] Update import statement: replace "import imghdr" with "import mimetypes"
- [x] Modify file type verification logic: use mimetypes.guess_type(temp_path) instead of imghdr.what(temp_path)
- [x] Update allowed types check: compare MIME type with allowed MIME types (image/png, image/jpeg, image/gif)
- [x] Test the application to ensure image upload functionality works correctly
