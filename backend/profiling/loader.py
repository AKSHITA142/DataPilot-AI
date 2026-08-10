import os
import csv
from typing import Tuple, Dict, Any, Optional
import pandas as pd


class DataLoader:
    """Utility class for validating and loading CSV and Parquet files into DataFrames."""

    @staticmethod
    def detect_delimiter(file_path: str) -> str:
        """Detect delimiter (comma, tab, semicolon) for CSV files."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sample = f.read(4096)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample, delimiters=[",", "\t", ";", "|"])
                return dialect.delimiter
        except Exception:
            return ","

    @classmethod
    def load_data(cls, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Loads CSV or Parquet file into a pandas DataFrame.
        Returns (DataFrame, metadata_dict).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found at path: {file_path}")

        file_size_bytes = os.path.getsize(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".csv", ".txt"]:
            delimiter = cls.detect_delimiter(file_path)
            df = pd.read_csv(file_path, delimiter=delimiter)
        elif ext in [".parquet", ".pq"]:
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Only .csv and .parquet are supported.")

        metadata = {
            "filename": os.path.basename(file_path),
            "file_size_bytes": file_size_bytes,
            "row_count": len(df),
            "column_count": len(df.columns),
            "format": ext.lstrip("."),
        }
        return df, metadata
