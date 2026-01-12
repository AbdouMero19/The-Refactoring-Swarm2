"""
File with BOTH style AND logical errors including EXTREME errors
This file has everything: style issues, logic bugs, undeclared variables, indentation errors
"""

import sys
import os,json

# Extreme error: Inconsistent indentation
def broken_function(x,y):
  result=x+y  # 2 spaces
    return result  # 4 spaces - INDENTATION ERROR

# Undeclared variable usage
def use_undeclared():
    print(undefined_variable)  # Variable not declared
    return mystery_var * 2  # Another undeclared variable

# Missing imports but using them
def use_missing_import():
    data=np.array([1,2,3])  # numpy not imported
    return pd.DataFrame(data)  # pandas not imported

class BrokenClass:
  def __init__(self,name,value):
      self.name=name
  # Missing self.value assignment
  
  def calculate(self):
    # Using undeclared instance variable
      return self.value*2+self.price  # price never defined

# Extreme indentation mess
def indentation_nightmare(items):
  result=[]
  for item in items:
   if item>0:
        result.append(item*2)
   else:
      result.append(item)
        print("Negative")  # Wrong indentation
  return result

# Division by zero + style issues
def dangerous_division(a,b):
    x=a/b  # No zero check
    y=x/0  # Intentional division by zero
    return y

# Undefined variables in expressions
def math_operations():
    total=x+y+z  # x, y, z not defined
    average=total/count  # count not defined
    return average*multiplier  # multiplier not defined

# Mixing tabs and spaces (Python 3 will error)
def tab_space_mix():
	x = 10  # Tab
    y = 20  # Spaces
	return x + y  # Tab

# Unreachable code + undeclared variable
def unreachable_code():
    return result  # result not declared
    x=10  # Unreachable
    print(x)  # Unreachable

# Infinite loop + undeclared variable
def infinite_disaster():
    while True:
        process(data)  # data not declared
        # No break condition

# Wrong number of return values
def inconsistent_returns(x):
    if x>0:
        return x,x*2
    else:
        return x  # Different return structure

# Using deleted variable
def use_deleted():
    value=100
    del value
    return value*2  # Using deleted variable

# Syntax errors in string formatting
def broken_formatting():
    name="Alice"
    age=30
    message=f"Name: {nama} Age: {age}"  # Typo: nama instead of name
    return message

# Class with missing methods but calling them
class IncompleteClass:
    def __init__(self,data):
        self.data=data
    
    def process(self):
        self.validate()  # Method doesn't exist
        return self.transform()  # Method doesn't exist

# Multiple errors in one function
def chaos_function(a,b,c):
  x=a+undefined_var  # Undeclared variable
    y=b/0  # Division by zero
  z=missing_func(c)  # Undefined function
      return x+y+z  # Wrong indentation
