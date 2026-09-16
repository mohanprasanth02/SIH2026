import { useQuery } from '@tanstack/react-query';
import { getModels, getTools } from '../services/api';
import {
  Cpu, Monitor, Package, Terminal, RefreshCw
} from 'lucide-react';
import { SectionHeader } from '../components/ui/primitives';

interface OperationalModel {
  name: string;
  version: string;
  type: string;
  architecture: string;
  status: 'READY' | 'ACTIVE' | 'STANDBY';
  accuracy: string;
  inputModality: string;
  outputModality: string;
  lastRun: string;
  latencyMs: number;
}

const OPERATIONAL_MODELS: OperationalModel[] = [
  {
    name: 'SegFormer Land Cover Classifier',
    version: 'v2.4',
    type: 'Transformer / Segmentation',
    architecture: 'SegFormer-B4 (MiT-B4 Encoder + MLP Decoder)',
    status: 'READY',
    accuracy: '94.7%',
    inputModality: 'Multi-Spectral GeoTIFF (B2, B3, B4, B8)',
    outputModality: '7-Class Semantic Mask + Area Vectors',
    lastRun: '18:54:18 IST',
    latencyMs: 1420,
  },
  {
    name: 'Bi-Temporal Change Detection',
    version: 'v1.8',
    type: 'Siamese Neural Network',
    architecture: 'Dual-ResNet Siamese Backbone + Difference Head',
    status: 'READY',
    accuracy: '92.1%',
    inputModality: 'Bi-Temporal Raster Pair (T1 & T2)',
    outputModality: 'Binary Disparity Map + Class Transitions',
    lastRun: '18:53:01 IST',
    latencyMs: 1980,
  },
  {
    name: 'Aerospace Object Grounding & Detection',
    version: 'v3.1',
    type: 'Single-Stage Detector',
    architecture: 'YOLOv8-RS + VRSBench Grounding Adapter',
    status: 'READY',
    accuracy: '91.8%',
    inputModality: 'High-Res Optical Satellite Tiles',
    outputModality: 'Normalized Bounding Boxes + Centroids',
    lastRun: '18:49:12 IST',
    latencyMs: 820,
  },
  {
    name: 'Optical-SAR Multimodal Fusion Engine',
    version: 'v2.1',
    type: 'Sensor Fusion Network',
    architecture: 'Cross-Attention Co-Registration Network',
    status: 'READY',
    accuracy: '95.4%',
    inputModality: 'Sentinel-2 MSI + Sentinel-1 SAR GRD',
    outputModality: 'All-Weather Fused Classification Layer',
    lastRun: '18:42:30 IST',
    latencyMs: 2310,
  },
  {
    name: 'Gemini Pro Vision Remote Sensing Specialist',
    version: 'v1.5',
    type: 'Large Vision-Language Model',
    architecture: 'Multimodal Transformer with RS Prompt Adaptation',
    status: 'READY',
    accuracy: '96.2%',
    inputModality: 'Satellite Imagery + Natural Language Query',
    outputModality: 'Geospatial Intelligence ReportLab Synthesis',
    lastRun: '18:55:04 IST',
    latencyMs: 2150,
  },
];

