
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

print("------------------------")
print("Try out propery")

class C:

    def __init__(self,name:str):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,new_name):
        self._name = new_name

c = C("abc123")
c.name = "xyz"
print(c.name)
c.name = None
print(c.name)

print("------------------------")
print("Try out class poperty")

def needs_class(class_to_use:type[C]):
    c = class_to_use("A")
    print(c.name)

needs_class(C)


print("------------------------")
print("List Subclasses")

class Base:
    def __init__(self):
        self.name = 'Base class'


class ABase(Base):
    def __init__(self):
        self.name = 'A Base'


class BBase(Base):
    def __init__(self):
        self.name = 'A Base'

for cls in Base.__subclasses__():
    print(cls.__name__)
    t = cls()
    print(t)

print("------------------------")
print("reverse search")

a = ['a','b','c']
for i, e in reversed(list(enumerate(a))):
    print(i, e)
print(a)
a.reverse()
print(a)

print("------------------------")
print("path back")


def find_path_back(path:list[str],start:str,target:str):
    start_index:int = None
    end_index:int = None
    for index, pos in reversed(list(enumerate(path))):
        if pos == target:
            start_index = index
            break
    for index, pos in list(enumerate(path))[start_index:]:
        if pos == start:
            end_index = index
            break

    return path[start_index:end_index]
        

path = ['1','target','2','3','target','a','b','c','start_position','x','y','z','start_position','','start_position']


result = find_path_back(path,start='start_position',target='target')
print(result)
            # we need
            #self.move_back = [target,a,b,c]

print("------------------------")
print("Reduce path")
path = [2,3,4,5,6,7,6,5,8]
# expected [2,3,4,5,8]


def reduce_path(path:list):
    pos_map = dict()
    for index,pos in enumerate(path):
        if pos in pos_map:
            pos_map[pos].append(index)
        else:
            pos_map[pos] = [index]
    
    if len(pos_map) > 0 :
        cut_start = None
        cut_end = None
        cut_diff = 0
        for pos, index_list in pos_map.items():
            diff = index_list[-1] - index_list[0]
            if diff > cut_diff:
                cut_diff = diff
                cut_start = index_list[0]
                cut_end =  index_list[-1]

        if not cut_start is None and not cut_end is None:
            return path[:cut_start] + path[cut_end:]

reduced = reduce_path(path)
print(reduced)

print("composition delegation")

class Router:

    def __init__(self,shared_list:list[int]):
        self.shared_list = shared_list

class MainClass:

    def __init__(self):
        self.shared_list:list[int] = []
        self.router = Router(self.shared_list)

m = MainClass()
m.shared_list.append(1)
print(m.router.shared_list)

print("Color map")
import numpy as np



    