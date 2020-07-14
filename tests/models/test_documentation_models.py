import json
import os
import runpy
import sys

import numpy as np
import pytest

import psyneulink as pnl


# NOTE: to add new models, run the script with valid results, then
# dump the results of a Composition to a file named
# {model_name}-{composition_name}.json in the same directory as
# the library models. Example for Cohen_Huston1994:
# json.dump(
#     Bidirectional_Stroop.results,
#     cls=pnl.PNLJSONEncoder,
#     fp=open('psyneulink/library/models/results/Cohen_Huston1994-Bidirectional_Stroop.json', 'w'),
#     indent=2,
# )
# Using prettier https://prettier.io/ can reduce the line footprint of
# the resulting file while not totally minifying it
@pytest.mark.parametrize(
    'model_name, composition_name, additional_args',
    [
        ('Cohen_Huston1994', 'Bidirectional_Stroop', []),
        ('Cohen_Huston1994_horse_race', 'Bidirectional_Stroop', []),
        ('GilzenratModel', 'task', ['--noise-stddev=0.0']),
        ('Kalanthroff_PCTC_2018', 'PCTC', []),
        ('MontagueDayanSejnowski96', 'comp_5a', ['--figure', '5a']),
        ('MontagueDayanSejnowski96', 'comp_5b', ['--figure', '5b']),
        ('MontagueDayanSejnowski96', 'comp_5c', ['--figure', '5c']),
        ('Nieuwenhuis2005Model', 'task', []),
    ]
)
def test_documentation_models(model_name, composition_name, additional_args):
    models_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'psyneulink',
        'library',
        'models'
    )
    model_file = os.path.join(models_dir, f'{model_name}.py')
    old_argv = sys.argv
    sys.argv = [model_file, '--no-plot'] + additional_args
    script_globals = runpy.run_path(model_file)
    sys.argv = old_argv

    expected_results_file = os.path.join(
        models_dir,
        'results',
        f'{model_name}-{composition_name}.json'
    )
    with open(expected_results_file) as fi:
        expected_results = pnl.convert_all_elements_to_np_array(json.loads(fi.read()))

    results = pnl.convert_all_elements_to_np_array(script_globals[composition_name].results)

    assert expected_results.shape == results.shape
    np.testing.assert_allclose(
        pytest.helpers.expand_np_ndarray(expected_results),
        pytest.helpers.expand_np_ndarray(results)
    )
