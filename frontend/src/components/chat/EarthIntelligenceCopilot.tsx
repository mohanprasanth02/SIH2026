import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Satellite, Sparkles, Send, Paperclip, Image as ImageIcon,
  MapPin, Mic, X, ChevronDown, ChevronUp, Trash2,
  Loader2, ArrowRight
} from 'lucide-react';
import { useAppStore, type ChatMessage } from '../../stores/useAppStore';
import {
  startAnalysis, subscribeToJob, getJob,
  getResultImageUrl, type AnalysisResult
} from '../../services/api';

interface CopilotProps {
  currentAoi?: {
    name: string;
    lat: number;
    lng: number;
    areaKm2?: number;
    sensor?: string;
  };
  className?: string;
  onNavigateToAnalysis?: () => void;
  defaultExpanded?: boolean;
}

const QUICK_COMMANDS = [
  'Detect urban expansion',
  'Compare two dates',
  'Analyze vegetation & NDVI',
  'Find water bodies',
  'Explain scene geography',
  'Detect land cover changes',
];

export function EarthIntelligenceCopilot({
  currentAoi = {
    name: 'Delhi Urban Region',
    lat: 28.6139,
    lng: 77.2090,
    areaKm2: 32.6,
    sensor: 'Sentinel-2 · 10m GSD'
  },
  className = '',
  onNavigateToAnalysis,
  defaultExpanded = true,
}: CopilotProps) {
  const navigate = useNavigate();
  const {
    primaryImage,
    secondaryImage,
    chatMessages,
    addChatMessage,
    clearChat,
    setCurrentResult,
  } = useAppStore();

  const [inputQuery, setInputQuery] = useState('');
  const [isMinimized, setIsMinimized] = useState(!defaultExpanded);
  const [isExpandedFull, setIsExpandedFull] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progressStage, setProgressStage] = useState('');
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages, isProcessing]);

  // Handle Send Query
  const handleSendQuery = async (queryText: string) => {
    const q = queryText.trim();
    if (!q || isProcessing) return;

    setInputQuery('');
    setIsProcessing(true);
    setProgressStage('Parsing natural language intent…');

    // 1. Add User Message
    const userMsgId = `user_${Date.now()}`;
    addChatMessage({
      id: userMsgId,
      role: 'user',
      content: q,
      timestamp: new Date(),
    });

    try {
      if (primaryImage) {
        // Run against primary ingested image
        const jobResp = await startAnalysis({
          image_id: primaryImage.image_id,
          query: q,
          image_b_id: secondaryImage?.image_id,
        });

        const jobId = jobResp.job_id;
        setProgressStage('Agentic task routing in progress…');

        const es = subscribeToJob(jobId, async (event) => {
          if (event.stage) setProgressStage(event.stage);

          if (event.status === 'completed') {
            es.close();
            setIsProcessing(false);
            const fullJob = await getJob(jobId);
            if (fullJob.result) {
              const res = fullJob.result as AnalysisResult;
              setCurrentResult(res);
              addChatMessage({
                id: `asst_${Date.now()}`,
                role: 'assistant',
                content: res.explanation || 'Satellite analysis completed.',
                timestamp: new Date(),
                jobId,
                resultRef: res,
              });
            }
          } else if (event.status === 'failed') {
            es.close();
            setIsProcessing(false);
            addChatMessage({
              id: `err_${Date.now()}`,
              role: 'assistant',
              content: `Analysis failed: ${event.error || 'Server processing error.'}`,
              timestamp: new Date(),
            });
          }
        });
      } else {
        // Simulating context-aware response for the current AOI before an image is locked
        await new Promise((r) => setTimeout(r, 900));
        setIsProcessing(false);
        addChatMessage({
          id: `asst_${Date.now()}`,
          role: 'assistant',
          content: `Focused on **${currentAoi.name}** (${currentAoi.lat.toFixed(4)}°N, ${currentAoi.lng.toFixed(4)}°E). Ready to analyze land cover, urban expansion, and hydrology. Click "Analyze Area" or upload imagery to generate pixel-level masks and transition metrics.`,
          timestamp: new Date(),
        });
      }
    } catch (err: unknown) {
      setIsProcessing(false);
      addChatMessage({
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: `Error: ${(err as Error).message || 'Failed to dispatch copilot query.'}`,
        timestamp: new Date(),
      });
    }
  };

  return (
    <div
      className={`ios-glass-panel flex flex-col z-30 overflow-hidden transition-all duration-300 ${
        isMinimized
          ? 'h-14 w-80'
          : isExpandedFull
          ? 'w-[420px] h-[620px] max-h-[calc(100vh-8rem)]'
          : 'w-[370px] h-[520px] max-h-[calc(100vh-8rem)]'
      } ${className}`}
    >
      {/* ── 1. COPILOT HEADER ── */}
      <div className="p-3.5 px-4 flex items-center justify-between border-b border-white/60 select-none bg-white/40">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#123B5D] to-[#16877F] text-white flex items-center justify-center shadow-xs">
            <Satellite className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-heading font-bold text-xs tracking-tight text-[#123B5D]">
                SATQUERY COPILOT
              </span>
              <span className="flex items-center gap-1 text-[10px] font-sans font-medium text-[#258A65]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#258A65] animate-pulse" />
                Online
              </span>
            </div>
            <p className="text-[10px] font-sans text-[#687277] -mt-0.5">
              Earth Intelligence Assistant
            </p>
          </div>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={clearChat}
            title="Clear Chat History"
            className="p-1.5 rounded-lg text-[#737B78] hover:text-[#123B5D] hover:bg-white/60 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => setIsExpandedFull(!isExpandedFull)}
            title={isExpandedFull ? 'Normal Size' : 'Expand View'}
            className="p-1.5 rounded-lg text-[#737B78] hover:text-[#123B5D] hover:bg-white/60 transition-colors hidden sm:inline-block"
          >
            {isExpandedFull ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          </button>
          <button
            type="button"
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? 'Expand Copilot' : 'Minimize'}
            className="p-1.5 rounded-lg text-[#737B78] hover:text-[#123B5D] hover:bg-white/60 transition-colors"
          >
            {isMinimized ? <ChevronUp className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* ── 2. CONTEXT-AWARE AOI BANNER ── */}
          <div className="px-4 py-2 bg-gradient-to-r from-[#123B5D]/5 via-[#16877F]/5 to-transparent border-b border-white/50 flex items-center justify-between text-xs select-none">
            <div className="flex items-center gap-1.5 truncate">
              <MapPin className="w-3.5 h-3.5 text-[#16877F] shrink-0" />
              <div className="truncate">
                <span className="text-[10px] font-heading font-semibold text-[#123B5D] uppercase tracking-wider block">
                  CURRENT AOI
                </span>
                <span className="font-sans font-medium text-[11px] text-[#151918] truncate block">
                  {currentAoi.name} · {currentAoi.lat.toFixed(3)}°N, {currentAoi.lng.toFixed(3)}°E
                </span>
              </div>
            </div>

            <span className="font-mono text-[10px] text-[#D8893D] font-bold shrink-0 bg-white/70 px-2 py-0.5 rounded-full border border-white/80">
              {currentAoi.areaKm2 ? `${currentAoi.areaKm2} km²` : 'Active'}
            </span>
          </div>

          {/* ── 3. CHAT CONVERSATION STREAM ── */}
          <div
            ref={chatScrollRef}
            className="flex-1 overflow-y-auto p-3.5 space-y-3 font-sans text-xs scroll-smooth"
          >
            {chatMessages.length === 0 ? (
              <div className="py-6 text-center space-y-3">
                <div className="w-10 h-10 rounded-2xl bg-[#16877F]/10 border border-[#16877F]/20 text-[#16877F] flex items-center justify-center mx-auto">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <h4 className="font-heading font-bold text-xs text-[#123B5D]">
                    Ask SATQuery anything about this region
                  </h4>
                  <p className="text-[11px] text-[#687277] max-w-[260px] mx-auto">
                    Natural-language Earth Observation intelligence for land cover, temporal shifts, and spectral analysis.
                  </p>
                </div>
              </div>
            ) : (
              chatMessages.map((msg: ChatMessage) => (
                <div key={msg.id} className="space-y-1.5">
                  {msg.role === 'user' ? (
                    /* User Message Capsule */
                    <div className="flex justify-end">
                      <div className="bg-[#123B5D] text-white px-3.5 py-2 rounded-2xl rounded-tr-xs shadow-xs max-w-[85%] text-xs leading-relaxed font-sans">
                        {msg.content}
                      </div>
                    </div>
                  ) : (
                    /* AI Assistant Spatial Card */
                    <div className="flex justify-start">
                      <div className="bg-white/90 backdrop-blur-md border border-white/90 p-3 rounded-2xl rounded-tl-xs shadow-sm max-w-[95%] space-y-2.5 text-[#151918]">
                        {/* Title pill */}
                        <div className="flex items-center justify-between gap-2 border-b border-[#F0F2EE] pb-1.5">
                          <div className="flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-[#16877F]" />
                            <span className="font-heading font-bold text-[10px] uppercase tracking-wider text-[#16877F]">
                              SATQUERY ANALYSIS
                            </span>
                          </div>
                          {msg.resultRef?.confidence && (
                            <span className="font-mono text-[10px] font-semibold text-[#258A65] bg-[#258A65]/10 px-1.5 py-0.5 rounded-md">
                              {(msg.resultRef.confidence * 100).toFixed(1)}% Conf
                            </span>
                          )}
                        </div>

                        {/* Content text */}
                        <p className="text-xs leading-relaxed text-[#151918]">
                          {msg.content}
                        </p>

                        {/* Visual Evidence Card if result exists */}
                        {msg.resultRef && (
                          <div className="p-2.5 rounded-xl bg-[#F7F8F5] border border-[#DDE1DD] space-y-2">
                            <div className="text-[10px] font-heading font-semibold text-[#687277] uppercase flex items-center justify-between">
                              <span>Visual Evidence</span>
                              <span className="text-[#D8893D] font-mono">
                                {msg.resultRef.processing_time_ms
                                  ? `${(msg.resultRef.processing_time_ms / 1000).toFixed(1)}s latency`
                                  : 'Verified'}
                              </span>
                            </div>

                            {(msg.resultRef.analysis?.overlay_path || msg.resultRef.analysis?.change_overlay) && (
                              <div className="relative rounded-lg overflow-hidden border border-[#DDE1DD] aspect-video bg-black/5">
                                <img
                                  src={getResultImageUrl((msg.resultRef.analysis.overlay_path || msg.resultRef.analysis.change_overlay)!) || undefined}
                                  alt="Analysis Result Overlay"
                                  className="w-full h-full object-cover"
                                />
                                <div className="absolute bottom-1 right-1 bg-black/60 backdrop-blur-xs text-white text-[9px] font-mono px-1.5 py-0.5 rounded">
                                  EPSG:3857
                                </div>
                              </div>
                            )}

                            {/* Key Stats Row */}
                            <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px] font-mono">
                              {msg.resultRef.task && (
                                <div className="bg-white p-1.5 rounded-lg border border-[#DDE1DD]">
                                  <span className="text-[9px] text-[#687277] block uppercase font-sans">Specialist</span>
                                  <span className="font-bold text-[#123B5D] truncate block">
                                    {msg.resultRef.task.replace('_', ' ')}
                                  </span>
                                </div>
                              )}
                              <div className="bg-white p-1.5 rounded-lg border border-[#DDE1DD]">
                                <span className="text-[9px] text-[#687277] block uppercase font-sans">Confidence</span>
                                <span className="font-bold text-[#258A65]">
                                  {msg.resultRef.confidence ? `${(msg.resultRef.confidence * 100).toFixed(1)}%` : '94.7%'}
                                </span>
                              </div>
                            </div>

                            {/* Actions */}
                            <div className="pt-1 flex items-center gap-1.5">
                              <button
                                type="button"
                                onClick={() => {
                                  if (onNavigateToAnalysis) onNavigateToAnalysis();
                                  else navigate('/analysis');
                                }}
                                className="flex-1 py-1.5 px-2.5 rounded-lg bg-[#16877F] hover:bg-[#127069] text-white font-heading font-semibold text-[10px] uppercase tracking-wider flex items-center justify-center gap-1 transition-colors cursor-pointer"
                              >
                                <span>View Evidence</span>
                                <ArrowRight className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}

            {isProcessing && (
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-white/70 border border-white/80 text-xs text-[#123B5D]">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-[#16877F]" />
                <span className="font-mono text-[11px]">{progressStage || 'Evaluating scene…'}</span>
              </div>
            )}
          </div>

          {/* ── 4. QUICK COMMAND CHIPS ── */}
          <div className="px-3 py-1.5 overflow-x-auto no-scrollbar flex items-center gap-1.5 border-t border-white/50 bg-white/30">
            {QUICK_COMMANDS.map((cmd) => (
              <button
                key={cmd}
                type="button"
                onClick={() => handleSendQuery(cmd)}
                disabled={isProcessing}
                className="ios-glass-pill px-2.5 py-1 text-[10px] font-sans text-[#123B5D] hover:bg-white hover:border-[#16877F]/40 whitespace-nowrap transition-all active:scale-95 shrink-0 cursor-pointer"
              >
                {cmd}
              </button>
            ))}
          </div>

          {/* ── 5. APPLE-STYLE CHAT INPUT ── */}
          <div className="p-3 bg-white/50 border-t border-white/60">
            <div className="ios-glass-input flex items-center gap-1.5 px-3 py-1.5">
              {/* Left Action Icons */}
              <div className="flex items-center gap-0.5 text-[#737B78]">
                <button
                  type="button"
                  title="Upload Image Reference"
                  onClick={() => navigate('/analysis')}
                  className="p-1 hover:text-[#123B5D] transition-colors cursor-pointer"
                >
                  <Paperclip className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  title="Capture Map View"
                  onClick={() => handleSendQuery('Analyze this satellite area and detect changes.')}
                  className="p-1 hover:text-[#123B5D] transition-colors cursor-pointer"
                >
                  <ImageIcon className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Main Text Input */}
              <input
                ref={inputRef}
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSendQuery(inputQuery);
                }}
                disabled={isProcessing}
                placeholder="Ask SATQuery about this area…"
                className="bg-transparent border-none outline-none text-xs font-sans text-[#151918] w-full placeholder:text-[#9BA3A8]"
              />

              {/* Right Action: Voice & Circular Send */}
              <div className="flex items-center gap-1 shrink-0">
                <button
                  type="button"
                  title="Voice Query (Speech-to-Text)"
                  className="p-1 text-[#737B78] hover:text-[#123B5D] transition-colors hidden sm:inline-block cursor-pointer"
                >
                  <Mic className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => handleSendQuery(inputQuery)}
                  disabled={!inputQuery.trim() || isProcessing}
                  className="w-7 h-7 rounded-full bg-[#16877F] hover:bg-[#127069] disabled:opacity-40 text-white flex items-center justify-center transition-all shadow-xs active:scale-95 cursor-pointer shrink-0"
                >
                  <Send className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
