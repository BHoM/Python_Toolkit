﻿from ToBHoM import ToBHoM

import argparse

@ToBHoM()
def example_method(a: int, b: int):
    """
    This is an example method.
    """
    return "hello there"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', required=True, help='An int value', type=int)
    parser.add_argument('-b', required=True, help='Another int value', type=int)
    args = parser.parse_args()
    
    example_method(args.a, args.b)