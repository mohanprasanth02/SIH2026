import { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  Satellite, Loader2, Search, X, Crosshair, Check
} from 'lucide-react';
import {
  captureSatelliteAOI, getSatellitePresets,
  type UploadResult, type SatellitePreset
} from '../../services/api';

const DEFAULT_CENTER: [number, number] = [77.2090, 28.6139]; // [lon, lat] Delhi default
const DEFAULT_ZOOM = 13;

interface Props {
  onAoiCaptured: (result: UploadResult) => void;
  onCancel?: () => void;
  defaultCenter?: [number, number];
  defaultZoom?: number;
}

type BasemapType = 'satellite' | 'hybrid' | 'streets' | 'topo';

export function MapAoiSelector({
  onAoiCaptured,
  onCancel,
  defaultCenter = DEFAULT_CENTER,
  defaultZoom = DEFAULT_ZOOM,
}: Props) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const baseTileLayerRef = useRef<L.TileLayer | null>(null);
  const isFlyingRef = useRef(false);

  const [basemap, setBasemap] = useState<BasemapType>('satellite');
  const [capturing, setCapturing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [presets, setPresets] = useState<SatellitePreset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string | null>('delhi_urban');
  const [locationName, setLocationName] = useState<string>('Delhi Urban Conurbation');

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<Array<{ display_name: string; lat: string; lon: string }>>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

  // AOI box coordinates [west, south, east, north]
  const [bbox, setBbox] = useState<[number, number, number, number]>([
    77.18, 28.58, 77.26, 28.64
  ]);
  const [currentZoom, setCurrentZoom] = useState<number>(defaultZoom);
  const [centerCoord, setCenterCoord] = useState<[number, number]>(defaultCenter);
  const [calculatedAreaKm2, setCalculatedAreaKm2] = useState<number>(32.6);

  // Synchronize update bounds
  const updateAoiBounds = useCallback(() => {
    const map = mapInstanceRef.current;
    if (!map || isFlyingRef.current) return;

    const bounds = map.getBounds();
    const center = map.getCenter();
    const zoom = Math.round(map.getZoom());

    setCenterCoord([center.lng, center.lat]);
    setCurrentZoom(zoom);

    // Centered AOI box covering middle 50% of viewport
    const west = bounds.getWest();
    const east = bounds.getEast();
    const south = bounds.getSouth();
    const north = bounds.getNorth();

    const lonSpan = east - west;
    const latSpan = north - south;

    const aoiWest = center.lng - lonSpan * 0.25;
    const aoiEast = center.lng + lonSpan * 0.25;
    const aoiSouth = center.lat - latSpan * 0.25;
    const aoiNorth = center.lat + latSpan * 0.25;

    setBbox([aoiWest, aoiSouth, aoiEast, aoiNorth]);

    // Calculate approximate area in km2
    const latDistKm = (aoiNorth - aoiSouth) * 111;
    const lngDistKm = (aoiEast - aoiWest) * 111 * Math.cos((center.lat * Math.PI) / 180);
    const area = Math.abs(latDistKm * lngDistKm);
    setCalculatedAreaKm2(Math.round(area * 10) / 10);
  }, []);

  const updateAoiBoundsRef = useRef(updateAoiBounds);
  updateAoiBoundsRef.current = updateAoiBounds;

  // Load presets
  useEffect(() => {
    let isMounted = true;
    getSatellitePresets()
      .then((data) => {
        if (isMounted && Array.isArray(data) && data.length > 0) {
          setPresets(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setPresets([
            {
              id: 'delhi_urban',
              name: 'Delhi Urban Conurbation, India',
              category: 'Urban',
              description: 'Dense urban fabric and Yamuna river corridor',
              bbox: [77.18, 28.58, 77.26, 28.64],
              zoom: 14,
              tags: ['urban', 'built_up'],
            },
            {
              id: 'kansas_agriculture',
              name: 'Kansas Pivot Crops, USA',
              category: 'Agriculture',
              description: 'Center-pivot circular crop fields',
              bbox: [-100.95, 37.95, -100.85, 38.02],
              zoom: 13,
              tags: ['agriculture', 'pivot_irrigation'],
            },
            {
              id: 'mumbai_harbor',
              name: 'Mumbai Harbor & Estuary, India',
              category: 'Water / Coastal',
              description: 'Coastal urban land-water boundary and port infrastructure',
              bbox: [72.85, 18.90, 72.95, 18.98],
              zoom: 13,
              tags: ['water', 'coastal', 'urban'],
            },
          ]);
        }
      });
    return () => { isMounted = false; };
  }, []);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const initialLat = defaultCenter ? defaultCenter[1] : 28.6139;
    const initialLng = defaultCenter ? defaultCenter[0] : 77.2090;

    const map = L.map(mapContainerRef.current, {
      center: [initialLat, initialLng],
      zoom: defaultZoom,
      zoomControl: false,
      attributionControl: true,
    });

    L.control.zoom({ position: 'topright' }).addTo(map);

    const tile = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        attribution: 'Esri, Maxar, Earthstar Geographics | SatQuery AOI',
        maxZoom: 18,
      }
    ).addTo(map);

    baseTileLayerRef.current = tile;
    mapInstanceRef.current = map;

    const handleMove = () => updateAoiBoundsRef.current();
    map.on('moveend', handleMove);
    map.on('zoomend', handleMove);

    updateAoiBoundsRef.current();

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [defaultCenter, defaultZoom]);

  // Basemap switcher
  const handleBasemapChange = (type: BasemapType) => {
    setBasemap(type);
    const map = mapInstanceRef.current;
    if (!map) return;

    if (baseTileLayerRef.current) {
      map.removeLayer(baseTileLayerRef.current);
    }

    let url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
    let attr = 'Esri World Imagery | SatQuery AOI';

    if (type === 'streets') {
      url = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
      attr = '© OpenStreetMap contributors';
    } else if (type === 'topo') {
      url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}';
      attr = 'Esri Topographic | SatQuery AOI';
    }

    const newLayer = L.tileLayer(url, { attribution: attr, maxZoom: 18 }).addTo(map);
    baseTileLayerRef.current = newLayer;
  };

  // Location search (Nominatim)
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    setShowSearchResults(true);
    try {
      const resp = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=4`
      );
      const data = await resp.json();
      setSearchResults(data);
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleSelectSearchResult = (result: { display_name: string; lat: string; lon: string }) => {
    const lat = parseFloat(result.lat);
    const lon = parseFloat(result.lon);
    setLocationName(result.display_name.split(',')[0]);
    setShowSearchResults(false);
    setSearchQuery('');

    if (mapInstanceRef.current) {
      isFlyingRef.current = true;
      mapInstanceRef.current.flyTo([lat, lon], 14, { duration: 1.2 });
      setTimeout(() => {
        isFlyingRef.current = false;
        updateAoiBounds();
      }, 1300);
    }
  };

  // Preset selection
  const handlePresetSelect = (preset: SatellitePreset) => {
    setSelectedPresetId(preset.id);
    setLocationName(preset.name.split(',')[0]);

    if (mapInstanceRef.current) {
      const [west, south, east, north] = preset.bbox;
      const centerLat = (south + north) / 2;
      const centerLng = (west + east) / 2;

      isFlyingRef.current = true;
      mapInstanceRef.current.flyTo([centerLat, centerLng], preset.zoom || 14, { duration: 1.2 });
      setTimeout(() => {
        isFlyingRef.current = false;
        updateAoiBounds();
      }, 1300);
    }
  };

  // Capture execution
  const handleCapture = async () => {
    setCapturing(true);
    setError(null);

    try {
      const result = await captureSatelliteAOI({
        bbox,
        zoom: currentZoom,
        source: basemap === 'satellite' ? 'satellite' : 'osm',
        name: locationName || `AOI_${centerCoord[1].toFixed(3)}N_${centerCoord[0].toFixed(3)}E`,
      });
      onAoiCaptured(result);
    } catch (err: unknown) {
      const msg = (err as Error)?.message || 'Failed to capture satellite AOI.';
      setError(msg);
    } finally {
      setCapturing(false);
    }
  };

  return (
    <div className="relative w-full h-full flex flex-col bg-[#F6F7F4] text-[#111516] overflow-hidden select-none font-sans">
      {/* ── TOP COMMAND STRIP ── */}
      <div className="h-11 bg-white border-b border-[#DDE1DD] px-4 flex items-center justify-between z-20 shrink-0 shadow-xs">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-[#0C7C72] text-white flex items-center justify-center">
            <Satellite className="w-3.5 h-3.5" />
          </div>
          <span className="font-heading font-semibold text-xs uppercase tracking-tight text-[#111516]">
            SATELLITE AOI SELECTION SYSTEM
          </span>
          <span className="text-[#DDE1DD] hidden sm:inline">|</span>
          <span className="text-[11px] font-mono text-[#687277] hidden sm:inline">
            SENTINEL-2 MSI · 10M GSD CALIBRATED
          </span>
        </div>

        <div className="flex items-center gap-2">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="p-1 rounded-md text-[#687277] hover:text-[#111516] hover:bg-[#F6F7F4] transition-colors cursor-pointer"
              title="Close AOI Selector"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* ── MAIN DOMINANT MAP CANVAS ── */}
      <div className="relative flex-1 min-h-0 w-full overflow-hidden">
        {/* Leaflet map instance */}
        <div ref={mapContainerRef} className="w-full h-full z-0" />

        {/* Dynamic AOI Target Box in center of viewport */}
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center z-10">
          <div
            className="border-2 border-dashed border-[#0C7C72] bg-[#0C7C72]/10 rounded-lg shadow-sm relative transition-all"
            style={{ width: '50%', height: '50%' }}
          >
            {/* Crosshairs on corners */}
            <div className="absolute -top-1.5 -left-1.5 w-3 h-3 border-t-2 border-l-2 border-[#0C7C72]" />
            <div className="absolute -top-1.5 -right-1.5 w-3 h-3 border-t-2 border-r-2 border-[#0C7C72]" />
            <div className="absolute -bottom-1.5 -left-1.5 w-3 h-3 border-b-2 border-l-2 border-[#0C7C72]" />
            <div className="absolute -bottom-1.5 -right-1.5 w-3 h-3 border-b-2 border-r-2 border-[#0C7C72]" />

            {/* Center target crosshair */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
              <Crosshair className="w-6 h-6 text-[#0C7C72] opacity-70" />
            </div>

            {/* Dimension badge */}
            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 bg-white/95 px-2.5 py-0.5 rounded-md border border-[#DDE1DD] text-[10px] font-mono text-[#0C7C72] shadow-xs whitespace-nowrap font-medium">
              TARGET BBOX: {bbox[1].toFixed(3)}°N, {bbox[0].toFixed(3)}°E to {bbox[3].toFixed(3)}°N, {bbox[2].toFixed(3)}°E
            </div>
          </div>
        </div>

        {/* ── FLOATING GIS COMMAND PANEL (Top Left) ── */}
        <div className="absolute top-4 left-4 z-20 bg-white/95 backdrop-blur-md border border-[#DDE1DD] rounded-xl p-3.5 text-xs shadow-md w-72 pointer-events-auto">
          <div className="flex items-center justify-between border-b border-[#DDE1DD] pb-2 mb-2.5">
            <span className="font-heading font-semibold text-[11px] uppercase tracking-tight text-[#0C7C72]">
              AOI CAPTURE TELEMETRY
            </span>
            <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-[#258A65]/10 text-[#258A65] border border-[#258A65]/20">
              ● LOCK
            </span>
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            <div className="flex items-center justify-between">
              <span className="text-[#687277]">CENTER:</span>
              <span className="text-[#111516] font-medium">
                {centerCoord[1].toFixed(4)}° N, {centerCoord[0].toFixed(4)}° E
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#687277]">AREA:</span>
              <span className="text-[#D8893D] font-bold">{calculatedAreaKm2} km²</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#687277]">RESOLUTION:</span>
              <span className="text-[#111516]">10 m (Z{currentZoom})</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#687277]">SOURCE:</span>
              <span className="text-[#258A65] font-semibold">Sentinel-2 MSI</span>
            </div>
          </div>

          {error && (
            <div className="mt-2 p-2 rounded-md bg-[#C84B4B]/10 border border-[#C84B4B]/30 text-[11px] font-mono text-[#C84B4B]">
              {error}
            </div>
          )}

          <div className="mt-3 pt-2.5 border-t border-[#DDE1DD]">
            <button
              type="button"
              onClick={handleCapture}
              disabled={capturing}
              className="btn-primary w-full py-2 text-xs font-heading font-semibold uppercase tracking-wider flex items-center justify-center gap-1.5 shadow-xs cursor-pointer"
            >
              {capturing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>CAPTURING SATELLITE TILES...</span>
                </>
              ) : (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>INGEST AOI IMAGERY</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* ── PROFESSIONAL GIS TOOLBAR (Top Right / Search) ── */}
        <div className="absolute top-4 right-14 z-20 flex items-center gap-2 pointer-events-auto">
          {/* Location Search Input */}
          <form onSubmit={handleSearch} className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search region or city..."
              className="bg-white/95 border border-[#DDE1DD] rounded-lg px-3 py-1.5 text-xs w-48 text-[#111516] focus:border-[#0C7C72] focus:w-60 transition-all outline-none font-sans shadow-xs"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[#687277] hover:text-[#0C7C72] cursor-pointer"
            >
              {searching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            </button>

            {/* Search results dropdown */}
            {showSearchResults && searchResults.length > 0 && (
              <div className="absolute top-full mt-1 right-0 w-64 bg-white border border-[#DDE1DD] rounded-lg shadow-md p-1 z-30 text-xs">
                {searchResults.map((r, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleSelectSearchResult(r)}
                    className="w-full text-left p-2 hover:bg-[#F6F7F4] rounded-md text-[#111516] truncate block cursor-pointer transition-colors"
                  >
                    {r.display_name}
                  </button>
                ))}
              </div>
            )}
          </form>

          {/* Basemap Switcher */}
          <div className="flex items-center gap-1 bg-white/95 border border-[#DDE1DD] rounded-lg p-1 text-xs shadow-xs">
            {(['satellite', 'streets', 'topo'] as const).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => handleBasemapChange(type)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-medium uppercase transition-colors cursor-pointer ${
                  basemap === type ? 'bg-[#0C7C72] text-white' : 'text-[#687277] hover:text-[#111516] hover:bg-[#F6F7F4]'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* ── PRESETS TAPE (Bottom Left) ── */}
        <div className="absolute bottom-4 left-4 z-20 hidden md:flex items-center gap-1.5 bg-white/95 border border-[#DDE1DD] rounded-lg p-1.5 text-xs shadow-sm">
          <span className="text-[#687277] font-semibold text-[10px] uppercase px-1">PRESETS:</span>
          {presets.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => handlePresetSelect(p)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
                selectedPresetId === p.id
                  ? 'bg-[#EEF0EC] text-[#0C7C72] border border-[#0C7C72]/30 font-semibold'
                  : 'text-[#687277] hover:text-[#111516] hover:bg-[#F6F7F4]'
              }`}
            >
              {p.name.split(',')[0]}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
