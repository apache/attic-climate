import os
import unittest
import datetime as dt

from webtest import TestApp

from backend.config import WORK_DIR
from backend.run_webservices import app
import backend.processing as bp

import ocw.metrics as metrics
import ocw.data_source.rcmed as rcmed
from ocw.dataset import Dataset
from ocw.evaluation import Evaluation

import numpy

test_app = TestApp(app)

class TestLocalDatasetLoad(unittest.TestCase):
    def setUp(self):
        self.dataset_object = {
            'dataset_id': os.path.abspath('/tmp/d1.nc'),
            'var_name': 'tasmax',
            'lat_name': 'lat',
            'lon_name': 'lon',
            'time_name': 'time'
        }

    def test_valid_load(self):
        dataset = bp._load_local_dataset_object(self.dataset_object)
        self.assertEqual(dataset.variable, self.dataset_object['var_name'])

    def test_default_name_assignment(self):
        dataset = bp._load_local_dataset_object(self.dataset_object)
        self.assertEqual(dataset.name, 'd1.nc')

    def test_custom_name_assignment(self):
        self.dataset_object['name'] = 'CustomName'
        dataset = bp._load_local_dataset_object(self.dataset_object)
        self.assertEqual(dataset.name, self.dataset_object['name'])

class TestDatasetProessingHelper(unittest.TestCase):
    def test_invalid_process_dataset_objects(self):
        invalid_dataset_object = {'data_source_id': 3, 'dataset_info': {}}
        self.assertRaises(
                ValueError,
                bp._process_dataset_object,
                invalid_dataset_object, 'fake parameter')

class TestRCMEDDatasetLoad(unittest.TestCase):
    def setUp(self):
        metadata = rcmed.get_parameters_metadata()
        # Load TRMM from RCMED
        dataset_dat = [m for m in metadata if m['parameter_id'] == '36'][0]

        self.dataset_info = {
            'dataset_id': int(dataset_dat['dataset_id']),
            'parameter_id': int(dataset_dat['parameter_id'])
        }

        self.eval_bounds = {
            'start_time': dt.datetime(1998, 02, 01),
            'end_time': dt.datetime(1998, 03, 01),
            'lat_min': -10,
            'lat_max': 10,
            'lon_min': -15,
            'lon_max': 15
        }

    def test_valid_load(self):
        dataset = bp._load_rcmed_dataset_object(self.dataset_info, self.eval_bounds)
        lat_min, lat_max, lon_min, lon_max = dataset.spatial_boundaries()
        start_time, end_time = dataset.time_range()

        self.assertTrue(self.eval_bounds['lat_min'] <= lat_min)
        self.assertTrue(self.eval_bounds['lat_max'] >= lat_max)
        self.assertTrue(self.eval_bounds['lon_min'] <= lon_min)
        self.assertTrue(self.eval_bounds['lon_max'] >= lon_max)
        self.assertTrue(self.eval_bounds['start_time'] <= start_time)
        self.assertTrue(self.eval_bounds['end_time'] >= end_time)

    def test_default_name_assignment(self):
        dataset = bp._load_rcmed_dataset_object(self.dataset_info, self.eval_bounds)
        self.assertEquals(dataset.name, 'TRMM v.7 Monthly Precipitation')

    def test_custom_name_assignment(self):
        self.dataset_info['name'] = 'CustomName'
        dataset = bp._load_rcmed_dataset_object(self.dataset_info, self.eval_bounds)
        self.assertEquals(dataset.name, self.dataset_info['name'])


class TestMetricLoad(unittest.TestCase):
    def test_get_valid_metric_options(self):
        metric_map = bp._get_valid_metric_options()
        bias = metric_map['Bias']()
        self.assertTrue(isinstance(bias, metrics.Bias))

    def test_valid_metric_load(self):
        metric_objs = bp._load_metrics(['Bias'])
        self.assertTrue(isinstance(metric_objs[0], metrics.Bias))

    def test_invalid_metric_load(self):
        self.assertRaises(ValueError, bp._load_metrics, ['AAA'])

