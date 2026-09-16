import { ShieldCheck, AlertTriangle, Cpu, Clock, Database } from 'lucide-react';
import type { AnalysisResult } from '../../services/api';
import { formatMs } from '../../utils/cn';
import { VisualEvidenceCard } from './VisualEvidenceCard';

interface Props {
  result: AnalysisResult;
}

export function EvidencePanel({ result }: Props) {
  const { analysis, metadata, processing_time_ms, tools_used } = result;

  const evidence: string[] = [];
  if (analysis.class_statistics) evidence.push('Land cover segmentation mask');
  if (analysis.class_statistics?.some((s) => s.area_km2 != null)) evidence.push('Spatial area calculations');
  if (metadata?.is_georeferenced) evidence.push('GeoTIFF CRS metadata');
  if (analysis.spectral_indices?.ndvi?.available) evidence.push('NDVI spectral index');
  if (analysis.spectral_indices?.ndwi?.available) evidence.push('NDWI spectral index');
  if (analysis.change_percentage != null) evidence.push('Change detection mask');
  if (analysis.sar_analysis) evidence.push('SAR backscatter analysis');

  const modelInfo = analysis.class_statistics?.[0] || null;

  return (
    <div className="space-y-4">
      {/* Visual evidence preview */}
      <VisualEvidenceCard result={result} />
      {/* Evidence items */}
      {evidence.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">Evidence Sources</p>
          <div className="space-y-1.5">
            {evidence.map((e, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-slate-300">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>{e}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Model provenance */}
      {modelInfo && (
        <div>
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">Model</p>
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-dark-700 border border-white/8">
            <Cpu className="w-4 h-4 text-brand-400 shrink-0" />
            <div className="min-w-0">
              <p className="text-xs font-medium text-white truncate">{modelInfo.model_name || 'Unknown'}</p>
              <p className="text-[10px] text-slate-500">{modelInfo.model_version || ''}</p>
            </div>
            <div className="ml-auto text-right">
              {modelInfo.confidence != null
                ? <p className="text-xs text-emerald-400">{(modelInfo.confidence * 100).toFixed(0)}% conf</p>
                : <p className="text-[10px] text-slate-600">Confidence N/A</p>
              }
            </div>
          </div>
        </div>
      )}

      {/* Spectral indices */}
      {analysis.spectral_indices && (
        <div>
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">Spectral Indices</p>
          <div className="space-y-1.5">
            {Object.entries(analysis.spectral_indices).map(([key, val]) => (
              <div key={key} className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full shrink-0 ${val.available ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                <span className="text-xs text-slate-400 uppercase font-mono w-12">{key}</span>
                {val.available
                  ? <span className="text-xs text-slate-300">mean = {val.mean?.toFixed(3)}</span>
                  : <span className="text-xs text-slate-600 truncate">{val.reason}</span>
                }
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-2">Data Quality Warnings</p>
          <div className="space-y-1.5">
            {result.warnings.map((w, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                <span>{w}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timing */}
      <div className="flex items-center gap-2 text-xs text-slate-500 pt-1">
        <Clock className="w-3.5 h-3.5" />
        <span>Processed in {formatMs(processing_time_ms)}</span>
        {tools_used?.length > 0 && (
          <>
            <span className="text-slate-700">·</span>
            <Database className="w-3.5 h-3.5" />
            <span>{tools_used.length} tool{tools_used.length !== 1 ? 's' : ''} used</span>
          </>
        )}
      </div>
    </div>
  );
}
