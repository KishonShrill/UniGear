"""Service module for Cloudinary image uploads and management."""

import logging
import os

import cloudinary.api
import cloudinary.uploader
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class ImageService:
    """Encapsulates image upload, extraction, and deletion via Cloudinary."""

    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

    @staticmethod
    def extract_public_id(image_url: str) -> str | None:
        """Extract Cloudinary public ID from a hosted image URL.

        Example:
            https://res.cloudinary.com/demo/image/upload/v12345/sample.jpg -> sample
        """
        if not image_url or not isinstance(image_url, str):
            return None
        try:
            filename = image_url.split("/")[-1]
            public_id = ".".join(filename.split(".")[:-1]) if "." in filename else filename
            return public_id or None
        except Exception as e:
            logger.warning("Failed to extract public_id from URL '%s': %s", image_url, e)
            return None

    @classmethod
    def upload_image(
        cls,
        file_obj: FileStorage,
        public_id: str | None = None,
        max_size: int = MAX_FILE_SIZE,
    ) -> str | None:
        """Validate and upload an image to Cloudinary.

        Args:
            file_obj: The file object from request.files.
            public_id: Optional custom public_id for Cloudinary.
            max_size: Maximum allowed file size in bytes.

        Returns:
            The secure Cloudinary URL, or None if upload failed or file invalid.
        """
        if not file_obj or not getattr(file_obj, "filename", None):
            return None

        # Validate file size
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)

        if size > max_size:
            raise ValueError(f"File size ({size} bytes) exceeds maximum limit of {max_size} bytes.")

        try:
            upload_kwargs = {}
            if public_id:
                upload_kwargs["public_id"] = public_id
            else:
                base_name = secure_filename(file_obj.filename)
                base_name = os.path.splitext(base_name)[0]
                if base_name:
                    upload_kwargs["public_id"] = base_name

            upload_result = cloudinary.uploader.upload(file_obj, **upload_kwargs)
            return upload_result.get("secure_url")
        except Exception as e:
            logger.error(
                "Cloudinary upload failed for %s: %s",
                getattr(file_obj, "filename", "unnamed"),
                e,
            )
            raise

    @classmethod
    def delete_image(cls, image_url: str) -> bool:
        """Delete an image from Cloudinary given its URL.

        Args:
            image_url: Hosted Cloudinary image URL.

        Returns:
            True if deletion succeeded or URL was empty, False on failure.
        """
        if not image_url:
            return True

        public_id = cls.extract_public_id(image_url)
        if not public_id:
            return False

        try:
            cloudinary.api.delete_resources([public_id], resource_type="image", type="upload")
            return True
        except Exception as e:
            logger.error("Failed to delete Cloudinary resource '%s': %s", public_id, e)
            return False

    @classmethod
    def delete_images(cls, image_urls: list[str]) -> bool:
        """Delete multiple images from Cloudinary given their URLs."""
        if not image_urls:
            return True

        public_ids = [pid for url in image_urls if (pid := cls.extract_public_id(url)) is not None]
        if not public_ids:
            return True

        try:
            cloudinary.api.delete_resources(public_ids, resource_type="image", type="upload")
            return True
        except Exception as e:
            logger.error("Failed to bulk delete Cloudinary resources: %s", e)
            return False