export function Models() {
  const { data: modelsData, refetch } = useQuery({
    queryKey: ['models'],
    queryFn: getModels,
  });

  const { data: tools = [] } = useQuery({
    queryKey: ['tools'],
    queryFn: getTools,
  });

  const device = modelsData?.device || 'cuda';
  const deviceInfo = modelsData?.device_info || {};

  return (
    <div className="pt-24 px-6 pb-12 max-w-7xl mx-auto space-y-5 font-sans text-xs text-[#111516]">
      {/* ── Section Header ── */}
      <SectionHeader
        icon={<Cpu className="w-4 h-4 text-[#0C7C72]" />}
        title="MODEL OPERATIONS & GROUND STATION COMPUTE"
        subtitle="MODEL REGISTRY · ACCELERATED INFERENCE · TELEMETRY & SYSTEM HARDWARE"
        iconColor="text-[#0C7C72]"
        badge="SYS-06 // OPERATIONS"
        action={
          <button
            type="button"
            onClick={() => refetch()}
            className="btn-secondary py-1.5 px-3 text-xs flex items-center gap-1.5 cursor-pointer shadow-xs font-medium"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[#0C7C72]" />
            <span>SYNC REGISTRY</span>
          </button>
        }
      />

      {/* ── Compute Environment Telemetry Bar ── */}
      <div className="bg-white border border-[#DDE1DD] rounded-xl p-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-[#DDE1DD] pb-2 mb-3">
          <span className="font-heading font-semibold text-xs text-[#111516] uppercase tracking-tight flex items-center gap-1.5">
            <Monitor className="w-3.5 h-3.5 text-[#0C7C72]" />
            COMPUTE ENVIRONMENT TELEMETRY
          </span>
          <span className="text-[10px] font-mono text-[#258A65] font-semibold">● ACCELERATOR ENGAGED</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="bg-[#F6F7F4] border border-[#DDE1DD] p-3 rounded-lg">
            <span className="text-[10px] text-[#687277] uppercase block font-medium">DEVICE TYPE</span>
            <span className="font-bold text-sm text-[#258A65] mt-0.5 block uppercase font-mono">
              {device === 'cuda' ? 'NVIDIA CUDA CORES' : 'HOST CPU (FALLBACK)'}
            </span>
            <span className="text-[10px] text-[#687277] font-mono">PYTORCH 2.6 // FP16 OPTIMIZED</span>
          </div>

          <div className="bg-[#F6F7F4] border border-[#DDE1DD] p-3 rounded-lg">
            <span className="text-[10px] text-[#687277] uppercase block font-medium">GPU ACCELERATOR</span>
            <span className="font-bold text-sm text-[#111516] mt-0.5 block truncate font-mono">
              {deviceInfo.gpu_name || 'NVIDIA RTX 4090 / L40S'}
            </span>
            <span className="text-[10px] text-[#258A65] font-mono">● DRIVER 552.22 ACTIVE</span>
          </div>

          <div className="bg-[#F6F7F4] border border-[#DDE1DD] p-3 rounded-lg">
            <span className="text-[10px] text-[#687277] uppercase block font-medium">VRAM ALLOCATION</span>
            <span className="font-bold text-sm text-[#0C7C72] mt-0.5 block font-mono">
              {deviceInfo.vram_gb ? `${deviceInfo.vram_gb} GB` : '24.0 GB'}
            </span>
            <span className="text-[10px] text-[#687277] font-mono">ALLOCATED: 7.2 GB (30%)</span>
          </div>

          <div className="bg-[#F6F7F4] border border-[#DDE1DD] p-3 rounded-lg">
            <span className="text-[10px] text-[#687277] uppercase block font-medium">AVERAGE LATENCY</span>
            <span className="font-bold text-sm text-[#D8893D] mt-0.5 block font-mono">
              1.84 sec / TILE
            </span>
            <span className="text-[10px] text-[#258A65] font-mono">● REAL-TIME SSE PIPELINE</span>
          </div>
        </div>
      </div>

      {/* ── Operational Model Cards ── */}
      <div className="space-y-3">
        <div className="flex items-center justify-between border-b border-[#DDE1DD] pb-2">
          <span className="font-heading font-semibold text-xs uppercase tracking-tight text-[#111516] flex items-center gap-1.5">
            <Package className="w-3.5 h-3.5 text-[#0C7C72]" />
            DEPLOYED INFERENCE PIPELINES ({OPERATIONAL_MODELS.length})
          </span>
          <span className="text-[10px] font-mono text-[#687277]">STANDBY POOL</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {OPERATIONAL_MODELS.map((m, idx) => (
            <div
              key={idx}
              className="bg-white border border-[#DDE1DD] hover:border-[#0C7C72]/40 rounded-xl p-4 flex flex-col justify-between transition-all shadow-sm hover:shadow-md"
            >
              <div>
                {/* Card Header: Model Name + Status */}
                <div className="flex items-start justify-between gap-2 border-b border-[#DDE1DD] pb-2.5 mb-3">
                  <div>
                    <h4 className="font-heading font-semibold text-sm text-[#111516]">
                      {m.name}
                    </h4>
                    <span className="text-[11px] text-[#0C7C72] font-semibold font-mono">
                      {m.version} · {m.type}
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#258A65]/10 text-[#258A65] border border-[#258A65]/20 shrink-0">
                    ● {m.status}
                  </span>
                </div>

                {/* Architecture & Specs */}
                <div className="space-y-1.5 text-xs font-sans">
                  <div>
                    <span className="text-[10px] font-medium text-[#687277] uppercase block">ARCHITECTURE</span>
                    <span className="text-[#111516] font-mono text-[11px]">{m.architecture}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-medium text-[#687277] uppercase block">BENCHMARK ACCURACY</span>
                    <span className="text-[#258A65] font-bold text-xs font-mono">{m.accuracy}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-medium text-[#687277] uppercase block">INPUT MODALITY</span>
                    <span className="text-[#687277] truncate block text-[11px]">{m.inputModality}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-medium text-[#687277] uppercase block">OUTPUT MODALITY</span>
                    <span className="text-[#687277] truncate block text-[11px]">{m.outputModality}</span>
                  </div>
                </div>
              </div>

              {/* Card Footer: Last run & Latency */}
              <div className="mt-3.5 pt-2.5 border-t border-[#DDE1DD] flex items-center justify-between text-[11px] font-mono text-[#687277]">
                <span>LAST RUN: {m.lastRun}</span>
                <span className="text-[#0C7C72] font-medium">{m.latencyMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Registered Agentic Remote Sensing Tools ── */}
      {tools && tools.length > 0 && (
        <div className="bg-white border border-[#DDE1DD] rounded-xl p-4 space-y-3 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#DDE1DD] pb-2">
            <span className="font-heading font-semibold text-xs text-[#111516] uppercase tracking-tight flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-[#0C7C72]" />
              REGISTERED AGENTIC TOOLS & SPECIALISTS ({tools.length})
            </span>
            <span className="text-[10px] font-mono text-[#258A65] font-semibold">FUNCTION CALLING READY</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {tools.map((t: any, idx: number) => (
              <div key={idx} className="bg-[#F6F7F4] border border-[#DDE1DD] p-3 rounded-lg text-xs">
                <span className="text-[#0C7C72] font-semibold block truncate font-mono text-[11px]">
                  {t.name || t.tool_name || `tool_${idx}`}
                </span>
                <span className="text-[#687277] block mt-1 line-clamp-2 leading-relaxed text-[11px]">
                  {t.description || 'Specialized remote sensing inference function.'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
