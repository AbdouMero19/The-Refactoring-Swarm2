import os # Unused import (Pylint Warning)

def CalculateSum(a,b): # Wrong naming convention (Pylint Convention)
    """
    A function with no proper docstring format.
    """
    res = a + b
    print(result) # ERROR: 'result' is not defined (Pylint Error)
    return res

# Missing final newline (Pylint Convention)