"""
GAMMA custom two-step pipelines
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import *

import pandas as pd
from sklearn.base import BaseEstimator

from .. import BaseEstimatorDF, ClassifierDF, LearnerDF, RegressorDF, TransformerDF

log = logging.getLogger(__name__)

__all__ = ["LearnerPipelineDF", "RegressorPipelineDF", "ClassifierPipelineDF"]

T = TypeVar("T")
T_FinalEstimatorDF = TypeVar("T_FinalEstimatorDF", bound=BaseEstimatorDF)
T_FinalLearnerDF = TypeVar("T_FinalLearnerDF", bound=LearnerDF)
T_FinalRegressorDF = TypeVar("T_FinalRegressorDF", bound=RegressorDF)
T_FinalClassifierDF = TypeVar("T_FinalClassifierDF", bound=ClassifierDF)


class _BaseEstimatorPipelineDF(
    BaseEstimator, BaseEstimatorDF, Generic[T_FinalEstimatorDF], metaclass=ABCMeta
):
    """
    A data frame enabled pipeline with an optional preprocessing step and a
    mandatory estimator step.

    :param preprocessing: the preprocessing step in the pipeline (defaults to ``None``)
    """

    def __init__(self, *, preprocessing: Optional[TransformerDF] = None) -> None:
        super().__init__()

        if preprocessing is not None and not isinstance(preprocessing, TransformerDF):
            raise TypeError(
                "arg preprocessing expected to be a TransformerDF but is a "
                f"{type(preprocessing).__name__}"
            )

        self.preprocessing = preprocessing

    @property
    @abstractmethod
    def final_estimator(self) -> T_FinalEstimatorDF:
        """
        The final estimator following the preprocessing step.
        """
        pass

    @property
    def preprocessing_name(self) -> str:
        """
        The name of the preprocessing step parameter.
        """
        return "preprocessing"

    @property
    @abstractmethod
    def final_estimator_name(self) -> str:
        """
        The name of the estimator step parameter.
        """
        pass

    # noinspection PyPep8Naming
    def fit(
        self: T,
        X: pd.DataFrame,
        y: Optional[Union[pd.Series, pd.DataFrame]] = None,
        feature_sequence: Optional[pd.Index] = None,
        sample_weight: Optional[pd.Series] = None,
        **fit_params,
    ) -> T:
        """
        Fit this pipeline using the given inputs.

        :param X: input data frame with observations as rows and features as columns
        :param y: an optional series or data frame with one or more outputs
        :param feature_sequence: the order in which features should be passed to the \
            final estimator (optional)
        :param sample_weight: sample weights for observations, to be passed to the final \
            estimator (optional)
        :param fit_params: additional keyword parameters as required by specific \
            estimator implementations
        :return: ``self``
        """
        self: _BaseEstimatorPipelineDF  # support type hinting in PyCharm

        X_preprocessed: pd.DataFrame = self._pre_fit_transform(X, y, **fit_params)

        if feature_sequence is not None:
            if not feature_sequence.is_unique:
                raise ValueError("arg feature_sequence contains duplicate values")
            features = X_preprocessed.columns
            if not features.is_unique:
                raise ValueError(
                    "arg X has columns with duplicate names after preprocessing"
                )
            features_reordered = feature_sequence.intersection(features, sort=False)
            if len(features_reordered) < len(features):
                raise ValueError(
                    "arg feature_sequence misses features: "
                    f"{', '.join(features.difference(feature_sequence))}"
                )
            X_preprocessed = X_preprocessed.reindex(columns=features_reordered)

        if sample_weight is None:
            self.final_estimator.fit(X_preprocessed, y, **fit_params)
        else:
            self.final_estimator.fit(
                X_preprocessed, y, sample_weight=sample_weight, **fit_params
            )

        return self

    @property
    def features_out(self) -> pd.Index:
        """
        Pandas column index of all features resulting from the preprocessing step.

        Same as :attr:`.features_in` if the preprocessing step is ``None``.
        """
        if self.preprocessing is not None:
            return self.preprocessing.features_out
        else:
            return self.features_in.rename(TransformerDF.COL_FEATURE_OUT)

    @property
    def is_fitted(self) -> bool:
        return (
            self.preprocessing is None or self.preprocessing.is_fitted
        ) and self.final_estimator.is_fitted

    def _get_features_in(self) -> pd.Index:
        if self.preprocessing is not None:
            return self.preprocessing.features_in
        else:
            return self.final_estimator.features_in

    def _get_n_outputs(self) -> int:
        if self.preprocessing is not None:
            return self.preprocessing.n_outputs
        else:
            return self.final_estimator.n_outputs

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


class LearnerPipelineDF(
    _BaseEstimatorPipelineDF[T_FinalLearnerDF],
    LearnerDF,
    Generic[T_FinalLearnerDF],
    metaclass=ABCMeta,
):

    # noinspection PyPep8Naming
    def predict(
        self, X: pd.DataFrame, **predict_params
    ) -> Union[pd.Series, pd.DataFrame]:
        return self.final_estimator.predict(self._pre_transform(X), **predict_params)

    # noinspection PyPep8Naming
    def fit_predict(
        self, X: pd.DataFrame, y: pd.Series, **fit_params
    ) -> Union[pd.Series, pd.DataFrame]:
        return self.final_estimator.fit_predict(
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
            return self.final_estimator.score(self._pre_transform(X), y)
        else:
            return self.final_estimator.score(
                self._pre_transform(X), y, sample_weight=sample_weight
            )


class RegressorPipelineDF(
    LearnerPipelineDF[T_FinalRegressorDF], RegressorDF, Generic[T_FinalRegressorDF]
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
        *,
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
    def final_estimator(self) -> T_FinalRegressorDF:
        return self.regressor

    @property
    def final_estimator_name(self) -> str:
        return "regressor"


class ClassifierPipelineDF(
    LearnerPipelineDF[T_FinalClassifierDF], ClassifierDF, Generic[T_FinalClassifierDF]
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
        *,
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
    def final_estimator(self) -> T_FinalClassifierDF:
        return self.classifier

    @property
    def final_estimator_name(self) -> str:
        return "classifier"

    # noinspection PyPep8Naming
    def predict_proba(
        self, X: pd.DataFrame, **predict_params
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        return self.classifier.predict_proba(self._pre_transform(X), **predict_params)

    # noinspection PyPep8Naming
    def predict_log_proba(
        self, X: pd.DataFrame, **predict_params
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        return self.classifier.predict_log_proba(
            self._pre_transform(X), **predict_params
        )

    # noinspection PyPep8Naming
    def decision_function(
        self, X: pd.DataFrame, **predict_params
    ) -> Union[pd.Series, pd.DataFrame]:
        return self.classifier.decision_function(
            self._pre_transform(X), **predict_params
        )