class TestSpatialRebinHelpers(unittest.TestCase):
    def test_latlon_bin_helper(self):
        eval_bounds = {
            'lat_min': -57.2,
            'lat_max': 58.2,
            'lon_min': -45.3,
            'lon_max': 39.2,
        }
        lat_step = 1
        lon_step = 1

        lats = numpy.arange(eval_bounds['lat_min'], eval_bounds['lat_max'])
        lons = numpy.arange(eval_bounds['lon_min'], eval_bounds['lon_max'])

        new_lats, new_lons = bp._calculate_new_latlon_bins(eval_bounds, lat_step, lon_step)

        self.assertTrue(numpy.array_equal(lats, new_lats))
        self.assertTrue(numpy.array_equal(lons, new_lons))

class TestCalculateGridShape(unittest.TestCase):
    def test_grid_shape_calculation(self):
        ref_dataset = _create_fake_dataset('foo')
        shape = bp._calculate_grid_shape(ref_dataset, max_cols=3)
        self.assertEquals(shape, (3, 3))

class TestBalanceGridShape(unittest.TestCase):
    def test_balance_grid_shape(self):
        # Test column imbalance
        self.assertEquals(bp._balance_grid_shape(7, 2, 6), (3, 3))
        self.assertEquals(bp._balance_grid_shape(7, 2, 4), (3, 3))
        self.assertEquals(bp._balance_grid_shape(10, 2, 6), (3, 4))
        self.assertEquals(bp._balance_grid_shape(20, 3, 7), (4, 5))

        # Test row imbalance
        self.assertEquals(bp._balance_grid_shape(7, 6, 2), (3, 3))
        self.assertEquals(bp._balance_grid_shape(7, 4, 2), (3, 3))
        self.assertEquals(bp._balance_grid_shape(10, 6, 2), (3, 4))
        self.assertEquals(bp._balance_grid_shape(20, 7, 3), (4, 5))

class TestFilePathCreation(unittest.TestCase):
    def setUp(self):
        self.full_evaluation = Evaluation(
            _create_fake_dataset('Ref'),
            [_create_fake_dataset('T1'), _create_fake_dataset('T2')],
            [metrics.TemporalStdDev(), metrics.Bias(), metrics.Bias()]
        )

        self.unary_evaluation = Evaluation(
            None,
            [_create_fake_dataset('T1'), _create_fake_dataset('T2')],
            [metrics.TemporalStdDev()]
        )

    def test_binary_metric_path_generation(self):
        time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.assertEquals(
            bp._generate_binary_eval_plot_file_path(self.full_evaluation,
                                                    0, # dataset_index
                                                    1, # metric_index
                                                    time_stamp),
            '/tmp/ocw/{}/ref_compared_to_t1_bias'.format(time_stamp)
        )

    def test_unary_metric_path_generation_full_eval(self):
        time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.assertEquals(
            bp._generate_unary_eval_plot_file_path(self.full_evaluation,
                                                   0, # dataset_index
                                                   0, # metric_index
                                                   time_stamp),
            '/tmp/ocw/{}/ref_temporalstddev'.format(time_stamp)
        )

        self.assertEquals(
            bp._generate_unary_eval_plot_file_path(self.full_evaluation,
                                                   1, # dataset_index
                                                   0, # metric_index
                                                   time_stamp),
            '/tmp/ocw/{}/t1_temporalstddev'.format(time_stamp)
        )

    def test_unary_metric_path_generation_partial_eval(self):
        time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.assertEquals(
            bp._generate_unary_eval_plot_file_path(self.unary_evaluation,
                                                   0, # dataset_index
                                                   0, # metric_index
                                                   time_stamp),
            '/tmp/ocw/{}/t1_temporalstddev'.format(time_stamp)
        )

        self.assertEquals(
            bp._generate_unary_eval_plot_file_path(self.unary_evaluation,
                                                   1, # dataset_index
                                                   0, # metric_index
                                                   time_stamp),
            '/tmp/ocw/{}/t2_temporalstddev'.format(time_stamp)
        )

