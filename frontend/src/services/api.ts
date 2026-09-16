/**
 * SatQuery AI - Frontend API Service
 * All calls go through the backend. NEVER expose API keys here.
 */
import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${BACKEND_URL}/api/v1`,
  timeout: 60_000,
});

// Attach JWT token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('satquery_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('satquery_token');
    }
    return Promise.reject(error);
  }
);

// ── Upload ─────────────────────────────────────────────────────────

export interface UploadResult {
  image_id: string;
  stored_filename: string;
  original_filename: string;
  detected_mime: string;
  thumbnail_url: string | null;
  metadata: ImageMetadata | null;
}

export interface ImageMetadata {
  filename: string;
  format: string;
  modality: string;
  file_size: number;
  width: number;
  height: number;
  band_count: number;
  dtype: string;
  band_descriptions: string[];
  is_georeferenced: boolean;
  crs: string | null;
  crs_authority: string | null;
  resolution_x: number | null;
  resolution_y: number | null;
  resolution_m: number | null;
  bounds: { left: number; bottom: number; right: number; top: number } | null;
  bounds_wgs84: { lon_min: number; lat_min: number; lon_max: number; lat_max: number } | null;
  nodata: number | null;
  acquisition_date: string | null;
  sensor: string | null;
  cloud_cover: number | null;
  warnings: string[];
}

export async function uploadImage(
  file: File,
  modality?: string,
  onProgress?: (pct: number) => void
): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  if (modality) formData.append('modality', modality);

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    },
  });
  return response.data;
}

// ── Satellite AOI & Live Map ───────────────────────────────────────

export interface SatellitePreset {
  id: string;
  name: string;
  category: string;
  description: string;
  bbox: [number, number, number, number];
  zoom: number;
  tags: string[];
}

export interface CaptureAoiRequest {
  bbox: [number, number, number, number];
  zoom?: number;
  source?: 'satellite' | 'osm';
  name?: string;
}

export async function captureSatelliteAOI(req: CaptureAoiRequest): Promise<UploadResult> {
  const response = await api.post('/satellite/aoi', req);
  return response.data;
}

export async function getSatellitePresets(): Promise<SatellitePreset[]> {
  const response = await api.get('/satellite/presets');
  return response.data.presets;
}

export interface GeocodeResult {
  name: string;
  lat: number;
  lng: number;
  bbox: [number, number, number, number];
  type?: string;
}

export async function geocodeLocation(query: string): Promise<GeocodeResult[]> {
  const q = query.trim();
  if (!q || q.length < 2) return [];

  // Check direct coordinates first: e.g. "48.8584, 2.2945"
  const cleaned = q.replace(/°|[NSEWnsew]/g, '').trim();
  if (cleaned.includes(',') || cleaned.includes(' ')) {
    const parts = cleaned.split(/[,\s]+/).filter(Boolean);
    if (parts.length === 2) {
      const lat = parseFloat(parts[0]);
      const lng = parseFloat(parts[1]);
      if (!isNaN(lat) && !isNaN(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
        return [{
          name: `Coordinates: ${lat.toFixed(4)}°, ${lng.toFixed(4)}°`,
          lat,
          lng,
          bbox: [lng - 0.04, lat - 0.04, lng + 0.04, lat + 0.04],
          type: 'coordinate'
        }];
      }
    }
  }

  try {
    const response = await api.get('/satellite/geocode', { params: { q } });
    if (response.data?.results && response.data.results.length > 0) {
      return response.data.results;
    }
  } catch {
    // fallback to direct photon query
  }

  // Client-side direct Photon fallback
  try {
    const res = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=7`);
    if (res.ok) {
      const data = await res.json();
      const results: GeocodeResult[] = [];
      for (const feat of data.features || []) {
        const props = feat.properties || {};
        const coords = feat.geometry?.coordinates;
        if (coords && coords.length >= 2) {
          const lng = coords[0];
          const lat = coords[1];
          const nameParts = [
            props.name,
            props.city && props.city !== props.name ? props.city : null,
            props.state && props.state !== props.name ? props.state : null,
            props.country
          ].filter(Boolean);
          const extent = props.extent;
          const bbox: [number, number, number, number] = extent && extent.length === 4
            ? [extent[0], extent[3], extent[2], extent[1]]
            : [lng - 0.04, lat - 0.04, lng + 0.04, lat + 0.04];
          results.push({
            name: nameParts.join(', ') || props.name || q,
            lat,
            lng,
            bbox,
            type: props.osm_value || 'place'
          });
        }
      }
      return results;
    }
  } catch {
    // ignore
  }

  return [];
}

