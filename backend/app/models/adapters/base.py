"""
SatQuery AI - Model Base Adapter + Registry
All AI/ML model adapters inherit from BaseModelAdapter.
ModelRegistry caches loaded models to avoid redundant loading.
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available")


def detect_device(requested: str = "auto") -> str:
    """
    Detect the best available compute device.
    Returns: "cuda", "mps", or "cpu"
    """
    if requested == "cpu":
        return "cpu"
    if not TORCH_AVAILABLE:
        return "cpu"

    if requested in ("auto", "cuda"):
        if torch.cuda.is_available():
            return "cuda"
        # Apple Silicon
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    return "cpu"


@dataclass
class ModelInfo:
    """Static information about a model."""
    name: str
    display_name: str
    version: str
    task: str
    description: str
    hf_model_id: Optional[str] = None
    supported_formats: List[str] = field(default_factory=list)
    supported_modalities: List[str] = field(default_factory=list)
    required_bands: Optional[List[str]] = None   # None = any
    min_resolution_m: Optional[float] = None
    max_resolution_m: Optional[float] = None


@dataclass
class ModelOutput:
    """Standardised output from any model adapter."""
    success: bool
    task: str
    model_name: str
    model_version: str
    device: str
    inference_time_ms: int
    data: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

    # Provenance — must always be populated
    source_tool: str = ""
    confidence: Optional[float] = None   # None if model does not output confidence


class BaseModelAdapter(ABC):
    """
    Abstract base class for all AI/ML model adapters.
    Enforces:
      - consistent interface
      - device detection
      - timing
      - provenance reporting
    """

    info: ModelInfo  # must be set by subclasses

    def __init__(self, device: str = "auto"):
        self.device = detect_device(device)
        self._model = None
        self._processor = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        """Load the model into memory. Idempotent."""
        if self._loaded:
            return
        logger.info(f"Loading model: {self.info.name} on {self.device}")
        try:
            self._load_impl()
            self._loaded = True
            logger.info(f"Model {self.info.name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {self.info.name}: {e}")
            raise RuntimeError(f"Model '{self.info.name}' failed to load: {e}") from e

    @abstractmethod
    def _load_impl(self) -> None:
        """Implement model loading (weights, tokeniser, processor etc.)."""
        pass

    def infer(self, **kwargs) -> ModelOutput:
        """
        Run inference. Loads model if not already loaded.
        Times execution and wraps errors.
        """
        if not self._loaded:
            self.load()

        start = time.perf_counter()
        try:
            result = self._infer_impl(**kwargs)
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.error(f"Inference failed for {self.info.name}: {e}", exc_info=True)
            return ModelOutput(
                success=False,
                task=self.info.task,
                model_name=self.info.name,
                model_version=self.info.version,
                device=self.device,
                inference_time_ms=elapsed_ms,
                error=str(e),
                source_tool=self.info.name,
            )

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        result.inference_time_ms = elapsed_ms
        return result

    @abstractmethod
    def _infer_impl(self, **kwargs) -> ModelOutput:
        """Implement actual inference. Must return ModelOutput."""
        pass

    def unload(self) -> None:
        """Free model from memory."""
        if self._model is not None:
            del self._model
            self._model = None
        if self._processor is not None:
            del self._processor
            self._processor = None
        if TORCH_AVAILABLE and self.device == "cuda":
            torch.cuda.empty_cache()
        self._loaded = False
        logger.info(f"Model {self.info.name} unloaded")


class ModelRegistry:
    """
    Singleton registry that manages model adapter instances.
    Prevents loading the same model multiple times.
    """

    _instance: Optional["ModelRegistry"] = None
    _adapters: Dict[str, BaseModelAdapter] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._adapters = {}
        return cls._instance

    def register(self, adapter: BaseModelAdapter) -> None:
        name = adapter.info.name
        if name not in self._adapters:
            self._adapters[name] = adapter
            logger.info(f"Registered model: {name}")

    def get(self, name: str) -> Optional[BaseModelAdapter]:
        return self._adapters.get(name)

    def get_or_raise(self, name: str) -> BaseModelAdapter:
        adapter = self.get(name)
        if adapter is None:
            raise ValueError(
                f"Model '{name}' is not registered. "
                f"Available: {list(self._adapters.keys())}"
            )
        return adapter

    def list_all(self) -> List[Dict[str, Any]]:
        result = []
        for name, adapter in self._adapters.items():
            result.append({
                "name": name,
                "display_name": adapter.info.display_name,
                "version": adapter.info.version,
                "task": adapter.info.task,
                "description": adapter.info.description,
                "loaded": adapter.is_loaded,
                "device": adapter.device,
                "supported_modalities": adapter.info.supported_modalities,
                "supported_formats": adapter.info.supported_formats,
            })
        return result

    def load_all(self) -> None:
        """Pre-load all registered models (warmup)."""
        for name, adapter in self._adapters.items():
            if not adapter.is_loaded:
                try:
                    adapter.load()
                except Exception as e:
                    logger.error(f"Could not load {name}: {e}")

    def device_info(self) -> Dict[str, Any]:
        """Return GPU/CPU system info."""
        info = {"device": "cpu", "cuda_available": False, "gpu_name": None, "vram_gb": None}
        if TORCH_AVAILABLE:
            info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info["device"] = "cuda"
                info["gpu_name"] = torch.cuda.get_device_name(0)
                props = torch.cuda.get_device_properties(0)
                info["vram_gb"] = round(props.total_memory / (1024 ** 3), 2)
        return info


# Global registry instance
model_registry = ModelRegistry()
