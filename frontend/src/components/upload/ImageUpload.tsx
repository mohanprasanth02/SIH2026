import { useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useDropzone } from 'react-dropzone';
import {
  X, AlertTriangle, CheckCircle2, Satellite,
  Info, FileType, Layers, MapPin, Calendar, Eye,
  Globe2, UploadCloud, Map
} from 'lucide-react';
import { uploadImage, type UploadResult } from '../../services/api';
import { formatBytes } from '../../utils/cn';
import { MapAoiSelector } from '../map/MapAoiSelector';

interface Props {
  onUploaded: (result: UploadResult) => void;
  label?: string;
  accept?: string[];
}

const ACCEPTED_EXTS = ['.tif', '.tiff', '.png', '.jpg', '.jpeg'];
const ACCEPTED_MIME = {
  'image/tiff':  ['.tif', '.tiff'],
  'image/png':   ['.png'],
  'image/jpeg':  ['.jpg', '.jpeg'],
};

export function ImageUpload({ onUploaded, label = 'Upload Satellite Image' }: Props) {
  const [mode, setMode] = useState<'upload' | 'map'>('upload');
  const [showMapModal, setShowMapModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    const file = acceptedFiles[0];

    setError(null);
    setUploadResult(null);
    setUploading(true);
    setUploadProgress(0);

    try {
      const result = await uploadImage(file, undefined, (pct) => setUploadProgress(pct));
      setUploadResult(result);
      onUploaded(result);
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        || (e instanceof Error ? e.message : 'Upload failed');
      setError(msg);
    } finally {
      setUploading(false);
    }
  }, [onUploaded]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_MIME,
    maxFiles: 1,
    disabled: uploading,
  });

  const handleAoiCaptured = (result: UploadResult) => {
    setUploadResult(result);
    onUploaded(result);
    setShowMapModal(false);
  };

  const clearResult = () => {
    setUploadResult(null);
    setError(null);
  };

  return (
    <div className="space-y-3">
      {/* Tab Switcher: Upload vs Live Satellite Map */}
      {!uploadResult && (
        <div className="flex rounded-lg p-1 bg-dark-700/80 border border-white/10 text-xs">
          <button
            type="button"
            onClick={() => setMode('upload')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md font-medium transition-all ${
              mode === 'upload'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <UploadCloud className="w-3.5 h-3.5" />
            Upload File
          </button>
          <button
            type="button"
            onClick={() => setMode('map')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md font-medium transition-all ${
              mode === 'map'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Globe2 className="w-3.5 h-3.5 text-teal-400" />
            Live Map AOI
          </button>
        </div>
      )}

      {/* Option 1: File Upload */}
      {!uploadResult && mode === 'upload' && (
        <div
          {...getRootProps()}
          className={`
            relative flex flex-col items-center justify-center gap-3 px-6 py-8
            rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200
            ${isDragActive && !isDragReject ? 'border-brand-500 bg-brand-900/20' : ''}
            ${isDragReject ? 'border-red-500 bg-red-900/10' : ''}
            ${!isDragActive ? 'border-white/15 hover:border-white/30 hover:bg-white/5' : ''}
            ${uploading ? 'pointer-events-none opacity-60' : ''}
          `}
        >
          <input {...getInputProps()} />
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-900/80 to-dark-800 border border-brand-700/30">
            {uploading
              ? <div className="w-6 h-6 border-2 border-brand-400 border-t-transparent rounded-full animate-spin" />
              : <Satellite className="w-7 h-7 text-brand-400" />
            }
          </div>

          {uploading ? (
            <div className="text-center">
              <p className="text-sm text-slate-300 font-medium">Uploading & analysing...</p>
              <div className="mt-2 w-48 progress-bar">
                <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
              <p className="mt-1 text-xs text-slate-500">{uploadProgress}%</p>
            </div>
          ) : (
            <div className="text-center">
              <p className="text-sm font-semibold text-white">
                {isDragReject ? 'Unsupported file type' : isDragActive ? 'Drop to upload' : label}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Drag & drop or click to select
              </p>
              <p className="mt-0.5 text-xs text-slate-600">
                {ACCEPTED_EXTS.join(', ')} · Max 2 GB
              </p>
            </div>
          )}
        </div>
      )}

      {/* Option 2: Live Satellite Map AOI Trigger */}
      {!uploadResult && mode === 'map' && (
        <div className="p-4 rounded-xl border border-white/10 bg-dark-800/80 space-y-3 text-center">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-br from-teal-900/80 to-dark-800 border border-teal-700/40 flex items-center justify-center">
            <Globe2 className="w-6 h-6 text-teal-400" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Select on Live Satellite Map</h4>
            <p className="text-xs text-slate-400 mt-1">
              Select any region worldwide or choose a preset to fetch live georeferenced satellite imagery.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowMapModal(true)}
            className="btn-primary w-full justify-center text-xs py-2 bg-gradient-to-r from-teal-600 to-brand-600 hover:from-teal-500 hover:to-brand-500 shadow-teal-950/50"
          >
            <Map className="w-3.5 h-3.5" />
            Open Interactive AOI Selector
          </button>
        </div>
      )}

      {/* Upload error */}
      {error && (
        <div className="flex items-start gap-3 p-3 rounded-lg bg-red-900/20 border border-red-700/30">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-red-300 font-medium">Upload Failed</p>
            <p className="text-xs text-red-400 mt-0.5">{error}</p>
          </div>
          <button onClick={clearResult} className="ml-auto text-red-400 hover:text-red-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Success + metadata */}
      {uploadResult && (
        <div className="space-y-3 animate-fade-in">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-emerald-900/20 border border-emerald-700/30">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-emerald-300 font-medium truncate">
                {uploadResult.original_filename}
              </p>
              <p className="text-xs text-emerald-500">
                {formatBytes(uploadResult.metadata?.file_size || 0)} · {uploadResult.detected_mime}
              </p>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <button
                type="button"
                onClick={() => setShowMapModal(true)}
                title="Select a different AOI on the live satellite map"
                className="px-2 py-1 text-xs rounded-md bg-teal-900/60 hover:bg-teal-800/80 text-teal-200 border border-teal-600/40 flex items-center gap-1 transition-colors"
              >
                <Globe2 className="w-3.5 h-3.5" />
                <span>Change AOI</span>
              </button>
              <button
                type="button"
                onClick={clearResult}
                title="Clear image"
                className="p-1.5 text-slate-400 hover:text-white rounded-md hover:bg-white/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {uploadResult.metadata && (
            <MetadataPanel meta={uploadResult.metadata} thumbnail={uploadResult.thumbnail_url} />
          )}
        </div>
      )}

      {/* Full-screen Modal for Live Map AOI Selector rendered directly into document.body */}
      {showMapModal &&
        createPortal(
          <div className="fixed inset-0 z-[99999] flex items-center justify-center p-3 sm:p-6 md:p-8 bg-black/85 backdrop-blur-md animate-fade-in">
            <div className="relative w-full max-w-5xl h-[88vh] max-h-[850px] flex flex-col rounded-2xl overflow-hidden shadow-2xl border border-white/20">
              <MapAoiSelector
                onAoiCaptured={handleAoiCaptured}
                onCancel={() => setShowMapModal(false)}
              />
            </div>
          </div>,
          document.body
        )}
    </div>
  );
}

function MetadataPanel({ meta, thumbnail }: { meta: UploadResult['metadata'] & {}; thumbnail: string | null }) {
  if (!meta) return null;

  const rows = [
    { icon: FileType,  label: 'Format',      value: `${meta.format.toUpperCase()} · ${meta.modality}` },
    { icon: Layers,    label: 'Dimensions',   value: `${meta.width} × ${meta.height} px, ${meta.band_count} band${meta.band_count !== 1 ? 's' : ''}` },
    meta.is_georeferenced && meta.crs
      ? { icon: MapPin, label: 'CRS',         value: meta.crs_authority || meta.crs }
      : { icon: Info,   label: 'CRS',         value: 'Not georeferenced' },
    meta.resolution_m
      ? { icon: Eye,    label: 'Resolution',  value: `~${meta.resolution_m.toFixed(1)} m/pixel` }
      : null,
    meta.acquisition_date
      ? { icon: Calendar, label: 'Acquired',  value: meta.acquisition_date }
      : null,
    meta.sensor
      ? { icon: Satellite, label: 'Sensor',   value: meta.sensor }
      : null,
  ].filter(Boolean);

  return (
    <div className="glass rounded-xl overflow-hidden">
      {/* Thumbnail + quick info */}
      {thumbnail && (
        <div className="relative h-36 bg-dark-900 overflow-hidden">
          <img
            src={`http://localhost:8000${thumbnail}`}
            alt="Satellite image thumbnail"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          <div className="absolute bottom-2 left-3">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${meta.is_georeferenced ? 'bg-emerald-900/80 text-emerald-300' : 'bg-amber-900/80 text-amber-300'}`}>
              {meta.is_georeferenced ? '✓ Georeferenced' : '⚠ No CRS'}
            </span>
          </div>
        </div>
      )}

      {/* Metadata rows */}
      <div className="p-3 space-y-1.5">
        {rows.map((row, i) => row && (
          <div key={i} className="flex items-center gap-2.5">
            <row.icon className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span className="text-xs text-slate-500 w-20 shrink-0">{row.label}</span>
            <span className="text-xs text-slate-300 truncate">{row.value}</span>
          </div>
        ))}
      </div>

      {/* Warnings */}
      {meta.warnings && meta.warnings.length > 0 && (
        <div className="px-3 pb-3 space-y-1">
          {meta.warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-amber-400">
              <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
