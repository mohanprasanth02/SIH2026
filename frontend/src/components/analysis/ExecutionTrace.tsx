import { CheckCircle2, XCircle, Loader2, Clock, Cpu, Wrench } from 'lucide-react';
import type { ExecutionStep } from '../../services/api';
import { formatMs } from '../../utils/cn';

interface Props {
  steps: ExecutionStep[];
}

export function ExecutionTrace({ steps }: Props) {
  if (!steps || steps.length === 0) {
    return <p className="text-xs text-slate-500 italic">No execution steps recorded.</p>;
  }

  return (
    <div className="space-y-2">
      {steps.map((step, i) => (
        <div key={i} className="flex gap-3 group">
          {/* Status icon */}
          <div className="flex flex-col items-center">
            <div className="mt-0.5">
              {step.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
              {step.status === 'failed'    && <XCircle className="w-4 h-4 text-red-400" />}
              {step.status === 'running'   && <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />}
              {step.status === 'skipped'   && <div className="w-4 h-4 rounded-full border border-slate-600" />}
            </div>
            {i < steps.length - 1 && (
              <div className="w-px flex-1 bg-white/8 mt-1 mb-0" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 pb-3">
            <div className="flex items-start justify-between gap-2">
              <p className="text-xs font-medium text-slate-200">{step.step_name}</p>
              {step.duration_ms != null && (
                <span className="text-[10px] text-slate-600 flex items-center gap-1 shrink-0">
                  <Clock className="w-2.5 h-2.5" />
                  {formatMs(step.duration_ms)}
                </span>
              )}
            </div>

            {/* Tool / Model badges */}
            <div className="flex gap-1.5 mt-1 flex-wrap">
              {step.tool && (
                <span className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-dark-700 text-slate-400 border border-white/5">
                  <Wrench className="w-2.5 h-2.5" />
                  {step.tool}
                </span>
              )}
              {step.model && (
                <span className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-dark-700 text-slate-400 border border-white/5">
                  <Cpu className="w-2.5 h-2.5" />
                  {step.model}
                </span>
              )}
            </div>

            {/* Output summary */}
            {step.output_summary && (
              <p className="mt-1 text-[10px] text-slate-500 leading-relaxed">{step.output_summary}</p>
            )}

            {/* Error */}
            {step.error && (
              <p className="mt-1 text-[10px] text-red-400 leading-relaxed">{step.error}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
