import json
from datetime import datetime

class QuanLyDiem:
    def __init__(self):
        self.sinh_vien = {}
        self.ten_file = "du_lieu_diem.json"
        self.load_du_lieu()

    def load_du_lieu(self):
        try:
            with open(self.ten_file, 'r', encoding='utf-8') as file:
                self.sinh_vien = json.load(file)
        except FileNotFoundError:
            self.sinh_vien = {}

    def luu_du_lieu(self):
        with open(self.ten_file, 'w', encoding='utf-8') as file:
            json.dump(self.sinh_vien, file, ensure_ascii=False, indent=4)

    def them_sinh_vien(self, ma_sv, ho_ten):
        if ma_sv not in self.sinh_vien:
            self.sinh_vien[ma_sv] = {
                "ho_ten": ho_ten,
                "diem": {},
                "ngay_cap_nhat": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            }
            self.luu_du_lieu()
            print(f"Đã thêm sinh viên {ho_ten} với mã số {ma_sv}")
        else:
            print("Mã số sinh viên đã tồn tại!")

    def nhap_diem(self, ma_sv, mon_hoc, diem):
        if ma_sv in self.sinh_vien:
            if 0 <= diem <= 10:
                self.sinh_vien[ma_sv]["diem"][mon_hoc] = diem
                self.sinh_vien[ma_sv]["ngay_cap_nhat"] = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                self.luu_du_lieu()
                print(f"Đã nhập điểm môn {mon_hoc} cho sinh viên {self.sinh_vien[ma_sv]['ho_ten']}")
            else:
                print("Điểm phải nằm trong khoảng từ 0 đến 10!")
        else:
            print("Không tìm thấy sinh viên với mã số này!")

    def xem_diem(self, ma_sv):
        if ma_sv in self.sinh_vien:
            sv = self.sinh_vien[ma_sv]
            print(f"\nThông tin sinh viên:")
            print(f"Mã số: {ma_sv}")
            print(f"Họ tên: {sv['ho_ten']}")
            print(f"Bảng điểm:")
            for mon, diem in sv['diem'].items():
                print(f"{mon}: {diem}")
            print(f"Cập nhật lần cuối: {sv['ngay_cap_nhat']}")
        else:
            print("Không tìm thấy sinh viên với mã số này!")

def main():
    ql = QuanLyDiem()
    while True:
        print("\n=== QUẢN LÝ ĐIỂM SINH VIÊN ===")
        print("1. Thêm sinh viên mới")
        print("2. Nhập điểm")
        print("3. Xem điểm")
        print("4. Thoát")
        
        lua_chon = input("\nChọn chức năng (1-4): ")
        
        if lua_chon == "1":
            ma_sv = input("Nhập mã số sinh viên: ")
            ho_ten = input("Nhập họ tên sinh viên: ")
            ql.them_sinh_vien(ma_sv, ho_ten)
            
        elif lua_chon == "2":
            ma_sv = input("Nhập mã số sinh viên: ")
            mon_hoc = input("Nhập tên môn học: ")
            try:
                diem = float(input("Nhập điểm (0-10): "))
                ql.nhap_diem(ma_sv, mon_hoc, diem)
            except ValueError:
                print("Vui lòng nhập điểm là số!")
                
        elif lua_chon == "3":
            ma_sv = input("Nhập mã số sinh viên cần xem điểm: ")
            ql.xem_diem(ma_sv)
            
        elif lua_chon == "4":
            print("Tạm biệt!")
            break
            
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
