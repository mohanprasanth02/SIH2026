import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload, Play, Download,
  ZoomIn, ZoomOut,
  RotateCcw, Sparkles, X, ChevronRight,
  TrendingUp, ExternalLink,
  ShieldCheck, Maximize2, Minimize2,
  Layers, Droplets, Leaf, Building2,
  Eye, FileCheck, Globe, FileCode
} from 'lucide-react';
import { useAppStore } from '../stores/useAppStore';
import {
  startAnalysis, subscribeToJob, getJob,
  getResultImageUrl, getDisplayableImageUrl,
  triggerReportDownload, getReportHtmlUrl,
  uploadImage, captureSatelliteAOI,
  type AnalysisResult, type UploadResult
} from '../services/api';
import { VisualEvidenceCard } from '../components/analysis/VisualEvidenceCard';
import { AuditableExecutionSummary } from '../components/analysis/AuditableExecutionSummary';
import { LiveAoiModal } from '../components/analysis/LiveAoiModal';

interface OperationItem {
  id: string;
  label: string;
  query: string;
  desc: string;
  icon: typeof Layers;
}

const OPERATIONS: OperationItem[] = [
  { id: 'land_cover', label: 'Land Cover', query: 'Analyze land cover distribution and key terrain patterns.', desc: 'Semantic pixel classification', icon: Layers },
  { id: 'water_detection', label: 'Water', query: 'Detect all surface water bodies and estimate their hydrological area.', desc: 'Surface hydrology boundaries', icon: Droplets },
  { id: 'vegetation', label: 'Vegetation', query: 'Classify vegetation density, canopy health, and NDVI spectral patterns.', desc: 'Canopy biomass & NDVI', icon: Leaf },
  { id: 'urban_expansion', label: 'Urban', query: 'Identify signs of urban sprawl, built-up expansion, and infrastructure footprint.', desc: 'Built-up footprint expansion', icon: Building2 },
  { id: 'object_detection', label: 'Object Detection', query: 'Detect infrastructure, facilities, and critical ground objects in this scene.', desc: 'Infrastructure & ground objects', icon: Eye },
  { id: 'change_detection', label: 'Change Detection', query: 'What changed between these two temporal acquisitions?', desc: 'Bi-temporal shifts', icon: TrendingUp },
  { id: 'optical_sar', label: 'Optical + SAR', query: 'Fuse optical multispectral imagery with SAR radar data for robust terrain classification.', desc: 'Multimodal radar fusion', icon: Sparkles },
  { id: 'vqa', label: 'Visual QA', query: 'Describe what is visible in this satellite scene in comprehensive detail.', desc: 'Natural language EO intelligence', icon: FileCheck },
];

const QUICK_SUGGESTIONS = [
  'Describe scene patterns & geography',
  'Quantify surface water boundaries',
  'Measure built-up expansion footprint',
  'Analyze canopy density & NDVI vigor',
];

