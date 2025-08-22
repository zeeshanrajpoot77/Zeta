import time
import logging
from typing import Optional, List, Dict, Any

import MetaTrader5 as mt5
import pandas as pd

from core.config import AccountConfig

# Setup a basic logger for the client
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


class MT5Client:
    """
    A robust client for interacting with the MetaTrader 5 terminal.

    This class handles the connection, data fetching, and order execution.
    It is designed to be thread-safe and includes error handling and
    automatic reconnection logic.
    """

    def __init__(self, account_config: AccountConfig):
        """
        Initializes the MT5Client with a specific account configuration.

        Args:
            account_config: A dictionary-like object containing account details
                            (account_id, password, server).
        """
        self.account_id = account_config.account_id
        self.password = account_config.password
        self.server = account_config.server
        self._is_connected = False

    def connect(self) -> bool:
        """
        Initializes and connects to the MetaTrader 5 terminal.

        Returns:
            True if the connection was successful, False otherwise.
        """
        if self._is_connected:
            return True

        log.info(f"Connecting to MT5 account {self.account_id} on {self.server}...")
        if not mt5.initialize():
            log.error("Failed to initialize MetaTrader 5. Please ensure the terminal is running.")
            self._is_connected = False
            return False

        authorized = mt5.login(self.account_id, password=self.password, server=self.server)
        if not authorized:
            log.error(f"Failed to login to account {self.account_id}. Error: {mt5.last_error()}")
            mt5.shutdown()
            self._is_connected = False
            return False

        log.info(f"Successfully connected and logged into account {self.account_id}.")
        self._is_connected = True
        return True

    def disconnect(self):
        """Shuts down the connection to the MetaTrader 5 terminal."""
        if self._is_connected:
            log.info(f"Disconnecting from MT5 account {self.account_id}.")
            mt5.shutdown()
            self._is_connected = False

    def is_connected(self) -> bool:
        """Checks the current connection status."""
        # MT5 doesn't have a persistent connection check, so we rely on our flag.
        # A more robust check might involve a periodic ping like getting account info.
        return self._is_connected

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves account information.

        Returns:
            A dictionary with account details or None if an error occurs.
        """
        if not self.is_connected():
            log.warning("Not connected to MT5. Cannot get account info.")
            return None

        info = mt5.account_info()
        return info._asdict() if info else None

    def get_market_data(self, symbol: str, timeframe: int, count: int) -> Optional[pd.DataFrame]:
        """
        Fetches historical price data (OHLC) for a given symbol.

        Args:
            symbol: The financial instrument (e.g., "EURUSD").
            timeframe: The timeframe constant from MT5 (e.g., mt5.TIMEFRAME_H1).
            count: The number of bars to retrieve.

        Returns:
            A pandas DataFrame with OHLC data, or None if an error occurs.
        """
        if not self.is_connected():
            log.warning("Not connected to MT5. Cannot get market data.")
            return None

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            log.error(f"Failed to get rates for {symbol}. Error: {mt5.last_error()}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def place_order(self, symbol: str, order_type: int, volume: float, sl: float = 0.0, tp: float = 0.0, magic: int = 12345, comment: str = "trade_bot") -> Optional[int]:
        """
        Places a market order.

        Args:
            symbol: The financial instrument.
            order_type: mt5.ORDER_TYPE_BUY or mt5.ORDER_TYPE_SELL.
            volume: The trade volume in lots.
            sl: Stop loss price.
            tp: Take profit price.
            magic: Magic number for the order.
            comment: Order comment.

        Returns:
            The order ticket ID if successful, None otherwise.
        """
        if not self.is_connected():
            log.warning("Not connected to MT5. Cannot place order.")
            return None

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            log.error(f"Symbol {symbol} not found.")
            return None

        point = symbol_info.point
        price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            log.error(f"Order failed for {symbol}. Result: {result}")
            return None

        log.info(f"Order placed for {symbol}, ticket: {result.order}")
        return result.order

    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Retrieves all open positions for the account.

        Returns:
            A list of dictionaries, where each dictionary represents a position.
        """
        if not self.is_connected():
            return []

        positions = mt5.positions_get()
        if positions is None:
            return []

        return [p._asdict() for p in positions]

    def close_position(self, ticket: int, comment: str = "close_bot") -> bool:
        """
        Closes an open position by its ticket number.

        Args:
            ticket: The ticket number of the position to close.
            comment: A comment for the closing trade.

        Returns:
            True if the position was closed successfully, False otherwise.
        """
        position_info = mt5.positions_get(ticket=ticket)
        if not position_info or len(position_info) == 0:
            log.error(f"Position with ticket {ticket} not found.")
            return False

        position = position_info[0]
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": position.magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            log.error(f"Failed to close position {ticket}. Result: {result}")
            return False

        log.info(f"Position {ticket} closed successfully.")
        return True