class TestPlotTitleCreation(unittest.TestCase):
    def setUp(self):
        self.full_evaluation = Evaluation(
            _create_fake_dataset('Ref'),
            [_create_fake_dataset('T1'), _create_fake_dataset('T2')],
            [metrics.TemporalStdDev(), metrics.Bias(), metrics.Bias()]
        )

        self.unary_evaluation = Evaluation(
            None,
            [_create_fake_dataset('T1'), _create_fake_dataset('T2')],
            [metrics.TemporalStdDev()]
        )

    def test_binary_plot_title_generation(self):
        self.assertEquals(
            bp._generate_binary_eval_plot_title(self.full_evaluation, 0, 1),
            'Bias of Ref compared to T1'
        )

    def test_unary_plot_title_generation_full_eval(self):
        self.assertEqual(
            bp._generate_unary_eval_plot_title(self.full_evaluation, 0, 0),
            'TemporalStdDev of Ref'
        )

        self.assertEqual(
            bp._generate_unary_eval_plot_title(self.full_evaluation, 1, 0),
            'TemporalStdDev of T1'
        )

	def test_unary_plot_title_generation_partial_eval(self):
		self.assertEquals(
            bp._generate_unary_eval_plot_title(self.unary_evaluation, 0, 0),
            'TemporalStdDev of T1'
        )

        self.assertEquals(
            bp._generate_unary_eval_plot_title(self.unary_evaluation, 1, 0),
            'TemporalStdDev of T2'
        )

class TestRunEvaluation(unittest.TestCase):
    def test_full_evaluation(self):
        data = {
            'reference_dataset': {
                'data_source_id': 1,
                'dataset_info': {
                    'dataset_id': os.path.abspath('/tmp/d1.nc'),
                    'var_name': 'tasmax',
                    'lat_name': 'lat',
                    'lon_name': 'lon',
                    'time_name': 'time'
                }
            },
            'target_datasets': [
                {
                    'data_source_id': 1,
                    'dataset_info': {
                        'dataset_id': os.path.abspath('/tmp/d2.nc'),
                        'var_name': 'tasmax',
                        'lat_name': 'lat',
                        'lon_name': 'lon',
                        'time_name': 'time'
                    }
                }
            ],
            'spatial_rebin_lat_step': 1,
            'spatial_rebin_lon_step': 1,
            'temporal_resolution': 365,
            'metrics': ['Bias'],
            'start_time': '1989-01-01 00:00:00',
            'end_time': '1991-01-01 00:00:00',
            'lat_min': -25.0,
            'lat_max': 22.0,
            'lon_min': -14.0,
            'lon_max': 40.0,
            'subregion_information': None
        }

        # NOTE: Sometimes the file download will die if you use the this WebTest
        # call for testing. If that is the case, download the files manually with wget.
        test_app.post_json('/processing/run_evaluation/', data)
        result_dirs = [x for x in os.listdir(WORK_DIR)
                       if os.path.isdir(os.path.join(WORK_DIR, x))]

        eval_dir = os.path.join(WORK_DIR, result_dirs[-1])
        eval_files = [f for f in os.listdir(eval_dir)
                      if os.path.isfile(os.path.join(eval_dir, f))]

        self.assertTrue(len(eval_files) == 1)
        self.assertEquals(eval_files[0], 'd1.nc_compared_to_d2.nc_bias.png')

class TestMetricNameRetrieval(unittest.TestCase):
    def test_metric_name_retrieval(self):
        invalid_metrics = ['ABCMeta', 'Metric', 'UnaryMetric', 'BinaryMetric']
        data = test_app.get('/processing/metrics/').json
        metrics = data['metrics']

        self.assertTrue(invalid_metrics not in metrics)
        self.assertTrue(len(metrics) > 0)
        self.assertTrue('Bias' in metrics)

def _create_fake_dataset(name):
    lats = numpy.array(range(-10, 25, 1))
    lons = numpy.array(range(-30, 40, 1))
    times = numpy.array(range(8))
    values = numpy.zeros((len(times), len(lats), len(lons)))

    return Dataset(lats, lons, times, values, name=name)
