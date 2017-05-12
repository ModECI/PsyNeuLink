from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.DDM import DDM
from PsyNeuLink.Components.Mechanisms.ProcessingMechanisms.DDM import DDMError

from PsyNeuLink.Components.Functions.Function import *
import numpy as np
from PsyNeuLink.Globals.Keywords import *
import pytest
from PsyNeuLink.Globals.Utilities import *

# ======================================= FUNCTION TESTS ============================================

# VALID FUNCTIONS:

# ------------------------------------------------------------------------------------------------
# TEST 1
# function = Integrator

def test_DDM_Integrator():
    stim = 10
    T = DDM(
            name='DDM',
            function = Integrator(
                                    integration_type= DIFFUSION,
                                  ),
            time_scale=TimeScale.TIME_STEP
           )
    val = float(T.execute(stim)[0])
    assert val == 10

# ------------------------------------------------------------------------------------------------
# TEST 2
# function = Bogacz

def test_DDM_Integrator():
    stim = 10
    T = DDM(
            name='DDM',
            function = BogaczEtAl()
           )
    val = float(T.execute(stim)[0])
    assert val == 1.0

# ------------------------------------------------------------------------------------------------
# # TEST 3
# # function = Navarro

# ******
# Requires matlab import
# ******

# def test_DDM_Integrator():
#     stim = 10
#     T = DDM(
#             name='DDM',
#             function = NavarroAndFuss()
#            )
#     val = float(T.execute(stim)[0])
#     assert val == 10


# ======================================= NOISE TESTS ============================================

# VALID NOISE:

# ------------------------------------------------------------------------------------------------
# TEST 1
# noise = Single float

def test_DDM_zero_noise():
    stim = 10
    T = DDM(
            name='DDM',
            function = Integrator(
                                    integration_type= DIFFUSION,
                                    noise = 0.0,
                                    rate = 1.0,
                                    time_step_size=1.0
                                  ),
            time_scale=TimeScale.TIME_STEP
           )
    val = float(T.execute(stim)[0])
    assert val == 10

# ------------------------------------------------------------------------------------------------
# TEST 2
# noise = Single float

def test_DDM_noise_0_5():
    stim = 10
    T = DDM(
            name='DDM',
            function = Integrator(
                                    integration_type= DIFFUSION,
                                    noise = 0.5,
                                    rate = 1.0,
                                    time_step_size=1.0
                                  ),
            time_scale=TimeScale.TIME_STEP
           )
    val = float(T.execute(stim)[0])
    assert val == 9.892974291631234

# ------------------------------------------------------------------------------------------------
# TEST 3
# noise = Single float

def test_DDM_noise_2_0():
    stim = 10
    T = DDM(
        name='DDM',
        function=Integrator(
            integration_type=DIFFUSION,
            noise=2.0,
            rate=1.0,
            time_step_size=1.0
        ),
        time_scale=TimeScale.TIME_STEP
    )
    val = float(T.execute(stim)[0])
    assert val == 9.785948583262465
# ------------------------------------------------------------------------------------------------

# INVALID NOISE:

# ------------------------------------------------------------------------------------------------
# TEST 1
# noise = Single int

def test_DDM_noise_int():
    with pytest.raises(FunctionError) as error_text:
        stim = 10
        T = DDM(
            name='DDM',
            function=Integrator(
                integration_type=DIFFUSION,
                noise=2,
                rate=1.0,
                time_step_size=1.0
            ),
            time_scale=TimeScale.TIME_STEP
        )
        val = float(T.execute(stim)[0])
    assert "When integration type is DIFFUSION, noise must be a float" in str(error_text.value)
# ------------------------------------------------------------------------------------------------
# TEST 2
# noise = Single fn

def test_DDM_noise_fn():
    with pytest.raises(FunctionError) as error_text:
        stim = 10
        T = DDM(
            name='DDM',
            function=Integrator(
                integration_type=DIFFUSION,
                noise=NormalDist().function,
                rate=1.0,
                time_step_size=1.0
            ),
            time_scale=TimeScale.TIME_STEP
        )
        val = float(T.execute(stim)[0])
    assert "When integration type is DIFFUSION, noise must be a float" in str(error_text.value)

# ======================================= INPUT TESTS ============================================

# VALID INPUTS:

# ------------------------------------------------------------------------------------------------
# TEST 1
# input = Int

def test_DDM_input_int():
    stim = 10
    T = DDM(
            name='DDM',
            function = Integrator(
                                    integration_type= DIFFUSION,
                                    noise = 0.0,
                                    rate = 1.0,
                                    time_step_size=1.0
                                  ),
            time_scale=TimeScale.TIME_STEP
           )
    val = float(T.execute(stim)[0])
    assert val == 10
