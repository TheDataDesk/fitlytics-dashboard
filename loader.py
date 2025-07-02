# loader.py
import pandas as pd

def load_orders() -> pd.DataFrame:
    """Load orders.parquet from the data folder."""
    return pd.read_parquet("data/orders.parquet")

def load_products() -> pd.DataFrame:
    """Load products.parquet from the data folder."""
    return pd.read_parquet("data/products.parquet")
