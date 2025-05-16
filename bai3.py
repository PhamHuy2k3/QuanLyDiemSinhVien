def find_farthest_value(arr, x):
    farthest_value = arr[0]
    max_distance = abs(arr[0] - x)
    for value in arr:
        distance = abs(value - x)
        if distance > max_distance:
            max_distance = distance
            farthest_value = value
    return farthest_value

input_array = input("Nhập các số thực cách nhau bằng dấu phẩy: ")
arr = [float(num) for num in input_array.split(",")]
x = float(input("Nhập giá trị x: "))
farthest_value = find_farthest_value(arr, x)
print(f"Giá trị xa {x} nhất là: {farthest_value}")

def find_nearest_value(arr, x):
    nearest_value = arr[0]
    print (nearest_value)
    min_distance = abs(arr[0] - x)

    for value in arr:
        distance = abs(value - x)
        if distance < min_distance:
            min_distance = distance
            nearest_value = value

    return nearest_value
input_array = input("Nhập các số thực cách nhau bằng dấu phẩy: ")
arr = [float(num) for num in input_array.split(",")]
x = float(input("Nhập giá trị x: "))
nearest_value = find_nearest_value(arr, x)
print(f"Giá trị xa {x} nhất là: {nearest_value}")