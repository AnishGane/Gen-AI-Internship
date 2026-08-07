"""
Object-Oriented Programming Concepts
"""

class SayHello():
    def __init__(self, *args, **kwargs):
        print("Hello")

hello = SayHello()

class Student():    
    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    def set_name(self, name):
        self.name = name
        
    def set_age(self, age):
        self.age = age

    def get_name_and_age(self):
        return self.name, self.age        
        
student = Student("Anish", 21)
student.set_name("New Anish")
student.set_age("22")
print(student.get_name_and_age())   

# __str__
class MyClass:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return f"MyClass {self.value}"

obj = MyClass(40)
print(f"obj: {obj}")

# Pyhton Inheritance

class Person:
    def __init__(self, fname, lname):
        self.first_name = fname
        self.last_name = lname

    def print_name(self):
        print(self.first_name, self.last_name)
        
class Student(Person):
    def __init__(self, fname, lname, age):
        super().__init__(fname, lname)
        self.age = age
        
    def welcome(self):
        print(f"Welcome, {self.first_name} {self.last_name} of {self.age} years old.")
        
std = Student("Mike", "Tyson", 40)
std.print_name()
std.welcome()

class Animal():
    pass

class Dog(Animal):
    pass

d = Dog()
print(isinstance(d, Animal))
print(isinstance(d, Dog))

# Polymorphism
class Car():
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def move(self):
            print("Drive!")

class Boat():
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def move(self):
            print("Sail!")

class Plane():
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def move(self):
            print("Fly!")
            
car1 = Car("Ford", "mustang")
boat1 = Boat("Honda", "Cruiser")
plane1 = Plane("Boeing", "747")

for vehicle in (car1, boat1, plane1):
    vehicle.move()
    
# Inheritance Class Polymorphism
class Animal:
    def __init__(self, name):
        self.name = name
        
    def make_sound(self):
        pass

class Dog(Animal):
    def make_sound(self):
        print("Woof!")

class Cat(Animal):
    def make_sound(self):
        print("Meow!")

dog = Dog("Buddy")
cat = Cat("Whiskers")

for animal in (dog, cat):
    animal.make_sound()
    print(f"Animal Name: {animal.name}")
    
# Pyhton Encapsulation
# Private Properties
class Person:
    def __init__(self, name, age):
        self.name = name
        self.__age = age

    def get_private_value(self):
        return self.__age
    
    def set_age(self, age):
        self.__age = age

p1 = Person("Anish", 21)
print(p1.name)
# print(p1.__age) # it causes Error
print(p1.get_private_value())
p1.set_age(22)
print(p1.get_private_value())   

# Private Methods
class Calculator:
    def __init__(self):
        self.result = 0

    def __validate(self, num):
        if not isinstance(num, (int, float)):
            return False
        return True

    def add(self, num):
        if self.__validate(num):
            self.result += num
        else:
            print("Invalid number!")

calc = Calculator()
calc.add(10)
calc.add(5)
print(f"Result of Calculator: {calc.result}")