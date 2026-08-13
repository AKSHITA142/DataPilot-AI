"""Smart target column detection using semantic matching, heuristics, and fallbacks."""

from typing import Optional, List
import difflib
import re
import pandas as pd


class SmartTargetDetector:
    """Detects the most likely target column from a DataFrame using multi-strategy matching.

    Strategy priority:
    1. User explicit target → trust it
    2. Semantic keyword extraction from mission text → fuzzy-match against column names
    3. Common target name patterns (target, label, class, price, churn, y, outcome, ...)
    4. Last column fallback
    """

    # Well-known target column names across domains
    COMMON_TARGET_NAMES = [
        "target", "label", "class", "y", "outcome", "result",
        "price", "churn", "is_churn", "survived", "diagnosis",
        "default", "fraud", "spam", "sentiment", "rating",
        "salary", "income", "revenue", "sales", "cost",
        "status", "category", "type", "grade",
    ]

    # Words to strip from mission text before matching (stop words)
    _STOP_WORDS = frozenset({
        "a", "an", "the", "is", "are", "was", "were", "be", "been",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "and", "or", "not", "no", "but", "if", "so", "as", "it",
        "this", "that", "these", "those", "my", "your", "their",
        "will", "would", "can", "could", "should", "shall", "may",
        "do", "does", "did", "has", "have", "had",
        "predict", "classify", "estimate", "model", "build",
        "using", "based", "data", "dataset", "value", "values",
        "high", "low", "maximum", "minimum", "optimize",
        "machine", "learning", "individual", "each", "every",
        "want", "need", "like", "use", "find", "determine",
        "attributes", "features", "columns", "demographic",
    })

    @classmethod
    def detect_target(
        cls,
        df: pd.DataFrame,
        user_mission: str = "",
        user_target: Optional[str] = None,
    ) -> Optional[str]:
        """Detects the best target column.

        Args:
            df: The raw DataFrame.
            user_mission: Free-text mission/goal from the user (e.g. "Predict income").
            user_target: Explicit target column name from the user (highest priority).

        Returns:
            The detected target column name, or None if detection fails.
        """
        if df.empty or len(df.columns) == 0:
            return None

        columns = list(df.columns)
        col_lower_map = {c.lower().strip(): c for c in columns}

        # --- Strategy 1: User explicit target ---
        if user_target and user_target.strip():
            clean = user_target.strip()
            if clean in columns:
                return clean
            # Case-insensitive match
            if clean.lower() in col_lower_map:
                return col_lower_map[clean.lower()]

        # --- Strategy 2: Semantic keyword extraction from mission text ---
        if user_mission and user_mission.strip():
            match = cls._semantic_match(user_mission, columns, col_lower_map)
            if match:
                return match

        # --- Strategy 3: Common target name patterns ---
        for name in cls.COMMON_TARGET_NAMES:
            if name in col_lower_map:
                return col_lower_map[name]

        # --- Strategy 4: Last column fallback ---
        if columns:
            return columns[-1]

        return None

    @classmethod
    def _semantic_match(
        cls,
        mission: str,
        columns: List[str],
        col_lower_map: dict,
    ) -> Optional[str]:
        """Extract keywords from mission text and fuzzy-match against column names."""
        # Tokenise mission into lowercase words
        tokens = re.findall(r"[a-zA-Z_]+", mission.lower())
        # Remove stop words
        keywords = [t for t in tokens if t not in cls._STOP_WORDS and len(t) > 1]

        if not keywords:
            return None

        col_lower_list = list(col_lower_map.keys())

        # Pass 1: Exact substring match (keyword == column name or keyword in column name)
        for kw in keywords:
            if kw in col_lower_map:
                return col_lower_map[kw]
            for cl in col_lower_list:
                if kw in cl or cl in kw:
                    return col_lower_map[cl]

        # Pass 2: Fuzzy match using difflib (threshold 0.6)
        best_score = 0.0
        best_col: Optional[str] = None
        for kw in keywords:
            matches = difflib.get_close_matches(kw, col_lower_list, n=1, cutoff=0.6)
            if matches:
                score = difflib.SequenceMatcher(None, kw, matches[0]).ratio()
                if score > best_score:
                    best_score = score
                    best_col = col_lower_map[matches[0]]

        return best_col
