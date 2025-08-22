import os
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, JSON, Column


# --- Database Configuration ---
# The database file will be created in the root of the project.
# This can be moved to a more appropriate data directory later.
DATABASE_FILE = "trading_bot.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# The `connect_args` is important for SQLite to allow multiple threads
# to interact with the database, which is crucial for our multi-threaded UI app.
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


# --- Data Models ---

class Strategy(SQLModel, table=True):
    """
    Represents a trading strategy, including its parameters and status.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    parameters: Dict = Field(sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to trades
    # trades: List["Trade"] = Relationship(back_populates="strategy")


class Trade(SQLModel, table=True):
    """
    Represents a single trade executed by the bot.
    This log is essential for analytics, reporting, and performance tracking.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    mt5_ticket: int = Field(index=True, unique=True)
    strategy_id: int = Field(foreign_key="strategy.id")
    account_id: int # MT5 account number

    symbol: str = Field(index=True)
    trade_type: str  # e.g., "BUY", "SELL"
    volume: float

    open_price: float
    open_time: datetime

    close_price: Optional[float] = None
    close_time: Optional[datetime] = None

    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    commission: Optional[float] = None
    swap: Optional[float] = None
    profit: Optional[float] = None

    # Relationship to strategy
    # strategy: Strategy = Relationship(back_populates="trades")


class Account(SQLModel, table=True):
    """
    Stores dynamic information and metrics for each managed MT5 account.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(unique=True) # From config, the MT5 login
    server: str

    balance: float = 0.0
    equity: float = 0.0
    leverage: int = 0

    last_update_time: datetime = Field(default_factory=datetime.utcnow)


# --- Database Initialization and Session ---

def create_db_and_tables():
    """
    Initializes the database and creates all tables defined by the SQLModels.
    This function should be called once at application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """
    Provides a database session for performing transactions.
    """
    return Session(engine)


# --- Example Usage / Initialization ---
if __name__ == '__main__':
    # This allows running the script directly to initialize the database
    print("Initializing database...")
    create_db_and_tables()
    print(f"Database '{DATABASE_FILE}' and tables created successfully.")

    # Example of adding a strategy
    with get_session() as session:
        # Check if a default strategy already exists
        default_strategy = session.query(Strategy).filter(Strategy.name == "Default MA Crossover").first()
        if not default_strategy:
            example_strategy = Strategy(
                name="Default MA Crossover",
                description="A simple moving average crossover strategy.",
                parameters={"fast_ma": 10, "slow_ma": 50, "timeframe": "H1"},
                is_active=True
            )
            session.add(example_strategy)
            session.commit()
            print("Added example strategy to the database.")
        else:
            print("Example strategy already exists.")
