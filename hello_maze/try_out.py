
from enum import Enum

class A:
    def __init__(self,param1):
        self.param1 = param1

        self._init()

    def _init(self):
        print("In A _init")

class B(A):
    def __init__(self,param1,param2):
        self.param2=param2
        super().__init__(param1)

    def _init(self):
        print("In B _init")

#a1 = B("1","2")

class ATypes(Enum):
    BLANK = A("Blank")
    STONE = A("Stone")


#for atype in (ATypes):
#    print(atype.value,"-",atype)


def test_func(parm1:(str |A)):
    if isinstance(parm1,str):
        print("parm1 is a string")
    if isinstance(parm1,A):
        print("parm1 is of class A")
    
def test_tuple(a:tuple[int,int]):
    print(a)

def test_str(a:str):
    print(a)

test_func("Test")
test_func(A("1"))
test_func(B("2","3"))

test_tuple((1,2))
test_tuple((1,2,3))
test_tuple((1))
test_tuple(("1"))
test_str(1)