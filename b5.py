def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_last_prime(arr):
    for num in reversed(arr):
        if is_prime(num):
            return num
    return -1  # Trường hợp không có số nguyên tố

# Ví dụ sử dụng
input_array = input("Nhập các số thực cách nhau bằng dấu phẩy: ")
arr = [float(num) for num in input_array.split(",")]
last_prime = find_last_prime(arr)
print(last_prime)  # Kết quả: 11