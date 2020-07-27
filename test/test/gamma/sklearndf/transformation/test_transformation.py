from typing import *

import numpy as np
import pandas as pd

# noinspection PyPackageRequirements
import pytest
import sklearn
from pandas.util.testing import assert_frame_equal
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import Normalizer

import gamma.sklearndf
import gamma.sklearndf.transformation
from gamma.sklearndf import TransformerDF
from gamma.sklearndf.classification import RandomForestClassifierDF
from gamma.sklearndf.transformation import (
    ColumnTransformerDF,
    KBinsDiscretizerDF,
    NormalizerDF,
    OneHotEncoderDF,
    RFECVDF,
    RFEDF,
    SelectFromModelDF,
    SparseCoderDF,
)
from gamma.sklearndf.transformation.extra import OutlierRemoverDF
from test.gamma.sklearndf import (
    check_expected_not_fitted_error,
    get_classes,
    get_wrapped_counterpart,
)

TRANSFORMERS_TO_TEST = get_classes(
    from_module=gamma.sklearndf.transformation,
    matching=r".*DF",
    excluding=[
        TransformerDF.__name__,
        OneHotEncoderDF.__name__,
        SelectFromModelDF.__name__,
        SparseCoderDF.__name__,
        ColumnTransformerDF.__name__,
        KBinsDiscretizerDF.__name__,
        RFECVDF.__name__,
        RFEDF.__name__,
        r".*WrapperDF",
    ],
)


@pytest.fixture
def test_data() -> pd.DataFrame:
    return pd.DataFrame(
        data={
            "c0": [0, 1, 2.5, 3, 4, 5.2, 6, 7, 8, 9],
            "c1": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        }
    )


@pytest.mark.parametrize(argnames="sklearndf_cls", argvalues=TRANSFORMERS_TO_TEST)
def test_wrapped_constructor(sklearndf_cls: Type[TransformerDF]) -> None:
    sklearndf_cls()


def test_special_wrapped_constructors() -> None:
    rf = RandomForestClassifierDF()

    with pytest.raises(NotImplementedError):
        OneHotEncoderDF()
    OneHotEncoderDF(sparse=False)

    SelectFromModelDF(estimator=rf)

    SparseCoderDF(dictionary=np.array([]))

    ColumnTransformerDF(transformers=[])

    with pytest.raises(NotImplementedError):
        KBinsDiscretizerDF()
    KBinsDiscretizerDF(encode="onehot-dense")

    RFECVDF(estimator=rf)

    RFEDF(estimator=rf)


@pytest.mark.parametrize(
    argnames="sklearn_cls",
    argvalues=get_classes(
        from_module=sklearn.preprocessing,
        matching=r".*PowerTransformer|QuantileTransformer|.*Scaler",
    ),
)
def test_various_transformers(sklearn_cls: Type, test_data: pd.DataFrame) -> None:
    # get the wrapped counterpart for sklearn:
    df_transf_cls = get_wrapped_counterpart(
        to_wrap=sklearn_cls, from_package=gamma.sklearndf.transformation
    )

    # initalize both kind of transformers
    df_t = df_transf_cls()
    non_df_t = sklearn_cls()

    # for sklearn >=0.22 - check if not_fitted error is raised properly:
    check_expected_not_fitted_error(estimator=df_t)

    # test fit-transform on both in conjecture with ColumnTransformer(DF)
    df_col_t = ColumnTransformerDF(transformers=[("t", df_t, ["c0"])], remainder="drop")
    transformed_df = df_col_t.fit_transform(X=test_data)

    assert isinstance(transformed_df, pd.DataFrame)

    non_df_col_t = ColumnTransformer(transformers=[("t", non_df_t, ["c0"])])

    transformed_non_df = non_df_col_t.fit_transform(X=test_data)

    assert "c0" in transformed_df.columns
    assert np.all(
        np.round(transformed_df["c0"].values, 1)
        == np.round(transformed_non_df.reshape(10), 1)
    )


def test_normalizer_df() -> None:
    x = [[4, 1, 2, 2], [1, 3, 9, 3], [5, 7, 5, 1]]
    test_df = pd.DataFrame(x)
    test_df.columns = ["a", "b", "c", "d"]

    non_df_normalizer = Normalizer(norm="l2")
    df_normalizer = NormalizerDF(norm="l2")

    transformed_non_df = non_df_normalizer.fit_transform(X=x)
    transformed_df = df_normalizer.fit_transform(X=test_df)

    # check equal results:
    assert np.array_equal(transformed_non_df, transformed_df.values)
    # check columns are preserved:
    assert np.all(transformed_df.columns == ["a", "b", "c", "d"])


@pytest.fixture
def df_outlier() -> pd.DataFrame:
    return pd.DataFrame(
        data={
            "c0": [0, 1, 2, 3, 4],
            "c1": [-1, 0, 0, 0, 1],
            "c2": [-10, 0, 1, 2, 3],
            "c3": [0, 1, 2, 3, 10],
        }
    )


def test_outlier_remover(df_outlier: pd.DataFrame) -> None:
    outlier_remover = OutlierRemoverDF(iqr_multiple=2)
    df_transformed = outlier_remover.fit_transform(df_outlier)
    df_transformed_expected = pd.DataFrame(
        data={
            "c0": [0, 1, 2, 3, 4],
            "c1": [np.nan, 0, 0, 0, np.nan],
            "c2": [np.nan, 0, 1, 2, 3],
            "c3": [0, 1, 2, 3, np.nan],
        }
    )
    assert_frame_equal(df_transformed, df_transformed_expected)
