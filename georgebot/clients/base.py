## ============================================================
## BASE.PY - Base client interface
## ============================================================
## All brain clients implement this interface.
## Swap brains without changing calling code.
## ============================================================

from abc import ABC, abstractmethod


class BaseBrain(ABC):
    """
    Base class for all AI brain clients.

    All brains must implement:
    - chat(context) -> response string
    - check() -> bool (is available)
    """

    @abstractmethod
    def chat(self, context: str, stream: bool = True) -> str:
        """
        Send context to model, get response.

        Args:
            context: Full context (system prompt + history)
            stream: Print as it arrives

        Returns:
            str: Model response
        """
        pass

    @abstractmethod
    def check(self) -> bool:
        """
        Check if this brain is available/configured.

        Returns:
            bool: True if ready to use
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Brain identifier for display."""
        pass
