# scientific calculator example in Python
import math

def add(a, b):
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    return math.pow(a, b)

def sqrt(a):
    if a < 0:
        raise ValueError("Cannot take square root of negative number")
    return math.sqrt(a)

def main():
    print("Scientific Calculator")
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    print("Addition:", add(a, b))
    print("Subtraction:", subtract(a, b))
    print("Multiplication:", multiply(a, b))
    try:
        print("Division:", divide(a, b))
    except ValueError as e:
        print(e)
    print("Power:", power(a, b))
    try:
        print("Square Root of first number:", sqrt(a))
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()