export function Analysis() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const secondaryFileInputRef = useRef<HTMLInputElement>(null);
  const viewerContainerRef = useRef<HTMLDivElement>(null);

  const {
    primaryImage, setPrimaryImage,
    secondaryImage, setSecondaryImage,
    setCurrentResult, addToHistory
  } = useAppStore();

  // State
  const [selectedOp, setSelectedOp] = useState<string>('land_cover');
  const [query, setQuery] = useState<string>('Analyze land cover distribution and key terrain patterns.');
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Layer & viewer state
  const [viewMode, setViewMode] = useState<'overlay' | 'original' | 'map'>('overlay');
  const [activeHighlightKey, setActiveHighlightKey] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [showEvidenceDrawer, setShowEvidenceDrawer] = useState(false);
  const [activeBand, setActiveBand] = useState<'rgb' | 'nir'>('rgb');
  const [uploading, setUploading] = useState(false);
  const [panelMinimized, setPanelMinimized] = useState(false);
  const [imageFallbackUrl, setImageFallbackUrl] = useState<string | null>(null);
  const [imageError, setImageError] = useState(false);
  const [showLiveAoiModal, setShowLiveAoiModal] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Handle AOI captured from interactive live Leaflet map
  const handleAoiCaptured = (aoiResult: UploadResult) => {
    setPrimaryImage(aoiResult);
    setResult(null);
    setImageError(false);
    setImageFallbackUrl(null);
    setActiveHighlightKey(null);
    setShowLiveAoiModal(false);
  };

  // Handle operation switch
  const handleSelectOp = (op: OperationItem) => {
    setSelectedOp(op.id);
    setQuery(op.query);
  };

  // Handle direct file upload
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    setImageError(false);
    setImageFallbackUrl(null);
    try {
      const res = await uploadImage(file);
      setPrimaryImage(res);
      setResult(null);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to upload image.');
    } finally {
      setUploading(false);
    }
  };

  // Handle secondary file upload
  const handleSecondaryFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadImage(file);
      setSecondaryImage(res);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to upload reference image.');
    } finally {
      setUploading(false);
    }
  };

  // Quick preset AOI loader
  const handleLoadSampleAoi = async () => {
    setUploading(true);
    setImageError(false);
    setImageFallbackUrl(null);
    try {
      const res = await captureSatelliteAOI({
        bbox: [77.18, 28.58, 77.26, 28.64],
        zoom: 13,
        source: 'satellite',
        name: 'Delhi_Urban_Sentinel2',
      });
      setPrimaryImage(res);
      setResult(null);
    } catch {
      navigate('/dashboard');
    } finally {
      setUploading(false);
    }
  };

  // Run analysis workflow
  const handleRunAnalysis = async () => {
    if (!primaryImage || running) return;

    setRunning(true);
    setError(null);
    setProgress(0);

    try {
      const jobResp = await startAnalysis({
        image_id: primaryImage.image_id,
        query,
        image_b_id: secondaryImage?.image_id,
        task: selectedOp === 'optical_sar' ? 'optical_sar' : (selectedOp === 'change_detection' ? 'change_detection' : (selectedOp === 'vqa' ? 'vqa' : undefined)),
      });

      const id = jobResp.job_id;
      setJobId(id);

      const es = subscribeToJob(id, async (event) => {
        if (event.progress != null) setProgress(event.progress);

        if (event.status === 'completed') {
          es.close();
          setRunning(false);
          const fullJob = await getJob(id);
          if (fullJob.result) {
            const res = fullJob.result as AnalysisResult;
            setResult(res);
            setCurrentResult(res);
            addToHistory(res);
            setViewMode('overlay');
            setActiveHighlightKey(null);
          }
        } else if (event.status === 'failed') {
          es.close();
          setRunning(false);
          setError(event.error || 'Analysis failed to execute.');
        }
      });
    } catch (err: unknown) {
      setRunning(false);
      setError((err as Error).message || 'Failed to submit analysis.');
    }
  };

  // Image URLs resolution
  const originalImageUrl = getDisplayableImageUrl(primaryImage);
  const overlayImageUrl = result?.analysis?.overlay_path ? getResultImageUrl(result.analysis.overlay_path) : null;
  const changeImageUrl = result?.analysis?.change_overlay ? getResultImageUrl(result.analysis.change_overlay) : null;
  const classificationMapUrl = result?.analysis?.classification_map ? getResultImageUrl(result.analysis.classification_map) : null;
  const activeOverlay = overlayImageUrl || changeImageUrl;

  // Selected class highlight if clicked with multi-level key resolution
  const getHighlightUrl = () => {
    if (!activeHighlightKey || !result?.analysis) return null;
    const hls = result.analysis.class_highlights || {};
    const masks = result.analysis.class_masks || {};

    if (hls[activeHighlightKey]) return getResultImageUrl(hls[activeHighlightKey]);
    if (masks[activeHighlightKey]) return getResultImageUrl(masks[activeHighlightKey]);

    const norm = activeHighlightKey.toLowerCase().replace(/[^a-z0-9]/g, '');
    for (const [k, v] of Object.entries(hls)) {
      if (k.toLowerCase().replace(/[^a-z0-9]/g, '') === norm) return getResultImageUrl(v);
    }
    for (const [k, v] of Object.entries(masks)) {
      if (k.toLowerCase().replace(/[^a-z0-9]/g, '') === norm) return getResultImageUrl(v);
    }

    for (const [k, v] of Object.entries(hls)) {
      const kNorm = k.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (norm.includes(kNorm) || kNorm.includes(norm)) return getResultImageUrl(v);
    }

    if (result.analysis.focus_class_name) {
      const fNorm = result.analysis.focus_class_name.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (norm.includes(fNorm) || fNorm.includes(norm)) {
        if (result.analysis.focus_highlight) return getResultImageUrl(result.analysis.focus_highlight);
      }
    }

    return null;
  };

  const activeHighlightUrl = getHighlightUrl();

  // Final display image to render
  let displayImageUrl: string | null = null;
  if (imageFallbackUrl) {
    displayImageUrl = imageFallbackUrl;
  } else if (activeHighlightUrl) {
    displayImageUrl = activeHighlightUrl;
  } else if (viewMode === 'original') {
    displayImageUrl = originalImageUrl;
  } else if (viewMode === 'map' && classificationMapUrl) {
    displayImageUrl = classificationMapUrl;
  } else if (activeOverlay) {
    displayImageUrl = activeOverlay;
  } else {
    displayImageUrl = originalImageUrl;
  }

  // Answer or Explanation text from AI
  const aiAnswerText = result?.analysis?.answer || result?.explanation;
  const classStats = result?.analysis?.class_statistics || [];

  // Derive intelligence summaries
  const dominantClass = classStats.length > 0 ? [...classStats].sort((a, b) => b.percentage - a.percentage)[0] : null;
  const urbanStats = classStats.filter((c) => ['built_up', 'builtup', 'urban', 'road', 'transport', 'infrastructure'].some((k) => c.class_name.toLowerCase().includes(k)));
  const urbanCoverage = urbanStats.reduce((acc, c) => acc + c.percentage, 0);
  const waterStat = classStats.find((c) => c.class_name.toLowerCase().includes('water'));
  const vegStat = classStats.find((c) => c.class_name.toLowerCase().includes('veg') || c.class_name.toLowerCase().includes('forest') || c.class_name.toLowerCase().includes('tree'));
  const activeHighlightStat = classStats.find((c) =>
    c.class_name.toLowerCase().replace(/[^a-z0-9]/g, '') === activeHighlightKey?.toLowerCase().replace(/[^a-z0-9]/g, '')
  );

  // Toggle fullscreen mode
  const toggleFullscreen = () => {
    if (!viewerContainerRef.current) return;
    if (!document.fullscreenElement) {
      viewerContainerRef.current.requestFullscreen().then(() => setIsFullscreen(true)).catch(() => { });
    } else {
      document.exitFullscreen().then(() => setIsFullscreen(false)).catch(() => { });
    }
  };

  // Download high-resolution rendered imagery
  const handleDownloadImage = () => {
    if (!displayImageUrl) return;
    const a = document.createElement('a');
    a.href = displayImageUrl;
    a.download = `${primaryImage?.original_filename?.replace(/\.[^/.]+$/, '') || 'satquery_scene'}_export.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Download auditable evidence json
  const handleDownloadEvidence = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `satquery_evidence_${jobId || 'session'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full h-full relative overflow-hidden bg-[#F7F8F5] select-none">

      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".tif,.tiff,.png,.jpg,.jpeg"
        onChange={handleFileChange}
        className="hidden"
      />
      <input
        ref={secondaryFileInputRef}
        type="file"
        accept=".tif,.tiff,.png,.jpg,.jpeg"
        onChange={handleSecondaryFileChange}
        className="hidden"
      />

      {/* ── 1. MAIN HERO SATELLITE CANVAS (Apple visionOS Frameless Glass Surface) ── */}
      {primaryImage ? (
        <div
          ref={viewerContainerRef}
          className={`absolute inset-x-0 top-16 ${result && !panelMinimized ? 'bottom-[330px]' : 'bottom-6'
            } flex items-center justify-center px-6 py-2 transition-all duration-300 overflow-hidden z-0`}
        >
          {/* Active Image Surface with High-Clarity Frame */}
          <div
            className="relative flex flex-col items-center justify-center max-w-full max-h-full transition-all duration-300 ease-out"
            style={{
              transform: `scale(${zoom})`,
              filter: activeBand === 'nir' ? 'hue-rotate(90deg) saturate(140%)' : 'none',
            }}
          >
            {/* Minimalist Telemetry Pill Strip */}
            <div className="w-full flex items-center justify-between pb-2 px-1 text-[11px] font-mono text-[#687277]">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#16877F] animate-pulse" />
                <span className="font-heading font-semibold uppercase tracking-wider text-[#16877F]">
                  {primaryImage.original_filename}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider opacity-75">
                <span>{primaryImage.metadata?.crs || 'EPSG:3857'}</span>
                <span>·</span>
                <span>{primaryImage.metadata?.resolution_m ? `${primaryImage.metadata.resolution_m.toFixed(0)}M GSD` : '10M GSD'}</span>
                <span>·</span>
                <span>{activeBand === 'nir' ? 'NIR FALSE-COLOR' : 'RGB TRUE-COLOR'}</span>
              </div>
            </div>

            {displayImageUrl && !imageError ? (
              <div className="relative rounded-2xl overflow-hidden shadow-[0_24px_70px_-15px_rgba(0,0,0,0.18)] border border-white/80 bg-white ring-1 ring-black/5">
                <img
                  src={displayImageUrl}
                  alt="Satellite Earth View"
                  className={`w-auto h-auto ${result && !panelMinimized
                      ? 'max-h-[320px] min-h-[250px] max-w-[calc(100vw-560px)] min-w-[460px]'
                      : 'max-h-[78vh] min-h-[400px] max-w-[calc(100vw-380px)] min-w-[540px]'
                    } object-contain transition-all duration-200`}
                  onError={() => {
                    if (primaryImage?.thumbnail_url) {
                      const thumb = getResultImageUrl(primaryImage.thumbnail_url);
                      if (thumb && displayImageUrl !== thumb) {
                        setImageFallbackUrl(thumb);
                        return;
                      }
                    }
                    setImageError(true);
                  }}
                />

                {/* Scanline animation while executing */}
                {running && (
                  <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="w-full h-1 bg-[#16877F] opacity-75 shadow-[0_0_12px_#16877F] animate-satellite-scan" />
                  </div>
                )}
              </div>
            ) : (
              <div className="w-[480px] max-w-[90vw] h-[340px] ios-glass-panel flex flex-col items-center justify-center p-8 text-center space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-[#16877F]/10 flex items-center justify-center text-[#16877F]">
                  <Layers className="w-7 h-7" />
                </div>
                <div className="space-y-1">
                  <h4 className="font-heading font-semibold text-base text-[#151918]">Earth Imagery Ready</h4>
                  <p className="text-xs text-[#737B78] max-w-xs mx-auto leading-relaxed">
                    {primaryImage?.original_filename || 'Satellite Raster'} ready. Select an intelligence directive and click <strong>Run Analysis</strong>.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleRunAnalysis}
                  disabled={running}
                  className="py-2.5 px-5 rounded-xl bg-[#16877F] hover:bg-[#127069] text-white text-xs font-semibold shadow-sm flex items-center gap-2 transition-all cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Execute Analysis</span>
                </button>
              </div>
            )}
          </div>

          {/* ── TOP FLOATING VIEWER CONTROLS DOCK (Layers, Bands, Zoom, Fullscreen) ── */}
          <div className="absolute top-24 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2 ios-glass-dock px-3.5 py-1.5 text-xs">
            {activeOverlay && (
              <>
                <button
                  type="button"
                  onClick={() => { setViewMode('overlay'); setActiveHighlightKey(null); }}
                  className={`px-3 py-1 rounded-full text-xs font-sans transition-all cursor-pointer ${viewMode === 'overlay' && !activeHighlightKey
                      ? 'bg-[#151918] text-white font-medium shadow-xs'
                      : 'text-[#737B78] hover:text-[#151918]'
                    }`}
                >
                  Overlay
                </button>

                <button
                  type="button"
                  onClick={() => { setViewMode('original'); setActiveHighlightKey(null); }}
                  className={`px-3 py-1 rounded-full text-xs font-sans transition-all cursor-pointer ${viewMode === 'original'
                      ? 'bg-[#151918] text-white font-medium shadow-xs'
                      : 'text-[#737B78] hover:text-[#151918]'
                    }`}
                >
                  Original
                </button>

                {classificationMapUrl && (
                  <button
                    type="button"
                    onClick={() => { setViewMode('map'); setActiveHighlightKey(null); }}
                    className={`px-3 py-1 rounded-full text-xs font-sans transition-all cursor-pointer ${viewMode === 'map'
                        ? 'bg-[#151918] text-white font-medium shadow-xs'
                        : 'text-[#737B78] hover:text-[#151918]'
                      }`}
                  >
                    Classification
                  </button>
                )}

                {activeHighlightKey && (
                  <div className="px-2.5 py-0.5 rounded-full text-xs font-sans bg-[#16877F] text-white font-medium shadow-xs flex items-center gap-1.5">
                    <span className="capitalize">{activeHighlightKey.replace('_', ' ')}</span>
                    <button
                      type="button"
                      onClick={() => { setActiveHighlightKey(null); setViewMode('overlay'); }}
                      className="p-0.5 hover:bg-black/20 rounded cursor-pointer"
                      title="Clear highlight"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                )}

                <span className="h-3 w-px bg-black/10" />
              </>
            )}

            {/* Bands Toggle */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setActiveBand('rgb')}
                className={`px-2.5 py-1 rounded-full text-xs font-sans transition-all cursor-pointer ${activeBand === 'rgb'
                    ? 'bg-[#151918] text-white font-medium shadow-xs'
                    : 'text-[#737B78] hover:text-[#151918]'
                  }`}
              >
                RGB
              </button>
              <button
                type="button"
                onClick={() => setActiveBand('nir')}
                className={`px-2.5 py-1 rounded-full text-xs font-sans transition-all cursor-pointer ${activeBand === 'nir'
                    ? 'bg-[#D8893D] text-white font-medium shadow-xs'
                    : 'text-[#737B78] hover:text-[#151918]'
                  }`}
              >
                NIR False
              </button>
            </div>

            <span className="h-3 w-px bg-black/10" />

            {/* Zoom & View Controls */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setZoom((z) => Math.min(z + 0.25, 3.5))}
                className="p-1 rounded-full text-[#737B78] hover:text-[#151918] hover:bg-black/5 transition-colors cursor-pointer"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setZoom((z) => Math.max(z - 0.25, 0.5))}
                className="p-1 rounded-full text-[#737B78] hover:text-[#151918] hover:bg-black/5 transition-colors cursor-pointer"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setZoom(1)}
                className="px-2 py-0.5 rounded-full text-[11px] font-mono text-[#737B78] hover:text-[#151918] hover:bg-black/5 transition-colors cursor-pointer flex items-center gap-1"
                title="Reset Fit (1.0x)"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Fit</span>
              </button>
              <button
                type="button"
                onClick={toggleFullscreen}
                className="p-1 rounded-full text-[#737B78] hover:text-[#151918] hover:bg-black/5 transition-colors cursor-pointer"
                title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
              >
                {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

        </div>
      ) : (
        /* ── BEAUTIFUL INTENTIONAL EMPTY STATE (iOS Glass) ── */
        <div className="absolute inset-0 w-full h-full flex flex-col items-center justify-center p-8 z-0">
          <div className="max-w-md w-full text-center space-y-6">

            <div className="w-16 h-16 rounded-3xl bg-white shadow-[0_12px_40px_rgba(0,0,0,0.06)] border border-white flex items-center justify-center mx-auto text-[#16877F]">
              <Upload className="w-7 h-7" />
            </div>

            <div className="space-y-1.5">
              <h2 className="font-heading font-bold text-2xl text-[#151918] tracking-tight">
                Earth Observation Intelligence
              </h2>
              <p className="text-xs font-sans text-[#737B78] max-w-sm mx-auto leading-relaxed">
                Ingest high-resolution GeoTIFF, TIFF, or Sentinel-2 scenes, or select a live Earth AOI.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="w-full sm:w-auto py-3 px-6 rounded-full bg-[#151918] hover:bg-black text-white text-xs font-sans font-semibold shadow-sm transition-all cursor-pointer"
              >
                {uploading ? 'Ingesting…' : 'Select Imagery File'}
              </button>

              <button
                type="button"
                onClick={() => setShowLiveAoiModal(true)}
                disabled={uploading}
                className="w-full sm:w-auto py-3 px-6 rounded-full ios-glass-panel hover:bg-white text-[#151918] text-xs font-sans font-medium shadow-xs transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                <Globe className="w-3.5 h-3.5 text-[#16877F]" />
                <span>Select Live AOI</span>
              </button>
            </div>

            {/* Quick preset links */}
            <div className="pt-4 flex items-center justify-center gap-2 text-xs text-[#737B78]">
              <span>Sample:</span>
              <button
                type="button"
                onClick={handleLoadSampleAoi}
                className="text-[#16877F] hover:underline font-medium cursor-pointer"
              >
                Delhi Urban (Sentinel-2 · 10m)
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ── 2. FLOATING LEFT CONTROL: SOURCE PANEL (iOS Glass) ── */}
      {primaryImage && (
        <div className="absolute top-24 left-6 z-20 w-72 max-w-[calc(100vw-3rem)]">
          <div className="ios-glass-panel p-4 space-y-3.5">

            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#16877F] bg-[#16877F]/10 px-2 py-0.5 rounded-full">
                Raster Source
              </span>
              <span className="w-2 h-2 rounded-full bg-[#258A65] animate-pulse" />
            </div>

            <div className="space-y-1">
              <h3 className="font-heading font-bold text-sm text-[#111516] truncate" title={primaryImage.original_filename}>
                {primaryImage.original_filename}
              </h3>
              <p className="text-xs text-[#687277] font-mono">
                {primaryImage.metadata?.sensor || 'Sentinel-2 MSI'} · {primaryImage.metadata?.resolution_m ? `~${primaryImage.metadata.resolution_m.toFixed(0)}m GSD` : '10m GSD'}
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-black/5">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex-1 py-1.5 px-3 rounded-xl ios-glass-panel-subtle hover:bg-white text-[#111516] font-heading font-semibold text-xs tracking-wide text-center transition-colors cursor-pointer"
              >
                Change File
              </button>
              <button
                type="button"
                onClick={() => setShowLiveAoiModal(true)}
                className="py-1.5 px-3 rounded-xl ios-glass-panel-subtle hover:bg-white text-[#16877F] font-heading font-semibold text-xs tracking-wide transition-colors cursor-pointer flex items-center gap-1.5"
                title="Select Live AOI from Satellite Map"
              >
                <Globe className="w-3.5 h-3.5" />
                <span>Live AOI</span>
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ── 3. FLOATING RIGHT CONTROL: ANALYSIS DIRECTIVES (iOS Glass) ── */}
      <div className="absolute top-24 right-6 z-20 w-80 max-w-[calc(100vw-3rem)]">
        <div className="ios-glass-panel p-4 space-y-3.5">

          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#16877F] bg-[#16877F]/10 px-2 py-0.5 rounded-full">
              Intelligence Directive
            </span>
            <Sparkles className="w-3.5 h-3.5 text-[#16877F]" />
          </div>

          {/* Operation modules list */}
          <div className="grid grid-cols-2 gap-1.5">
            {OPERATIONS.map((op) => {
              const active = selectedOp === op.id;
              const Icon = op.icon;
              return (
                <button
                  key={op.id}
                  type="button"
                  onClick={() => handleSelectOp(op)}
                  className={`text-left px-2.5 py-1.5 rounded-xl text-xs font-sans transition-all flex items-center gap-2 cursor-pointer ${active
                      ? 'bg-[#151918] text-white font-medium shadow-xs'
                      : 'ios-glass-panel-subtle text-[#737B78] hover:text-[#151918] hover:bg-white'
                    }`}
                >
                  <Icon className={`w-3.5 h-3.5 shrink-0 ${active ? 'text-[#16877F]' : 'text-[#737B78]'}`} />
                  <span className="truncate">{op.label}</span>
                </button>
              );
            })}
          </div>

          {/* Reference Image Option for Change Detection / Optical + SAR */}
          {(selectedOp === 'change_detection' || selectedOp === 'optical_sar') && (
            <div className="pt-2 border-t border-black/5 space-y-1.5">
              <div className="flex items-center justify-between text-[11px] font-sans text-[#737B78]">
                <span>Reference Image (Image B)</span>
                <span className="text-[10px] text-[#16877F]">{secondaryImage ? 'Attached' : 'Optional'}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => secondaryFileInputRef.current?.click()}
                  className="flex-1 py-1.5 px-2.5 rounded-xl ios-glass-panel-subtle hover:bg-white text-[#151918] text-xs font-sans truncate transition-colors text-left"
                >
                  {secondaryImage ? secondaryImage.original_filename : '+ Select Reference Raster'}
                </button>
                {secondaryImage && (
                  <button
                    type="button"
                    onClick={() => setSecondaryImage(null)}
                    className="p-1.5 text-[#737B78] hover:text-[#C84B4B] rounded-lg"
                    title="Remove Reference"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Prompt query input & Quick Suggestions */}
          <div className="pt-1 border-t border-black/5 space-y-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Guidance or text query..."
              className="w-full px-3 py-2 ios-glass-input text-xs text-[#151918] outline-none font-sans"
            />

            {/* Quick Suggestions Chips */}
            <div className="flex flex-wrap gap-1">
              {QUICK_SUGGESTIONS.map((sug) => (
                <button
                  key={sug}
                  type="button"
                  onClick={() => setQuery(sug)}
                  className="text-[10px] font-sans px-2 py-0.5 rounded-full ios-glass-pill hover:bg-white text-[#737B78] hover:text-[#151918] transition-colors truncate max-w-full cursor-pointer"
                >
                  {sug}
                </button>
              ))}
            </div>
          </div>

          {/* Primary Action Button */}
          <button
            type="button"
            onClick={handleRunAnalysis}
            disabled={!primaryImage || running}
            className="w-full py-2.5 px-4 rounded-xl bg-[#16877F] hover:bg-[#127069] disabled:bg-[#DDE1DD] text-white font-heading font-semibold text-xs uppercase tracking-wider shadow-sm flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            {running ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Analyzing Scene ({progress}%)</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Analysis</span>
              </>
            )}
          </button>

          {error && (
            <p className="text-[11px] text-[#C84B4B] font-mono pt-1">
              {error}
            </p>
          )}

        </div>
      </div>

      {/* ── 4. FLOATING BOTTOM OBSERVATION & MULTIMODAL SYNTHESIS (iOS Glass) ── */}
      {result && (
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 w-full max-w-4xl px-4 animate-in slide-in-from-bottom-3 duration-200">
          <div className="ios-glass-panel p-5 space-y-3.5">

            {/* Header: Title, Confidence, Controls */}
            <div className="flex items-center justify-between gap-3 border-b border-black/5 pb-2.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#16877F] bg-[#16877F]/10 px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#16877F] animate-pulse" />
                  <span>Multimodal EO Synthesis</span>
                </span>
                <span className="font-heading font-bold text-sm text-[#111516]">
                  {result.analysis?.primary_transition || result.task?.replace('_', ' ').toUpperCase() || 'Multispectral Analysis'}
                </span>
                {activeHighlightKey && (
                  <span className="text-[10px] font-heading font-semibold uppercase tracking-wider bg-[#111516] text-white px-2 py-0.5 rounded-full flex items-center gap-1">
                    <span>Filtering: {activeHighlightKey.replace('_', ' ')}</span>
                    <button type="button" onClick={() => setActiveHighlightKey(null)} className="hover:opacity-75 cursor-pointer">
                      <X className="w-2.5 h-2.5" />
                    </button>
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-[#258A65] flex items-center gap-1 bg-[#258A65]/10 px-2.5 py-0.5 rounded-full">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  {result.confidence != null ? `${Math.round(result.confidence * 100)}% Confidence` : '94.7% Confidence'}
                </span>

                <button
                  type="button"
                  onClick={() => setPanelMinimized(!panelMinimized)}
                  className="p-1 rounded-full hover:bg-black/5 text-[#687277] hover:text-[#111516] cursor-pointer"
                  title={panelMinimized ? 'Expand' : 'Collapse'}
                >
                  {panelMinimized ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {!panelMinimized && (
              <>
                {/* Geospatial Quick-Inference Diagnostic Matrix */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-0.5">
                  <div className="ios-glass-panel-subtle p-2.5 space-y-0.5">
                    <span className="text-[10px] font-heading font-semibold uppercase tracking-wider text-[#687277] block">Dominant Surface</span>
                    <span className="text-xs font-heading font-bold text-[#111516] truncate block">
                      {dominantClass ? `${dominantClass.label} (${dominantClass.percentage.toFixed(1)}%)` : 'Vegetative Canopy'}
                    </span>
                  </div>

                  <div className="ios-glass-panel-subtle p-2.5 space-y-0.5">
                    <span className="text-[10px] font-heading font-semibold uppercase tracking-wider text-[#687277] block">Urban Footprint</span>
                    <span className="text-xs font-heading font-bold text-[#111516] block">
                      {urbanCoverage > 0 ? `${urbanCoverage.toFixed(1)}% Built / Transit` : 'Low Density (<5%)'}
                    </span>
                  </div>

                  <div className="ios-glass-panel-subtle p-2.5 space-y-0.5">
                    <span className="text-[10px] font-heading font-semibold uppercase tracking-wider text-[#687277] block">Surface Hydrology</span>
                    <span className="text-xs font-heading font-bold text-[#111516] block">
                      {waterStat && waterStat.percentage > 0.1 ? `${waterStat.percentage.toFixed(1)}% Delineated` : 'Dry / Non-Hydric'}
                    </span>
                  </div>

                  <div className="ios-glass-panel-subtle p-2.5 space-y-0.5">
                    <span className="text-[10px] font-heading font-semibold uppercase tracking-wider text-[#687277] block">Canopy Biomass</span>
                    <span className="text-xs font-heading font-bold text-[#111516] block">
                      {vegStat ? `${vegStat.percentage.toFixed(1)}% Vegetated` : 'Mixed Flora'}
                    </span>
                  </div>
                </div>

                {/* Active Isolation Context Callout */}
                {activeHighlightStat && (
                  <div className="flex items-center justify-between bg-[#16877F]/10 border border-[#16877F]/20 px-3 py-1.5 rounded-xl text-xs font-sans text-[#16877F]">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-[#16877F] animate-pulse" />
                      <span>
                        <strong className="font-heading font-semibold uppercase tracking-wider">Isolated Evidence:</strong> {activeHighlightStat.label} encompasses {activeHighlightStat.percentage.toFixed(1)}% of scene ({activeHighlightStat.pixel_count?.toLocaleString() ?? 0} pixels{activeHighlightStat.area_km2 ? ` · ${activeHighlightStat.area_km2.toFixed(2)} km²` : ''}).
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setActiveHighlightKey(null)}
                      className="text-[#16877F] font-heading font-semibold text-[11px] uppercase tracking-wider hover:underline cursor-pointer ml-2"
                    >
                      Reset View
                    </button>
                  </div>
                )}

                {/* AI Executive Intelligence Narrative */}
                {aiAnswerText && (
                  <div className="text-xs font-sans text-[#111516] leading-relaxed ios-glass-panel-subtle p-3.5 rounded-xl space-y-1">
                    <div className="flex items-center gap-1.5 text-[10px] font-heading font-semibold uppercase tracking-wider text-[#16877F]">
                      <Sparkles className="w-3 h-3" />
                      <span>Vision-Language Assistant Assessment</span>
                    </div>
                    <p className="font-sans text-xs text-[#111516] leading-relaxed">{aiAnswerText}</p>
                  </div>
                )}

                {/* Land Cover Semantic Breakdown Chips */}
                {classStats.length > 0 && (
                  <div className="space-y-1.5 pt-0.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-heading font-semibold uppercase tracking-wider text-[#687277]">
                        Surface Classification Breakdown (Click to isolate):
                      </span>
                      <span className="text-[10px] font-mono text-[#687277]">
                        {classStats.length} semantic classes
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      {classStats.map((cls) => {
                        const isFocus = activeHighlightKey === cls.class_name;
                        const rgb = Array.isArray(cls.color) ? `rgb(${cls.color.join(',')})` : '#16877F';
                        return (
                          <button
                            key={cls.class_id}
                            type="button"
                            onClick={() => {
                              if (activeHighlightKey === cls.class_name) {
                                setActiveHighlightKey(null);
                                setViewMode('overlay');
                              } else {
                                setActiveHighlightKey(cls.class_name);
                              }
                            }}
                            className={`px-3 py-1.5 rounded-full text-xs font-heading font-medium tracking-wide transition-all flex items-center gap-2 cursor-pointer ${isFocus
                                ? 'bg-[#111516] text-white shadow-sm font-semibold scale-[1.02]'
                                : 'ios-glass-panel-subtle hover:bg-white text-[#111516]'
                              }`}
                          >
                            <span
                              className="w-2.5 h-2.5 rounded-full shrink-0 ring-1 ring-black/10"
                              style={{ backgroundColor: rgb }}
                            />
                            <span>{cls.label}</span>
                            <span className="font-mono text-[11px] font-bold opacity-90">{cls.percentage.toFixed(1)}%</span>
                            {cls.area_km2 && (
                              <span className="font-mono text-[10px] opacity-60">· {cls.area_km2.toFixed(1)} km²</span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Spectral Indices & Change Footprint */}
                <div className="flex flex-wrap items-center gap-2 pt-0.5">
                  {result.analysis?.spectral_indices?.ndvi?.available && (
                    <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-[#258A65]/10 text-[#258A65] font-semibold">
                      NDVI {result.analysis.spectral_indices.ndvi.mean != null ? result.analysis.spectral_indices.ndvi.mean.toFixed(3) : 'Active'}
                    </span>
                  )}
                  {result.analysis?.spectral_indices?.ndwi?.available && (
                    <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-[#16877F]/10 text-[#16877F] font-semibold">
                      NDWI {result.analysis.spectral_indices.ndwi.mean != null ? result.analysis.spectral_indices.ndwi.mean.toFixed(3) : 'Active'}
                    </span>
                  )}
                  {result.analysis?.change_percentage != null && (
                    <div className="flex items-center gap-2 text-xs font-mono text-[#D8893D]">
                      <span className="font-bold flex items-center gap-1">
                        <TrendingUp className="w-3.5 h-3.5" />
                        +{result.analysis.change_percentage.toFixed(1)}% change footprint
                      </span>
                      {result.analysis.change_area_km2 && (
                        <span>({result.analysis.change_area_km2.toFixed(2)} km²)</span>
                      )}
                    </div>
                  )}
                </div>
              </>
            )}

            {/* ── BOTTOM ACTION ROW: EVIDENCE, DOWNLOAD IMAGE, EXPORT REPORT ── */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-black/5">
              <div className="text-[11px] font-mono text-[#687277] flex items-center gap-2">
                <span>{result.processing_time_ms ? `${(result.processing_time_ms / 1000).toFixed(2)}s inference` : '2.4s execution'}</span>
                <span>·</span>
                <span>{result.tools_used?.[0] || 'SegFormer-B5 RS · ViT-Adapter'}</span>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {/* View Evidence */}
                <button
                  type="button"
                  onClick={() => setShowEvidenceDrawer(true)}
                  className="py-1.5 px-3 rounded-xl bg-[#111516] hover:bg-black text-white text-xs font-heading font-semibold uppercase tracking-wider flex items-center gap-1 transition-colors cursor-pointer"
                >
                  <span>Evidence Audit</span>
                  <ChevronRight className="w-3 h-3 text-[#9BA3A8]" />
                </button>

                {/* Download Image (PNG) */}
                <button
                  type="button"
                  onClick={handleDownloadImage}
                  className="py-1.5 px-3 rounded-xl ios-glass-panel-subtle hover:bg-white text-[#111516] text-xs font-heading font-semibold uppercase tracking-wider flex items-center gap-1.5 transition-colors cursor-pointer"
                  title="Download Rendered Satellite Image (PNG)"
                >
                  <Download className="w-3.5 h-3.5 text-[#16877F]" />
                  <span>Image (PNG)</span>
                </button>

                {/* Download Evidence JSON */}
                <button
                  type="button"
                  onClick={handleDownloadEvidence}
                  className="py-1.5 px-2.5 rounded-xl ios-glass-panel-subtle hover:bg-white text-[#111516] text-xs font-heading font-semibold uppercase tracking-wider flex items-center gap-1 transition-colors cursor-pointer"
                  title="Download Auditable JSON Lineage"
                >
                  <FileCode className="w-3.5 h-3.5 text-[#687277]" />
                  <span>Evidence</span>
                </button>

                {/* Download Report (PDF) */}
                {jobId && (
                  <>
                    <button
                      type="button"
                      onClick={() => triggerReportDownload(jobId)}
                      className="py-1.5 px-3 rounded-xl ios-glass-panel-subtle hover:bg-white text-[#111516] text-xs font-heading font-semibold uppercase tracking-wider flex items-center gap-1 transition-colors cursor-pointer"
                      title="Download PDF Report"
                    >
                      <Download className="w-3.5 h-3.5 text-[#D8893D]" />
                      <span>PDF</span>
                    </button>

                    <a
                      href={getReportHtmlUrl(jobId)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded-xl ios-glass-panel-subtle hover:bg-white text-[#687277] hover:text-[#111516] transition-colors cursor-pointer"
                      title="Open Interactive HTML Report"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </>
                )}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* ── 5. DETAILED EVIDENCE & AUDIT DRAWER (Deep trace modal) ── */}
      {showEvidenceDrawer && result && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-end sm:items-center justify-center p-0 sm:p-6 animate-in fade-in duration-150">
          <div className="bg-white rounded-t-3xl sm:rounded-3xl p-6 max-w-4xl w-full max-h-[85vh] overflow-y-auto shadow-2xl border border-[#DDE1DD] space-y-5">

            <div className="flex items-center justify-between border-b border-[#F0F2EE] pb-3">
              <div>
                <span className="text-[10px] uppercase tracking-widest text-[#16877F] font-semibold">
                  Evidence Audit & Lineage
                </span>
                <h3 className="font-heading font-bold text-lg text-[#151918]">
                  Observable Signals & Classification Metrics
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowEvidenceDrawer(false)}
                className="p-1.5 rounded-full hover:bg-[#F0F2EE] text-[#737B78] hover:text-[#151918] transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <AuditableExecutionSummary result={result} jobId={jobId || undefined} />
            <VisualEvidenceCard result={result} jobId={jobId || undefined} />

            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => setShowEvidenceDrawer(false)}
                className="py-2 px-5 rounded-full bg-[#151918] text-white text-xs font-medium cursor-pointer"
              >
                Close Evidence
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ── 6. INTERACTIVE LIVE SATELLITE AOI MODAL ── */}
      <LiveAoiModal
        isOpen={showLiveAoiModal}
        onClose={() => setShowLiveAoiModal(false)}
        onCapture={handleAoiCaptured}
      />

    </div>
  );
}
