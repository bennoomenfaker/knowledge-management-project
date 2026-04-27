import os
import io
from typing import Optional
from minio import Minio
from minio.error import S3Error


class StorageService:
    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "admin",
        secret_key: str = "admin123",
        secure: bool = False,
        bucket_name: str = "documents"
    ):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket_name = bucket_name
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Bucket creation error: {e}")
    
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        user_id: str,
        pfe_id: str,
        content_type: str = "application/pdf"
    ) -> Optional[str]:
        try:
            file_path = f"{user_id}/{pfe_id}/{file_name}"
            
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=io.BytesIO(file_content),
                length=len(file_content),
                content_type=content_type
            )
            
            return file_path
        except Exception as e:
            print(f"MinIO upload error: {e}")
            return None
    
    async def download_file(self, file_path: str) -> Optional[bytes]:
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            return response.read()
        except Exception as e:
            print(f"MinIO download error: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except Exception as e:
            print(f"MinIO delete error: {e}")
            return False
    
    async def get_file_url(self, file_path: str) -> Optional[str]:
        try:
            url = self.client.presigned_get_object(self.bucket_name, file_path)
            return url
        except Exception as e:
            print(f"MinIO URL error: {e}")
            return None
    
    async def read_file(self, file_path: str) -> Optional[bytes]:
        return await self.download_file(file_path)


_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service