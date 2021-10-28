# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# *************************************  CompositionFunctionApproximator ***********************************************

"""

Contents
--------

  * `ParameterEstimationComposition_Overview`
  * `ParameterEstimationComposition_Data_Fitting`
  * `ParameterEstimationComposition_Optimization`
  * `ParameterEstimationComposition_Supported_Optimizers`
  * `ParameterEstimationComposition_Class_Reference`


.. _ParameterEstimationComposition_Overview:

Overview
--------

A `ParameterEstimationComposition` is a subclass of `Composition` that is used to estimate parameters of
another `Composition` (its `target <ParameterEstimationComposition.target>` in order to fit that to a set of
data (`ParameterEstimationComposition_Data_Fitting`) or to optimize the `results <Composition.results>` of the
`target <ParameterEstimationComposition.target>` according to an `objective_function`
(`ParameterEstimationComposition_Optimization`). In either case, when the ParameterEstimationComposition is `run
<Composition.run>` with a given set of `inputs <Composition_Execution_Inputs>`, it returns the set of parameters
that it estimates best satisfy either of those conditions using its `optimization_function
<ParameterEstimationComposition.optimization_function>`.

.. _ParameterEstimationComposition_Data_Fitting:

Data Fitting
------------

The ParameterEstimationComposition can be used to find a set of parameters for another "target" Composition such that,
when that Composition is run with a given set of inputs, its results best match a specified set of empirical data. A
ParameterEstimationComposition can be configured for data fitting by specifying the arguments of its constructor as
follows:

    * **target** - specifies the `Composition` for which parameters are to be estimated.

    * **parameters** - list[Parameters]
        specifies the parameters of the `target <ParameterEstimationComposition.target>` Composition to be estimated.

    * **data** - specifies the inputs to the `target <ParameterEstimationComposition.target>` Composition over which its
        parameters are to be estimated.

    * **objective_function** -- ??this is automatically specified as MLE??

    * **optimization_function**  OptimizationFunction, function or method
        specifies the function used to estimate the parameters of the `target <ParameterEstimationComposition.target>`
        Composition.



   * **target** - specifies the `Composition` for which parameters are to be estimated.

   * **data** - specifies the inputs to the `target <ParameterEstimationComposition.target>` Composition over which its
        parameters are to be estimated. This is assigned as the **state_feature_values** argument of the constructor
        for the ParameterEstimationComposition's `OptimizationControlMechanism`.

    parameters : list[Parameters]
        determines the parameters of the `target <ParameterEstimationComposition.target>` Composition to be estimated.
        This is assigned as the **control_signals** argument of the constructor for the ParameterEstimationComposition's
        `OptimizationControlMechanism`.

    outcome_variables : list[Composition output nodes]
        determines the `OUTPUT` `Nodes <Composition_Nodes>` of the `target <ParameterEstimationComposition.target>`
        Composition, the `values <Mechanism_Base.value>` of which are either compared to the **data** when the
        ParameterEstimationComposition is used for `data fitting <ParameterEstimationComposition_Data_Fitting>`,
        or evaluated by the ParameterEstimationComposition's `optimization_function
        <ParameterEstimationComposition.optimization_function>` when it is used for `parameter optimization
        <ParameterEstimationComposition_Optimization>`.

    optimization_function : OptimizationFunction, function or method
        determines the function used to estimate the parameters of the `target <ParameterEstimationComposition.target>`
        Composition.  This is assigned as the `function <OptimizationControlMechanism.function>` of the
        ParameterEstimationComposition's `OptimizationControlMechanism`.

    results : array
        contains the values of the `parameters <ParameterEstimationComposition.parameters>` of the
         `target <ParameterEstimationComposition.target>` Composition that best satisfy the
        `optimization_function <ParameterEstimationComposition.optimization_function>` given the `data
        <ParameterEstimationComposition.data>`.  This is the same as the final set of `control_signals
        <ControlMechanism.control_signals>` for the ParameterEstimationComposition's `OptimizationControlMechanism`.


of the `target <ParameterEstimationComposition.target>` Composition that
best fit the data

The  **target**
argument ParameterEstimationComposition's constructor is used to specify the Composition for which the parameters
are to be estimated; its **data** argument is used to specify the data to be fit for parameter *estimation*,
its **parameters** argument is used to specify the parameters of the **target** Composition to be estimated,
and its **optimization_function** is used to specify either an optimizer in another supported Python package (see
`ParameterEstimationComposition_Supported_Optimizers`), or a PsyNeuLink `OptimizationFunction`.  The optimized set
of parameters are returned when executing the  ParameterEstimationComposition`s `run <Composition.run>` method,
and stored in its `results <ParameterEstimationComposition.results>` attribute.


.. _ParameterEstimationComposition_Optimization

Parameter Optimization
----------------------


.. _ParameterEstimationComposition_Supported_Optimizers:

Supported Optimizers
--------------------

TBD


.. _ParameterEstimationComposition_Class_Reference:

Class Reference
---------------

"""

