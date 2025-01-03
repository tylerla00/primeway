import numpy as np
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(arg1, arg2="arg2_value"):
    print("Hello from the cloud again!")
    logging.info("Hello from the cloud again here!")
    # User's computation code here
    arr = np.array([1, 2, 3])
    print("arr", arr)
    logging.info(f"arr: {arr}")
    time.sleep(5)

    arr = np.array([4, 5, 6])
    print("arr2", arr)
    logging.info(f"arr23: {arr}")


    time.sleep(10)

    arr = np.array([7, 8, 9])
    print("arr2", arr)
    logging.info(f"arr45: {arr}")

if __name__ == "__main__":
    main(1, arg2="updated arg2")


# import runpod

# runpod.api_key = "1BWA440QUYLETAH8X614UGY6X1JJHDV58NPD1VL5"

# print(runpod.get_gpus())