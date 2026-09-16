import { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  X, Globe, Check,
  Loader2, Compass, Search, MapPin,
  Satellite
} from 'lucide-react';
import { captureSatelliteAOI, geocodeLocation, type UploadResult } from '../../services/api';

const TILE_LAYERS = {
  satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
  hybrid: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
  streets: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
};

const GLOBAL_PRESETS = [
  { id: 'delhi', name: 'Delhi Urban, India', bbox: [77.18, 28.58, 77.26, 28.64] as [number, number, number, number], zoom: 13 },
  { id: 'dubai', name: 'Dubai Palm, UAE', bbox: [55.10, 25.10, 55.18, 25.16] as [number, number, number, number], zoom: 14 },
  { id: 'cairo', name: 'Cairo Nile, Egypt', bbox: [31.21, 30.01, 31.28, 30.08] as [number, number, number, number], zoom: 13 },
  { id: 'manhattan', name: 'New York Manhattan, USA', bbox: [-74.02, 40.70, -73.94, 40.78] as [number, number, number, number], zoom: 14 },
  { id: 'singapore', name: 'Singapore Port', bbox: [103.78, 1.24, 103.86, 1.30] as [number, number, number, number], zoom: 14 },
  { id: 'tokyo', name: 'Tokyo Bay, Japan', bbox: [139.75, 35.62, 139.83, 35.68] as [number, number, number, number], zoom: 13 },
];

interface LiveAoiModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (result: UploadResult) => void;
}

