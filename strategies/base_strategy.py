from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import pandas as pd

from core.mt5_client import MT5Client


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    This class defines the interface that all strategies must implement
    to be compatible with the TradingEngine. It provides a structured way
    to receive market data and generate trading signals.

    Attributes:
        name (str): The name of the strategy.
        params (Dict[str, Any]): A dictionary of strategy-specific parameters.
    """

    def __init__(self, name: str, params: Dict[str, Any]):
        self.name = name
        self.params = params

    @abstractmethod
    def check_signal(self, client: MT5Client, symbol: str) -> Optional[str]:
        """
        Analyzes market data and generates a trading signal.

        This is the core method of the strategy. The TradingEngine will call
        this method for each symbol the strategy is configured to run on.

        Args:
            client (MT5Client): The MT5Client instance for the current account,
                                used to fetch necessary data.
            symbol (str): The symbol to analyze (e.g., "EURUSD").

        Returns:
            Optional[str]: A signal string ("BUY", "SELL", "CLOSE"), or None if
                           no action should be taken.
        """
        pass

    def __str__(self) -> str:
        return f"{self.name} (Parameters: {self.params})"
