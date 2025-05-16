def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def get_prime_numbers(numbers):
    return [num for num in numbers if is_prime(num)]

# Input list of integers
input_list = []
n = int(input("Nhập số lượng phần tử: "))
for i in range(n):
    num = int(input(f"Nhập số thứ {i+1}: "))
    input_list.append(num)

# Get prime numbers and print results
prime_list = get_prime_numbers(input_list)

print("Danh sách ban đầu:", input_list)
print("Danh sách các số nguyên tố:", prime_list)