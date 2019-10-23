import numpy as np
import pytest

from psyneulink.core.components.functions.transferfunctions import Linear
from psyneulink.core.compositions.composition import Composition
from psyneulink.core.components.mechanisms.processing.transfermechanism import TransferMechanism
from psyneulink.core.components.mechanisms.processing.processingmechanism import ProcessingMechanism
from psyneulink.core.components.process import Process
from psyneulink.core.components.system import System
from psyneulink.core.scheduling.condition import Never, WhenFinished
from psyneulink.library.components.mechanisms.processing.transfer.lcamechanism import \
    LCAMechanism, MAX_VS_AVG, MAX_VS_NEXT
from psyneulink.core.globals.keywords import RESULT

class TestLCA:
    def test_LCAMechanism_length_1(self):

        T = TransferMechanism(function=Linear(slope=1.0))
        L = LCAMechanism(function=Linear(slope=2.0),
                         self_excitation=3.0,
                         leak=0.5,
                         competition=1.0,  #  competition does not matter because we only have one unit
                         time_step_size=0.1)
        C = Composition()
        C.add_linear_processing_pathway([T,L])
        L.reinitialize_when = Never()
        #  - - - - - - - Equations to be executed  - - - - - - -

        # new_transfer_input =
        # previous_transfer_input
        # + (leak * previous_transfer_input_1 + self_excitation * result1 + competition * result2 + outside_input1) * dt
        # + noise

        # result = new_transfer_input*2.0

        # recurrent_matrix = [[3.0]]

        #  - - - - - - - - - - - - - -  - - - - - - - - - - - -

        results=[]
        def record_execution():
            results.append(L.parameters.value.get(C)[0][0])

        C.run(inputs={T: [1.0]},
              num_trials=3,
              call_after_trial=record_execution)

        # - - - - - - - TRIAL 1 - - - - - - -

        # new_transfer_input = 0.0 + ( 0.5 * 0.0 + 3.0 * 0.0 + 0.0 + 1.0)*0.1 + 0.0    =    0.1
        # f(new_transfer_input) = 0.1 * 2.0 = 0.2

        # - - - - - - - TRIAL 2 - - - - - - -

        # new_transfer_input = 0.1 + ( 0.5 * 0.1 + 3.0 * 0.2 + 0.0 + 1.0)*0.1 + 0.0    =    0.265
        # f(new_transfer_input) = 0.265 * 2.0 = 0.53

        # - - - - - - - TRIAL 3 - - - - - - -

        # new_transfer_input = 0.265 + ( 0.5 * 0.265 + 3.0 * 0.53 + 0.0 + 1.0)*0.1 + 0.0    =    0.53725
        # f(new_transfer_input) = 0.53725 * 2.0 = 1.0745

        assert np.allclose(results, [0.2, 0.53, 1.0745])

    def test_LCAMechanism_length_2(self):
        # Note: since the LCAMechanism's threshold is not specified in this test, each execution only updates
        #       the Mechanism once.

        T = TransferMechanism(function=Linear(slope=1.0), size=2)
        L = LCAMechanism(function=Linear(slope=2.0),
                         size=2,
                         self_excitation=3.0,
                         leak=0.5,
                         competition=1.0,
                         time_step_size=0.1)

        C = Composition()
        C.add_linear_processing_pathway([T,L])
        L.reinitialize_when = Never()
        #  - - - - - - - Equations to be executed  - - - - - - -

        # new_transfer_input =
        # previous_transfer_input
        # + (leak * previous_transfer_input_1 + self_excitation * result1 + competition * result2 + outside_input1) * dt
        # + noise

        # result = new_transfer_input*2.0

        # recurrent_matrix = [[3.0]]

        #  - - - - - - - - - - - - - -  - - - - - - - - - - - -

        results=[]
        def record_execution():
            results.append(L.parameters.value.get(C)[0])

        C.run(inputs={T: [1.0, 2.0]},
              num_trials=3,
              call_after_trial=record_execution)

        # - - - - - - - TRIAL 1 - - - - - - -

        # new_transfer_input_1 = 0.0 + ( 0.5 * 0.0 + 3.0 * 0.0 - 1.0*0.0 + 1.0)*0.1 + 0.0    =    0.1
        # f(new_transfer_input_1) = 0.1 * 2.0 = 0.2

        # new_transfer_input_2 = 0.0 + ( 0.5 * 0.0 + 3.0 * 0.0 - 1.0*0.0 + 2.0)*0.1 + 0.0    =    0.2
        # f(new_transfer_input_2) = 0.2 * 2.0 = 0.4

        # - - - - - - - TRIAL 2 - - - - - - -

        # new_transfer_input = 0.1 + ( 0.5 * 0.1 + 3.0 * 0.2 - 1.0*0.4 + 1.0)*0.1 + 0.0    =    0.225
        # f(new_transfer_input) = 0.265 * 2.0 = 0.45

        # new_transfer_input_2 = 0.2 + ( 0.5 * 0.2 + 3.0 * 0.4 - 1.0*0.2 + 2.0)*0.1 + 0.0    =    0.51
        # f(new_transfer_input_2) = 0.1 * 2.0 = 1.02

        # - - - - - - - TRIAL 3 - - - - - - -

        # new_transfer_input = 0.225 + ( 0.5 * 0.225 + 3.0 * 0.45 - 1.0*1.02 + 1.0)*0.1 + 0.0    =    0.36925
        # f(new_transfer_input) = 0.36925 * 2.0 = 0.7385

        # new_transfer_input_2 = 0.51 + ( 0.5 * 0.51 + 3.0 * 1.02 - 1.0*0.45 + 2.0)*0.1 + 0.0    =    0.9965
        # f(new_transfer_input_2) = 0.9965 * 2.0 = 1.463

        assert np.allclose(results, [[0.2, 0.4], [0.45, 1.02], [0.7385, 1.993]])

    def test_equivalance_of_threshold_and_when_finished_condition(self):
        # Note: This tests the equivalence of results when the threshold is specified (in which case a single
        #       call to execution should loop until it reaches threshold) and when it is not specified by
        #       a condition is added to the scheduler that it execute until its is_finished method is True.
        lca_until_thresh = LCAMechanism(size=2, threshold=0.7) # Note: , execute_to_threshold=True by default
        response = ProcessingMechanism(size=2)
        comp = Composition()
        comp.add_linear_processing_pathway([lca_until_thresh,response])
        comp.scheduler.add_condition(response, WhenFinished(lca_until_thresh))
        result1 = comp.run(inputs={lca_until_thresh:[1,0]})

        lca_single_step = LCAMechanism(size=2, threshold=0.7, execute_until_finished=False)
        comp2 = Composition()
        response2 = ProcessingMechanism(size=2)
        comp2.add_linear_processing_pathway([lca_single_step,response2])
        comp2.scheduler.add_condition(response2, WhenFinished(lca_single_step))
        result2 = comp2.run(inputs={lca_single_step:[1,0]})
        assert np.allclose(result1, result2)

    def test_LCAMechanism_threshold(self):
        # Note: In this test and the following ones, since the LCAMechanism's threshold is specified
        #       it executes until the it reaches threshold.
        lca = LCAMechanism(size=2, threshold=0.7)
        comp = Composition()
        comp.add_node(lca)
        result = comp.run(inputs={lca:[1,0]})
        assert np.allclose(result, [[0.71463572, 0.28536428]])

    def test_LCAMechanism_threshold_with_max_vs_next(self):
        lca = LCAMechanism(size=3, threshold=0.1, threshold_criterion=MAX_VS_NEXT)
        response = ProcessingMechanism(size=3)
        comp = Composition()
        comp.add_linear_processing_pathway([lca,response])
        comp.scheduler.add_condition(response, WhenFinished(lca))
        # comp.add_node(lca)
        result = comp.run(inputs={lca:[1,0.5,0]})
        assert np.allclose(result, [[0.52200799, 0.41310248, 0.31228985]])
        # assert np.allclose(result, [[0.5, 0.39960759, 0.30699604]])

    def test_LCAMechanism_threshold_with_max_vs_avg(self):
        lca = LCAMechanism(size=3, threshold=0.1, threshold_criterion=MAX_VS_AVG)
        response = ProcessingMechanism(size=3)
        comp = Composition()
        comp.add_linear_processing_pathway([lca,response])
        comp.scheduler.add_condition(response, WhenFinished(lca))
        result = comp.run(inputs={lca:[1,0.5,0]})
        assert np.allclose(result, [[0.5100369 , 0.43776452, 0.36808511]])

    def test_LCAMechanism_threshold_with_str(self):
        lca = LCAMechanism(size=2, threshold=0.7, threshold_criterion='MY_OUTPUT_PORT',
                         output_ports=[RESULT, 'MY_OUTPUT_PORT'])
        response = ProcessingMechanism(size=2)
        comp = Composition()
        comp.add_linear_processing_pathway([lca,response])
        comp.scheduler.add_condition(response, WhenFinished(lca))
        result = comp.run(inputs={lca:[1,0]})
        assert np.allclose(result, [[0.71463572, 0.28536428]])

    def test_LCAMechanism_threshold_with_int(self):
        lca = LCAMechanism(size=2, threshold=0.7, threshold_criterion=1, output_ports=[RESULT, 'MY_OUTPUT_PORT'])
        response = ProcessingMechanism(size=2)
        comp = Composition()
        comp.add_linear_processing_pathway([lca,response])
        comp.scheduler.add_condition(response, WhenFinished(lca))
        result = comp.run(inputs={lca:[1,0]})
        assert np.allclose(result, [[0.71463572, 0.28536428]])

