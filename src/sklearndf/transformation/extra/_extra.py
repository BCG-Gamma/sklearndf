"""
Core implementation of :mod:`sklearndf.transformation.extra`
"""

import logging
from abc import ABCMeta
from typing import Optional, TypeVar, Union

import pandas as pd
from boruta import BorutaPy
from sklearn.base import BaseEstimator

from pytools.api import AllTracker, inheritdoc

from ... import TransformerDF
from ..._wrapper import _MetaEstimatorWrapperDF, make_df_transformer
from .._wrapper import _ColumnSubsetTransformerWrapperDF, _NDArrayTransformerWrapperDF

log = logging.getLogger(__name__)

__all__ = ["OutlierRemoverDF", "BorutaDF"]


#
# type variables
#

T_Self = TypeVar("T_Self")


#
# Ensure all symbols introduced below are included in __all__
#

__tracker = AllTracker(globals())


#
# Class definitions
#


@inheritdoc(match="[see superclass]")
class OutlierRemoverDF(TransformerDF, BaseEstimator):
    """
    Remove outliers according to Tukey's method.

    A sample is considered an outlier if it is outside the range
    :math:`[Q_1 - iqr\\_ multiple(Q_3-Q_1), Q_3 + iqr\\_ multiple(Q_3-Q_1)]`
    where :math:`Q_1` and :math:`Q_3` are the lower and upper quartiles.

    :param iqr_multiple: the multiple used to define the range of non-outlier
      samples in the above explanation (defaults to 3.0 as per Tukey's definition of
      far outliers)
    """

    def __init__(self, iqr_multiple: float = 3.0):
        super().__init__()
        if iqr_multiple < 0.0:
            raise ValueError(f"arg iqr_multiple is negative: {iqr_multiple}")
        self.iqr_multiple = iqr_multiple
        self.threshold_low_ = None
        self.threshold_high_ = None
        self._features_original = None

    # noinspection PyPep8Naming
    def fit(
        self: T_Self,
        X: pd.DataFrame,
        y: Optional[Union[pd.Series, pd.DataFrame]] = None,
        **fit_params,
    ) -> T_Self:
        """
        Fit the transformer.

        :return: the fitted transformer
        """

        self: OutlierRemoverDF  # support type hinting in PyCharm

        q1: pd.Series = X.quantile(q=0.25)
        q3: pd.Series = X.quantile(q=0.75)
        threshold_iqr: pd.Series = (q3 - q1) * self.iqr_multiple
        self.threshold_low_ = q1 - threshold_iqr
        self.threshold_high_ = q3 + threshold_iqr
        self._features_original = X.columns.to_series()
        return self

    # noinspection PyPep8Naming
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Return ``X`` with outliers are replaced by ``NaN``.

        :return: the ``X`` where outliers are replaced by ``NaN``
        """
        return X.where(cond=(X >= self.threshold_low_) & (X <= self.threshold_high_))

    # noinspection PyPep8Naming
    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform is not implemented.

        :raises NotImplementedError:
        """
        raise NotImplementedError("inverse transform is not implemented")

    @property
    def is_fitted(self) -> bool:
        """[see superclass]"""
        return self.threshold_low_ is not None

    def _get_features_original(self) -> pd.Series:
        return self._features_original

    def _get_features_in(self) -> pd.Index:
        return self.feature_names_original_.index

    def _get_n_outputs(self) -> int:
        return 0


class _BorutaPyWrapperDF(
    _MetaEstimatorWrapperDF[BorutaPy],
    _NDArrayTransformerWrapperDF[BorutaPy],
    _ColumnSubsetTransformerWrapperDF[BorutaPy],
    metaclass=ABCMeta,
):
    def _get_features_out(self) -> pd.Index:
        return self.feature_names_in_[self.native_estimator.support_]


BorutaDF = make_df_transformer(BorutaPy, df_wrapper_type=_BorutaPyWrapperDF)


__tracker.validate()
