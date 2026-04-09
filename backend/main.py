from __future__ import annotations

import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from backend.transcription import (
    TranscriptionServiceError,
    resolve_transcription_language,
    transcribe_audio_file,
)

app = FastAPI(title="The Bridge Speech API")


@app.on_event("startup")
async def log_startup_diagnostics() -> None:
    print(
        "[backend] Startup diagnostic: "
        f"OPENAI_API_KEY present={bool(os.getenv('OPENAI_API_KEY'))} "
        f"transcription_language={resolve_transcription_language()}"
    )


@app.post("/api/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> dict[str, str]:
    try:
        audio_bytes = await file.read()
        text = transcribe_audio_file(
            audio_bytes=audio_bytes,
            filename=file.filename or "audio-upload",
            content_type=file.content_type or "",
            language=language,
        )
    except TranscriptionServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    finally:
        await file.close()

    return {"text": text}
