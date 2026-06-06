# DEEPCRAFT Studio 5.12.5418.0+7793ebcc9f383586f202c2d2f6eafbd7ebe6519d
# Copyright © 2023- Imagimob AB, All Rights Reserved.
# 
# Generated at 06/06/2026 08:56:08 UTC. Any changes will be lost.
# 
# Layer                          Shape           Type       Function
# Sliding Window (data points)   [512,2]         float      dequeue
# Hann smoothing                 [512,2]         float      dequeue
# Real Discrete Fourier Transform [512,2,2]       float      dequeue
# Mel Filterbank                 [512,2,26]      float      dequeue
# Power to Decibel               [512,2,26]      float      dequeue
# 

import numpy as np
import enum

_K5 = np.empty((8400), dtype=np.int8)	# byte (8 bit) 
_K3 = np.empty((512,2), dtype=np.float32)	# float (32 bit) 
_K7 = np.empty((512,2), dtype=np.float32)	# float (32 bit) 
_K8 = np.empty((512,2,2), dtype=np.float32)	# float (32 bit) 
_K13 = np.empty((512,2,26), dtype=np.float32)	# float (32 bit) 

_K6 = np.array([0.00000000000000000000E+000, 0.00000000000000000000E+000, ]).reshape((2))
_K12 = np.array([0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 0.00000000000000000000E+000, 1.00000000000000000000E+000, 1.00000000000000000000E+000, 1.00000000000000000000E+000, 1.00000000000000000000E+000, 1.00000000000000000000E+000, ]).reshape((28))

class ReturnStatus(enum.Enum): 
    RET_SUCCESS = 0
    RET_NODATA = -1
    RET_NOMEM = -2

class SlidingWindowTime:
    def __init__(self, input_size: int, window_count : int):
        self._data_buffer = []
        self._time_buffer = []
        self._data_buffer_size = input_size * window_count
        self._input_size = input_size
        self._window_count = window_count
            
    def enqueue(self, data, time):
    
        self._data_buffer.extend(data.flatten())

        if len(self._data_buffer) > self._data_buffer_size:
            return ReturnStatus.RET_NOMEM                

        self._time_buffer.extend([time.flatten().min(), time.flatten().max()])
        return ReturnStatus.RET_SUCCESS

    def dequeue(self, data_out, data_stride: int, time_out):
        data_window_size = np.prod(data_out.shape)
        if len(self._data_buffer) >= data_window_size:
            data_window = np.array(self._data_buffer[:data_window_size]).reshape(data_out.shape)
            np.copyto(data_out, data_window)
            del self._data_buffer[:(data_stride * self._input_size)]
           
            timestamp_count = 2 * self._window_count;
            time_window = np.array(self._time_buffer[:timestamp_count]).reshape(timestamp_count)
            time_out[0] = time_window.min()
            time_out[1] = time_window.max()
            del self._time_buffer[:2 * data_stride]
            
            return ReturnStatus.RET_SUCCESS

        return ReturnStatus.RET_NODATA

def hann_mul(a, b, output):
    np.multiply(a, b, out=output)

def rfft(input, output, axis):
    result = np.fft.rfft(input, axis=-axis-1)                  # compute FFT
    np.stack((result.real, result.imag), axis=-1, out=output)  # flatten complex array (e.g. complex [4,3,6] to float [4,3,6,2])

def mel(input, filter_points, output, nsize, htk):  
    if not htk:
        raise NotImplementedError("not implemented. htk must be true")

    filters = np.zeros((len(filter_points)-2, nsize), dtype=np.float32)
    for n in range(len(filter_points)-2):
        n0 = int(filter_points[n])
        n1 = int(filter_points[n + 1])
        n2 = int(filter_points[n + 2])
        filters[n, n0 : n1] = np.linspace(0, 1, n1 - n0, endpoint=False)
        filters[n, n1 : n2] = np.linspace(1, 0, n2 - n1, endpoint=False)

    np.dot(filters, input, out=output)

def power_to_db(input, output, ref, amin, topdb):
    log_spec = 10.0 * np.log10(np.maximum(amin, input)) - 10.0 * np.log10(np.maximum(amin, ref))
    log_spec = np.maximum(log_spec, log_spec.max() - topdb)
    np.copyto(output, log_spec)


class Model:
    def __init__(self):
        self._K5 = SlidingWindowTime(2, 512)
        self.data_in_count = 2
        self.data_in_shape = (2)
        self.time_in_count = 1
        self.time_in_shape = (1)
        self.data_out_count = 26624
        self.data_out_shape = (512,2,26)
        self.time_out_count = 2
        self.time_out_shape = (2)
        self.api = 'queue'

    def enqueue(self, data_in : np.array, time_in : np.array):
        """
        Enqueue features. Returns SUCCESS (0) on success, else RET_NOMEM (-2) when low on memory.
        
        Parameters:
         data_in(float[2]): DESCRIPTION. [2]
         time_in(float[1]): DESCRIPTION. [1]
        """
        
        return_status = self._K5.enqueue(data_in, time_in)
        if return_status != ReturnStatus.RET_SUCCESS:
            return return_status
        
        return ReturnStatus.RET_SUCCESS

    def dequeue(self, data_out : np.array, time_out : np.array):
        """
        Dequeue features. RET_SUCCESS (0) on success, RET_NODATA (-1) if no data is available, RET_NOMEM (-2) on internal memory error
        
        Parameters:
         data_out(float[26624]): DESCRIPTION. [512,2,26]
         time_out(float[2]): DESCRIPTION. [2]
        """
        
        return_status = self._K5.dequeue(_K3, 128, time_out.reshape([2]))
        if return_status != ReturnStatus.RET_SUCCESS:
            return return_status
        
        hann_mul(_K3, _K6, _K7)
        rfft(_K7, _K8, 0)
        mel(_K8, _K12, _K13, 2, True)
        power_to_db(_K13, data_out.reshape([512,2,26]), 1, 1E-10, 80)
        return ReturnStatus.RET_SUCCESS

