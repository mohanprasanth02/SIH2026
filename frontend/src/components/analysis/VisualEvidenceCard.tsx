import { useState } from 'react';
import {
  Sparkles, Layers, Image as ImageIcon, Maximize2,
  Download, ShieldCheck, X, ZoomIn, ZoomOut, RotateCcw,
  SplitSquareVertical, GitCompare, Radio, Target, FileDown
} from 'lucide-react';
import {
  type AnalysisResult,
  getResultImageUrl,
  triggerReportDownload,
} from '../../services/api';
import { rgbToCSS, cn } from '../../utils/cn';

interface VisualEvidenceCardProps {
  result: AnalysisResult;
  jobId?: string;
  className?: string;
  defaultLayer?: string;
}

export function VisualEvidenceCard({
  result,
  jobId,
  className,
  defaultLayer,
}: VisualEvidenceCardProps) {
  const { analysis, metadata, task } = result;

  // Detect task type
  const isChangeTask = !!analysis.change_map || task.includes('change');
  const isSarTask = !!analysis.sar_path || task.includes('sar') || !!analysis.sensor_consensus;
  const isGroundingTask = !!analysis.grounding_evidence || task.includes('ground');

  // Resolve all URLs
  const originalUrl = getResultImageUrl(analysis.original_path);
  const overlayUrl = getResultImageUrl(analysis.overlay_path);
  const changeMapUrl = getResultImageUrl(analysis.change_map);
  const changeOverlayUrl = getResultImageUrl(analysis.change_overlay);
  const afterUrl = getResultImageUrl(analysis.after_path);
  const opticalUrl = getResultImageUrl(analysis.optical_path) || originalUrl;
  const sarUrl = getResultImageUrl(analysis.sar_path);
  const groundingUrl = getResultImageUrl(analysis.grounding_evidence);

  // Land cover highlights
  const stats = analysis.class_statistics || [];
  const focusName = analysis.focus_class_name;
  const availableHighlights = analysis.class_highlights || {};
  const highlightKeys = Object.keys(availableHighlights);

  const initialClass =
    focusName && availableHighlights[focusName]
      ? focusName
      : highlightKeys.length > 0
      ? highlightKeys[0]
      : null;

  const [selectedClass, setSelectedClass] = useState<string | null>(initialClass);

  // Active highlight URL
  const activeHighlightUrl = selectedClass && availableHighlights[selectedClass]
    ? getResultImageUrl(availableHighlights[selectedClass])
    : getResultImageUrl(analysis.focus_highlight);

  // Determine default active layer
  const initialLayer = defaultLayer || (
    isChangeTask
      ? (changeOverlayUrl ? 'change_overlay' : 'change_map')
      : isSarTask
      ? 'fused'
      : isGroundingTask
      ? 'grounding'
      : (activeHighlightUrl ? 'highlight' : (overlayUrl ? 'overlay' : 'original'))
  );

  const [activeLayer, setActiveLayer] = useState<string>(initialLayer);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const [splitPosition, setSplitPosition] = useState<number>(50);
  const [showSplitView, setShowSplitView] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);

  // Resolve image to display based on activeLayer
  let currentImageUrl: string | null = null;
  if (isChangeTask) {
    if (activeLayer === 'change_overlay') currentImageUrl = changeOverlayUrl || changeMapUrl || afterUrl;
    else if (activeLayer === 'change_map') currentImageUrl = changeMapUrl || changeOverlayUrl;
    else if (activeLayer === 'before') currentImageUrl = originalUrl;
    else if (activeLayer === 'after') currentImageUrl = afterUrl;
    else currentImageUrl = changeMapUrl || changeOverlayUrl || afterUrl || originalUrl;
  } else if (isSarTask) {
    if (activeLayer === 'fused') currentImageUrl = overlayUrl || changeMapUrl || opticalUrl;
    else if (activeLayer === 'sar') currentImageUrl = sarUrl;
    else if (activeLayer === 'optical') currentImageUrl = opticalUrl;
    else currentImageUrl = overlayUrl || sarUrl || opticalUrl;
  } else if (isGroundingTask) {
    if (activeLayer === 'grounding') currentImageUrl = groundingUrl || overlayUrl || originalUrl;
    else currentImageUrl = originalUrl;
  } else {
    if (activeLayer === 'original') currentImageUrl = originalUrl;
    else if (activeLayer === 'overlay') currentImageUrl = overlayUrl || activeHighlightUrl;
    else currentImageUrl = activeHighlightUrl || overlayUrl || originalUrl;
  }

  // Fallback if none found
  if (!currentImageUrl) {
    currentImageUrl = activeHighlightUrl || overlayUrl || originalUrl || changeMapUrl || sarUrl;
  }

  // Split view images
  const splitLeftImage = isChangeTask ? originalUrl : (isSarTask ? opticalUrl : originalUrl);
  const splitRightImage = isChangeTask ? (afterUrl || changeMapUrl) : (isSarTask ? sarUrl : (activeHighlightUrl || overlayUrl));

  // Download image handler
  const handleDownloadImage = () => {
    if (!currentImageUrl) return;
    const link = document.createElement('a');
    link.href = currentImageUrl;
    link.download = `satquery_evidence_${activeLayer}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // If there are no images at all, don't show the card
  if (!currentImageUrl && !originalUrl && !changeMapUrl) {
    return null;
  }

  return (
    <div
      className={cn(
        'rounded-xl bg-white border border-[#DDE1DD] overflow-hidden shadow-sm transition-all relative font-sans',
        className
      )}
    >
      {/* Header bar */}
      <div className="px-4 py-2.5 bg-white border-b border-[#DDE1DD] flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#0C7C72] animate-pulse" />
          <span className="text-xs font-semibold text-[#111516] tracking-tight flex items-center gap-1.5 font-heading">
            <ShieldCheck className="w-3.5 h-3.5 text-[#0C7C72]" />
            {isChangeTask ? 'BI-TEMPORAL CHANGE EVIDENCE & MAP' : isSarTask ? 'OPTICAL + SAR MULTI-SENSOR EVIDENCE' : isGroundingTask ? 'GROUNDED REGIONS & SPATIAL RETICLES' : 'VISUAL EVIDENCE & GROUNDED MARKS'}
          </span>

          {/* Quick badge */}
          {analysis.primary_transition && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#D8893D]/10 border border-[#D8893D]/20 text-[#D8893D]">
              {analysis.primary_transition}
            </span>
          )}
          {analysis.primary_location && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#0C7C72]/10 border border-[#0C7C72]/20 text-[#0C7C72]">
              📍 {analysis.primary_location}
            </span>
          )}
          {analysis.target_name && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#258A65]/10 border border-[#258A65]/20 text-[#258A65]">
              🎯 Grounded: {analysis.target_name}
            </span>
          )}
        </div>

        {/* Action icons */}
        <div className="flex items-center gap-1.5">
          {/* Split Compare Button */}
          {splitLeftImage && splitRightImage && (
            <button
              type="button"
              onClick={() => setShowSplitView((prev) => !prev)}
              title="Toggle Split Slider Comparison"
              className={cn(
                'p-1.5 px-2.5 rounded-md border text-xs transition-all flex items-center gap-1 cursor-pointer',
                showSplitView
                  ? 'bg-[#0C7C72] border-[#0C7C72] text-white shadow-2xs'
                  : 'bg-[#F6F7F4] border-[#DDE1DD] text-[#687277] hover:text-[#111516] hover:bg-[#EEF0EC]'
              )}
            >
              <SplitSquareVertical className="w-3.5 h-3.5" />
              <span className="text-[11px] font-medium">Compare Slider</span>
            </button>
          )}

          {/* Download Evidence PNG */}
          <button
            type="button"
            onClick={handleDownloadImage}
            title="Download Evidence Image"
            className="p-1.5 px-2.5 rounded-md bg-[#F6F7F4] border border-[#DDE1DD] text-[#687277] hover:text-[#111516] hover:bg-[#EEF0EC] transition-all flex items-center gap-1 text-[11px] cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Save Image</span>
          </button>

          {/* Download Full PDF Report */}
          {jobId && (
            <button
              type="button"
              onClick={() => triggerReportDownload(jobId)}
              title="Download Full Analysis PDF Report"
              className="p-1.5 px-2.5 rounded-md bg-[#258A65] hover:bg-[#1E7253] text-white transition-all flex items-center gap-1 text-[11px] font-medium shadow-2xs cursor-pointer"
            >
              <FileDown className="w-3.5 h-3.5" />
              <span>PDF Report</span>
            </button>
          )}

          {/* Fullscreen Lightbox */}
          <button
            type="button"
            onClick={() => {
              setZoomLevel(1);
              setIsLightboxOpen(true);
            }}
            title="Maximize View"
            className="p-1.5 rounded-md bg-[#F6F7F4] border border-[#DDE1DD] text-[#687277] hover:text-[#111516] hover:bg-[#EEF0EC] transition-all cursor-pointer"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Layer selector tabs */}
      <div className="px-3 pt-2 pb-2 bg-[#F6F7F4] flex flex-wrap items-center gap-1.5 border-b border-[#DDE1DD] text-xs">
        {isChangeTask ? (
          <>
            {changeOverlayUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('change_overlay'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'change_overlay' && !showSplitView
                    ? 'bg-white text-[#D8893D] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <Sparkles className="w-3 h-3 text-[#D8893D]" />
                Change Overlay
              </button>
            )}
            {changeMapUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('change_map'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'change_map' && !showSplitView
                    ? 'bg-white text-[#0C7C72] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <GitCompare className="w-3 h-3 text-[#0C7C72]" />
                Change Map
              </button>
            )}
            {originalUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('before'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'before' && !showSplitView
                    ? 'bg-white text-[#111516] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <ImageIcon className="w-3 h-3 text-[#687277]" />
                Before Image (T1)
              </button>
            )}
            {afterUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('after'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'after' && !showSplitView
                    ? 'bg-white text-[#258A65] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <ImageIcon className="w-3 h-3 text-[#258A65]" />
                After Image (T2)
              </button>
            )}
          </>
        ) : isSarTask ? (
          <>
            <button
              type="button"
              onClick={() => { setActiveLayer('fused'); setShowSplitView(false); }}
              className={cn(
                'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                activeLayer === 'fused' && !showSplitView
                  ? 'bg-white text-[#0C7C72] border border-[#DDE1DD] shadow-2xs font-semibold'
                  : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
              )}
            >
              <Layers className="w-3 h-3 text-[#0C7C72]" />
              Fused Consensus Map
            </button>
            {sarUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('sar'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'sar' && !showSplitView
                    ? 'bg-white text-[#D8893D] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <Radio className="w-3 h-3 text-[#D8893D]" />
                SAR Radar Backscatter
              </button>
            )}
            {opticalUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('optical'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'optical' && !showSplitView
                    ? 'bg-white text-[#258A65] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <ImageIcon className="w-3 h-3 text-[#258A65]" />
                Optical RGB
              </button>
            )}
          </>
        ) : isGroundingTask ? (
          <>
            {groundingUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('grounding'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'grounding' && !showSplitView
                    ? 'bg-white text-[#0C7C72] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <Target className="w-3 h-3 text-[#0C7C72]" />
                🎯 Grounded Reticles & Masks
              </button>
            )}
            {originalUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('original'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'original' && !showSplitView
                    ? 'bg-white text-[#111516] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <ImageIcon className="w-3 h-3 text-[#687277]" />
                Original Satellite
              </button>
            )}
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={() => { setActiveLayer('highlight'); setShowSplitView(false); }}
              className={cn(
                'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                activeLayer === 'highlight' && !showSplitView
                  ? 'bg-white text-[#0C7C72] border border-[#DDE1DD] shadow-2xs font-semibold'
                  : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
              )}
            >
              <Sparkles className="w-3 h-3 text-[#0C7C72]" />
              Feature Marks
            </button>
            {overlayUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('overlay'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'overlay' && !showSplitView
                    ? 'bg-white text-[#258A65] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <Layers className="w-3 h-3 text-[#258A65]" />
                Classification Map
              </button>
            )}
            {originalUrl && (
              <button
                type="button"
                onClick={() => { setActiveLayer('original'); setShowSplitView(false); }}
                className={cn(
                  'px-2.5 py-1 rounded-md text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer',
                  activeLayer === 'original' && !showSplitView
                    ? 'bg-white text-[#111516] border border-[#DDE1DD] shadow-2xs font-semibold'
                    : 'text-[#687277] hover:text-[#111516] hover:bg-white/50'
                )}
              >
                <ImageIcon className="w-3 h-3 text-[#687277]" />
                Original Satellite
              </button>
            )}
          </>
        )}
      </div>

      {/* Class focus chips (for land cover) */}
      {!isChangeTask && !isSarTask && !isGroundingTask && highlightKeys.length > 0 && activeLayer === 'highlight' && !showSplitView && (
        <div className="px-3 py-1.5 bg-white flex flex-wrap items-center gap-1.5 border-b border-[#DDE1DD]">
          <span className="text-[10px] text-[#687277] font-medium uppercase tracking-wide mr-1">
            Focus Feature:
          </span>
          {highlightKeys.map((clsKey) => {
            const stat = stats.find((s) => s.class_name.toLowerCase() === clsKey.toLowerCase());
            const isSelected = selectedClass === clsKey;
            const pct = stat ? stat.percentage.toFixed(1) : null;
            const label = stat ? stat.label : clsKey;
            const colorRgb = stat ? rgbToCSS(stat.color) : '#0C7C72';

            return (
              <button
                key={clsKey}
                type="button"
                onClick={() => setSelectedClass(clsKey)}
                className={cn(
                  'flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium transition-all cursor-pointer',
                  isSelected
                    ? 'bg-[#EEF0EC] text-[#111516] border border-[#0C7C72] shadow-2xs'
                    : 'bg-[#F6F7F4] text-[#687277] hover:text-[#111516] hover:bg-[#EEF0EC] border border-transparent'
                )}
              >
                <div className="w-2 h-2 rounded-full shrink-0" style={{ background: colorRgb }} />
                <span>{label}</span>
                {pct && <span className="opacity-80 font-mono text-[10px]">({pct}%)</span>}
              </button>
            );
          })}
        </div>
      )}

      {/* Main Image Viewer Area */}
      <div className="relative bg-[#EEF0EC]/60 flex items-center justify-center overflow-hidden min-h-[260px] max-h-[440px] p-2">
        {showSplitView && splitLeftImage && splitRightImage ? (
          /* Split slider comparison */
          <div className="relative w-full h-full min-h-[300px] select-none">
            {/* Background Left Image */}
            <img
              src={splitLeftImage}
              alt="Comparison baseline"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />
            {/* Foreground Right Image clipped by slider */}
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ clipPath: `inset(0 ${100 - splitPosition}% 0 0)` }}
            >
              <img
                src={splitRightImage}
                alt="Comparison layer"
                className="absolute inset-0 w-full h-full object-contain pointer-events-none"
              />
            </div>
            {/* Split divider handle */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-[#0C7C72] cursor-ew-resize flex items-center justify-center shadow-md"
              style={{ left: `${splitPosition}%` }}
            >
              <div className="w-6 h-6 rounded-full bg-white border-2 border-[#0C7C72] flex items-center justify-center text-[#0C7C72] text-[10px] shadow-md font-bold">
                ⇔
              </div>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              value={splitPosition}
              onChange={(e) => setSplitPosition(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-10"
              aria-label="Comparison slider position"
            />
            {/* Badges for split */}
            <span className="absolute bottom-3 left-3 px-2 py-1 rounded-md bg-white/90 text-[10px] text-[#111516] shadow-xs border border-[#DDE1DD] pointer-events-none font-mono">
              {isChangeTask ? 'Before (T1)' : isSarTask ? 'Optical' : 'Original Scene'}
            </span>
            <span className="absolute bottom-3 right-3 px-2 py-1 rounded-md bg-white/90 text-[10px] text-[#0C7C72] shadow-xs border border-[#0C7C72]/30 pointer-events-none font-mono font-semibold">
              {isChangeTask ? 'After / Change Map' : isSarTask ? 'SAR Backscatter' : 'Evidence Highlight'}
            </span>
          </div>
        ) : (
          /* Single layer view */
          currentImageUrl && (
            <img
              src={currentImageUrl}
              alt="Visual Evidence"
              className="w-full h-full object-contain max-h-[440px] rounded-lg shadow-sm bg-white transition-all duration-200"
            />
          )
        )}
      </div>

      {/* Footer Info Strip */}
      <div className="px-4 py-2 bg-white border-t border-[#DDE1DD] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#687277]">
        <div className="flex items-center gap-3">
          {metadata && metadata.width && (
            <span>
              Raster: {metadata.width}×{metadata.height} px
            </span>
          )}
          {metadata?.crs && (
            <span className="font-mono text-[10px] text-[#687277] truncate max-w-[140px]">
              {metadata.crs}
            </span>
          )}
        </div>

        {/* Change stats */}
        {analysis.change_percentage != null && (
          <div className="flex items-center gap-2 font-mono text-[#D8893D] font-medium">
            <span>Changed: {analysis.change_percentage.toFixed(1)}%</span>
            {analysis.change_area_km2 && <span>({analysis.change_area_km2.toFixed(3)} km²)</span>}
          </div>
        )}
      </div>

      {/* Lightbox Modal */}
      {isLightboxOpen && currentImageUrl && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex flex-col items-center justify-center p-4">
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <button
              onClick={() => setZoomLevel((z) => Math.min(z + 0.5, 4))}
              className="p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-5 h-5" />
            </button>
            <button
              onClick={() => setZoomLevel((z) => Math.max(z - 0.5, 0.5))}
              className="p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <button
              onClick={() => setZoomLevel(1)}
              className="p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors cursor-pointer"
              title="Reset Zoom"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
            <button
              onClick={() => setIsLightboxOpen(false)}
              className="p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 ml-2 transition-colors cursor-pointer"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="max-w-[90vw] max-h-[85vh] overflow-auto flex items-center justify-center">
            <img
              src={currentImageUrl}
              alt="Enlarged evidence"
              style={{ transform: `scale(${zoomLevel})`, transition: 'transform 0.15s ease' }}
              className="object-contain max-h-[80vh] rounded-lg shadow-2xl bg-white"
            />
          </div>
        </div>
      )}
    </div>
  );
}
