import unittest
import numpy as np
import random
import brainspy
from brainspy.processors.hardware.drivers.ni.setup import NationalInstrumentsSetup
from tests.unit.processors.hardware.utils import check_test_configs
from brainspy.processors.hardware.drivers.nidaq import CDAQtoNiDAQ


class NIDAQ_Output_Synchronise_Test(unittest.TestCase):
    """
    Test synchronise_output_data of the Nidaq Driver.

    To run this file, the device has to be connected to a NIDAQ setup and
    the device configurations have to be specified depending on the setup.

    The test mode has to be set to HARDWARE_NIDAQ in tests/main.py.
    The required keys have to be defined in the get_configs() function.

    Some sample keys have been defined to run tests which do not require connection
    to the hardware.
    """

    def get_configs(self):
        """
        Generate configurations to initialize the Nidaq driver
        """
        configs = {}
        configs["inverted_output"] = True
        configs["amplification"] = 100
        configs["output_clipping_range"] = [-1, 1]

        configs["instrument_type"] = "cdaq_to_nidaq"
        configs["instruments_setup"] = {}
        configs["instruments_setup"]["multiple_devices"] = False
        # TODO Specify the name of the Trigger Source
        configs["instruments_setup"]["trigger_source"] = "a"

        # TODO Specify the name of the Activation instrument
        configs["instruments_setup"]["activation_instrument"] = "b"

        # TODO Specify the Activation channels (pin numbers)
        # For example, [1,2,3,4,5,6,7]
        configs["instruments_setup"]["activation_channels"] = [
            1, 2, 3, 4, 5, 6, 7
        ]

        # TODO Specify the activation Voltage ranges
        # For example, [[-1.2, 0.6],[-1.2, 0.6],[-1.2, 0.6],[-1.2, 0.6],[-1.2, 0.6],[-0.7, 0.3],[-0.7, 0.3]]
        configs["instruments_setup"]["activation_voltage_ranges"] = [
            [-1.2, 0.6], [-1.2, 0.6], [-1.2, 0.6], [-1.2, 0.6], [-1.2, 0.6],
            [-0.7, 0.3], [-0.7, 0.3]
        ]

        # TODO Specify the name of the Readout Instrument
        configs["instruments_setup"]["readout_instrument"] = "c"

        # TODO Specify the readout channels
        # For example, [4]
        configs["instruments_setup"]["readout_channels"] = [4]
        configs["instruments_setup"]["activation_sampling_frequency"] = 500
        configs["instruments_setup"]["readout_sampling_frequency"] = 1000
        configs["instruments_setup"]["average_io_point_difference"] = True
        return configs

    @unittest.skipUnless(
        brainspy.TEST_MODE == "HARDWARE_NIDAQ",
        "Method deactivated as it is only possible to be tested on a CDAQ TO NIDAQ setup"
    )
    def test_synchronise_output_data(self):
        """
        Test to synchornise output data with random shape of data
        """
        a1 = random.randint(1, 1000)
        a2 = random.randint(1, 9)
        configs = self.get_configs()
        nidaq = CDAQtoNiDAQ(configs)
        y = np.random.rand(a1, a2)
        try:
            nidaq.original_shape = y.shape[0]
            val = nidaq.synchronise_output_data(y)
        except (Exception):
            self.fail("Could not synchronise output data")
        finally:
            self.assertIsNotNone(val)
            nidaq.close_tasks()

    @unittest.skipUnless(
        brainspy.TEST_MODE == "HARDWARE_NIDAQ",
        "Method deactivated as it is only possible to be tested on a CDAQ TO NIDAQ setup"
    )
    def test_synchronise_output_data_single_dimension(self):
        """
        Input data with single dimension raises an Index Error
        """
        a1 = random.randint(1, 1000)
        configs = self.get_configs()
        nidaq = CDAQtoNiDAQ(configs)
        y = np.random.rand(a1)
        with self.assertRaises(IndexError):
            nidaq.synchronise_output_data(y)
        nidaq.close_tasks()

    @unittest.skipUnless(
        brainspy.TEST_MODE == "HARDWARE_NIDAQ",
        "Method deactivated as it is only possible to be tested on a CDAQ TO NIDAQ setup"
    )
    def test_synchronise_invalid_type(self):
        """
        Invalid type for input raises a Type Error
        """
        configs = self.get_configs()
        nidaq = CDAQtoNiDAQ(configs)
        with self.assertRaises(AssertionError):
            nidaq.synchronise_output_data("Invalid type")
        with self.assertRaises(AssertionError):
            nidaq.synchronise_output_data(100)
        with self.assertRaises(AssertionError):
            nidaq.synchronise_output_data([1, 2, 3, 4])
        nidaq.close_tasks()


if __name__ == "__main__":
    testobj = NIDAQ_Output_Synchronise_Test()
    configs = testobj.get_configs()
    try:
        NationalInstrumentsSetup.type_check(configs)
        if check_test_configs(configs):
            raise unittest.SkipTest("Configs are missing. Skipping all tests.")
        else:
            unittest.main()
    except (Exception):
        print(Exception)
        raise unittest.SkipTest(
            "Configs not specified correctly. Skipping all tests.")
