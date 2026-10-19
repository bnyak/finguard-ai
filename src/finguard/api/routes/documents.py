from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import APIRouter, File, HTTPException, UploadFile

from finguard.api.schemas import DocumentUploadResponse
from finguard.ingestion.service import ingest_pdf


router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/documents", response_model=DocumentUploadResponse)
def upload_document(file: UploadFile = File(...)):

    # 1. Validate filename
    filename = Path(file.filename or "").name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException( status_code=400, detail="Only PDF files are allowed", )

    # 2. Read with a file-size limit
    content = file.file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException( status_code=413, detail="PDF exceeds the 10 MB limit", )

    # 3. Check PDF file signature
    if not content.startswith(b"%PDF-"):
        raise HTTPException( status_code=400, detail="Invalid PDF file", )

    # 4. Save temporarily and ingest
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / filename
        temp_path.write_bytes(content)

        try:
            document_id = ingest_pdf(temp_path)
        except Exception:
            raise HTTPException( status_code=500, detail="Document ingestion failed", )

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        message="Document ingested successfully",
    )