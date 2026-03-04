import os
import tempfile

from app.services.pptx_builder import create_pptx


class TestCreatePptx:
    def test_creates_file(self):
        slides_data = [
            {"title": "소개", "bullets": ["첫 번째 포인트", "두 번째 포인트", "세 번째 포인트"]},
            {"title": "본론", "bullets": ["핵심 내용 1", "핵심 내용 2"]},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pptx")
            result = create_pptx(slides_data, "테스트 영상 제목", output_path)
            assert os.path.exists(result)
            assert result == output_path

    def test_empty_slides(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "empty.pptx")
            result = create_pptx([], "빈 슬라이드", output_path)
            assert os.path.exists(result)

    def test_special_characters(self):
        slides_data = [
            {"title": "특수문자 <>&\"' 테스트", "bullets": ["불릿 <test>", "불릿 &amp;"]},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "special.pptx")
            result = create_pptx(slides_data, "특수문자 테스트", output_path)
            assert os.path.exists(result)
