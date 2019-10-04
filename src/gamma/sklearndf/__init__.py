#
# NOT FOR CLIENT USE!
#
# This is a pre-release library under development. Handling of IP rights is still
# being investigated. To avoid causing any potential IP disputes or issues, DO NOT USE
# ANY OF THIS CODE ON A CLIENT PROJECT, not even in modified form.
#
# Please direct any queries to any of:
# - Jan Ittner
# - Jörg Schneider
# - Florent Martin
#

"""
The Gamma scikit-learn DF library.

Enhances scikit-learn estimators for advanced support of data frames.

The abstract class :class:`BaseEstimatorDF` and its subclasses wrap subclasses of
:class:`~sklearn.base.BaseEstimator` such that transform methods return data frames
with feature names in the column index.

The enhanced base estimators also offer attributes
:attr:`~BaseEstimatorDF.features_in`, :attr:`~TransformerDF.features_out`, and
:attr:`~TransformerDF.features_original`, which enable tracing features back to the
original inputs even across complex pipelines.
"""

import logging
from abc import ABC, abstractmethod
from typing import *

import pandas as pd
from sklearn.base import (
    BaseEstimator,
    ClassifierMixin,
    clone,
    RegressorMixin,
    TransformerMixin,
)

log = logging.getLogger(__name__)

__all__ = [
    "BaseEstimatorDF",
    "BaseLearnerDF",
    "ClassifierDF",
    "RegressorDF",
    "TransformerDF",
]

#
# type variables
#

# noinspection PyShadowingBuiltins
_T = TypeVar("_T")
_T_EstimatorDF = TypeVar("_T_EstimatorDF")

#
# class definitions
#


class BaseEstimatorDF(ABC):
    """
    Mix-in class for scikit-learn estimators with enhanced support for data frames.
    """

    COL_FEATURE_IN = "feature_in"

    def __init__(self) -> None:
        super().__init__()
        if not isinstance(self, BaseEstimator):
            raise TypeError(
                f"class {type(self).__name__} is required to inherit from class "
                f"{BaseEstimator.__name__}"
            )

    @property
    def root_estimator(self) -> BaseEstimator:
        """
        If this estimator delegates to another estimator in one or more layers,
        return the innermost wrapped estimator; otherwise, return ``self``.

        :return: the original estimator that this estimator delegates to
        """

        estimator = cast(BaseEstimator, self)

        while hasattr(estimator, "delegate_estimator"):
            estimator: BaseEstimator = estimator.delegate_estimator

        return estimator

    # noinspection PyPep8Naming
    @abstractmethod
    def fit(
        self: _T,
        X: pd.DataFrame,
        y: Optional[Union[pd.Series, pd.DataFrame]] = None,
        **fit_params,
    ) -> _T:
        pass

    @property
    @abstractmethod
    def is_fitted(self) -> bool:
        """`True` if this estimator is fitted, else `False`"""
        pass

    @property
    def features_in(self) -> pd.Index:
        """
        The pandas column index with the names of the features this estimator has been
        fitted on; raises an `AttributeError` if this estimator is not fitted
        """
        self._ensure_fitted()
        return self._get_features_in().rename(self.COL_FEATURE_IN)

    @property
    def n_outputs(self) -> int:
        """
        The number of outputs this estimator has been fitted on;
        raises an `AttributeError` if this estimator is not fitted
        """
        self._ensure_fitted()
        return self._get_n_outputs()

    @abstractmethod
    def get_params(self, deep=True) -> Dict[str, Any]:
        """
        Get parameters for this estimator.

        :param deep: if ``True``, return the parameters for this estimator and \
        contained sub-objects that are estimators

        :return: mapping of the parameter names to their values
        """
        pass

    @abstractmethod
    def set_params(self: _T, **kwargs) -> _T:
        """
        Set the parameters of this estimator.

        Valid parameter keys can be listed with ``get_params()``.

        :returns self
        """
        pass

    def clone(self: _T_EstimatorDF) -> _T_EstimatorDF:
        """
        Make an unfitted clone of this estimator.

        :return: the unfitted clone
        """
        return clone(self)

    def _ensure_fitted(self) -> None:
        # raise an AttributeError if this transformer is not fitted
        if not self.is_fitted:
            raise AttributeError("estimator is not fitted")

    @abstractmethod
    def _get_features_in(self) -> pd.Index:
        # get the input columns as a pandas Index
        pass

    @abstractmethod
    def _get_n_outputs(self) -> int:
        # get the number of outputs this estimator has been fitted to
        pass


class BaseLearnerDF(BaseEstimatorDF, ABC):
    """
    Base mix-in class for scikit-learn predictors with enhanced support for data frames.
    """

    # noinspection PyPep8Naming
    @abstractmethod
    def predict(
        self, X: pd.DataFrame, **predict_params
    ) -> Union[pd.Series, pd.DataFrame]:
        pass

    # noinspection PyPep8Naming
    @abstractmethod
    def fit_predict(self, X: pd.DataFrame, y: pd.Series, **fit_params) -> pd.Series:
        pass

    # noinspection PyPep8Naming
    @abstractmethod
    def score(
        self, X: pd.DataFrame, y: pd.Series, sample_weight: Optional[pd.Series] = None
    ) -> float:
        pass


class TransformerDF(BaseEstimatorDF, TransformerMixin, ABC):
    """
    Mix-in class for scikit-learn transformers with enhanced support for data frames.
    """

    COL_FEATURE_OUT = "feature_out"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._features_original = None

    # noinspection PyPep8Naming
    @abstractmethod
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        pass

    # noinspection PyPep8Naming
    def fit_transform(
        self, X: pd.DataFrame, y: Optional[pd.Series] = None, **fit_params
    ) -> pd.DataFrame:
        return self.fit(X, y, **fit_params).transform(X)

    # noinspection PyPep8Naming
    @abstractmethod
    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        pass

    @property
    def features_original(self) -> pd.Series:
        """
        Pandas series mapping the output features (the series's index) to the
        original input features (the series' values)
        """
        self._ensure_fitted()
        if self._features_original is None:
            self._features_original = (
                self._get_features_original()
                .rename(self.COL_FEATURE_IN)
                .rename_axis(index=self.COL_FEATURE_OUT)
            )
        return self._features_original

    @property
    def features_out(self) -> pd.Index:
        """
        Pandas column index with the names of the features produced by this transformer
        """
        self._ensure_fitted()
        return self._get_features_out().rename(self.COL_FEATURE_OUT)

    @abstractmethod
    def _get_features_original(self) -> pd.Series:
        """
        :return: a mapping from this transformer's output columns to the original
        columns as a series
        """
        pass

    def _get_features_out(self) -> pd.Index:
        # default behaviour: get index returned by features_original
        return self.features_original.index


class RegressorDF(BaseLearnerDF, RegressorMixin, ABC):
    """
    Mix-in class for scikit-learn regressors with enhanced support for data frames.
    """


class ClassifierDF(BaseLearnerDF, ClassifierMixin, ABC):
    """
    Mix-in class for scikit-learn classifiers with enhanced support for data frames.
    """

    # noinspection PyPep8Naming
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        pass

    # noinspection PyPep8Naming
    @abstractmethod
    def predict_log_proba(
        self, X: pd.DataFrame
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        pass

    # noinspection PyPep8Naming
    @abstractmethod
    def decision_function(self, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        pass
