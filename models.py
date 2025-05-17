import datetime

class MonHoc:
    def __init__(self, ma_mh, ten_mh, so_tin_chi):
        if not ma_mh or not ten_mh:
            raise ValueError("Mã môn học và Tên môn học không được để trống.")
        if not isinstance(so_tin_chi, int) or so_tin_chi <= 0:
            raise ValueError("Số tín chỉ phải là một số nguyên dương.")
        
        self.ma_mh = ma_mh
        self.ten_mh = ten_mh
        self.so_tin_chi = so_tin_chi

    def __str__(self):
        return f"{self.ten_mh} ({self.ma_mh}) - {self.so_tin_chi} tín chỉ"

    def to_dict(self):
        return {"ten_mh": self.ten_mh, "so_tin_chi": self.so_tin_chi}

    @classmethod
    def from_dict(cls, ma_mh, data):
        return cls(ma_mh, data["ten_mh"], data["so_tin_chi"])

class SinhVien:
    def __init__(self, ma_sv, ho_ten, lop_hoc, truong, khoa):
        if not ma_sv.isdigit() or len(ma_sv) != 9:
            raise ValueError("Mã SV không hợp lệ (phải là 9 chữ số).")
        
        self.ma_sv = ma_sv
        self.ho_ten = ho_ten
        self.lop_hoc = lop_hoc
        self.truong = truong
        self.khoa = khoa
        self.diem = {}  # Sẽ lưu dạng {ma_mon_hoc_obj.ma_mh: diem_so}
        self.ngay_cap_nhat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def them_diem(self, mon_hoc_obj, diem_so):
        if not isinstance(mon_hoc_obj, MonHoc):
            raise TypeError("Đối tượng môn học không hợp lệ.")
        if not (0 <= diem_so <= 10):
            raise ValueError("Điểm phải từ 0 đến 10.")
        self.diem[mon_hoc_obj.ma_mh] = diem_so
        self.ngay_cap_nhat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def tinh_gpa(self, danh_sach_mon_hoc_data): # danh_sach_mon_hoc_data là dict {ma_mh: MonHoc_obj}
        if not self.diem:
            return 0.0
        
        tong_diem_nhan_tin_chi = 0
        tong_so_tin_chi = 0
        
        for ma_mh, diem_val in self.diem.items():
            mon_hoc_obj = danh_sach_mon_hoc_data.get(ma_mh)
            if mon_hoc_obj:
                tong_diem_nhan_tin_chi += diem_val * mon_hoc_obj.so_tin_chi
                tong_so_tin_chi += mon_hoc_obj.so_tin_chi
            else:
                print(f"Cảnh báo (trong SinhVien.tinh_gpa): Không tìm thấy thông tin môn học cho mã '{ma_mh}' của SV '{self.ma_sv}'.")
        
        return tong_diem_nhan_tin_chi / tong_so_tin_chi if tong_so_tin_chi > 0 else 0.0

    def to_dict(self):
        return {
            "ho_ten": self.ho_ten, "lop_hoc": self.lop_hoc, "truong": self.truong,
            "khoa": self.khoa, "diem": self.diem, "ngay_cap_nhat": self.ngay_cap_nhat
        }

    @classmethod
    def from_dict(cls, ma_sv, data):
        sv = cls(ma_sv, data["ho_ten"], data["lop_hoc"], data["truong"], data["khoa"])
        sv.diem = data.get("diem", {})
        sv.ngay_cap_nhat = data.get("ngay_cap_nhat", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return sv