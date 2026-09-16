# SatQuery AI - Smart India Hackathon (SIH) 2026

> **AI-Powered Satellite Imagery Intelligence & Natural Language Earth Observation Platform**

SatQuery AI enables interactive exploration, segmentation, change detection, and intelligence extraction from high-resolution satellite imagery (Sentinel-2, Landsat, PlanetScope, and custom GeoTIFFs) using deep learning vision adapters, GIS processing pipelines, and conversational LLM reasoning.

---

## 🌟 Key Features

- 🛰️ **Natural Language Geospatial Queries**: Query satellite data via AI Copilot ("Find water bodies near Chennai", "Detect urbanization expansion between 2022 and 2025").
- 🗺️ **Interactive Mission Control & GIS Dashboard**: High-performance raster and vector visualization with MapLibre GL, layer toggles, split-screen comparisons, and AOI bounding box drawing.
- 🔬 **Multi-Model Vision Pipeline**:
  - Semantic Land Cover Classification (water, vegetation, urban, roads, bare soil)
  - Deep Learning Segmentation with PyTorch adapters
  - Temporal Change Detection & Differential Analytics
- ⚡ **High-Performance Architecture**:
  - FastAPI asynchronous backend with task orchestration
  - React 18 + Vite + TypeScript frontend with TailwindCSS
  - Geospatial processing with Rasterio, Shapely, PyProj, and GDAL

---

## 📂 Project Structure

```
satquery-ai/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── agents/           # LLM Copilot & Reasoning Agents
│   │   ├── api/routes/       # REST API endpoints (analysis, satellite, jobs)
│   │   ├── config/           # App settings & environment configs
│   │   ├── gis/              # Rasterio/GDAL GeoTIFF processing utilities
│   │   ├── models/           # Segmentation models, adapters, registries
│   │   └── services/         # AOI querying, satellite data pipelines
│   ├── requirements.txt      # Python dependencies
│   └── satquery_dev.db       # Local SQLite development database (ignored)
├── frontend/                 # React + TypeScript + Vite UI
│   ├── src/
│   │   ├── components/       # UI Components (GIS map, chat, dashboards)
│   │   ├── pages/            # Mission Control, Analysis, Change Detection
│   │   └── services/         # API client & state management
│   └── package.json          # Node dependencies
├── docs/                     # Architecture flowcharts and specifications
├── scripts/                  # Data generation & pipeline test scripts
├── tests/                    # Unit and integration test suites
└── .env.example              # Environment variables template
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- GDAL / Rasterio compatible environment (optional for full GIS acceleration)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your GEMINI_API_KEY and configs

uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The application will be accessible at `http://localhost:5173` connecting to backend APIs at `http://localhost:8000`.

---

## 📜 License
Developed for Smart India Hackathon (SIH) 2026.
