import numpy as np
import psyneulink as pnl
import pytest

class TestComponent:

    def test_detection_of_legal_arg_in_kwargs(self):
        assert isinstance(pnl.ProcessingMechanism().reinitialize_when, pnl.Never)
        assert isinstance(pnl.ProcessingMechanism(reinitialize_when=pnl.AtTrialStart()).reinitialize_when,
                          pnl.AtTrialStart)

    def test_detection_of_illegal_arg_in_kwargs(self):
        with pytest.raises(pnl.ComponentError) as error_text:
            pnl.ProcessingMechanism(flim_flam=1)
        assert "Unrecognized argument in constructor for ProcessingMechanism-0 (type: ProcessingMechanism): 'flim_flam'"

    def test_detection_of_illegal_args_in_kwargs(self):
        with pytest.raises(pnl.ComponentError) as error_text:
            pnl.ProcessingMechanism(name='MY_MECH', flim_flam=1, grumblabble=2)
        assert "Unrecognized arguments in constructor for MY_MECH (type: ProcessingMechanism): 'flim_flam, grumblabble'"

    def test_component_execution_counts_for_standalone_mechanism(self):
        """Note: input_state should not update execution count, since it has no afferents"""

        T = pnl.TransferMechanism()

        T.execute()
        assert T.current_execution_count == 1
        assert T.input_state.current_execution_count == 0
        assert T.parameter_states[pnl.SLOPE].current_execution_count == 1
        assert T.output_state.current_execution_count == 1

        T.execute()
        assert T.current_execution_count == 2
        assert T.input_state.current_execution_count == 0
        assert T.parameter_states[pnl.SLOPE].current_execution_count == 2
        assert T.output_state.current_execution_count == 2

        T.execute()
        assert T.current_execution_count == 3
        assert T.input_state.current_execution_count == 0
        assert T.parameter_states[pnl.SLOPE].current_execution_count == 3
        assert T.output_state.current_execution_count == 3

    def test_component_execution_counts_for_mechanisms_in_composition(self):

        T1 = pnl.TransferMechanism()
        T2 = pnl.TransferMechanism()
        c = pnl.Composition()
        c.add_node(T1)
        c.add_node(T2)
        c.add_projection(sender=T1, receiver=T2)

        input_dict = {T1:[[0]]}

        c.run(input_dict)
        assert T2.current_execution_count == 1
        assert T2.input_state.current_execution_count == 1
        assert T2.parameter_states[pnl.SLOPE].current_execution_count == 1
        assert T2.output_state.current_execution_count == 1

        c.run(input_dict)
        assert T2.current_execution_count == 2
        assert T2.input_state.current_execution_count == 2
        assert T2.parameter_states[pnl.SLOPE].current_execution_count == 2
        assert T2.output_state.current_execution_count == 2

        c.run(input_dict)
        assert T2.current_execution_count == 3
        assert T2.input_state.current_execution_count == 3
        assert T2.parameter_states[pnl.SLOPE].current_execution_count == 3
        assert T2.output_state.current_execution_count == 3