# ------------------------------------------------------------------------------------------------
# TEST 2
# input = List len 1

def test_DDM_input_list_len_1():
    stim = [10]
    T = DDM(
            name='DDM',
            function = Integrator(
                                    integration_type= DIFFUSION,
                                    noise = 0.0,
                                    rate = 1.0,
                                    time_step_size=1.0
                                  ),
            time_scale=TimeScale.TIME_STEP
           )
    val = float(T.execute(stim)[0])
    assert val == 10

# ------------------------------------------------------------------------------------------------
# TEST 3
# input = Float

def test_DDM_input_float():
    stim = 10.0
    T = DDM(
            name='DDM',
            function = Integrator(
                                    integration_type= DIFFUSION,
                                    noise = 0.0,
                                    rate = 1.0,
                                    time_step_size=1.0
                                  ),
            time_scale=TimeScale.TIME_STEP
           )
    val = float(T.execute(stim)[0])
    assert val == 10.0

# ------------------------------------------------------------------------------------------------

# INVALID INPUTS:

# ------------------------------------------------------------------------------------------------
# TEST 1
# input = List len 2

def test_DDM_input_list_len_2():
    with pytest.raises(DDMError) as error_text:
        stim = [10, 10]
        T = DDM(
                name='DDM',
                default_input_value=[0, 0],
                function = Integrator(
                                        integration_type= DIFFUSION,
                                        noise = 0.0,
                                        rate = 1.0,
                                        time_step_size=1.0
                                      ),
                time_scale=TimeScale.TIME_STEP
               )
        val = float(T.execute(stim)[0])
    assert "must have only a single numeric item" in str(error_text.value)
# ------------------------------------------------------------------------------------------------
# TEST 2
# input = Fn

# ******
# Should functions be caught in validation, rather than with TypeError [just check callable()]?
# So that functions cause the same error as lists (see TEST 1 above)
# ******

def test_DDM_input_fn():
    with pytest.raises(TypeError) as error_text:
        stim = NormalDist().function
        T = DDM(
                name='DDM',
                function = Integrator(
                                        integration_type= DIFFUSION,
                                        noise = 0.0,
                                        rate = 1.0,
                                        time_step_size=1.0
                                      ),
                time_scale=TimeScale.TIME_STEP
               )
        val = float(T.execute(stim)[0])
    assert "unsupported operand type" in str(error_text.value)


# ======================================= RATE TESTS ============================================

# VALID RATES:

# ------------------------------------------------------------------------------------------------
# TEST 1
# rate = Int

def test_DDM_rate_int():
    stim = 10
    T = DDM(
            name='DDM',
            function = Integrator(
                                    integration_type= DIFFUSION,
                                    noise = 0.0,
                                    rate = 5,
                                    time_step_size=1.0
                                  ),
            time_scale=TimeScale.TIME_STEP
           )
    val = float(T.execute(stim)[0])
    assert val == 50

# ------------------------------------------------------------------------------------------------
# TEST 2
# rate = list len 1
#
# def test_DDM_rate_list_len_1():
#     stim = 10
#     T = DDM(
#         name='DDM',
#         function=Integrator(
#             integration_type=DIFFUSION,
#             noise=0.0,
#             rate=[5],
#             time_step_size=1.0
#         ),
#         time_scale=TimeScale.TIME_STEP
#     )
#     val = float(T.execute(stim)[0])
#     assert val == 50

# ------------------------------------------------------------------------------------------------
# TEST 3
# rate = float
#
# def test_DDM_rate_float():
#     stim = 10
#     T = DDM(
#         name='DDM',
#         function=Integrator(
#             integration_type=DIFFUSION,
#             noise=0.0,
#             rate=5,
#             time_step_size=1.0
#         ),
#         time_scale=TimeScale.TIME_STEP
#     )
#     val = float(T.execute(stim)[0])
#     assert val == 50

# ------------------------------------------------------------------------------------------------

# INVALID RATES:

# ------------------------------------------------------------------------------------------------
# TEST 1
# rate = fn

# ******
# Currently can't test because DDM is going to parameter_spec() which is throwing an error due to 'inspect' module
# ******

# def test_DDM_input_rate_fn():
#     with pytest.raises(DDMError) as error_text:
#         stim = [10, 10]
#         T = DDM(
#                 name='DDM',
#                 default_input_value=[0, 0],
#                 function = Integrator(
#                                         integration_type= DIFFUSION,
#                                         noise = 0.0,
#                                         rate = NormalDist().function,
#                                         time_step_size=1.0
#                                       ),
#                 time_scale=TimeScale.TIME_STEP
#                )
#         val = float(T.execute(stim)[0])
#     assert "must have only a single numeric item" in str(error_text.value)
# ------------------------------------------------------------------------------------------------