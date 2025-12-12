# Zeta Trading Bot ⚡

Welcome to **Zeta**, a high-performance, Python-based algorithmic trading framework designed for MetaTrader 5 (MT5).

## 🚀 Speed & Efficiency
Zeta is built with a "performance-first" philosophy. It includes:
- **Optimized Data Fetching**: Smart caching and efficient data type handling.
- **Asynchronous UI**: A responsive PySide6 interface that doesn't block the trading engine.
- **Batched Logging**: High-throughput logging system that minimizes IO overhead.
- **Modular Design**: Plug-and-play strategies and extendable architecture.

## 📚 Table of Contents
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Strategies](#strategies)
- [Configuration](#configuration)
- [Development](#development)

## ⚡ Quick Start

### Prerequisites
- Python 3.9+
- MetaTrader 5 Terminal (installed and running)
- [Poetry](https://python-poetry.org/) (optional, but recommended)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/zeta.git
    cd zeta
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    # or
    poetry install
    ```

3.  **Configure**:
    Create a `config.yaml` file (see [Configuration](#configuration)).

4.  **Run**:
    ```bash
    python main.py
    ```

## 🏗️ Architecture

Zeta is composed of three main layers:

1.  **Core (`core/`)**:
    - `engine.py`: The heart of the bot. Runs the trading loop, manages threads, and executes strategies.
    - `mt5_client.py`: A robust, thread-safe wrapper around the `MetaTrader5` Python API.
    - `database.py`: Handles data persistence using SQLModel (SQLite).

2.  **Strategies (`strategies/`)**:
    - Contains the trading logic.
    - `base_strategy.py`: Abstract base class for all strategies.
    - `ma_crossover_strategy.py`: Example implementation of a Moving Average Crossover.

3.  **User Interface (`ui/`)**:
    - `main_window.py`: The PySide6 application window.
    - `log_handler.py`: Custom logging handler for displaying logs in the UI.

## 🧠 Strategies

Strategies are dynamically loaded from the `strategies/` directory.

### Creating a New Strategy

1.  Create a new file in `strategies/`, e.g., `my_strategy.py`.
2.  Inherit from `BaseStrategy`.
3.  Implement `check_signal(self, client, symbol)`.

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def check_signal(self, client, symbol):
        # Your logic here
        return "BUY" # or "SELL" or None
```

## ⚙️ Configuration

Create a `config.py` or `config.yaml` (implementation dependent) to set up your accounts.

```yaml
accounts:
  - account_id: 12345678
    password: "your_password"
    server: "MetaQuotes-Demo"
    enabled: true
```

## 👨‍💻 Development

### Running Tests
```bash
python -m unittest discover tests
```

### Performance Benchmarking
We encourage measuring performance before and after changes. Use `time.perf_counter()` or the `cProfile` module.

---
*Built with speed by Bolt.* ⚡
