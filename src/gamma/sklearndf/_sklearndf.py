"""
Core implementation of :mod:`gamma.sklearndf`
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import *

import pandas as pd
from sklearn.base import (
    BaseEstimator,
    ClassifierMixin,
    RegressorMixin,
    TransformerMixin,
    clone,
)

from gamma.common.fit import FittableMixin, T_Self

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

T_EstimatorDF = TypeVar("T_EstimatorDF")

#
# class definitions
#


class BaseEstimatorDF(FittableMixin[pd.DataFrame], metaclass=ABCMeta):
    """
    Mix-in class for scikit-learn estimators with enhanced support for data frames.
    """

    COL_FEATURE_IN = "feature_in"

    def __new__(cls: Type["BaseEstimatorDF"], *args, **kwargs) -> object:
        # make sure this DF estimator also is a subclass of
        if not issubclass(cls, BaseEstimator):
            raise TypeError(
                f"class {cls.__name__} is required to be "
                f"a subclass of {BaseEstimator.__name__}"
            )

        return super().__new__(cls, *args, **kwargs)

    @property
    def root_estimator(self) -> BaseEstimator:
        """
        If this estimator delegates to another estimator in one or more layers,
        return the innermost wrapped estimator; otherwise, return ``self``.

        :return: the original estimator that this estimator delegates to
        """

        estimator = cast(BaseEstimator, self)

        while True:
            delegate: BaseEstimator = getattr(
                estimator, "delegate_estimator", estimator
            )
            if delegate is estimator:
                # no delegate defined, or estimator is its own delegate
                # (which should not happen)
                return estimator
            estimator = delegate

    # noinspection PyPep8Naming
    @abstractmethod
    def fit(
        self: T_Self,
        X: pd.DataFrame,
        y: Optional[Union[pd.Series, pd.DataFrame]] = None,
        **fit_params,
    ) -> T_Self:
        pass

    @property
    def features_in(self) -> pd.Index:
        """
        The pandas column index with the names of the features this estimator has been
        fitted on; raises an ``AttributeError`` if this estimator is not fitted
        """
        self._ensure_fitted()
        return self._get_features_in().rename(self.COL_FEATURE_IN)

    @property
    def n_outputs(self) -> int:
        """
        The number of outputs this estimator has been fitted on;
        raises an ``AttributeError`` if this estimator is not fitted
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
    def set_params(self: T_Self, **kwargs) -> T_Self:
        """
        Set the parameters of this estimator.

        Valid parameter keys can be listed with ``get_params()``.

        :returns self
        """
        pass

    def clone(self: T_EstimatorDF) -> T_EstimatorDF:
        """
        Make an unfitted clone of this estimator.

        :return: the unfitted clone
        """
        return clone(self)

    @abstractmethod
    def _get_features_in(self) -> pd.Index:
        # get the input columns as a pandas Index
        pass

    @abstractmethod
    def _get_n_outputs(self) -> int:
        # get the number of outputs this estimator has been fitted to
        pass


class BaseLearnerDF(BaseEstimatorDF, metaclass=ABCMeta):
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


class TransformerDF(BaseEstimatorDF, TransformerMixin, metaclass=ABCMeta):
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


class RegressorDF(BaseLearnerDF, RegressorMixin, metaclass=ABCMeta):
    """
    Mix-in class for scikit-learn regressors with enhanced support for data frames.
    """


class ClassifierDF(BaseLearnerDF, ClassifierMixin, metaclass=ABCMeta):
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