import numpy as np

from psyneulink.core.components.mechanisms.modulatory.control.optimizationcontrolmechanism import \
    OptimizationControlMechanism
from psyneulink.core.components.mechanisms.processing.objectivemechanism import ObjectiveMechanism
from psyneulink.core.components.ports.modulatorysignals.controlsignal import ControlSignal
from psyneulink.core.compositions.composition import Composition, NodeRole
from psyneulink.core.globals.context import Context
from psyneulink.core.globals.sampleiterator import SampleSpec
from psyneulink.core.globals.utilities import convert_to_list

__all__ = ['ParameterEstimationComposition']


class ParameterEstimationCompositionError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value


class ParameterEstimationComposition(Composition):
    """Subclass of `Composition` that estimates specified parameters of a target Composition to optimize a function
    over a set of data.

    Automatically implements an OptimizationControlMechanism as its `controller <Composition.controller>`,
    that is constructed using arguments to the ParameterEstimationComposition's constructor as described below.

    Arguments
    ---------

    target : Composition
        specifies the `Composition` for which parameters are to be `fit to data
        <ParameterEstimationComposition_Data_Fitting>` or `optimized <ParameterEstimationComposition_Optimization>`.

    parameters : dict[Parameter:Union[Iterator, Function, List, value]
        specifies the parameters of the `target <ParameterEstimationComposition.target>` Composition used to `fit
        it to data <ParameterEstimationComposition_Data_Fitting>` or `optimize its performance
        <ParameterEstimationComposition_Optimization>` according to the `optimization_function
        <ParameterEstimationComposition.optimization_function>`, and either the range of values to be evaluated for
        each, or priors that define a distribution.

    outcome_variables : list[Composition output nodes]
        specifies the `OUTPUT` `Nodes <Composition_Nodes>` of the `target <ParameterEstimationComposition.target>`
        Composition, the `values <Mechanism_Base.value>` of which are either compared to the **data** when the
        ParameterEstimationComposition is used for `data fitting <ParameterEstimationComposition_Data_Fitting>`
        or used by the `optimization_function <ParameterEstimationComposition.optimization_function>` when the
        ParameterEstimationComposition is used for `parameter optimization
        <ParameterEstimationComposition_Optimization>`.

    data : array : default None
        specifies the data to to be fit when the ParameterEstimationComposition is used for
        `data fitting <ParameterEstimationComposition_Data_Fitting>`.

    objective_function : ObjectiveFunction, function or method
        specifies the function that must be optimized (maximized or minimized) when the ParameterEstimationComposition
        is used for `paramater optimization <ParameterEstimationComposition_Optimization>`.

    optimization_function : OptimizationFunction, function or method
        specifies the function used to evaluate the `fit to data <ParameterEstimationComposition_Data_Fitting>` or
        `optimize <ParameterEstimationComposition_Optimization>` the parameters of the `target
        <ParameterEstimationComposition.target>` Composition.

    Attributes
    ----------

    target : Composition
        determines the `Composition` for which parameters are used to `fit data
        <ParameterEstimationComposition_Data_Fitting>` or `optimize its performance
        <ParameterEstimationComposition_Optimization>` as defined by the `objective_function
        <ParameterEstimationComposition.objective_function>`.  This is assigned as the `agent_rep
        <OptimizationControlMechanism.agent_rep>` attribute of the ParameterEstimationComposition's
        `OptimizationControlMechanism`.

    parameters : list[Parameters]
        determines the parameters of the `target <ParameterEstimationComposition.target>` Composition used to `fit
        it to data <ParameterEstimationComposition_Data_Fitting>` or `optimize its performance
        <ParameterEstimationComposition_Optimization>` according to the `optimization_function
        <ParameterEstimationComposition.optimization_function>`. These are assigned to the **control** argument of
        the constructor for the ParameterEstimationComposition's `OptimizationControlMechanism`, that is used to
        construct its `control_signals <OptimizationControlMechanism.control_signals>`.

    parameter_ranges_or_priors : List[Union[Iterator, Function, ist or Value]
        determines the range of values evaluated for each `parameter <ParameterEstimationComposition.parameters>`.
        These are assigned as the `allocation_samples <ControlSignal.allocation_samples>` for the `ControlSignal`
        assigned to the ParameterEstimationComposition` `OptimizationControlMechanism` corresponding to each of the
        specified `parameters <ParameterEstimationComposition.parameters>`.

    outcome_variables : list[Composition Output Nodes]
        determines the `OUTPUT` `Nodes <Composition_Nodes>` of the `target <ParameterEstimationComposition.target>`
        Composition, the `values <Mechanism_Base.value>` of which are either compared to the **data** when the
        ParameterEstimationComposition is used for `data fitting <ParameterEstimationComposition_Data_Fitting>`,
        or evaluated by the ParameterEstimationComposition's `optimization_function
        <ParameterEstimationComposition.optimization_function>` when it is used for `parameter optimization
        <ParameterEstimationComposition_Optimization>`.

    data : array
        determines the data to be fit by the model specified by the `target <ParameterEstimationComposition.target>`
        Composition when the ParameterEstimationComposition is used for `data fitting
        <ParameterEstimationComposition_Data_Fitting>`. These are passed to the optimizer specified
        by the `optimization_function <ParameterEstimationComposition.optimization_function>` specified as the
        `function <OptimizationControlMechanism.function> of the ParameterEstimationComposition's
        `OptimizationControlMechanism`.
        FIX: NEEDS TO BE ORGANIZED IN A WAY THAT IS COMPATIBLE WITH outcome_variables [SAME NUMBER OF ITEMS IN OUTER
             DIMENSION, WITH CORRESPONDING TYPES]

    objective_function : ObjectiveFunction, function or method
        FIX: IS EITHER:  THE NAME OF THE EXTERNAL OPTIMIZER FOR DATA FITTING OR A FUNCTION THAT IS OPTIMIZED FOR
            PARAMETER OPTIMIZATION [DAVE WANTS TO CALL THIS THE OPTIMZATION FUNCTION]
            Elfi, PYMC, S

    optimization_function : OptimizationFunction, function or method
        determines the function used to estimate the parameters of the `target <ParameterEstimationComposition.target>`
        Composition that either best fit the **data** when the ParameterEstimationComposition is used for `data
        fitting <ParameterEstimationComposition_Data_Fitting>`, or that achieve some maximum or minimum value of the
        the `optimization_function <ParameterEstimationComposition.optimization_function>` when the
        ParameterEstimationComposition is used for `parameter optimization
        <ParameterEstimationComposition_Optimization>`.  This is assigned as the `function
        <OptimizationControlMechanism.function>` of the ParameterEstimationComposition's `OptimizationControlMechanism`.
        FIX: DAVE'S OptimizationFunction [DAVE WANTS TO CALL THIS THE OBJECTIVE_FUNTION]

    results : array
        contains the values of the `parameters <ParameterEstimationComposition.parameters>` of the
         `target <ParameterEstimationComposition.target>` Composition that best fit the **data** when the
         ParameterEstimationComposition is used for `data fitting <ParameterEstimationComposition_Data_Fitting>`,
         or that optimize performance of the `target <ParameterEstimationComposition.target>` according to the
         `optimization_function <ParameterEstimationComposition.optimization_function>` when the
         ParameterEstimationComposition is used for `parameter `optimization_function
         <ParameterEstimationComposition.optimization_function>`.  This is the same as the final set of `values
         <ControlSignal.value>` for the `control_signals <ControlMechanism.control_signals>` of the
         ParameterEstimationComposition's `OptimizationControlMechanism`.
    """

    def __init__(self,
                 target, # agent_rep
                 parameters, # OCM control_signals
                 outcome_variables,  # OCM monitor_for_control
                 optimization_function, # function of OCM
                 data=None, # arg of OCM function
                 objective_function=None, # function of OCM ObjectiveMechanism
                 num_estimates=1, # num seeds per parameter combination (i.e., of OCM allocation_samples)
                 name=None,
                 **param_defaults):

        pem = self._instantiate_pem(target,
                                    parameters,
                                    outcome_variables,
                                    data,
                                    objective_function,
                                    optimization_function,
                                    num_estimates)

        super().__init__(name=name, nodes=target, controller=pem, **param_defaults)

        #FIX: CHECK THAT THIS WORKS AND, IF SO, REMOVE OVERRIDE OF execute METHOD BELOW
        self.require_node_roles(self.controller, NodeRole.OUTPUT)

    def _instantiate_pem(self,
                         target,
                         parameters,
                         outcome_variables,
                         data,
                         objective_function,
                         optimization_function,
                         num_estimates
                         ):


        # FIX: MOVE THIS TO validation METHOD?
        if data and objective_function:
            raise ParameterEstimationCompositionError(f"Both 'data' and 'objective_function' were specified for "
                                                      f"'{self.name}'; must choose one: 'data' for fitting "
                                                      f"or 'objective_function' for optimization.")

        # # FIX: MOVE THIS TO validation METHOD?
        # # Ensure parameters are in target composition
        # bad_params = [p for p in parameters if p not in target.parameters]
        # if bad_params:
        #     raise ParameterEstimationCompositionError(f"The following parameters "
        #                                               f"were not found in '{target.name}': {bad_params}.")

        # FIX: MOVE THIS TO validation METHOD?
        # Ensure outcome_variables are OutputPorts in target
        bad_ports = [p for p in outcome_variables if not [p is not node and p not in node.output_ports for node in
                                                          target.nodes]]
        if bad_ports:
            raise ParameterEstimationCompositionError(f"The following outcome_variables were not found as "
                                                      f"nodes or OutputPorts in '{target.name}': {bad_ports}.")

        # # FIX: NEED TO GET CORRECT METHOD FOR "find_random_params"
        # random_params = target.find_random_params()

        # FIX: should seeds be prespecified as list or passed as a random generator? Or should this be an option?
        random_seeds = SampleSpec(num=num_estimates, function=np.random.default_rng())
        randomization_control_signal = ControlSignal(modulates=random_params,
                                                     allocation_samples=random_seeds)
        parameters = convert_to_list(parameters).append(randomization_control_signal)

        if data:
            objective_function = objective_function(data)

        return OptimizationControlMechanism(control_signals=parameters,
                                            objective_mechanism=ObjectiveMechanism(monitor=outcome_variables,
                                                                                   function=objective_function),
                                            function=optimization_function)

    # FIX: USE THIS IF ASSIGNING PEM AS OUTPUT Node DOESN'T WORK
    def execute(self, **kwargs):
        super().execute(kwargs)
        optimized_control_allocation = self.controller.output_values
        self.results[-1] = optimized_control_allocation
        return optimized_control_allocation

    # FIX: IF DATA WAS SPECIFIED, CHECK THAT INPUTS ARE APPROPRIATE FOR THOSE DATA.
    def run(self):
        pass

    def adapt(self,
              feature_values,
              control_allocation,
              net_outcome,
              context=None):
        """Adjust parameters of `function <FunctionAppproximator.function>` to improve prediction of `target
        <FunctionAppproximator.target>` from `input <FunctionAppproximator.input>`.
        """
        raise ParameterEstimationCompositionError("Subclass of {} ({}) must implement {} method.".
                                                   format(ParameterEstimationComposition.__name__,
                                                          self.__class__.__name__, repr('adapt')))

    def evaluate(self,
                 feature_values,
                 control_allocation,
                 num_estimates,
                 num_trials_per_estimate,
                 base_context=Context(execution_id=None),
                 context=None):
        """Return `target <FunctionAppproximator.target>` predicted by `function <FunctionAppproximator.function> for
        **input**, using current set of `prediction_parameters <FunctionAppproximator.prediction_parameters>`.
        """
        # FIX: AUGMENT TO USE num_estimates and num_trials_per_estimate
        return self.function(feature_values, control_allocation, context=context)