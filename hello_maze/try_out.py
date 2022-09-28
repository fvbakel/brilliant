
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

print("------------------------")
print("Try out 1")
a1 = B("1","2")

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


print("------------------------")
print("Try out 2")
test_func("Test")
test_func(A("1"))
test_func(B("2","3"))

test_tuple((1,2))
test_tuple((1,2,3))
test_tuple((1))
test_tuple(("1"))
test_str(1)

print("------------------------")
print("Try out 3")
class X:
    def __init__(self):
        self.children : list[A]
        self._init()

    def _init(self):
        self.children = []
        self.children.append(self._init_child())

    def _init_child(self):
        return A("Test")

    def get_child(self,index:int):
        return self.children[index]

class Y(X):
    def __init__(self):
        self.children : list[B]
        super().__init__()
    
    def _init_child(self):
        return B("Test","Test2")

    def get_child(self,index:int) -> B:
        super().get_child(index)


def test_X_Y_class():
    x_1 = X()
    child_x_1 = x_1.get_child(0)
    print("child_x_1", child_x_1)

    y_1 = Y()
    child_y_1 = y_1.get_child(0)
    print("child_y_1", child_y_1)


test_X_Y_class()

print("------------------------")
print("Try out 4")
from dataclasses import dataclass

@dataclass(frozen=True,eq=True)
class DataClass_1:
    one:A
    two:A

set_DataClass_1:set[DataClass_1] = set()

a = A("1")
b = A("2")

c = DataClass_1(a,b)
d = DataClass_1(a,b)

set_DataClass_1.add(c)
set_DataClass_1.add(d)

if len(set_DataClass_1) == 1:
    print("Same dataclass is added only once!")