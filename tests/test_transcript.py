from app.services.transcript import chunk_transcript


class TestChunkTranscript:
    def test_basic_chunking(self):
        transcript = [
            {"text": "안녕하세요", "start": 0.0, "duration": 2.0},
            {"text": "오늘은", "start": 60.0, "duration": 2.0},
            {"text": "파이썬을", "start": 120.0, "duration": 2.0},
            {"text": "배워봅시다", "start": 200.0, "duration": 2.0},
        ]
        chunks = chunk_transcript(transcript, chunk_minutes=3)
        assert len(chunks) >= 1
        assert "안녕하세요" in chunks[0]

    def test_empty_transcript(self):
        assert chunk_transcript([], chunk_minutes=3) == []

    def test_single_entry(self):
        transcript = [{"text": "테스트", "start": 0.0, "duration": 1.0}]
        chunks = chunk_transcript(transcript, chunk_minutes=3)
        assert len(chunks) == 1
        assert "테스트" in chunks[0]

    def test_chunk_boundary(self):
        # Entries at 0s, 179s (within 3min), 181s (next chunk)
        transcript = [
            {"text": "첫번째", "start": 0.0, "duration": 1.0},
            {"text": "두번째", "start": 179.0, "duration": 1.0},
            {"text": "세번째", "start": 181.0, "duration": 1.0},
        ]
        chunks = chunk_transcript(transcript, chunk_minutes=3)
        assert len(chunks) >= 2
