import pysd
import unittest
import inspect
import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal



print 'Testing module at location:', pysd.__file__


class Test_Vensim_Importer(unittest.TestCase):
    """ Test Import functionality """
    @classmethod
    def setUpClass(cls):
        cls.model = pysd.read_vensim('tests/old_tests/vensim/Teacup.mdl')

    def test_documentation(self):
        self.assertIsInstance(self.model.components.doc(), basestring)


class Test_PySD(unittest.TestCase):
    """ Testing basic execution functionality """
        #Probably should change this, because we modify the model when we
        #run it with new parameters, and best practice would be to make these
        #tests independednt"""
    
    @classmethod
    def setUpClass(cls):
        cls.model = pysd.read_vensim('tests/old_tests/vensim/Teacup.mdl')
    
    def test_run(self):
        stocks = self.model.run()
        self.assertTrue(stocks['teacup_temperature'].loc[29]<100)


    def test_run_return_timestamps(self):
        #re: https://github.com/JamesPHoughton/pysd/issues/17

        stocks = self.model.run(return_timestamps=[1,5,7])
        self.assertEqual(stocks.index[0],1)
    
        stocks = self.model.run(return_timestamps=5)
        self.assertEqual(stocks.index[0],5)


    def test_run_return_columns(self):
        #re: https://github.com/JamesPHoughton/pysd/issues/26
        result = self.model.run(return_columns=['room_temperature','teacup_temperature'])
        self.assertEqual(set(result.columns), set(['room_temperature','teacup_temperature']))
        #self.model.run(return_columns='room_temperature') #still to develop

    def test_initial_conditions(self):
        stocks = self.model.run(initial_condition=(0, {'teacup_temperature':33}))
        self.assertEqual(stocks['teacup_temperature'].loc[0], 33)
        
        stocks = self.model.run(initial_condition='current', return_timestamps=range(31,45))
        self.assertGreater(stocks['teacup_temperature'].loc[44], 0)
    
        with self.assertRaises(ValueError):
            self.model.run(initial_condition='bad value')

    def test_set_constant_parameter(self):
        #re: https://github.com/JamesPHoughton/pysd/issues/5
        self.model.set_components({'room_temperature':20})
        self.assertEqual(self.model.components.room_temperature(),20)
        
        self.model.run(params={'room_temperature':70})
        self.assertEqual(self.model.components.room_temperature(),70)

    def test_set_timeseries_parameter(self):
        temp_timeseries = pd.Series(index=range(30), data=range(20,80,2))
        values = self.model.run(params={'room_temperature':temp_timeseries},
                                return_columns=['teacup_temperature', 'room_temperature'])
        self.assertEqual(values['room_temperature'].loc[29], temp_timeseries.iloc[-1])

    @unittest.skip("in development")
    def test_docs(self):
        #test that the model prints the documentation
        print model #tests model.__str__
        print model.doc() #tests the function we wrote
        model.doc(short=True) #tests condensed model function printing.

    def test_collection(self):
        self.model.run(params={'room_temperature':75},
                  return_timestamps=range(0,30), collect=True)
        self.model.run(params={'room_temperature':25}, initial_condition='current',
                  return_timestamps=range(30,60), collect=True)
        stocks = self.model.get_record()
        self.assertTrue(all(stocks.index.values == np.array(range(0,60))))
        #We may drop this use case, as its relatively low value, and meeting it makes things slower.


class Test_Meta_Stuff(unittest.TestCase):
    """ The tests in this class test pysd's interaction with itself
        and other modules. """

    def test_multiple_load(self):
        model_1 = pysd.read_vensim('tests/old_tests/vensim/Teacup.mdl')
        model_1.run()

        model_2 = pysd.read_vensim('tests/old_tests/vensim/test_lookups.mdl')
        model_2.run()


class Test_Vensim_Models(unittest.TestCase):
    """ All of the tests here call upon a specific model file 
        that matches the name of the function """
    
    def test_number_handling(self):
        model = pysd.read_vensim('tests/old_tests/vensim/test_number_handling.mdl')
        
        #test integer division
        self.assertEqual(model.components.quotient(), model.components.quotient_target())

    def test_lookups(self):
        model = pysd.read_vensim('tests/old_tests/vensim/test_lookups.mdl')
        self.assertEqual(model.components.lookup_function_table(.4),.44)
        model.run()

    def test_long_variable_names(self):
        #re: https://github.com/JamesPHoughton/pysd/issues/19
        model = pysd.read_vensim('tests/old_tests/vensim/test_long_variable_names.mdl')
        self.assertEqual(model.components.particularly_efflusive_auxilliary_descriptor(),2)

    def test_vensim_functions(self):
        model = pysd.read_vensim('tests/old_tests/vensim/test_vensim_functions.mdl')
        testval = model.run(return_columns=['flow']).loc[10].values
        self.assertTrue(testval >= 1.556 and testval <= 1.558)

    def test_time(self):
        #re: https://github.com/JamesPHoughton/pysd/issues/25
        model = pysd.read_vensim('tests/old_tests/vensim/test_time.mdl')
        model.run()

    def test_multi_views(self):
        #just to make sure having multiple sheets doesn't influence reading
        model = pysd.read_vensim('tests/old_tests/vensim/test_multi_views.mdl')
        model.run()

    def test_delays(self):
        #re: https://github.com/JamesPHoughton/pysd/issues/18
        model = pysd.read_vensim('tests/old_tests/vensim/test_delays.mdl')
        model.run()

    def test_smooth(self):
        #re: https://github.com/JamesPHoughton/pysd/issues/18
        model = pysd.read_vensim('tests/old_tests/vensim/test_smooth.mdl')
        results = model.run(return_columns=['function_output','structure_output'])
        assert_series_equal(results['function_output'], results['structure_output'])

    def test_initial(self):
        model = pysd.read_vensim('tests/old_tests/vensim/test_initial.mdl')
        results = model.run(return_columns=['stocka',
                                            'stocka_initial_measured_value'])
        self.assertEqual(results.iloc[5]['stocka_initial_measured_value'],
                         results.iloc[0]['stocka'])

    def test_special_variable_names(self):
        model = pysd.read_vensim('tests/old_tests/vensim/test_special_variable_names.mdl')
        model.run()

    def test_variable_names_with_quotes(self):
        model = pysd.read_vensim('tests/old_tests/vensim/test_variable_names_with_quotes.mdl')
        model.run()

class Test_Xmile_Models(unittest.TestCase):

    def test_teacup(self):
        model = pysd.read_xmile('tests/old_tests/xmile/teacup.xmile')
        model.run()

if __name__ == '__main__':
    unittest.main()
