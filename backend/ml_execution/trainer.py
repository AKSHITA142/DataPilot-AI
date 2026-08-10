import importlib
import inspect
import logging
from typing import Any, Dict, Optional, Type

from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    AdaBoostClassifier,
    AdaBoostRegressor,
)
from sklearn.linear_model import (
    LogisticRegression,
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    SGDRegressor,
    HuberRegressor,
    RidgeClassifier,
)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.gaussian_process import GaussianProcessRegressor

logger = logging.getLogger("datapilot.ml_execution.trainer")

# Dynamic import for XGBoost
try:
    xgb_mod = importlib.import_module("xgboost")
    XGBClassifier = getattr(xgb_mod, "XGBClassifier")
    XGBRegressor = getattr(xgb_mod, "XGBRegressor")
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

# Dynamic import for LightGBM
try:
    lgb_mod = importlib.import_module("lightgbm")
    LGBMClassifier = getattr(lgb_mod, "LGBMClassifier")
    LGBMRegressor = getattr(lgb_mod, "LGBMRegressor")
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

# Dynamic import for CatBoost
try:
    cat_mod = importlib.import_module("catboost")
    CatBoostClassifier = getattr(cat_mod, "CatBoostClassifier")
    CatBoostRegressor = getattr(cat_mod, "CatBoostRegressor")
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False


class ModelTrainerFactory:
    """Factory creating scikit-learn compatible model estimators for tabular tasks."""

    CLASSIFICATION_MODELS: Dict[str, Type[Any]] = {
        "svc": SVC,
        "supportvectorclassifier": SVC,
        "gaussiannb": GaussianNB,
        "multinomialnb": MultinomialNB,
        "bernoullinb": BernoulliNB,
        "naivebayes": GaussianNB,
        "knn": KNeighborsClassifier,
        "kneighborsclassifier": KNeighborsClassifier,
        "logisticregression": LogisticRegression,
        "decisiontree": DecisionTreeClassifier,
        "decisiontreeclassifier": DecisionTreeClassifier,
        "randomforest": RandomForestClassifier,
        "randomforestclassifier": RandomForestClassifier,
        "extratrees": ExtraTreesClassifier,
        "extratreesclassifier": ExtraTreesClassifier,
        "gradientboosting": GradientBoostingClassifier,
        "gradientboostingclassifier": GradientBoostingClassifier,
        "histgradientboosting": HistGradientBoostingClassifier,
        "histgradientboostingclassifier": HistGradientBoostingClassifier,
        "adaboost": AdaBoostClassifier,
        "adaboostclassifier": AdaBoostClassifier,
        "ridgeclassifier": RidgeClassifier,
        "mlp": MLPClassifier,
        "mlpclassifier": MLPClassifier,
        "lda": LinearDiscriminantAnalysis,
        "lineardiscriminantanalysis": LinearDiscriminantAnalysis,
        "qda": QuadraticDiscriminantAnalysis,
        "quadraticdiscriminantanalysis": QuadraticDiscriminantAnalysis,
    }

    REGRESSION_MODELS: Dict[str, Type[Any]] = {
        "linearregression": LinearRegression,
        "ridge": Ridge,
        "lasso": Lasso,
        "elasticnet": ElasticNet,
        "svr": SVR,
        "supportvectorregressor": SVR,
        "knnregressor": KNeighborsRegressor,
        "kneighborsregressor": KNeighborsRegressor,
        "decisiontreeregressor": DecisionTreeRegressor,
        "randomforestregressor": RandomForestRegressor,
        "extratreesregressor": ExtraTreesRegressor,
        "gradientboostingregressor": GradientBoostingRegressor,
        "histgradientboostingregressor": HistGradientBoostingRegressor,
        "adaboostregressor": AdaBoostRegressor,
        "gaussianprocessregressor": GaussianProcessRegressor,
        "mlpregressor": MLPRegressor,
        "sgdregressor": SGDRegressor,
        "huberregressor": HuberRegressor,
    }

    @classmethod
    def get_estimator(
        cls,
        model_name: str,
        task_type: str = "classification",
        params: Optional[Dict[str, Any]] = None,
        random_state: int = 42,
    ) -> Any:
        """Instantiates a scikit-learn estimator by name and task type with safe defaults."""
        name_clean = model_name.lower().replace(" ", "").replace("_", "").replace("-", "")
        params = params.copy() if params else {}

        # 1. Handle XGBoost
        if name_clean in ("xgboost", "xgbclassifier", "xgbregressor"):
            if HAS_XGBOOST:
                cls_model = XGBClassifier if task_type == "classification" else XGBRegressor
                params.setdefault("random_state", random_state)
                return cls_model(**params)
            else:
                logger.warning("XGBoost not installed; falling back to HistGradientBoosting")
                cls_model = HistGradientBoostingClassifier if task_type == "classification" else HistGradientBoostingRegressor
                params.setdefault("random_state", random_state)
                return cls_model(**params)

        # 2. Handle LightGBM
        if name_clean in ("lightgbm", "lgbmclassifier", "lgbmregressor"):
            if HAS_LIGHTGBM:
                cls_model = LGBMClassifier if task_type == "classification" else LGBMRegressor
                params.setdefault("random_state", random_state)
                return cls_model(**params)
            else:
                logger.warning("LightGBM not installed; falling back to HistGradientBoosting")
                cls_model = HistGradientBoostingClassifier if task_type == "classification" else HistGradientBoostingRegressor
                params.setdefault("random_state", random_state)
                return cls_model(**params)

        # 3. Handle CatBoost
        if name_clean in ("catboost", "catboostclassifier", "catboostregressor"):
            if HAS_CATBOOST:
                cls_model = CatBoostClassifier if task_type == "classification" else CatBoostRegressor
                params.setdefault("random_state", random_state)
                params.setdefault("verbose", 0)
                return cls_model(**params)
            else:
                logger.warning("CatBoost not installed; falling back to GradientBoosting")
                cls_model = GradientBoostingClassifier if task_type == "classification" else GradientBoostingRegressor
                params.setdefault("random_state", random_state)
                return cls_model(**params)

        # 4. Standard Model Lookup
        models_dict = cls.CLASSIFICATION_MODELS if task_type == "classification" else cls.REGRESSION_MODELS
        model_cls = models_dict.get(name_clean)

        if not model_cls:
            logger.warning(f"Unknown model name '{model_name}'; defaulting to RandomForest for task '{task_type}'")
            model_cls = RandomForestClassifier if task_type == "classification" else RandomForestRegressor

        # 5. Smart Defaults per Model Type
        if model_cls == SVC:
            params.setdefault("probability", True)
        elif model_cls == LogisticRegression:
            params.setdefault("max_iter", 1000)
        elif model_cls in (MLPClassifier, MLPRegressor):
            params.setdefault("max_iter", 500)

        # 6. Safely inspect parameters to pass random_state only if supported
        try:
            init_params = inspect.signature(model_cls.__init__).parameters
            if "random_state" in init_params and "random_state" not in params:
                params["random_state"] = random_state
        except Exception:
            pass

        return model_cls(**params)
