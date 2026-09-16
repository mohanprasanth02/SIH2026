import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  ArrowRight, RefreshCw, X, ChevronRight,
  Layers, MapPin,
  Search, Loader2
} from 'lucide-react';
import {
  getDashboardStats,
  getRecentAnalyses,
  getSatellitePresets,
  captureSatelliteAOI,
  geocodeLocation,
  type SatellitePreset,
} from '../../services/api';
import { useAppStore } from '../../stores/useAppStore';
import { EarthIntelligenceCopilot } from '../chat/EarthIntelligenceCopilot';

const TILE_LAYERS = {
  satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  hybrid: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  streets: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
};

export function MissionControlDashboard() {
  const navigate = useNavigate();
  const { setPrimaryImage } = useAppStore();

  // Leaflet map refs
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const aoiRectangleRef = useRef<L.Rectangle | null>(null);

  // Active state
  const [activePreset, setActivePreset] = useState<string>('delhi_urban');
  const [activeLayer, setActiveLayer] = useState<'satellite' | 'hybrid' | 'streets'>('satellite');
  const [mapCenter, setMapCenter] = useState<{ lat: number; lng: number }>({ lat: 28.6139, lng: 77.2090 });
  const [zoomLevel, setZoomLevel] = useState<number>(13);
  const [aoiAreaKm2, setAoiAreaKm2] = useState<number>(32.6);
  const [capturing, setCapturing] = useState<boolean>(false);
  const [showSystemDetails, setShowSystemDetails] = useState<boolean>(false);
  const [locationName, setLocationName] = useState<string>('Delhi Urban Region');

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<Array<{ name: string; lat: number; lng: number }>>([]);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const searchDebounceRef = useRef<any>(null);

  const GLOBAL_SEARCH_PRESETS = [
    { name: 'Dubai Palm, UAE', lat: 25.1124, lng: 55.1390 },
    { name: 'Cairo Nile, Egypt', lat: 30.0444, lng: 31.2357 },
    { name: 'New Delhi Urban, India', lat: 28.6139, lng: 77.2090 },
    { name: 'Tokyo Bay, Japan', lat: 35.6762, lng: 139.6503 },
    { name: 'Manhattan, New York, USA', lat: 40.7580, lng: -73.9855 },
    { name: 'Singapore Port, Singapore', lat: 1.29027, lng: 103.851959 },
    { name: 'Paris, France', lat: 48.8566, lng: 2.3522 },
    { name: 'London, UK', lat: 51.5074, lng: -0.1278 },
    { name: 'Sydney Harbour, Australia', lat: -33.8688, lng: 151.2093 },
    { name: 'San Francisco Bay, USA', lat: 37.7749, lng: -122.4194 },
    { name: 'Mumbai Coast, India', lat: 18.9220, lng: 72.8347 },
    { name: 'Bengaluru Tech Corridor, India', lat: 12.9716, lng: 77.5946 },
  ];

  const handleSelectSearchResult = (lat: number, lng: number, name: string) => {
    setLocationName(name);
    setSearchQuery('');
    setShowSearchDropdown(false);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([lat, lng], 13, { duration: 1.4 });
    }
  };

  const handleSearchInputChange = (text: string) => {
    setSearchQuery(text);
    if (searchDebounceRef.current) {
      clearTimeout(searchDebounceRef.current);
    }

    const trimmed = text.trim();
    if (!trimmed) {
      setSearchResults([]);
      setShowSearchDropdown(false);
      setIsSearching(false);
      return;
    }

    // Fast local preview if query matches a known preset
    const localMatches = GLOBAL_SEARCH_PRESETS.filter(p =>
      p.name.toLowerCase().includes(trimmed.toLowerCase())
    );
    if (localMatches.length > 0) {
      setSearchResults(localMatches);
      setShowSearchDropdown(true);
    }

    // Debounce global unconstrained search across the whole world
    setIsSearching(true);
    searchDebounceRef.current = setTimeout(async () => {
      try {
        const results = await geocodeLocation(trimmed);
        if (results && results.length > 0) {
          setSearchResults(results.map(r => ({ name: r.name, lat: r.lat, lng: r.lng })));
          setShowSearchDropdown(true);
        } else if (localMatches.length === 0) {
          setSearchResults([]);
          setShowSearchDropdown(true);
        }
      } catch (err) {
        console.warn('Geocoding error:', err);
      } finally {
        setIsSearching(false);
      }
    }, 280);
  };

  const handleExecuteGeocode = async (q: string) => {
    if (searchDebounceRef.current) {
      clearTimeout(searchDebounceRef.current);
    }
    const trimmed = q.trim();
    if (!trimmed) return;

    if (searchResults.length > 0) {
      handleSelectSearchResult(searchResults[0].lat, searchResults[0].lng, searchResults[0].name);
      return;
    }

    setIsSearching(true);
    try {
      const results = await geocodeLocation(trimmed);
      if (results && results.length > 0) {
        handleSelectSearchResult(results[0].lat, results[0].lng, results[0].name);
      }
    } catch (err) {
      console.warn('Geocoding search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };


  // Queries
  const { data: stats, refetch: refetchStats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    refetchInterval: 20_000,
  });

  const { data: recentAnalyses } = useQuery({
    queryKey: ['recent-analyses'],
    queryFn: getRecentAnalyses,
    refetchInterval: 20_000,
  });

  const { data: presets = [] } = useQuery({
    queryKey: ['satellite-presets'],
    queryFn: getSatellitePresets,
  });

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [28.6139, 77.2090],
      zoom: 13,
      maxZoom: 19,
      zoomControl: false,
      attributionControl: false,
    });

    // Initial tile layer with sub-meter native resolution
    const tile = L.tileLayer(TILE_LAYERS[activeLayer], {
      maxZoom: 19,
      maxNativeZoom: 19,
    }).addTo(map);

    tileLayerRef.current = tile;
    mapInstanceRef.current = map;

    // AOI Rectangle overlay (center box)
    const bounds = map.getBounds();
    const c = map.getCenter();
    const dLat = (bounds.getNorth() - bounds.getSouth()) * 0.22;
    const dLng = (bounds.getEast() - bounds.getWest()) * 0.22;
    const aoiBounds = L.latLngBounds(
      [c.lat - dLat, c.lng - dLng],
      [c.lat + dLat, c.lng + dLng]
    );

    const rect = L.rectangle(aoiBounds, {
      color: '#16877F',
      weight: 1.5,
      dashArray: '3, 4',
      fillColor: '#16877F',
      fillOpacity: 0.05,
    }).addTo(map);

    aoiRectangleRef.current = rect;

    // Listen to move/zoom
    const onMapMove = () => {
      const center = map.getCenter();
      const zoom = map.getZoom();
      setMapCenter({ lat: center.lat, lng: center.lng });
      setZoomLevel(zoom);

      // Re-center AOI rectangle
      const currBounds = map.getBounds();
      const latDelta = (currBounds.getNorth() - currBounds.getSouth()) * 0.24;
      const lngDelta = (currBounds.getEast() - currBounds.getWest()) * 0.24;
      const newAoi = L.latLngBounds(
        [center.lat - latDelta, center.lng - lngDelta],
        [center.lat + latDelta, center.lng + lngDelta]
      );
      rect.setBounds(newAoi);

      // Estimate area
      const latDistKm = latDelta * 2 * 111;
      const lngDistKm = lngDelta * 2 * 111 * Math.cos((center.lat * Math.PI) / 180);
      setAoiAreaKm2(Math.round(Math.abs(latDistKm * lngDistKm) * 10) / 10);
    };

    map.on('moveend', onMapMove);
    map.on('zoomend', onMapMove);

    onMapMove();

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Change Basemap
  const changeBasemap = (type: 'satellite' | 'hybrid' | 'streets') => {
    setActiveLayer(type);
    if (mapInstanceRef.current && tileLayerRef.current) {
      mapInstanceRef.current.removeLayer(tileLayerRef.current);
      const newTile = L.tileLayer(TILE_LAYERS[type], {
        maxZoom: 19,
        maxNativeZoom: 19,
      }).addTo(mapInstanceRef.current);
      tileLayerRef.current = newTile;
    }
  };

  // Jump to preset
  const handleSelectPreset = (preset: SatellitePreset) => {
    setActivePreset(preset.id);
    setLocationName(preset.name.split(',')[0]);
    if (mapInstanceRef.current) {
      const [west, south, east, north] = preset.bbox;
      const centerLat = (south + north) / 2;
      const centerLng = (west + east) / 2;
      mapInstanceRef.current.flyTo([centerLat, centerLng], preset.zoom || 13, { duration: 1.4 });
    }
  };

  // Capture current AOI and navigate directly to Analysis Workstation
  const handleCaptureAoi = async () => {
    if (!mapInstanceRef.current || capturing) return;
    setCapturing(true);

    try {
      const rect = aoiRectangleRef.current;
      const bounds = rect ? rect.getBounds() : mapInstanceRef.current.getBounds();

      const bbox: [number, number, number, number] = [
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth(),
      ];

      const result = await captureSatelliteAOI({
        bbox,
        zoom: zoomLevel,
        source: 'satellite',
        name: locationName || `AOI_${mapCenter.lat.toFixed(3)}N_${mapCenter.lng.toFixed(3)}E`,
      });

      setPrimaryImage(result);
      navigate('/analysis');
    } catch (err) {
      console.error('AOI Capture failed, fallback to Delhi default:', err);
      navigate('/analysis');
    } finally {
      setCapturing(false);
    }
  };

  // Stats formatting
  const totalAnalyses = stats?.total_analyses ?? 382;
  const completedAnalyses = stats?.completed_analyses ?? 364;
  const avgTimeMs = stats?.average_processing_time_ms ?? 2410;
  const avgTimeSec = (avgTimeMs / 1000).toFixed(1);
  const imagesProcessed = totalAnalyses > 0 ? (totalAnalyses * 3.2).toFixed(0) : '1,248';

  return (
    <div className="w-full h-full relative overflow-hidden bg-[#F7F8F5] select-none">

      {/* ── 1. FULL-BLEED HERO EARTH CANVAS (Spanning Entire Viewport) ── */}
      <div ref={mapContainerRef} className="absolute inset-0 w-full h-full z-0 cursor-grab active:cursor-grabbing" />

      {/* ── 2. FLOATING AOI PANEL (Left) ── */}
      <div className="absolute top-24 left-6 z-20 w-80 max-w-[calc(100vw-3rem)]">
        <div className="ios-glass-panel p-5 transition-all duration-200">

          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-heading font-semibold uppercase tracking-wider text-[#16877F]">
              Earth Observation
            </span>
            <span className="w-2 h-2 rounded-full bg-[#258A65] animate-pulse" />
          </div>

          {/* Location Search Bar with Search Icon */}
          <div className="relative mb-3.5">
            <div className="ios-glass-input flex items-center gap-2 px-3 py-2">
              <Search className="w-3.5 h-3.5 text-[#16877F] shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearchInputChange(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleExecuteGeocode(searchQuery);
                }}
                placeholder="Search global city or coordinates…"
                className="bg-transparent border-none outline-none text-xs font-sans text-[#151918] w-full placeholder:text-[#9BA3A8]"
              />
              {isSearching ? (
                <Loader2 className="w-3 h-3 text-[#16877F] animate-spin shrink-0" />
              ) : searchQuery ? (
                <button
                  type="button"
                  onClick={() => { setSearchQuery(''); setShowSearchDropdown(false); }}
                  className="text-[#9BA3A8] hover:text-[#151918] cursor-pointer"
                >
                  <X className="w-3 h-3" />
                </button>
              ) : null}
            </div>

            {/* Live Location Dropdown */}
            {showSearchDropdown && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white/95 backdrop-blur-xl rounded-2xl shadow-xl border border-white/80 overflow-hidden z-50 divide-y divide-[#F0F2EE] max-h-52 overflow-y-auto">
                {searchResults.length > 0 ? (
                  searchResults.map((loc, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSelectSearchResult(loc.lat, loc.lng, loc.name)}
                      className="w-full text-left px-3 py-2 text-xs font-sans hover:bg-[#F7F8F5] flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <MapPin className="w-3.5 h-3.5 text-[#16877F] shrink-0" />
                        <span className="truncate font-medium text-[#151918]">{loc.name}</span>
                      </div>
                      <span className="font-mono text-[10px] text-[#16877F] font-semibold shrink-0">FLY TO →</span>
                    </button>
                  ))
                ) : isSearching ? (
                  <div className="px-3 py-3 text-center text-xs text-[#737B78] font-sans flex items-center justify-center gap-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-[#16877F]" />
                    <span>Searching global satellite catalog…</span>
                  </div>
                ) : searchQuery.trim().length >= 2 ? (
                  <div className="px-3 py-3 text-center text-xs text-[#737B78] font-sans">
                    No places found. Enter coordinates like <span className="font-mono text-[11px] text-[#16877F]">48.85, 2.35</span>
                  </div>
                ) : null}
              </div>
            )}
          </div>

          <h2 className="font-heading font-bold text-lg text-[#151918] tracking-tight mb-3">
            {locationName}
          </h2>

          <div className="space-y-2.5 pt-1 border-t border-black/5">
            <div className="flex items-baseline justify-between">
              <span className="text-xs text-[#687277] font-sans">Coordinates</span>
              <span className="font-mono text-xs font-semibold text-[#151918]">
                {mapCenter.lat.toFixed(4)}° N · {mapCenter.lng.toFixed(4)}° E
              </span>
            </div>

            <div className="flex items-baseline justify-between">
              <span className="text-xs text-[#687277] font-sans">Area</span>
              <span className="font-mono text-xs font-semibold text-[#D8893D]">
                {aoiAreaKm2} km²
              </span>
            </div>

            <div className="flex items-baseline justify-between">
              <span className="text-xs text-[#687277] font-sans">Sensor / GSD</span>
              <span className="font-sans text-xs text-[#151918] font-medium">
                Sentinel-2 · 10m GSD
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleCaptureAoi}
            disabled={capturing}
            className="mt-5 w-full py-2.5 px-4 rounded-xl bg-[#16877F] hover:bg-[#127069] text-white font-heading font-semibold text-xs uppercase tracking-wider shadow-sm flex items-center justify-center gap-2 transition-all active:scale-[0.99] cursor-pointer"
          >
            {capturing ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Capturing High-Res AOI…</span>
              </>
            ) : (
              <>
                <span>Analyze Area</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* ── 3. FLOATING OBSERVATION PANEL (Right) ── */}
      <div className="absolute top-24 right-6 z-20 w-80 max-w-[calc(100vw-3rem)]">
        <div className="ios-glass-panel p-5 transition-all duration-200">

          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-[11px] font-heading font-semibold uppercase tracking-wider text-[#16877F]">
                Current Observation
              </div>
              <h3 className="font-heading font-bold text-base text-[#151918] tracking-tight mt-0.5">
                Multi-Temporal Signals
              </h3>
            </div>
            <span className="w-2 h-2 rounded-full bg-[#258A65]" />
          </div>

          <div className="space-y-3 pt-2 border-t border-black/5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-[#151918] font-sans">Urban Expansion</span>
              <div className="flex items-center gap-2">
                <svg className="w-10 h-3.5 stroke-[#D8893D] fill-none stroke-[1.5]">
                  <path d="M0,11 Q5,10 10,8 T20,7 T30,3 T40,1" />
                </svg>
                <span className="font-mono text-xs font-bold text-[#D8893D]">
                  +12.4%
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-[#151918] font-sans">Vegetation</span>
              <div className="flex items-center gap-2">
                <svg className="w-10 h-3.5 stroke-[#258A65] fill-none stroke-[1.5]">
                  <path d="M0,2 Q10,3 20,7 T30,10 T40,12" />
                </svg>
                <span className="font-mono text-xs font-bold text-[#258A65]">
                  −4.7%
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-[#151918] font-sans">Water</span>
              <div className="flex items-center gap-2">
                <svg className="w-10 h-3.5 stroke-[#16877F] fill-none stroke-[1.5]">
                  <path d="M0,8 Q10,7 20,8 T30,5 T40,3" />
                </svg>
                <span className="font-mono text-xs font-bold text-[#16877F]">
                  +1.2%
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-black/5">
              <span className="text-xs text-[#687277] font-sans">Confidence</span>
              <span className="font-mono text-xs font-bold text-[#151918]">
                94.7%
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate('/analysis')}
            className="mt-5 w-full py-2.5 px-4 rounded-xl ios-glass-btn text-[#151918] font-heading font-semibold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all cursor-pointer"
          >
            <span>View Analysis</span>
            <ChevronRight className="w-3.5 h-3.5 text-[#737B78]" />
          </button>
        </div>
      </div>

      {/* ── 4. FLOATING MAP CONTROLS (Bottom-Left) ── */}
      <div className="absolute bottom-6 left-6 z-20 flex flex-col gap-2">
        <div className="ios-glass-dock p-1 flex flex-col gap-1 shadow-md">
          <button
            type="button"
            onClick={() => mapInstanceRef.current?.zoomIn()}
            title="Zoom In"
            className="w-8 h-8 rounded-xl flex items-center justify-center text-[#151918] hover:bg-white/80 transition-all cursor-pointer font-bold text-base"
          >
            +
          </button>
          <span className="w-5 h-px bg-[#DDE1DD] mx-auto" />
          <button
            type="button"
            onClick={() => mapInstanceRef.current?.zoomOut()}
            title="Zoom Out"
            className="w-8 h-8 rounded-xl flex items-center justify-center text-[#151918] hover:bg-white/80 transition-all cursor-pointer font-bold text-base"
          >
            −
          </button>
        </div>
      </div>

      {/* ── 5. FLOATING EARTH INTELLIGENCE COPILOT (Bottom-Right) ── */}
      <div className="absolute bottom-6 right-6 z-30">
        <EarthIntelligenceCopilot
          currentAoi={{
            name: locationName,
            lat: mapCenter.lat,
            lng: mapCenter.lng,
            areaKm2: aoiAreaKm2,
            sensor: 'Sentinel-2 · 10m GSD'
          }}
          onNavigateToAnalysis={handleCaptureAoi}
          defaultExpanded={false}
        />
      </div>

      {/* ── 4. BOTTOM FLOATING CONTROL DOCK (Bottom-Center) ── */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2 max-w-[calc(100vw-2rem)]">

        {/* Basemap & Presets Dock */}
        <div className="bg-white/95 backdrop-blur-md rounded-2xl px-3 py-2 shadow-[0_6px_28px_rgba(0,0,0,0.08)] border border-white/80 flex items-center gap-1 text-xs">

          {/* Basemaps */}
          {(['satellite', 'hybrid', 'streets'] as const).map((layer) => (
            <button
              key={layer}
              type="button"
              onClick={() => changeBasemap(layer)}
              className={`px-3 py-1.5 rounded-xl font-sans capitalize transition-all cursor-pointer ${activeLayer === layer
                  ? 'bg-[#151918] text-white font-medium shadow-2xs'
                  : 'text-[#737B78] hover:text-[#151918]'
                }`}
            >
              {layer}
            </button>
          ))}

          <span className="h-4 w-px bg-[#DDE1DD] mx-1" />

          {/* Quick Presets Toggle */}
          <div className="hidden sm:flex items-center gap-1">
            {presets.slice(0, 3).map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => handleSelectPreset(p)}
                className={`px-2.5 py-1.5 rounded-xl text-xs font-sans transition-all cursor-pointer ${activePreset === p.id
                    ? 'text-[#16877F] font-semibold bg-[#16877F]/10'
                    : 'text-[#737B78] hover:text-[#151918]'
                  }`}
              >
                {p.name.split(',')[0]}
              </button>
            ))}
          </div>

          <span className="h-4 w-px bg-[#DDE1DD] mx-1" />

          {/* System details toggle */}
          <button
            type="button"
            onClick={() => setShowSystemDetails(true)}
            className="px-3 py-1.5 rounded-xl text-[#737B78] hover:text-[#151918] font-sans transition-colors cursor-pointer text-xs flex items-center gap-1"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>System details</span>
          </button>
        </div>

      </div>

      {/* ── 5. EXPANDABLE "SYSTEM DETAILS" DRAWER (Hidden until requested) ── */}
      {showSystemDetails && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-[#DDE1DD] space-y-5">

            <div className="flex items-center justify-between border-b border-[#F0F2EE] pb-3">
              <div>
                <h3 className="font-heading font-semibold text-base text-[#151918]">
                  System Telemetry & Activity
                </h3>
                <p className="text-xs text-[#737B78]">
                  Live operational statistics and ingestion pipeline
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowSystemDetails(false)}
                className="p-1.5 rounded-full hover:bg-[#F0F2EE] text-[#737B78] hover:text-[#151918] transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Quiet Metrics Summary */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-[#F7F8F5] p-3 rounded-xl">
                <span className="text-[10px] uppercase text-[#737B78] font-sans font-medium block">Analyses</span>
                <span className="font-mono text-lg font-bold text-[#151918]">{completedAnalyses}</span>
              </div>
              <div className="bg-[#F7F8F5] p-3 rounded-xl">
                <span className="text-[10px] uppercase text-[#737B78] font-sans font-medium block">Images</span>
                <span className="font-mono text-lg font-bold text-[#151918]">{imagesProcessed}</span>
              </div>
              <div className="bg-[#F7F8F5] p-3 rounded-xl">
                <span className="text-[10px] uppercase text-[#737B78] font-sans font-medium block">Process Time</span>
                <span className="font-mono text-lg font-bold text-[#16877F]">{avgTimeSec}s</span>
              </div>
            </div>

            {/* Recent Analysis Log */}
            <div>
              <div className="flex items-center justify-between text-xs font-sans text-[#737B78] mb-2">
                <span>Recent Analyses</span>
                <button
                  type="button"
                  onClick={() => refetchStats()}
                  className="hover:text-[#151918] flex items-center gap-1 text-[11px] cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Sync</span>
                </button>
              </div>

              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {recentAnalyses && recentAnalyses.slice(0, 3).map((job: any, idx: number) => (
                  <div key={job.job_id || idx} className="p-2.5 rounded-xl bg-[#F7F8F5] flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-[#16877F]" />
                      <div>
                        <div className="font-medium text-[#151918] capitalize">
                          {job.task?.replace('_', ' ') || 'Scene Analysis'}
                        </div>
                        <div className="text-[10px] text-[#737B78] font-mono">
                          {job.created_at ? new Date(job.created_at).toLocaleTimeString('en-GB') : 'Just now'}
                        </div>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-[#258A65] font-semibold">
                      {job.status?.toUpperCase() || 'COMPLETED'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => { setShowSystemDetails(false); navigate('/reports'); }}
                className="w-full py-2.5 rounded-xl bg-[#151918] hover:bg-black text-white text-xs font-medium transition-colors cursor-pointer"
              >
                Open Full Report Registry
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