export function LiveAoiModal({ isOpen, onClose, onCapture }: LiveAoiModalProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const aoiRectangleRef = useRef<L.Rectangle | null>(null);

  const [activeLayer, setActiveLayer] = useState<'satellite' | 'hybrid' | 'streets'>('satellite');
  const [mapCenter, setMapCenter] = useState<{ lat: number; lng: number }>({ lat: 28.6139, lng: 77.2090 });
  const [zoomLevel, setZoomLevel] = useState<number>(13);
  const [aoiAreaKm2, setAoiAreaKm2] = useState<number>(32.6);
  const [locationName, setLocationName] = useState<string>('Delhi Urban Conurbation');
  const [capturing, setCapturing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<Array<{ name: string; lat: number; lng: number }>>([]);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const searchDebounceRef = useRef<any>(null);

  const handleSelectSearchResult = (lat: number, lng: number, name: string) => {
    setLocationName(name);
    setSearchQuery('');
    setShowSearchDropdown(false);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([lat, lng], 13, { duration: 1.2 });
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

    const localMatches = GLOBAL_PRESETS
      .filter(p => p.name.toLowerCase().includes(trimmed.toLowerCase()))
      .map(p => {
        const [w, s, e, n] = p.bbox;
        return { name: p.name, lat: (s + n) / 2, lng: (w + e) / 2 };
      });
    if (localMatches.length > 0) {
      setSearchResults(localMatches);
      setShowSearchDropdown(true);
    }

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

  // Initialize Map when modal opens
  useEffect(() => {
    if (!isOpen || !mapContainerRef.current) return;

    // Small delay to ensure DOM dimensions are ready
    const timer = setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
        return;
      }

      const map = L.map(mapContainerRef.current!, {
        center: [mapCenter.lat, mapCenter.lng],
        zoom: zoomLevel,
        maxZoom: 19,
        zoomControl: false,
        attributionControl: false,
      });

      const tile = L.tileLayer(TILE_LAYERS[activeLayer], { maxZoom: 19, maxNativeZoom: 19 }).addTo(map);
      tileLayerRef.current = tile;
      mapInstanceRef.current = map;

      // AOI Rectangle overlay
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
        weight: 2,
        dashArray: '4, 4',
        fillColor: '#16877F',
        fillOpacity: 0.1,
      }).addTo(map);

      aoiRectangleRef.current = rect;

      const onMapMove = () => {
        const center = map.getCenter();
        const zoom = map.getZoom();
        setMapCenter({ lat: center.lat, lng: center.lng });
        setZoomLevel(zoom);

        const currBounds = map.getBounds();
        const latDelta = (currBounds.getNorth() - currBounds.getSouth()) * 0.22;
        const lngDelta = (currBounds.getEast() - currBounds.getWest()) * 0.22;
        const newAoi = L.latLngBounds(
          [center.lat - latDelta, center.lng - lngDelta],
          [center.lat + latDelta, center.lng + lngDelta]
        );
        rect.setBounds(newAoi);

        const latDistKm = latDelta * 2 * 111;
        const lngDistKm = lngDelta * 2 * 111 * Math.cos((center.lat * Math.PI) / 180);
        setAoiAreaKm2(Math.round(Math.abs(latDistKm * lngDistKm) * 10) / 10);
      };

      map.on('moveend', onMapMove);
      map.on('zoomend', onMapMove);
      onMapMove();
    }, 100);

    return () => {
      clearTimeout(timer);
    };
  }, [isOpen]);

  // Clean up map on close
  useEffect(() => {
    if (!isOpen && mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }
  }, [isOpen]);

  // Switch tile layer
  const handleSwitchLayer = (type: 'satellite' | 'hybrid' | 'streets') => {
    setActiveLayer(type);
    if (mapInstanceRef.current && tileLayerRef.current) {
      mapInstanceRef.current.removeLayer(tileLayerRef.current);
      const newTile = L.tileLayer(TILE_LAYERS[type], { maxZoom: 19, maxNativeZoom: 19 }).addTo(mapInstanceRef.current);
      tileLayerRef.current = newTile;
    }
  };

  // Jump to preset
  const handleSelectPreset = (preset: typeof GLOBAL_PRESETS[0]) => {
    setLocationName(preset.name.split(',')[0]);
    if (mapInstanceRef.current) {
      const [west, south, east, north] = preset.bbox;
      const centerLat = (south + north) / 2;
      const centerLng = (west + east) / 2;
      mapInstanceRef.current.flyTo([centerLat, centerLng], preset.zoom, { duration: 1.2 });
    }
  };

  // Capture AOI
  const [captureStage, setCaptureStage] = useState('Fetching high-resolution satellite tiles…');

  const handleCapture = async () => {
    if (!mapInstanceRef.current || capturing) return;
    setCapturing(true);
    setError(null);
    setCaptureStage('Fetching high-resolution satellite tiles…');

    const t1 = setTimeout(() => setCaptureStage('Stitching raster mosaic & cropping AOI…'), 500);
    const t2 = setTimeout(() => setCaptureStage('Sharpening edges & generating georeferenced GeoTIFF…'), 1100);

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

      clearTimeout(t1);
      clearTimeout(t2);
      onCapture(result);
      onClose();
    } catch (err: unknown) {
      clearTimeout(t1);
      clearTimeout(t2);
      setError((err as Error).message || 'Failed to capture satellite AOI.');
    } finally {
      setCapturing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="ios-glass-dock max-w-4xl w-full h-[85vh] max-h-[700px] flex flex-col shadow-2xl border border-white/80 overflow-hidden relative">
        
        {/* Progressive Loading State Overlay */}
        {capturing && (
          <div className="absolute inset-0 z-50 bg-white/90 backdrop-blur-md flex flex-col items-center justify-center p-6 text-center space-y-4 animate-in fade-in duration-200">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#123B5D] to-[#16877F] text-white flex items-center justify-center shadow-lg">
              <Satellite className="w-7 h-7 animate-pulse" />
            </div>
            <div className="space-y-1.5">
              <span className="text-[11px] font-heading font-bold uppercase tracking-widest text-[#16877F]">
                SATQUERY OBSERVATION PIPELINE
              </span>
              <h3 className="font-heading font-bold text-base text-[#151918]">
                Generating High-Resolution Analysis AOI
              </h3>
              <p className="text-xs text-[#687277] font-mono">
                {captureStage}
              </p>
            </div>
            <div className="w-52 h-1.5 bg-[#DDE1DD] rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-[#123B5D] via-[#16877F] to-[#258A65] w-full animate-pulse" />
            </div>
          </div>
        )}

        {/* Header */}
        <div className="p-4 px-6 flex items-center justify-between border-b border-[#F0F2EE]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-[#16877F]/10 flex items-center justify-center text-[#16877F]">
              <Globe className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-heading font-bold text-sm text-[#151918]">
                Target Area of Interest (AOI)
              </h3>
              <p className="text-[11px] font-sans text-[#737B78]">
                Pan & zoom anywhere on Earth or choose a preset to capture live satellite rasters
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-[#F0F2EE] text-[#737B78] hover:text-[#151918] transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Bar & Presets Bar */}
        <div className="px-6 py-2 bg-[#F7F8F5] border-b border-[#F0F2EE] flex flex-wrap items-center gap-2 text-xs">
          <div className="relative flex-1 min-w-[240px]">
            <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-[#DDE1DD] focus-within:border-[#16877F] transition-all">
              <Search className="w-3.5 h-3.5 text-[#16877F] shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearchInputChange(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleExecuteGeocode(searchQuery);
                }}
                placeholder="Search any place in the world or coordinates…"
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

            {/* Live Search Dropdown */}
            {showSearchDropdown && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-xl shadow-xl border border-[#DDE1DD] overflow-hidden z-50 divide-y divide-[#F0F2EE] max-h-48 overflow-y-auto">
                {searchResults.length > 0 ? (
                  searchResults.map((loc, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSelectSearchResult(loc.lat, loc.lng, loc.name)}
                      className="w-full text-left px-3 py-2 text-xs font-sans hover:bg-[#F7F8F5] flex items-center justify-between transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <MapPin className="w-3 h-3 text-[#16877F] shrink-0" />
                        <span className="truncate font-medium text-[#151918]">{loc.name}</span>
                      </div>
                      <span className="font-mono text-[10px] text-[#16877F] font-semibold shrink-0">FLY TO →</span>
                    </button>
                  ))
                ) : isSearching ? (
                  <div className="px-3 py-2.5 text-center text-xs text-[#737B78] font-sans flex items-center justify-center gap-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-[#16877F]" />
                    <span>Searching global database…</span>
                  </div>
                ) : searchQuery.trim().length >= 2 ? (
                  <div className="px-3 py-2.5 text-center text-xs text-[#737B78] font-sans">
                    No places found. Enter coordinates like 48.85, 2.35
                  </div>
                ) : null}
              </div>
            )}
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto">
            <span className="text-[10px] uppercase tracking-wider font-semibold text-[#737B78] shrink-0">
              Presets:
            </span>
            {GLOBAL_PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => handleSelectPreset(p)}
                className="px-2 py-1 rounded-lg bg-white hover:bg-[#EEF0EC] border border-[#DDE1DD] text-[#151918] font-sans text-[11px] whitespace-nowrap transition-colors cursor-pointer"
              >
                {p.name.split(',')[0]}
              </button>
            ))}
          </div>
        </div>

        {/* Map Viewport Area */}
        <div className="flex-1 relative w-full h-full overflow-hidden bg-[#E2E5E0]">
          <div ref={mapContainerRef} className="absolute inset-0 w-full h-full z-0" />

          {/* Floating Reticle Crosshair HUD */}
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center z-10">
            <div className="relative w-48 h-36 border border-[#16877F]/60 rounded-xl shadow-[0_0_24px_rgba(22,135,127,0.15)] flex items-center justify-center">
              <span className="absolute top-1 left-1.5 text-[9px] font-mono font-semibold text-[#16877F] uppercase tracking-widest bg-white/90 px-1.5 py-0.5 rounded">
                AOI TARGET
              </span>
              <div className="w-2 h-2 rounded-full bg-[#16877F]" />
            </div>
          </div>

          {/* Map Top Floating Controls (Basemap Switcher) */}
          <div className="absolute top-4 left-4 z-20 flex items-center gap-1 bg-white/90 backdrop-blur-md p-1 rounded-xl shadow-md border border-white/80 text-xs">
            {(['satellite', 'hybrid', 'streets'] as const).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => handleSwitchLayer(type)}
                className={`px-3 py-1 rounded-lg capitalize text-xs font-sans transition-all cursor-pointer ${
                  activeLayer === type
                    ? 'bg-[#151918] text-white font-medium shadow-2xs'
                    : 'text-[#737B78] hover:text-[#151918]'
                }`}
              >
                {type}
              </button>
            ))}
          </div>

          {/* Map Bottom Telemetry Pill */}
          <div className="absolute bottom-4 left-4 z-20 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-xl shadow-md border border-white/80 flex items-center gap-3 text-xs font-mono text-[#151918]">
            <div className="flex items-center gap-1">
              <Compass className="w-3.5 h-3.5 text-[#16877F]" />
              <span>{Math.abs(mapCenter.lat).toFixed(4)}°{mapCenter.lat >= 0 ? 'N' : 'S'}, {Math.abs(mapCenter.lng).toFixed(4)}°{mapCenter.lng >= 0 ? 'E' : 'W'}</span>
            </div>
            <span>·</span>
            <span>Zoom {zoomLevel}</span>
            <span>·</span>
            <span className="font-semibold text-[#258A65]">~{aoiAreaKm2} km²</span>
          </div>

        </div>

        {/* Footer Actions */}
        <div className="p-4 px-6 bg-white border-t border-[#F0F2EE] flex flex-col sm:flex-row items-center justify-between gap-3">
          
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <input
              type="text"
              value={locationName}
              onChange={(e) => setLocationName(e.target.value)}
              placeholder="Target Location Label..."
              className="px-3 py-2 rounded-xl bg-[#F7F8F5] border border-[#DDE1DD] text-xs font-sans text-[#151918] outline-none w-full sm:w-64"
            />
          </div>

          {error && (
            <span className="text-xs text-[#C84B4B] font-sans">
              {error}
            </span>
          )}

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <button
              type="button"
              onClick={onClose}
              className="py-2 px-4 rounded-xl text-xs font-sans font-medium text-[#737B78] hover:text-[#151918] transition-colors cursor-pointer"
            >
              Cancel
            </button>

            <button
              type="button"
              onClick={handleCapture}
              disabled={capturing}
              className="py-2.5 px-6 rounded-xl bg-[#16877F] hover:bg-[#127069] disabled:bg-[#DDE1DD] text-white text-xs font-sans font-semibold shadow-sm flex items-center gap-2 transition-all cursor-pointer"
            >
              {capturing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Ingesting Satellite Tiles…</span>
                </>
              ) : (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Capture & Load AOI</span>
                </>
              )}
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}
