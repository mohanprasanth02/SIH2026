$pptxPath = "E:\Study\SIH\satquery-ai\SATQuery_AI_SIH_2026.pptx"
$pdfPath  = "E:\Study\SIH\satquery-ai\SATQuery_AI_SIH_2026.pdf"
$outDir   = "E:\Study\SIH\satquery-ai\scratch\slide_images"

if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$ppt = New-Object -ComObject PowerPoint.Application
# Do not show window
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue

try {
    $presentation = $ppt.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    
    # 1. Export as PDF (32 = ppSaveAsPDF)
    Write-Host "Exporting to PDF: $pdfPath ..."
    $presentation.SaveAs($pdfPath, 32)
    Write-Host "PDF export successful!"

    # 2. Export each slide as high-res PNG (1920x1080)
    Write-Host "Exporting slides as high-res PNGs to $outDir ..."
    $slideIndex = 1
    foreach ($slide in $presentation.Slides) {
        $slideImg = Join-Path $outDir "slide_$slideIndex.png"
        $slide.Export($slideImg, "PNG", 1920, 1080)
        Write-Host "Exported Slide $slideIndex -> $slideImg"
        $slideIndex++
    }

    $presentation.Close()
} catch {
    Write-Host "Error during export: $_"
} finally {
    $ppt.Quit()
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
