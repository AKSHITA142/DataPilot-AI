from typing import List, Optional, Dict, Any, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, MinMaxScaler, RobustScaler


class ColumnSelectorTransformer(BaseEstimator, TransformerMixin):
    """Transformer that filters columns by name or data type."""

    def __init__(self, columns: Optional[List[str]] = None, dtype_include: Optional[List[str]] = None):
        self.columns = columns
        self.dtype_include = dtype_include
        self.selected_columns_: List[str] = []

    def fit(self, X: pd.DataFrame, y=None):
        if self.columns is not None:
            self.selected_columns_ = [col for col in self.columns if col in X.columns]
        elif self.dtype_include is not None:
            self.selected_columns_ = list(X.select_dtypes(include=self.dtype_include).columns)
        else:
            self.selected_columns_ = list(X.columns)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_df = pd.DataFrame(X)
        if not self.selected_columns_:
            return X_df
        return X_df[self.selected_columns_]


class ImputerTransformer(BaseEstimator, TransformerMixin):
    """Custom scikit-learn compatible Imputer supporting mean, median, mode, constant."""

    def __init__(self, strategy: str = "mean", fill_value: Optional[Any] = None):
        self.strategy = strategy
        self.fill_value = fill_value
        self.imputers_: Dict[str, Any] = {}

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y=None):
        X_df = pd.DataFrame(X)
        for col in X_df.columns:
            if self.strategy == "mean" and pd.api.types.is_numeric_dtype(X_df[col]):
                val = X_df[col].mean()
            elif self.strategy == "median" and pd.api.types.is_numeric_dtype(X_df[col]):
                val = X_df[col].median()
            elif self.strategy == "mode":
                mode_res = X_df[col].mode()
                val = mode_res.iloc[0] if not mode_res.empty else (self.fill_value or 0)
            elif self.strategy == "constant":
                val = self.fill_value if self.fill_value is not None else 0
            else:
                val = X_df[col].median() if pd.api.types.is_numeric_dtype(X_df[col]) else "missing"

            self.imputers_[col] = val
        return self

    def transform(self, X: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        X_df = pd.DataFrame(X).copy()
        for col, val in self.imputers_.items():
            if col in X_df.columns:
                X_df[col] = X_df[col].fillna(val)
        return X_df


class CategoricalEncoderTransformer(BaseEstimator, TransformerMixin):
    """Custom encoder supporting onehot, ordinal, frequency, and target encoding."""

    def __init__(self, method: str = "onehot"):
        self.method = method
        self.encoder_: Optional[Any] = None
        self.freq_maps_: Dict[str, Dict[Any, float]] = {}
        self.encoded_columns_: List[str] = []

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y=None):
        X_df = pd.DataFrame(X)
        categorical_cols = list(X_df.select_dtypes(include=["object", "category"]).columns)

        if not categorical_cols:
            return self

        if self.method == "onehot":
            self.encoder_ = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
            self.encoder_.fit(X_df[categorical_cols])
        elif self.method == "ordinal":
            self.encoder_ = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
            self.encoder_.fit(X_df[categorical_cols])
        elif self.method == "frequency":
            for col in categorical_cols:
                freqs = X_df[col].value_counts(normalize=True).to_dict()
                self.freq_maps_[col] = freqs

        return self

    def transform(self, X: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        X_df = pd.DataFrame(X).copy()
        categorical_cols = list(X_df.select_dtypes(include=["object", "category"]).columns)

        if not categorical_cols:
            return X_df

        if self.method == "onehot" and self.encoder_:
            encoded_arr = self.encoder_.transform(X_df[categorical_cols])
            encoded_cols = self.encoder_.get_feature_names_out(categorical_cols)
            encoded_df = pd.DataFrame(encoded_arr, columns=encoded_cols, index=X_df.index)
            X_df = X_df.drop(columns=categorical_cols).join(encoded_df)
        elif self.method == "ordinal" and self.encoder_:
            X_df[categorical_cols] = self.encoder_.transform(X_df[categorical_cols])
        elif self.method == "frequency":
            for col in categorical_cols:
                freq_map = self.freq_maps_.get(col, {})
                X_df[col] = X_df[col].map(freq_map).fillna(0.0)

        return X_df


class FeatureScalerTransformer(BaseEstimator, TransformerMixin):
    """Custom scaler supporting standard, minmax, and robust scaling on numeric columns."""

    def __init__(self, method: str = "standard"):
        self.method = method
        self.scaler_: Optional[Any] = None
        self.numeric_cols_: List[str] = []

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y=None):
        X_df = pd.DataFrame(X)
        self.numeric_cols_ = list(X_df.select_dtypes(include=[np.number]).columns)

        if not self.numeric_cols_:
            return self

        if self.method == "standard":
            self.scaler_ = StandardScaler()
        elif self.method == "minmax":
            self.scaler_ = MinMaxScaler()
        elif self.method == "robust":
            self.scaler_ = RobustScaler()
        else:
            self.scaler_ = StandardScaler()

        self.scaler_.fit(X_df[self.numeric_cols_])
        return self

    def transform(self, X: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        X_df = pd.DataFrame(X).copy()
        if self.scaler_ and self.numeric_cols_:
            valid_cols = [c for c in self.numeric_cols_ if c in X_df.columns]
            if valid_cols:
                X_df[valid_cols] = self.scaler_.transform(X_df[valid_cols])
        return X_df
