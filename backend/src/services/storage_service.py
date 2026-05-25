from fastapi import UploadFile

def upload_file_to_cloud(file: UploadFile, folder: str = "uploads") -> str:
    # Placeholder for Cloudinary / AWS S3
    print(f"Uploading {file.filename} to {folder}")
    return f"https://example-storage.com/{folder}/{file.filename}"