// ── Analysis ──────────────────────────────────────────────────────

export interface AnalyzeRequest {
  image_id: string;
  query: string;
  image_b_id?: string;
  task?: string;
  parameters?: Record<string, unknown>;
}

export interface JobResponse {
  job_id: string;
  status: string;
  message: string;
}

export async function startAnalysis(req: AnalyzeRequest): Promise<JobResponse> {
  const response = await api.post('/analyze', req);
  return response.data;
}

export async function startLandCoverAnalysis(req: AnalyzeRequest): Promise<JobResponse> {
  const response = await api.post('/analyze/area', req);
  return response.data;
}

export async function startChangeDetection(req: AnalyzeRequest): Promise<JobResponse> {
  const response = await api.post('/analyze/change', req);
  return response.data;
}

export async function startOpticalSAR(req: AnalyzeRequest): Promise<JobResponse> {
  const response = await api.post('/analyze/optical-sar', req);
  return response.data;
}

export async function startVQA(req: AnalyzeRequest): Promise<JobResponse> {
  const response = await api.post('/analyze/vqa', req);
  return response.data;
}

// ── Jobs ──────────────────────────────────────────────────────────

export interface JobState {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  stage: string;
  progress: number;
  error: string | null;
  result: AnalysisResult | null;
  execution_steps: ExecutionStep[];
  step?: ExecutionStep;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface ExecutionStep {
  step_index: number;
  step_name: string;
  tool: string | null;
  model: string | null;
  status: string;
  output_summary: string | null;
  error: string | null;
  duration_ms: number | null;
}

export interface ClassStatistic {
  class_id: number;
  class_name: string;
  label: string;
  color: [number, number, number];
  pixel_count: number;
  percentage: number;
  area_m2: number | null;
  area_ha: number | null;
  area_km2: number | null;
  source_tool: string;
  model_name: string;
  model_version: string;
  confidence: number | null;
}

export interface ExecutionSummary {
  query?: string;
  inputs?: Record<string, any>;
  detected_task?: string;
  selected_tools?: string[];
  selected_models?: string[];
  rs_domain_adaptations?: string[];
  key_outputs?: Record<string, any>;
  confidence?: number;
  processing_time_ms?: number;
}

export interface AnalysisResult {
  task: string;
  tools_used: string[];
  query: string;
  confidence?: number;
  execution_summary?: ExecutionSummary;
  metadata: ImageMetadata;
  metadata_b: ImageMetadata | null;
  analysis: {
    class_statistics?: ClassStatistic[];
    total_pixels?: number;
    spectral_indices?: Record<string, { available: boolean; mean?: number; reason?: string }>;
    classification_map?: string;
    overlay_path?: string;
    original_path?: string;
    focus_class?: number;
    focus_class_name?: string;
    focus_highlight?: string;
    class_highlights?: Record<string, string>;
    class_masks?: Record<string, string>;
    confidence?: number;
    // Bi-temporal Change Detection & CDVQA
    change_percentage?: number;
    change_area_km2?: number;
    change_area_ha?: number;
    change_area_m2?: number;
    class_changes?: ClassStatistic[];
    change_map?: string;
    change_overlay?: string;
    primary_transition?: string;
    primary_location?: string;
    locations?: string[];
    after_path?: string;
    // Optical + SAR
    optical_path?: string;
    sar_path?: string;
    sensor_consensus?: Record<string, any>;
    // Grounding & VRSBench
    target_name?: string;
    target_class_id?: number;
    bounding_boxes?: Array<{
      ymin: number;
      xmin: number;
      ymax: number;
      xmax: number;
      norm_ymin?: number;
      norm_xmin?: number;
      norm_ymax?: number;
      norm_xmax?: number;
      pixel_count?: number;
      percentage?: number;
    }>;
    centroids?: Array<{ x: number; y: number }>;
    grounding_evidence?: string;
    question?: string;
    answer?: string;
    caption?: string;
    sar_analysis?: Record<string, unknown>;
    error?: string;
    warnings?: string[];
  };
  explanation: string;
  execution_steps: ExecutionStep[];
  processing_time_ms: number;
  warnings: string[];
}

export function getReportDownloadUrl(jobId: string): string {
  return `${BACKEND_URL}/api/v1/reports/${jobId}/download`;
}

export function getReportHtmlUrl(jobId: string): string {
  return `${BACKEND_URL}/api/v1/reports/${jobId}/html`;
}

export function triggerReportDownload(jobId: string) {
  const url = getReportDownloadUrl(jobId);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `satquery_report_${jobId.slice(0, 8)}.pdf`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Resolves a result image path or URL into a fully-qualified browser URL.
 */
export function getResultImageUrl(pathOrUrl?: string | null): string | null {
  if (!pathOrUrl) return null;
  if (
    pathOrUrl.startsWith('http://') ||
    pathOrUrl.startsWith('https://') ||
    pathOrUrl.startsWith('blob:') ||
    pathOrUrl.startsWith('data:')
  ) {
    return pathOrUrl;
  }
  if (pathOrUrl.startsWith('/')) {
    return `${BACKEND_URL}${pathOrUrl}`;
  }
  const filename = pathOrUrl.replace(/^.*[\\/]/, '');
  return `${BACKEND_URL}/results/${filename}`;
}

/**
 * Resolves an UploadResult into a web-renderable image URL (PNG/JPEG thumbnail or web raster).
 * Fixes broken image tags when raw files are GeoTIFF (.tif/.tiff).
 */
export function getDisplayableImageUrl(
  image?: UploadResult | null,
  overridePath?: string | null
): string | null {
  if (overridePath) {
    return getResultImageUrl(overridePath);
  }
  if (!image) return null;
  if (image.thumbnail_url) {
    return getResultImageUrl(image.thumbnail_url);
  }
  if (image.stored_filename) {
    if (/\.(png|jpg|jpeg|webp)$/i.test(image.stored_filename)) {
      return getResultImageUrl(image.stored_filename);
    }
    const stem = image.stored_filename.replace(/\.[^/.]+$/, '');
    return getResultImageUrl(`/results/${stem}_thumb.png`);
  }
  return null;
}

export async function getJob(jobId: string): Promise<JobState> {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
}

export interface JobSummaryItem {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  stage: string;
  progress: number;
  error: string | null;
  task?: string;
  query?: string;
  confidence?: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export async function listJobs(): Promise<JobSummaryItem[]> {
  const response = await api.get('/jobs');
  return response.data.jobs;
}

export async function cancelJob(jobId: string): Promise<void> {
  await api.post(`/jobs/${jobId}/cancel`);
}

/**
 * Subscribe to SSE job status stream.
 * Returns an EventSource; caller is responsible for closing it.
 */
export function subscribeToJob(
  jobId: string,
  onEvent: (event: Partial<JobState>) => void,
  onError?: (e: Event) => void
): EventSource {
  const url = `${BACKEND_URL}/api/v1/jobs/${jobId}/status`;
  const es = new EventSource(url);
  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onEvent(data);
    } catch { /* ignore parse errors */ }
  };
  if (onError) es.onerror = onError;
  return es;
}

// ── Dashboard ─────────────────────────────────────────────────────

export interface DashboardStats {
  total_analyses: number;
  completed_analyses: number;
  failed_analyses: number;
  running_analyses: number;
  average_processing_time_ms: number | null;
  task_breakdown: Record<string, number>;
  device: string;
  device_info: { cuda_available: boolean; gpu_name: string | null; vram_gb: number | null };
  models_loaded: number;
  models_registered: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await api.get('/dashboard/stats');
  return response.data;
}

export async function getRecentAnalyses() {
  const response = await api.get('/dashboard/recent');
  return response.data.recent_analyses;
}

// ── Models ────────────────────────────────────────────────────────

export async function getModels() {
  const response = await api.get('/models');
  return response.data;
}

export async function getTools() {
  const response = await api.get('/tools');
  return response.data.tools;
}

// ── Auth ──────────────────────────────────────────────────────────

export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  const token = response.data.access_token;
  localStorage.setItem('satquery_token', token);
  return response.data;
}

export async function logout() {
  localStorage.removeItem('satquery_token');
}

export function isLoggedIn(): boolean {
  return !!localStorage.getItem('satquery_token');
}

// ── Utilities ─────────────────────────────────────────────────────

export function getImageUrl(path: string | null): string | null {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `${BACKEND_URL}/results/${path.split('/').pop()}`;
}
