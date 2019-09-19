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
GAMMA custom pipelines
"""

import logging
from abc import ABC, abstractmethod
from typing import *

import pandas as pd
from sklearn.base import BaseEstimator

from gamma.sklearndf import (
    BaseEstimatorDF,
    BasePredictorDF,
    ClassifierDF,
    RegressorDF,
    TransformerDF,
)

log = logging.getLogger(__name__)

__all__ = [
    "EstimatorPipelineDF",
    "PredictorPipelineDF",
    "RegressorPipelineDF",
    "ClassifierPipelineDF",
]

T_FinalEstimatorDF = TypeVar("T_FinalEstimatorDF", bound=BaseEstimatorDF)
T_FinalPredictorDF = TypeVar("T_FinalPredictorDF", bound=BasePredictorDF)
T_FinalRegressorDF = TypeVar("T_FinalRegressorDF", bound=RegressorDF)
T_FinalClassifierDF = TypeVar("T_FinalClassifierDF", bound=ClassifierDF)


class EstimatorPipelineDF(
    BaseEstimatorDF, BaseEstimator, Generic[T_FinalEstimatorDF], ABC
):
    """
    A data frame enabled pipeline with an optional preprocessing step and a
    mandatory estimator step.

    :param preprocessing: the preprocessing step in the pipeline (defaults to ``None``)
    """

    def __init__(self, preprocessing: Optional[TransformerDF] = None) -> None:
        super().__init__()

        if preprocessing is not None and not isinstance(preprocessing, TransformerDF):
            raise TypeError(
                "arg preprocessing expected to be a TransformerDF but is a "
                f"{type(preprocessing).__name__}"
            )

        self.preprocessing = preprocessing

    @property
    @abstractmethod
    def final_estimator_(self) -> T_FinalEstimatorDF:
        """
        The final estimator following the preprocessing step.
        """
        pass

    @property
    def preprocessing_param_(self) -> str:
        """
        The name of the preprocessing step parameter.
        """
        return "preprocessing"

    @property
    @abstractmethod
    def final_estimator_param_(self) -> str:
        """
        The name of the estimator step parameter.
        """
        pass

    # noinspection PyPep8Naming
    def fit(
        self,
        X: pd.DataFrame,
        y: Optional[Union[pd.Series, pd.DataFrame]] = None,
        **fit_params,
    ) -> "EstimatorPipelineDF[T_FinalEstimatorDF]":
        self.final_estimator_.fit(
            self._pre_fit_transform(X, y, **fit_params), y, **fit_params
        )
        return self

    @property
    def is_fitted(self) -> bool:
        return self.preprocessing.is_fitted and self.final_estimator_.is_fitted

    def _get_features_in(self) -> pd.Index:
        if self.preprocessing is not None:
            return self.preprocessing.features_in
        else:
            return self.final_estimator_.features_in

    # noinspection PyPep8Naming
    def _pre_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.preprocessing is not None:
            return self.preprocessing.transform(X)
        else:
            return X

    # noinspection PyPep8Naming
    def _pre_fit_transform(
        self, X: pd.DataFrame, y: pd.Series, **fit_params
    ) -> pd.DataFrame:
        if self.preprocessing is not None:
            return self.preprocessing.fit_transform(X, y, **fit_params)
        else:
            return X


class PredictorPipelineDF(
    EstimatorPipelineDF[T_FinalPredictorDF], Generic[T_FinalPredictorDF], ABC
):

    # noinspection PyPep8Naming
    def predict(
        self, X: pd.DataFrame, **predict_params
    ) -> Union[pd.Series, pd.DataFrame]:
        return self.final_estimator_.predict(self._pre_transform(X), **predict_params)

    # noinspection PyPep8Naming
    def fit_predict(self, X: pd.DataFrame, y: pd.Series, **fit_params) -> pd.Series:
        return self.final_estimator_.fit_predict(
            self._pre_fit_transform(X, y, **fit_params), y, **fit_params
        )

    # noinspection PyPep8Naming
    def score(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
        sample_weight: Optional[Any] = None,
    ) -> float:
        if sample_weight is None:
            return self.final_estimator_.score(self._pre_transform(X), y)
        else:
            return self.final_estimator_.score(
                self._pre_transform(X), y, sample_weight=sample_weight
            )

    @property
    def n_outputs(self) -> int:
        return self.final_estimator_.n_outputs


class RegressorPipelineDF(
    PredictorPipelineDF[T_FinalRegressorDF], RegressorDF, Generic[T_FinalRegressorDF]
):
    """
    A data frame enabled pipeline with an optional preprocessing step and a
    mandatory regression step.

    :param preprocessing: the preprocessing step in the pipeline (defaults to ``None``)
    :param regressor: the classifier used in the pipeline
    :type regressor: :class:`.RegressorDF`
    """

    def __init__(
        self,
        regressor: T_FinalRegressorDF,
        preprocessing: Optional[TransformerDF] = None,
    ) -> None:
        super().__init__(preprocessing=preprocessing)

        if not isinstance(regressor, RegressorDF):
            raise TypeError(
                f"arg regressor expected to be a {RegressorDF.__name__} but is a "
                f"{type(regressor).__name__}"
            )

        self.regressor = regressor

    @property
    def final_estimator_(self) -> T_FinalRegressorDF:
        return self.regressor

    @property
    def final_estimator_param_(self) -> str:
        return "regressor"


class ClassifierPipelineDF(
    PredictorPipelineDF[T_FinalClassifierDF], ClassifierDF, Generic[T_FinalClassifierDF]
):
    """
    A data frame enabled pipeline with an optional preprocessing step and a
    mandatory classification step.

    :param preprocessing: the preprocessing step in the pipeline (defaults to ``None``)
    :param classifier: the classifier used in the pipeline
    :type classifier: :class:`.ClassifierDF`
    """

    def __init__(
        self,
        classifier: T_FinalClassifierDF,
        preprocessing: Optional[TransformerDF] = None,
    ) -> None:
        super().__init__(preprocessing=preprocessing)

        if not isinstance(classifier, ClassifierDF):
            raise TypeError(
                f"arg predictor expected to be a {ClassifierDF.__name__} but is a "
                f"{type(classifier).__name__}"
            )
        self.classifier = classifier

    @property
    def final_estimator_(self) -> T_FinalClassifierDF:
        return self.classifier

    @property
    def final_estimator_param_(self) -> str:
        return "classifier"

    # noinspection PyPep8Naming
    def predict_proba(self, X: pd.DataFrame) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        return self.classifier.predict_proba(self._pre_transform(X))

    # noinspection PyPep8Naming
    def predict_log_proba(
        self, X: pd.DataFrame
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        return self.classifier.predict_log_proba(self._pre_transform(X))

    # noinspection PyPep8Naming
    def decision_function(self, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        return self.classifier.decision_function(self._pre_transform(X))
