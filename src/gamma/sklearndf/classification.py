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
Data frame versions of all sklearn regressors
"""
import logging
from abc import ABC
from typing import *

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis,
    QuadraticDiscriminantAnalysis,
)
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    BaggingClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.linear_model import (
    LogisticRegression,
    LogisticRegressionCV,
    PassiveAggressiveClassifier,
    Perceptron,
    RidgeClassifier,
    RidgeClassifierCV,
    SGDClassifier,
)
from sklearn.multiclass import (
    OneVsOneClassifier,
    OneVsRestClassifier,
    OutputCodeClassifier,
)
from sklearn.multioutput import ClassifierChain, MultiOutputClassifier
from sklearn.naive_bayes import BernoulliNB, ComplementNB, GaussianNB, MultinomialNB
from sklearn.neighbors import (
    KNeighborsClassifier,
    NearestCentroid,
    RadiusNeighborsClassifier,
)
from sklearn.neural_network import MLPClassifier
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from sklearn.svm import LinearSVC, NuSVC, SVC
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier

from gamma.common import ListLike
from gamma.sklearndf import ClassifierDF
from gamma.sklearndf._wrapper import (
    ClassifierWrapperDF,
    df_estimator,
    MetaClassifierWrapperDF,
)

log = logging.getLogger(__name__)


__all__ = [sym for sym in dir() if sym.endswith("DF")]

#
# neighbors
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class NearestCentroidDF(NearestCentroid, ClassifierDF):
    """
    Wraps :class:`sklearn.neighbors.nearest_centroid.NearestCentroid`; accepts and
    returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class KNeighborsClassifierDF(KNeighborsClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.neighbors.classification.KNeighborsClassifier`; accepts and
    returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class RadiusNeighborsClassifierDF(RadiusNeighborsClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.neighbors.classification.RadiusNeighborsClassifier`; accepts
    and returns data frames.
    """

    pass


#
# voting
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=MetaClassifierWrapperDF)
class VotingClassifierDF(VotingClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.ensemble.voting.VotingClassifier`; accepts and returns data
    frames.
    """

    pass


#
# ensemble
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class RandomForestClassifierDF(RandomForestClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.ensemble.forest.RandomForestClassifier`; accepts and returns
    data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class ExtraTreesClassifierDF(ExtraTreesClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.ensemble.forest.ExtraTreesClassifier`; accepts and returns
    data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class GradientBoostingClassifierDF(GradientBoostingClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.ensemble.gradient_boosting.GradientBoostingClassifier`;
    accepts and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class AdaBoostClassifierDF(AdaBoostClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.ensemble.weight_boosting.AdaBoostClassifier`; accepts and
    returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class BaggingClassifierDF(BaggingClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.ensemble.bagging.BaggingClassifier`; accepts and returns data
    frames.
    """

    pass


#
# tree
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class DecisionTreeClassifierDF(DecisionTreeClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.tree.tree.DecisionTreeClassifier`; accepts and returns data
    frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class ExtraTreeClassifierDF(ExtraTreeClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.tree.tree.ExtraTreeClassifier`; accepts and returns data
    frames.
    """

    pass


#
# discriminant analysis
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class QuadraticDiscriminantAnalysisDF(QuadraticDiscriminantAnalysis, ClassifierDF):
    """
    Wraps :class:`sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis`; accepts
    and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class LinearDiscriminantAnalysisDF(LinearDiscriminantAnalysis, ClassifierDF):
    """
    Wraps :class:`sklearn.discriminant_analysis.LinearDiscriminantAnalysis`; accepts and
    returns data frames.
    """

    pass


#
# naive bayes
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class GaussianNBDF(GaussianNB, ClassifierDF):
    """
    Wraps :class:`sklearn.naive_bayes.GaussianNB`; accepts and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class MultinomialNBDF(MultinomialNB, ClassifierDF):
    """
    Wraps :class:`sklearn.naive_bayes.MultinomialNB`; accepts and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class ComplementNBDF(ComplementNB, ClassifierDF):
    """
    Wraps :class:`sklearn.naive_bayes.ComplementNB`; accepts and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class BernoulliNBDF(BernoulliNB, ClassifierDF):
    """
    Wraps :class:`sklearn.naive_bayes.BernoulliNB`; accepts and returns data frames.
    """

    pass


#
# calibration
#

# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=MetaClassifierWrapperDF)
class CalibratedClassifierCVDF(CalibratedClassifierCV, ClassifierDF):
    """
    Wraps :class:`sklearn.calibration.CalibratedClassifierCV`; accepts and returns data
    frames.
    """

    pass


#
# SVM
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class SVCDF(SVC, ClassifierDF):
    """
    Wraps :class:`sklearn.svm.classes.SVC`; accepts and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class NuSVCDF(NuSVC, ClassifierDF):
    """
    Wraps :class:`sklearn.svm.classes.NuSVC`; accepts and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class LinearSVCDF(LinearSVC, ClassifierDF):
    """
    Wraps :class:`sklearn.svm.classes.LinearSVC`; accepts and returns data frames.
    """

    pass


#
# dummy
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class DummyClassifierDF(DummyClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.dummy.DummyClassifier`; accepts and returns data frames.
    """

    pass


#
# gaussian process
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class GaussianProcessClassifierDF(GaussianProcessClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.gaussian_process.gpc.GaussianProcessClassifier`; accepts and
    returns data frames.
    """

    pass


#
# linear model
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class LogisticRegressionDF(LogisticRegression, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.logistic.LogisticRegression`; accepts and returns
    data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class LogisticRegressionCVDF(LogisticRegressionCV, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.logistic.LogisticRegressionCV`; accepts and
    returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class LogisticRegressionCVDF(LogisticRegressionCV, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.logistic.LogisticRegressionCV`; accepts and
    returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class PassiveAggressiveClassifierDF(PassiveAggressiveClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.passive_aggressive.PassiveAggressiveClassifier`;
    accepts and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class PerceptronDF(Perceptron, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.perceptron.Perceptron`; accepts and returns data
    frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class SGDClassifierDF(SGDClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.stochastic_gradient.SGDClassifier`; accepts and
    returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class RidgeClassifierDF(RidgeClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.ridge.RidgeClassifier`; accepts and returns data
    frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class RidgeClassifierCVDF(RidgeClassifierCV, ClassifierDF):
    """
    Wraps :class:`sklearn.linear_model.ridge.RidgeClassifierCV`; accepts and returns
    data frames.
    """

    pass


#
# semi-supervised
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class LabelPropagationDF(LabelPropagation, ClassifierDF):
    """
    Wraps :class:`sklearn.semi_supervised.label_propagation.LabelPropagation`; accepts
    and returns data frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class LabelSpreadingDF(LabelSpreading, ClassifierDF):
    """
    Wraps :class:`sklearn.semi_supervised.label_propagation.LabelSpreading`; accepts and
    returns data frames.
    """

    pass


#
# multi-class
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=MetaClassifierWrapperDF)
class OneVsRestClassifierDF(OneVsRestClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.multiclass.OneVsRestClassifier`; accepts and returns data
    frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=MetaClassifierWrapperDF)
class OneVsOneClassifierDF(OneVsOneClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.multiclass.OneVsOneClassifier`; accepts and returns data
    frames.
    """

    pass


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=MetaClassifierWrapperDF)
class OutputCodeClassifierDF(OutputCodeClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.multiclass.OutputCodeClassifier`; accepts and returns data
    frames.
    """

    pass


#
# multi-output
#

# estimators attribute of abstract class MultiOutputEstimator
ATTR_MULTI_OUTPUT_ESTIMATORS = "estimators_"


class _MultiOutputClassifierWrapperDF(
    MetaClassifierWrapperDF[MultiOutputClassifier], ABC
):
    # noinspection PyPep8Naming
    def _prediction_with_class_labels(
        self,
        X: pd.DataFrame,
        y: Union[pd.Series, pd.DataFrame, list, np.ndarray],
        classes: Optional[ListLike[Any]] = None,
    ) -> Union[pd.Series, pd.DataFrame, List[pd.DataFrame]]:

        # if we have a multi-output classifier, prediction of probabilities
        # yields a list of NumPy arrays
        if not isinstance(y, list):
            raise ValueError(
                "prediction of multi-output classifier expected to be a list of NumPy "
                f"arrays, but got type {type(y)}"
            )

        delegate_estimator = self.delegate_estimator

        # store the super() object as this is not available within a generator
        sup = super()

        # usually the delegate estimator will provide a list of estimators used
        # to predict each output. If present, use these estimators to get
        # individual class labels for each output; otherwise we cannot assign class
        # labels
        if hasattr(delegate_estimator, ATTR_MULTI_OUTPUT_ESTIMATORS):
            return [
                sup._prediction_with_class_labels(
                    X=X, y=output, classes=getattr(estimator, "classes_", None)
                )
                for estimator, output in zip(
                    getattr(delegate_estimator, ATTR_MULTI_OUTPUT_ESTIMATORS), y
                )
            ]
        else:
            return [
                sup._prediction_with_class_labels(X=X, y=output, classes=None)
                for output in y
            ]


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=_MultiOutputClassifierWrapperDF)
class MultiOutputClassifierDF(MultiOutputClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.multioutput.MultiOutputClassifier`; accepts and returns data
    frames.
    """

    pass


#
# chaining
#


class _ClassifierChainWrapperDF(MetaClassifierWrapperDF[ClassifierChain], ABC):
    # noinspection PyPep8Naming
    def _prediction_with_class_labels(
        self,
        X: pd.DataFrame,
        y: Union[pd.Series, pd.DataFrame, list, np.ndarray],
        classes: Optional[ListLike[Any]] = None,
    ) -> Union[pd.Series, pd.DataFrame, List[pd.DataFrame]]:
        return super()._prediction_with_class_labels(
            X=X, y=y, classes=range(self.n_outputs)
        )


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=_ClassifierChainWrapperDF)
class ClassifierChainDF(ClassifierChain, ClassifierDF):
    """
    Wraps :class:`sklearn.multioutput.ClassifierChain`; accepts and returns data frames.
    """

    pass


#
# neural network
#


# noinspection PyAbstractClass
@df_estimator(df_wrapper_type=ClassifierWrapperDF)
class MLPClassifierDF(MLPClassifier, ClassifierDF):
    """
    Wraps :class:`sklearn.neural_network.multilayer_perceptron.MLPClassifier`; accepts
    and returns data frames.
    """

    pass
