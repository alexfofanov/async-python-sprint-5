from datetime import timedelta
from io import BytesIO
from uuid import UUID

from aiohttp import ClientResponse, ClientSession
from miniopy_async import Minio

from src.core.config import app_settings


class MinioHandler:
    def __init__(self) -> None:
        self.minio_client = Minio(
            endpoint=app_settings.minio_endpoint,
            access_key=app_settings.minio_root_user,
            secret_key=app_settings.minio_root_password,
            secure=False,
        )
        self.bucket_name = app_settings.minio_bucket_name
        self.expires = timedelta(seconds=app_settings.minio_url_expires_sec)

    async def create_backet(self, backet_name: str) -> None:
        """
        Создание бакета
        """

        if not await self.minio_client.bucket_exists(backet_name):
            await self.minio_client.make_bucket(backet_name)
        self.bucket_name = backet_name

    async def write(
        self,
        file_name: UUID,
        file_data: bytes,
        file_size: int,
        user_file_name: str,
    ) -> None:
        """
        Запись файла
        """

        metadata = {
            'Content-Disposition': f'attachment; filename="{user_file_name}"'
        }
        with BytesIO(file_data) as file_stream:
            await self.minio_client.put_object(
                self.bucket_name,
                str(file_name),
                file_stream,
                length=file_size,
                part_size=app_settings.minio_part_size_byte,
                metadata=metadata,
            )

    async def read(self, file_name) -> ClientResponse:
        """
        Чтение файла
        """

        async with ClientSession() as session:
            response = await self.minio_client.get_object(
                self.bucket_name, str(file_name), session
            )

        return response

    async def delete_files_in_bucket(self) -> None:
        """
        Удаление фалов в бакете
        """

        objects = await self.minio_client.list_objects(
            self.bucket_name, recursive=True
        )
        for obj in objects:
            await self.minio_client.remove_object(
                self.bucket_name, obj.object_name
            )

    async def delete_bucket(self) -> None:
        """
        Удаление бакета
        """

        await self.delete_files_in_bucket()
        await self.minio_client.remove_bucket(self.bucket_name)


minio_handler = MinioHandler()
