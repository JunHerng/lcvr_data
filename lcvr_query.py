"""
Code to query LCVR array. Description to be updated as code develops

Author: Gan Jun Herng
Date: 6 May 2022
"""

from distutils.debug import DEBUG
from multiprocessing import dummy
from unittest import result
from S15lib.instruments import lcr_driver as lcr
from S15lib.instruments import TimeStampTDC1 as tdc
import numpy as np
import time
import sys

lcr_path = 'COM6'
tdc_path = 'COM35'
tdc_int_time = 0.3 # seconds
output_file = time.strftime("%Y%m%d_%H%M%S_lcvr_v3.csv")
idx = -2 # -4,-3,-2,-1 --> V1,V2,V3,V4


v_max_list = [10,10,10,10]
v_min_list = [10,10,10,10] 
v_min_list[idx] = 0

# Create class object
lcvr = lcr.LCRDriver(lcr_path)
tdc1 = tdc(tdc_path, integration_time=tdc_int_time)

# Initialize
lcvr.all_channels_on()

# while True:
# try:
#     user_prompt = "Enter voltages (V): \n"
#     user_input = input(user_prompt)
#     if user_input == "":
#         pass
#     else:
#         # parse input
#         try:
#             voltage_list = user_input.split(',')
#             voltage_floats = [float(x) for x in voltage_list]
#             if max(voltage_floats) > 10 or min(voltage_floats) < 0:
#                 print("Voltages must be between 0 and 10V")
#                 continue
#             else:
#                 lcvr.V1,lcvr.V2,lcvr.V3,lcvr.V4 = [voltage_floats[i] for i in (0,1,2,3)]
#         except ValueError:
#             print("Only 4 values, separated by commas, are allowed.")
# except KeyboardInterrupt:
#     print("Exiting program \n")
#     sys.exit()

def lcvr_multiple_query(min_volts: list, max_volts:list, interval:float, n: int):
    print('Starting program... \n')
    min_volts_np = np.array(min_volts, dtype=np.float32)
    max_volts_np = np.array(max_volts, dtype=np.float32)
    num_steps = np.floor((max_volts_np-min_volts_np)/interval)
    max_steps = np.int32(np.max(num_steps))
    for i in range(max_steps):
        # Take a voltage step
        print(f'Step:{i+1}/{max_steps}')
        min_volts_np[idx] += interval
        print(f'min_volts_np: {min_volts_np}')
        result_np = np.array([])
        for i in range(n):
            # Make n measurements at this voltage
            lcvr.V1,lcvr.V2,lcvr.V3,lcvr.V4 = [min_volts_np[i] for i in (0,1,2,3)]
            response = np.array(tdc1.get_counts(tdc_int_time))
            print(f'response: {response}')
            if result_np.size == 0:
                result_np = response
            else:
                # Collate results into matrix
                result_np = np.vstack([result_np,response])
                print(f'result_np: {result_np}')
        # Take average of all rows in matrix
        result_np = np.int32(result_np.mean(0))
        result_np = [str(entry) for entry in result_np]
        print(f'Final result: {result_np}')
        result_string = ','.join(result_np)
        with open(output_file, 'a+') as f:
            f.write(f'{min_volts_np[idx]:.3f}' + f',{result_string}' + '\n')
        f.close()
        print(f'Logged to {output_file}\n')


lcvr_multiple_query(v_min_list, v_max_list, 0.10, 10)