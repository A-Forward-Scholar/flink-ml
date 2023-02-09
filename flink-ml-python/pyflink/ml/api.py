################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

from abc import ABC, abstractmethod
from typing import TypeVar, List, Generic

from pyflink.table import Table, StreamTableEnvironment

from pyflink.ml.param import WithParams

T = TypeVar('T')
E = TypeVar('E')
M = TypeVar('M')


class Stage(WithParams[T], ABC):
    """
    Base class for a node in a Pipeline or Graph. The interface is only a concept, and does not have
    any actual functionality. Its subclasses could be Estimator, Model, Transformer or AlgoOperator.
    No other classes should inherit this interface directly.

    Each stage is with parameters, and requires a public empty constructor for restoration.
    """

    @abstractmethod
    def save(self, path: str) -> None:
        """
        Saves this stage to the given path.
        """
        pass

    @classmethod
    @abstractmethod
    def load(cls, t_env: StreamTableEnvironment, path: str) -> T:
        """
        Instantiates a new stage instance based on the data read from the given path.
        """
        pass


class AlgoOperator(Stage[T], ABC):
    """
    An AlgoOperator takes a list of tables as inputs and produces a list of tables as results. It
    can be used to encode generic multi-input multi-output computation logic.
    """

    @abstractmethod
    def transform(self, *inputs: Table) -> List[Table]:
        """
        Applies the AlgoOperator on the given input tables and returns the result tables.

        :param inputs: A list of tables.
        :return: A list of tables.
        """
        pass


class Transformer(AlgoOperator[T], ABC):
    """
    A Transformer is an AlgoOperator with the semantic difference that it encodes the transformation
    logic, such that a record in the output typically corresponds to one record in the input. In
    contrast, an AlgoOperator is a better fit to express aggregation logic where a record in the
    output could be computed from an arbitrary number of records in the input.
    """
    pass


class Model(Transformer[T], ABC):
    """
    A Model is typically generated by invoking :func:`~Estimator.fit`. A Model is a Transformer with
    the extra APIs to set and get model data.
    """

    def set_model_data(self, *inputs: Table) -> 'Model':
        raise Exception("This operation is not supported.")

    def get_model_data(self) -> List[Table]:
        """
        Gets a list of tables representing the model data. Each table could be an unbounded stream
        of model data changes.

        :return: A list of tables.
        """
        raise Exception("This operation is not supported.")


class Estimator(Generic[E, M], Stage[E], ABC):
    """
    Estimators are responsible for training and generating Models.
    """

    def fit(self, *inputs: Table) -> Model[M]:
        """
        Trains on the given inputs and produces a Model.

        :param inputs: A list of tables.
        :return: A Model.
        """
        pass