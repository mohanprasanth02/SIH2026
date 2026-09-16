"""SatQuery AI - Reports Route"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, HTMLResponse, JSONResponse
from app.workers.job_manager import job_manager
from app.services.report_service import ReportService

router = APIRouter()
report_service = ReportService()


@router.get("/reports/{job_id}")
async def get_report(job_id: str):
    """Return report metadata for a completed job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        return JSONResponse(content={"status": job.status, "report": None})

    return JSONResponse(content={
        "status": "available",
        "job_id": job_id,
        "download_url": f"/api/v1/reports/{job_id}/download",
        "html_url": f"/api/v1/reports/{job_id}/html",
        "message": "Report available for PDF download and HTML preview.",
    })


@router.get("/reports/{job_id}/download")
async def download_report(job_id: str):
    """Generate and download PDF report for a completed job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis job is not yet completed")

    pdf_bytes = report_service.generate_pdf(job.to_dict(), job_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="satquery_report_{job_id[:8]}.pdf"'},
    )


@router.get("/reports/{job_id}/html")
async def get_html_report(job_id: str):
    """View styled printable HTML report in browser."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis job is not yet completed")

    html_content = report_service.generate_html(job.to_dict(), job_id)
    return HTMLResponse(content=html_content)
