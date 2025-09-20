# adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ModelAdapter(ABC):
    """
    Abstract adapter interface for text generation models.
    Implementations must be safe to instantiate without making network calls.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.0,
        **kwargs,
    ) -> str:
        """
        Generate text given a prompt.
        Returns the generated string.
        """
        raise NotImplementedError

    @abstractmethod
    def info(self) -> Dict[str, Any]:
        """
        Return basic info about the adapter (model name, backend used, etc.)
        """
        raise NotImplementedError
