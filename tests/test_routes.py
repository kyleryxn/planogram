"""Tests for FastAPI route handlers."""

import io
from datetime import date, time
from unittest.mock import patch

from PIL import Image
from starlette.testclient import TestClient

from main import app
from planogram.models import ParsedSchedule, ScheduleEvent
from planogram.routes.upload import MAX_IMAGE_PX, resize
from tests.conftest import TEST_SETTINGS, make_image_bytes

client = TestClient(app, raise_server_exceptions=False)


class TestIndexRoute:
    def test_get_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_get_renders_upload_form(self):
        response = client.get("/")
        assert "Upload" in response.text
        assert 'action="/upload"' in response.text


class TestUploadRoute:
    def test_empty_file_returns_400(self):
        with patch("planogram.routes.upload.get_settings", return_value=TEST_SETTINGS):
            response = client.post(
                "/upload",
                files={"file": ("schedule.jpg", b"", "image/jpeg")},
            )
        assert response.status_code == 400

    def test_valid_image_redirects_to_review(self, tmp_path):
        mock_events = [
            ScheduleEvent(title="Work", date=date(2025, 1, 6), start_time=time(9, 0))
        ]
        with patch("planogram.routes.upload.get_settings", return_value=TEST_SETTINGS), \
             patch("planogram.routes.upload.parser.parse_events", return_value=(mock_events, "raw")), \
             patch("planogram.routes.upload.TMP_DIR", tmp_path):
            response = client.post(
                "/upload",
                files={"file": ("schedule.jpg", make_image_bytes(), "image/jpeg")},
                data={"person_name": ""},
                follow_redirects=False,
            )
        assert response.status_code == 303
        assert "/review?id=" in response.headers["location"]

    def test_invalid_image_returns_422(self):
        with patch("planogram.routes.upload.get_settings", return_value=TEST_SETTINGS):
            response = client.post(
                "/upload",
                files={"file": ("schedule.jpg", b"not-an-image", "image/jpeg")},
            )
        assert response.status_code == 422

    def test_parser_error_returns_422(self, tmp_path):
        with patch("planogram.routes.upload.get_settings", return_value=TEST_SETTINGS), \
             patch("planogram.routes.upload.parser.parse_events", side_effect=ValueError("bad json")):
            response = client.post(
                "/upload",
                files={"file": ("schedule.jpg", make_image_bytes(), "image/jpeg")},
            )
        assert response.status_code == 422


class TestReviewRoute:
    def test_unknown_session_id_returns_404(self):
        with patch("planogram.routes.review.get_settings", return_value=TEST_SETTINGS):
            response = client.get("/review?id=nonexistent-00000000")
        assert response.status_code == 404

    def test_valid_session_renders_review(self, tmp_path):
        schedule = ParsedSchedule(
            events=[ScheduleEvent(title="Work", date=date(2025, 1, 6), start_time=time(9, 0))],
            raw_ocr_text="raw",
            source_image_name="schedule.jpg",
        )
        session_id = "test-session-1234"
        (tmp_path / f"{session_id}.json").write_text(schedule.model_dump_json())

        with patch("planogram.routes.review.get_settings", return_value=TEST_SETTINGS), \
             patch("planogram.routes.review.TMP_DIR", tmp_path):
            response = client.get(f"/review?id={session_id}")

        assert response.status_code == 200
        assert "Work" in response.text


class TestResizeHelper:
    def test_small_image_unchanged(self):
        img_bytes = make_image_bytes(100, 100)
        result, media_type = resize(img_bytes)
        with Image.open(io.BytesIO(result)) as img:
            assert img.size == (100, 100)
        assert media_type == "image/jpeg"

    def test_oversized_image_shrunk(self):
        img_bytes = make_image_bytes(3000, 3000)
        result, _ = resize(img_bytes)
        with Image.open(io.BytesIO(result)) as img:
            assert max(img.size) <= MAX_IMAGE_PX

    def test_aspect_ratio_preserved(self):
        img_bytes = make_image_bytes(3000, 1500)
        result, _ = resize(img_bytes)
        with Image.open(io.BytesIO(result)) as img:
            w, h = img.size
            assert abs((w / h) - 2.0) < 0.01
