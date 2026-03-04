from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def get_transcript(video_id: str, language: str = "ko") -> list[dict]:
    """
    Extract subtitles from a YouTube video using youtube_transcript_api.

    Fallback order: requested language -> English -> auto-generated.
    Each returned dict has keys: text, start, duration.

    Raises RuntimeError if no transcript is found.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        raise RuntimeError(f"Transcripts are disabled for video: {video_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve transcripts for video {video_id}: {e}")

    transcript = None

    # Try requested language first
    try:
        transcript = transcript_list.find_transcript([language])
    except NoTranscriptFound:
        pass

    # Fallback to English
    if transcript is None:
        try:
            transcript = transcript_list.find_transcript(["en"])
        except NoTranscriptFound:
            pass

    # Fallback to any auto-generated transcript
    if transcript is None:
        try:
            generated = [t for t in transcript_list if t.is_generated]
            if generated:
                transcript = generated[0]
        except Exception:
            pass

    if transcript is None:
        raise RuntimeError(f"No transcript found for video: {video_id}")

    raw = transcript.fetch()
    return [{"text": entry["text"], "start": entry["start"], "duration": entry["duration"]} for entry in raw]


def chunk_transcript(transcript: list[dict], chunk_minutes: int = 3) -> list[str]:
    """
    Split a transcript into time-based chunks.

    Each chunk covers `chunk_minutes` minutes of video content.
    Returns a list of concatenated text strings, one per chunk.
    """
    if not transcript:
        return []

    chunk_seconds = chunk_minutes * 60
    chunks = []
    current_texts = []
    chunk_end = chunk_seconds

    for entry in transcript:
        start = entry["start"]

        # Advance chunk boundary until this entry fits
        while start >= chunk_end:
            if current_texts:
                chunks.append(" ".join(current_texts))
                current_texts = []
            chunk_end += chunk_seconds

        current_texts.append(entry["text"])

    # Append remaining text as the last chunk
    if current_texts:
        chunks.append(" ".join(current_texts))

    return chunks
