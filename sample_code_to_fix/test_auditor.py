import os # Unused import (Pylint Warning)

def CalculateSum(a,b): # Wrong naming convention (Pylint Convention)
    """
    A function with no proper docstring format.
    """
    res = a + b
    print(result) # ERROR: 'result' is not defined (Pylint Error)
    print(wassim) # WARNING: 'wassim' is not defined (Pylint Warning)
    z=z/0 # ERROR: Division by zero (Pylint Error)
    
    return res,z

# Missing final newline (Pylint Convention)