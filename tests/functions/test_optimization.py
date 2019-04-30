import numpy as np
import psyneulink.core.llvm as pnlvm
import psyneulink.core.components.functions.function as Function
import psyneulink.core.components.functions.objectivefunctions as Functions
import psyneulink.core.components.functions.optimizationfunctions as OPTFunctions
import psyneulink.core.globals.keywords as kw
from psyneulink.core.globals.sampleiterator import SampleIterator
import pytest

SIZE=5
# Some metrics (CROSS_ENTROPY) don't like 0s
test_var = np.random.rand(SIZE) + Function.EPSILON
EPS = float(Function.EPSILON)
search_space = [SampleIterator([EPS, 1.0]) for i in range(SIZE)]
results = {
    Functions.Stability: {
        kw.ENERGY: {
            True: {
                OPTFunctions.MINIMIZE: ((1.0, 1.0, 1.0, 1.0, 1.0), -0.4, [], []),
                OPTFunctions.MAXIMIZE: ((EPS, EPS, EPS, EPS, EPS), -1.9721522630525296e-32, [], []),
            },
            False: {
                OPTFunctions.MINIMIZE: ((1.0, 1.0, 1.0, 1.0, 1.0), -10.0, [], []),
                OPTFunctions.MAXIMIZE: ((EPS, EPS, EPS, EPS, EPS), -4.930380657631324e-31, [], []),
            },
        },
        kw.ENTROPY: {
            True: {
                OPTFunctions.MINIMIZE: ((1.0, 1.0, 1.0, 1.0, 1.0), -1.3862943611198906, [], []),
                OPTFunctions.MAXIMIZE: ((EPS, EPS, EPS, EPS, 1.0), 6.931471805599453, [], []),
            },
            False: {
                OPTFunctions.MINIMIZE: ((1.0, 1.0, 1.0, 1.0, 1.0), -6.931471805599453, [], []),
                OPTFunctions.MAXIMIZE: ((EPS, EPS, EPS, EPS, 1.0), 34.657359027997266, [], []),
            },
        },
    },
}

@pytest.mark.function
@pytest.mark.benchmark
@pytest.mark.optimization_function
@pytest.mark.parametrize("direction", [OPTFunctions.MINIMIZE, OPTFunctions.MAXIMIZE])
@pytest.mark.parametrize("normalize", [True, False])
@pytest.mark.parametrize("metric", [kw.ENERGY, kw.ENTROPY])
@pytest.mark.parametrize("obj_func", [Functions.Stability])
def test_basic(obj_func, metric, normalize, direction, benchmark):
    variable = test_var
    result = results[obj_func][metric][normalize][direction]
    benchmark.group = "OptimizationFunction " + str(obj_func) + " " + metric

    of = obj_func(default_variable=variable, metric=metric, normalize=normalize)
    f = OPTFunctions.GridSearch(objective_function=of, default_variable=variable, search_space=search_space, direction=direction)
    res = f.function(variable)
    benchmark(f.function, variable)

    assert np.allclose(res[0], result[0])
    assert np.allclose(res[1], result[1])
    assert np.allclose(res[2], result[2])
    assert np.allclose(res[3], result[3])


@pytest.mark.llvm
@pytest.mark.function
@pytest.mark.benchmark
@pytest.mark.optimization_function
@pytest.mark.parametrize("direction", [OPTFunctions.MINIMIZE, OPTFunctions.MAXIMIZE])
@pytest.mark.parametrize("normalize", [True, False])
@pytest.mark.parametrize("metric", [kw.ENERGY, kw.ENTROPY])
@pytest.mark.parametrize("obj_func", [Functions.Stability])
def test_llvm(obj_func, metric, normalize, direction, benchmark):
    variable = test_var
    result = results[obj_func][metric][normalize][direction]
    benchmark.group = "OptimizationFunction " + str(obj_func) + " " + metric

    of = obj_func(default_variable=variable, metric=metric, normalize=normalize)
    f = OPTFunctions.GridSearch(objective_function=of, default_variable=variable, search_space=search_space, direction=direction)
    e = pnlvm.execution.FuncExecution(f)
    res = e.execute(variable)
    benchmark(e.execute, variable)

    assert np.allclose(res[0], result[0])
    assert np.allclose(res[1], result[1])


@pytest.mark.llvm
@pytest.mark.cuda
@pytest.mark.function
@pytest.mark.optimization_function
@pytest.mark.benchmark
@pytest.mark.parametrize("direction", [OPTFunctions.MINIMIZE, OPTFunctions.MAXIMIZE])
@pytest.mark.parametrize("normalize", [True, False])
@pytest.mark.parametrize("metric", [kw.ENERGY, kw.ENTROPY])
@pytest.mark.parametrize("obj_func", [Functions.Stability])
def test_ptx_cuda(obj_func, metric, normalize, direction, benchmark):
    variable = test_var
    result = results[obj_func][metric][normalize][direction]
    benchmark.group = "OptimizationFunction " + str(obj_func) + " " + metric

    of = obj_func(default_variable=variable, metric=metric, normalize=normalize)
    f = OPTFunctions.GridSearch(objective_function=of, default_variable=variable, search_space=search_space, direction=direction)
    e = pnlvm.execution.FuncExecution(f)
    res = e.cuda_execute(variable)
    benchmark(e.cuda_execute, variable)

    assert np.allclose(res[0], result[0])
    assert np.allclose(res[1], result[1])
