"""Unit tests for helper utilities and ImageService."""
import io
import unittest
from unittest.mock import MagicMock, patch
from werkzeug.datastructures import FileStorage

from app.utils.helpers import convert_size, format_address, split_address
from app.utils.image_service import ImageService


class TestHelpers(unittest.TestCase):
    """Tests for app.utils.helpers functions."""

    def test_convert_size_valid(self):
        self.assertEqual(convert_size(1), "XS")
        self.assertEqual(convert_size(2), "S")
        self.assertEqual(convert_size(3), "M")
        self.assertEqual(convert_size(4), "L")
        self.assertEqual(convert_size(5), "XL")
        self.assertEqual(convert_size(6), "2XL")

    def test_convert_size_invalid(self):
        with self.assertRaises(ValueError):
            convert_size(0)
        with self.assertRaises(ValueError):
            convert_size(7)
        with self.assertRaises(ValueError):
            convert_size(-1)

    def test_split_address(self):
        street, barangay, city = split_address("123 Main St, Barangay 1, Iligan City")
        self.assertEqual(street, "123 Main St")
        self.assertEqual(barangay, "Barangay 1")
        self.assertEqual(city, "Iligan City")

    def test_split_address_empty_or_none(self):
        self.assertEqual(split_address(""), ("", "", ""))
        self.assertEqual(split_address(None), ("", "", ""))

    def test_split_address_partial(self):
        self.assertEqual(split_address("123 Main St"), ("123 Main St", "", ""))
        self.assertEqual(split_address("123 Main St, Barangay 1"), ("123 Main St", "Barangay 1", ""))

    def test_format_address(self):
        formatted = format_address("123 Main St", "Barangay 1", "Iligan City")
        self.assertEqual(formatted, "123 Main St, Barangay 1, Iligan City")

    def test_format_address_with_nones_or_blanks(self):
        self.assertEqual(format_address("123 Main St", None, "Iligan City"), "123 Main St, Iligan City")
        self.assertEqual(format_address("", "", ""), "")
        self.assertEqual(format_address(None, None, None), "")


class TestImageService(unittest.TestCase):
    """Tests for app.utils.image_service.ImageService."""

    def test_extract_public_id(self):
        url = "https://res.cloudinary.com/demo/image/upload/v12345/sample_image.jpg"
        self.assertEqual(ImageService.extract_public_id(url), "sample_image")

    def test_extract_public_id_no_extension(self):
        url = "https://res.cloudinary.com/demo/image/upload/v12345/sample_image"
        self.assertEqual(ImageService.extract_public_id(url), "sample_image")

    def test_extract_public_id_invalid(self):
        self.assertIsNone(ImageService.extract_public_id(""))
        self.assertIsNone(ImageService.extract_public_id(None))

    @patch("cloudinary.uploader.upload")
    def test_upload_image_success(self, mock_upload):
        mock_upload.return_value = {"secure_url": "https://res.cloudinary.com/demo/image/upload/test.jpg"}

        file_obj = FileStorage(
            stream=io.BytesIO(b"fake image data"),
            filename="test.jpg",
            content_type="image/jpeg",
        )

        result_url = ImageService.upload_image(file_obj)
        self.assertEqual(result_url, "https://res.cloudinary.com/demo/image/upload/test.jpg")
        mock_upload.assert_called_once()

    def test_upload_image_none_or_empty(self):
        self.assertIsNone(ImageService.upload_image(None))
        empty_file = FileStorage(stream=io.BytesIO(b""), filename="")
        self.assertIsNone(ImageService.upload_image(empty_file))

    def test_upload_image_exceeds_max_size(self):
        large_data = b"x" * 100
        file_obj = FileStorage(
            stream=io.BytesIO(large_data),
            filename="large.jpg",
            content_type="image/jpeg",
        )
        with self.assertRaises(ValueError):
            ImageService.upload_image(file_obj, max_size=50)

    @patch("cloudinary.api.delete_resources")
    def test_delete_image_success(self, mock_delete):
        mock_delete.return_value = {"deleted": {"sample": "deleted"}}
        result = ImageService.delete_image("https://res.cloudinary.com/demo/image/upload/sample.jpg")
        self.assertTrue(result)
        mock_delete.assert_called_once_with(["sample"], resource_type="image", type="upload")

    def test_delete_image_empty(self):
        self.assertTrue(ImageService.delete_image(""))
        self.assertTrue(ImageService.delete_image(None))

    @patch("cloudinary.api.delete_resources")
    def test_delete_image_failure(self, mock_delete):
        mock_delete.side_effect = Exception("Cloudinary API error")
        result = ImageService.delete_image("https://res.cloudinary.com/demo/image/upload/sample.jpg")
        self.assertFalse(result)

    @patch("cloudinary.api.delete_resources")
    def test_delete_images_bulk(self, mock_delete):
        mock_delete.return_value = {"deleted": {"img1": "deleted", "img2": "deleted"}}
        urls = [
            "https://res.cloudinary.com/demo/image/upload/img1.jpg",
            "https://res.cloudinary.com/demo/image/upload/img2.jpg",
        ]
        result = ImageService.delete_images(urls)
        self.assertTrue(result)
        mock_delete.assert_called_once_with(["img1", "img2"], resource_type="image", type="upload")

    def test_delete_images_empty_list(self):
        self.assertTrue(ImageService.delete_images([]))


if __name__ == "__main__":
    unittest.main()
