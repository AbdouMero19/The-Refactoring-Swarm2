"""
File with ONLY logical errors
Good style but incorrect logic
"""


def divide_numbers(a, b):
    """Divide two numbers - but has division by zero risk"""
    return a / b


def find_maximum(numbers):
    """Find maximum in list - but fails on empty list"""
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value


def calculate_average(numbers):
    """Calculate average - but doesn't handle empty list"""
    total = sum(numbers)
    return total / len(numbers)


def get_user_age(users, user_id):
    """Get user age - but doesn't check if user exists"""
    return users[user_id]['age']


def process_data(data):
    """Process data - infinite loop risk"""
    count = 0
    while count < 10:
        data.append(count)
        # Missing: count += 1
    return data


def factorial(n):
    """Calculate factorial - but doesn't handle negative numbers"""
    if n == 0:
        return 1
    return n * factorial(n - 1)


class BankAccount:
    """Bank account with logical errors"""
    
    def __init__(self, balance):
        self.balance = balance
    
    def withdraw(self, amount):
        """Withdraw money - no check for insufficient funds"""
        self.balance = self.balance - amount
        return self.balance
    
    def transfer(self, other_account, amount):
        """Transfer money - can result in negative balance"""
        self.balance -= amount
        other_account.balance += amount
