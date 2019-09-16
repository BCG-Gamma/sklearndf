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
Specialised transformer wrappers.
"""

import logging
from abc import ABC, abstractmethod
from typing import *

import pandas as pd
from sklearn.base import TransformerMixin

from gamma.sklearndf._wrapper import TransformerWrapperDF

log = logging.getLogger(__name__)


#
# type variables
#

T_Transformer = TypeVar("T_Transformer", bound=TransformerMixin)


#
# wrapper classes for transformers
#


class NDArrayTransformerWrapperDF(
    TransformerWrapperDF[T_Transformer], Generic[T_Transformer]
):
    """
    `TransformerDF` whose delegate transformer only accepts numpy ndarrays.

    Wraps around the delegate transformer and converts the data frame to an array when
    needed.
    """

    # noinspection PyPep8Naming
    @staticmethod
    def _convert_X_for_delegate(X: pd.DataFrame) -> Any:
        return X.values

    @staticmethod
    def _convert_y_for_delegate(y: Optional[Union[pd.Series, pd.DataFrame]]) -> Any:
        return None if y is None else y.values


class ColumnSubsetTransformerWrapperDF(
    TransformerWrapperDF[T_Transformer], Generic[T_Transformer]
):
    """
    Transforms a data frame without changing column names, but possibly removing
    columns.

    All output columns of a :class:`ColumnSubsetTransformerWrapperDF` have the same
    names as their associated input columns. Some columns can be removed.
    Implementations must define ``_make_delegate_estimator`` and ``_get_columns_out``.
    """

    @abstractmethod
    def _get_columns_out(self) -> pd.Index:
        # return column labels for arrays returned by the fitted transformer.
        pass

    def _get_columns_original(self) -> pd.Series:
        # return the series with output columns in index and output columns as values
        columns_out = self._get_columns_out()
        return pd.Series(index=columns_out, data=columns_out.values)


class ColumnPreservingTransformerWrapperDF(
    ColumnSubsetTransformerWrapperDF[T_Transformer], Generic[T_Transformer]
):
    """
    Transform a data frame keeping exactly the same columns.

    A ``ColumnPreservingTransformerWrapperDF`` does not add, remove, or rename any of
    the input columns.
    """

    def _get_columns_out(self) -> pd.Index:
        return self.columns_in


class BaseMultipleInputsPerOutputTransformerWrapperDF(
    TransformerWrapperDF[T_Transformer], Generic[T_Transformer], ABC
):
    """
    Transform data whom output columns have multiple input columns.
    """

    @abstractmethod
    def _get_columns_out(self) -> pd.Index:
        # make this method abstract to ensure subclasses override the default
        # behaviour, which usually relies on method `_get_columns_original`
        pass

    def _get_columns_original(self) -> pd.Series:
        raise NotImplementedError(
            f"{type(self.delegate_estimator).__name__} transformers map multiple "
            "inputs to individual output columns; current sklearndf implementation "
            "only supports many-to-1 mappings from output columns to input columns"
        )


class BaseDimensionalityReductionWrapperDF(
    BaseMultipleInputsPerOutputTransformerWrapperDF[T_Transformer],
    Generic[T_Transformer],
    ABC,
):
    """
    Transform data making dimensionality reduction style transform.
    """

    @property
    @abstractmethod
    def _n_components(self) -> int:
        pass

    def _get_columns_out(self) -> pd.Index:
        return pd.Index([f"x_{i}" for i in range(self._n_components)])


class NComponentsDimensionalityReductionWrapperDF(
    BaseDimensionalityReductionWrapperDF[T_Transformer], Generic[T_Transformer]
):
    """
    Transform features doing dimensionality reductions.

    The delegate transformer has a ``n_components`` attribute.
    """

    _ATTR_N_COMPONENTS = "n_components"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._validate_delegate_attribute(attribute_name=self._ATTR_N_COMPONENTS)

    @property
    def _n_components(self) -> int:
        return getattr(self.delegate_estimator, self._ATTR_N_COMPONENTS)


class ComponentsDimensionalityReductionWrapperDF(
    BaseDimensionalityReductionWrapperDF[T_Transformer], Generic[T_Transformer]
):
    """
    Apply dimensionality reduction on a data frame.

    The delegate transformer has a ``components_`` attribute which is an array of
    shape (n_components, n_features) and we use n_components to determine the number
    of output columns.
    """

    _ATTR_COMPONENTS = "components_"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    # noinspection PyPep8Naming
    def _post_fit(
        self, X: pd.DataFrame, y: Optional[pd.Series] = None, **fit_params
    ) -> None:
        # noinspection PyProtectedMember
        super()._post_fit(X, y, **fit_params)
        self._validate_delegate_attribute(attribute_name=self._ATTR_COMPONENTS)

    @property
    def _n_components(self) -> int:
        return len(getattr(self.delegate_estimator, self._ATTR_COMPONENTS))


class FeatureSelectionWrapperDF(
    ColumnSubsetTransformerWrapperDF[T_Transformer], Generic[T_Transformer], ABC
):
    """
    Wrapper for feature selection transformers.

    The delegate transformer has a `get_support` method providing the indices of the
    selected input columns
    """

    _ATTR_GET_SUPPORT = "get_support"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._validate_delegate_attribute(attribute_name=self._ATTR_GET_SUPPORT)

    def _get_columns_out(self) -> pd.Index:
        get_support = getattr(self.delegate_estimator, self._ATTR_GET_SUPPORT)
        return self.columns_in[get_support()]