class TestLCAReinitialize:

    def test_reinitialize_run(self):

        L = LCAMechanism(name="L",
                         function=Linear,
                         initial_value=0.5,
                         integrator_mode=True,
                         leak=0.1,
                         competition=0,
                         self_excitation=1.0,
                         time_step_size=1.0,
                         noise=0.0)
        P = Process(name="P",
                    pathway=[L])
        S = System(name="S",
                   processes=[P])

        L.reinitialize_when = Never()
        assert np.allclose(L.integrator_function.previous_value, 0.5)
        assert np.allclose(L.initial_value, 0.5)
        assert np.allclose(L.integrator_function.initializer, 0.5)

        S.run(inputs={L: 1.0},
              num_trials=2,
              initialize=True,
              initial_values={L: 0.0})

        # IntegratorFunction fn: previous_value + (rate*previous_value + new_value)*time_step_size + noise*(time_step_size**0.5)

        # Trial 1    |   variable = 1.0 + 0.0
        # integration: 0.5 + (0.1*0.5 + 1.0)*1.0 + 0.0 = 1.55
        # linear fn: 1.55*1.0 = 1.55
        # Trial 2    |   variable = 1.0 + 1.55
        # integration: 1.55 + (0.1*1.55 + 2.55)*1.0 + 0.0 = 4.255
        #  linear fn: 4.255*1.0 = 4.255
        assert np.allclose(L.integrator_function.parameters.previous_value.get(S), 4.255)

        L.integrator_function.reinitialize(0.9, context=S)

        assert np.allclose(L.integrator_function.parameters.previous_value.get(S), 0.9)
        assert np.allclose(L.parameters.value.get(S), 4.255)

        L.reinitialize(0.5, context=S)

        assert np.allclose(L.integrator_function.parameters.previous_value.get(S), 0.5)
        assert np.allclose(L.parameters.value.get(S), 0.5)

        S.run(inputs={L: 1.0},
              num_trials=2)
        # Trial 3    |   variable = 1.0 + 0.5
        # integration: 0.5 + (0.1*0.5 + 1.5)*1.0 + 0.0 = 2.05
        # linear fn: 2.05*1.0 = 2.05
        # Trial 4    |   variable = 1.0 + 2.05
        # integration: 2.05 + (0.1*2.05 + 3.05)*1.0 + 0.0 = 5.305
        #  linear fn: 5.305*1.0 = 5.305
        assert np.allclose(L.integrator_function.parameters.previous_value.get(S), 5.305)
        assert np.allclose(L.initial_value, 0.5)
        assert np.allclose(L.integrator_function.initializer, 0.5)

class TestClip:

    def test_clip_float(self):
        L = LCAMechanism(clip=[-2.0, 2.0],
                         function=Linear,
                         integrator_mode=False)
        assert np.allclose(L.execute(3.0), 2.0)
        assert np.allclose(L.execute(-3.0), -2.0)

    def test_clip_array(self):
        L = LCAMechanism(default_variable=[[0.0, 0.0, 0.0]],
                         clip=[-2.0, 2.0],
                         function=Linear,
                         integrator_mode=False)
        assert np.allclose(L.execute([3.0, 0.0, -3.0]), [2.0, 0.0, -2.0])

    def test_clip_2d_array(self):
        L = LCAMechanism(default_variable=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                         clip=[-2.0, 2.0],
                         function=Linear,
                         integrator_mode=False)
        assert np.allclose(L.execute([[-5.0, -1.0, 5.0], [5.0, -5.0, 1.0], [1.0, 5.0, 5.0]]),
                           [[-2.0, -1.0, 2.0], [2.0, -2.0, 1.0], [1.0, 2.0, 2.0]])