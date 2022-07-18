import unittest

import torch
import numpy as np
import random
from brainspy.processors import dnpu
from brainspy.utils.pytorch import TorchUtils
from brainspy.processors.processor import Processor

class ProcessorTest(unittest.TestCase):
    """
    Class for testing 'dnpu.py'.
    """
    def __init__(self, *args, **kwargs) -> None:
        super(ProcessorTest, self).__init__(*args, **kwargs)
        self.configs = {}
        self.configs["processor_type"] = "simulation"
        self.configs["electrode_effects"] = {}
        self.configs["electrode_effects"]["clipping_value"] = None
        self.configs["driver"] = {}
        self.configs["waveform"] = {}
        self.configs["waveform"]["plateau_length"] = 1
        self.configs["waveform"]["slope_length"] = 0

        self.info = {}
        self.info['model_structure'] = {}
        self.info['model_structure']['hidden_sizes'] = [90, 90, 90, 90, 90]
        self.info['model_structure']['D_in'] = 7
        self.info['model_structure']['D_out'] = 1
        self.info['model_structure']['activation'] = 'relu'
        self.info['electrode_info'] = {}
        self.info['electrode_info']['electrode_no'] = 8
        self.info['electrode_info']['activation_electrodes'] = {}
        self.info['electrode_info']['activation_electrodes']['electrode_no'] = 7
        self.info['electrode_info']['activation_electrodes'][
            'voltage_ranges'] = np.array([[-0.55, 0.325], [-0.95, 0.55],
                                          [-1., 0.6], [-1., 0.6], [-1., 0.6],
                                          [-0.95, 0.55], [-0.55, 0.325]])
        self.info['electrode_info']['output_electrodes'] = {}
        self.info['electrode_info']['output_electrodes']['electrode_no'] = 1
        self.info['electrode_info']['output_electrodes']['amplification'] = [28.5]
        self.info['electrode_info']['output_electrodes']['clipping_value'] = None

        self.node = Processor(self.configs, self.info)
        self.model = dnpu.DNPU(self.node, data_input_indices=[[3, 4]])
        self.dim1 =  torch.randint(1, 4, (1,1)).squeeze().item()
        self.dim2 =  torch.randint(1, 7, (1,1)).squeeze().item()
        random_data_indices = [np.random.choice(np.arange(0, 7), size=self.dim2, replace=False).tolist() for _ in range(self.dim1)]
        # Test extreme cases (where (input) dimension are zero, when (input)dimensions are more than electrodes available, when(input) dimensions are equal to electrode number)
        self.multi_model = dnpu.DNPU(self.node, data_input_indices=random_data_indices)

    # def test_merge_numpy(self):
    #     """
    #     Test merging numpy arrays.
    #     """
    #     inputs = TorchUtils.format(
    #         np.array([
    #             [1.0, 5.0, 9.0, 13.0],
    #             [2.0, 6.0, 10.0, 14.0],
    #             [3.0, 7.0, 11.0, 15.0],
    #             [4.0, 8.0, 12.0, 16.0],
    #         ]))
    #     control_voltages = inputs + TorchUtils.format(np.ones(inputs.shape))
    #     input_indices = [0, 2, 4, 6]
    #     control_voltage_indices = [7, 5, 3, 1]
    #     result = merge_electrode_data(input_data=inputs,
    #                                   control_data=control_voltages,
    #                                   input_data_indices=input_indices,
    #                                   control_indices=control_voltage_indices)
    #     self.assertEqual(result.shape, (4, 8))
    #     self.assertIsInstance(result, np.ndarray)
    #     target = np.array([
    #         [1.0, 14.0, 5.0, 10.0, 9.0, 6.0, 13.0, 2.0],
    #         [2.0, 15.0, 6.0, 11.0, 10.0, 7.0, 14.0, 3.0],
    #         [3.0, 16.0, 7.0, 12.0, 11.0, 8.0, 15.0, 4.0],
    #         [4.0, 17.0, 8.0, 13.0, 12.0, 9.0, 16.0, 5.0],
    #     ])
    #     for i in range(target.shape[0]):
    #         for j in range(target.shape[1]):
    #             self.assertEqual(result[i][j], target[i][j])

    def test_merge_torch(self):
        """
        Test merging torch tensors.
        """
        inputs = TorchUtils.format(
            torch.tensor(
                [
                    [1.0, 5.0, 9.0, 13.0],
                    [2.0, 6.0, 10.0, 14.0],
                    [3.0, 7.0, 11.0, 15.0],
                    [4.0, 8.0, 12.0, 16.0],
                ],
                device=TorchUtils.get_device(),
                dtype=torch.get_default_dtype(),
            ))
        control_voltages = inputs + TorchUtils.format(
            torch.ones(inputs.shape, dtype=torch.get_default_dtype()))
        control_voltages.to(TorchUtils.get_device())
        input_indices = [0, 2, 4, 6]
        control_voltage_indices = [7, 5, 3, 1]
        result = dnpu.merge_electrode_data(input_data=inputs,
                                      control_data=control_voltages,
                                      input_data_indices=input_indices,
                                      control_indices=control_voltage_indices)
        result2 = dnpu.merge_electrode_data(input_data=inputs,
                                      control_data=control_voltages,
                                      input_data_indices=input_indices,
                                      control_indices=control_voltage_indices)
        self.assertEqual(result.shape, (4, 8))
        self.assertEqual(result2.shape, (4, 8))
        self.assertIsInstance(result, torch.Tensor)
        target = torch.tensor(
            [
                [1.0, 14.0, 5.0, 10.0, 9.0, 6.0, 13.0, 2.0],
                [2.0, 15.0, 6.0, 11.0, 10.0, 7.0, 14.0, 3.0],
                [3.0, 16.0, 7.0, 12.0, 11.0, 8.0, 15.0, 4.0],
                [4.0, 17.0, 8.0, 13.0, 12.0, 9.0, 16.0, 5.0],
            ],
            dtype=torch.float32,
        )
        for i in range(target.shape[0]):
            for j in range(target.shape[1]):
                self.assertEqual(result[i][j], target[i][j])
                self.assertEqual(result2[i][j], target[i][j])

    def test_forward_pass(self):
        try:
            self.model.set_forward_pass("for")
            self.model.set_forward_pass("vec")
            self.multi_model.set_forward_pass("for")
            self.multi_model.set_forward_pass("vec")
        except:
            self.fail("Failed setting forward pass DNPU")

        with self.assertRaises(ValueError):
            self.model.set_forward_pass("matrix")
            self.multi_model.set_forward_pass("matrix")

        with self.assertRaises(ValueError):
            self.model.set_forward_pass(["vec"])
            self.multi_model.set_forward_pass(["vec"])

    def test_init_node_no(self):
        try:
            self.model.init_node_no()
            self.multi_model.init_node_no()
        except:
            self.fail("Failed calculating nodes DNPU")

    def test_activ_elec(self):
        try:
            input_data_electrode_no, control_electrode_no = self.model.init_activation_electrode_no()
            input_data_electrode_no, control_electrode_no = self.multi_model.init_activation_electrode_no()
        except:
            self.fail("Failed Initializing activation electrode DNPU")

    def test_init_elec_info(self):
        try:
            self.model.init_electrode_info([[0, 2]])
        except:
            self.fail("Failed Initializing electrode info DNPU")

    def test_sample_control(self):
        try:
            control_voltage = self.model.sample_controls()
            control_voltage = self.multi_model.sample_controls()
        except:
            self.fail("Failed sampling control voltage")
 
    def test_init(self):
        try:
            self.model._init_bias()
            self.model._init_learnable_parameters()
            self.multi_model._init_bias()
            self.multi_model._init_learnable_parameters()
        except:
            self.fail("Failed Initializing bias and parameters")

    def test_forward(self):
        try:
            x1 = torch.randn(size=(10, 2))
            x2 = torch.randn(size=(10, self.dim1*self.dim2))
            y = self.model.forward_for(x1)
            y2 = self.multi_model.forward_for(x2)
        except:
            self.fail("Failed Initializing electrode info DNPU")


if __name__ == "__main__":
    unittest.main()
