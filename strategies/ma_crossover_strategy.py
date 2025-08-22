from typing import Optional, Dict, Any

import MetaTrader5 as mt5
import pandas as pd

from core.mt5_client import MT5Client
from strategies.base_strategy import BaseStrategy


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    A simple strategy based on the crossover of two moving averages.

    - A "BUY" signal is generated when the short-term MA crosses above the long-term MA.
    - A "SELL" signal is generated when the short-term MA crosses below the long-term MA.
    """

    def __init__(self, name: str, params: Dict[str, Any]):
        """
        Initializes the strategy with specific parameters.

        Required params:
            - short_ma_period (int): The period for the short-term moving average.
            - long_ma_period (int): The period for the long-term moving average.
            - timeframe (str): The MT5 timeframe to use (e.g., 'TIMEFRAME_H1').
        """
        super().__init__(name, params)
        self.short_ma_period = self.params.get("short_ma_period", 20)
        self.long_ma_period = self.params.get("long_ma_period", 50)

        # Convert string timeframe from config to MT5 constant
        self.timeframe_str = self.params.get("timeframe", "TIMEFRAME_H1")
        self.timeframe = getattr(mt5, self.timeframe_str, mt5.TIMEFRAME_H1)

    def check_signal(self, client: MT5Client, symbol: str) -> Optional[str]:
        """
        Analyzes market data for a moving average crossover.

        Args:
            client: The MT5Client instance.
            symbol: The symbol to analyze.

        Returns:
            "BUY", "SELL", or None.
        """
        # We need enough data to calculate the longest moving average.
        # We fetch a bit more for stability.
        num_candles = self.long_ma_period + 5

        market_data = client.get_market_data(symbol, self.timeframe, num_candles)

        if market_data is None or len(market_data) < self.long_ma_period:
            # Not enough data to compute the moving averages
            return None

        # Calculate moving averages
        market_data['short_ma'] = market_data['close'].rolling(window=self.short_ma_period).mean()
        market_data['long_ma'] = market_data['close'].rolling(window=self.long_ma_period).mean()

        # We need at least two points of the long MA to detect a crossover
        if market_data['long_ma'].isna().sum() > len(market_data) - 2:
            return None

        # Get the last two completed candles
        last_candle = market_data.iloc[-2]
        prev_candle = market_data.iloc[-3]

        # Check for bullish crossover (BUY signal)
        if prev_candle['short_ma'] <= prev_candle['long_ma'] and last_candle['short_ma'] > last_candle['long_ma']:
            return "BUY"

        # Check for bearish crossover (SELL signal)
        if prev_candle['short_ma'] >= prev_candle['long_ma'] and last_candle['short_ma'] < last_candle['long_ma']:
            return "SELL"

        return None
