"""
File with ONLY style/formatting errors (PEP8 violations)
No logical errors - code runs correctly but has poor style
"""

def calculate_sum( x,y,z ):
    """Calculate sum of three numbers"""
    Total=x+y+z
    return Total


class MyClass:
    def __init__(self,name,age):
        self.Name=name
        self.Age=age
    
    def get_info( self ):
        return f"{self.Name} is {self.Age} years old"


def process_list(items):
    result=[]
    for i in items:
        if i>0:
            result.append(i*2)
        else:
            result.append(i)
    return result


x=10
y=20
CONSTANT_VALUE=100

my_list=[1,2,3,4,5]
my_dict={'key1':'value1','key2':'value2'}

if x>5:result=x*2
else:result=x

def long_function_with_many_parameters(param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
    return param1+param2+param3+param4+param5+param6+param7+param8+param9+param10
