# models.py
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
    def __init__(self, ma_sv, ho_ten, lop_hoc, truong, khoa, hoc_ky_nhap_hoc): # Đổi tên hoc_ky
        if not ma_sv: # Bỏ kiểm tra isdigit và len ở đây, để QuanLyDiem xử lý
            raise ValueError("Mã SV không được để trống.") 

        self.ma_sv = ma_sv
        self.ho_ten = ho_ten
        self.lop_hoc = lop_hoc
        self.truong = truong
        self.khoa = khoa
        self.hoc_ky_nhap_hoc = hoc_ky_nhap_hoc # Đổi tên từ hoc_ky
        self.diem = {}  # Sẽ là: {hoc_ky_nhap: {ma_mon_hoc: diem_so}}
        self.ngay_cap_nhat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def them_diem(self, hoc_ky_diem, ma_mon_hoc, diem_so): # Đổi tên hoc_ky_nhap -> hoc_ky_diem
        if not hoc_ky_diem:
            raise ValueError("Học kỳ nhập điểm không được để trống.")
        if not (0 <= diem_so <= 10):
            raise ValueError("Điểm phải từ 0 đến 10.")
        
        hoc_ky_diem_norm = str(hoc_ky_diem).strip()
        ma_mon_hoc_norm = str(ma_mon_hoc).strip().upper()

        if hoc_ky_diem_norm not in self.diem:
            self.diem[hoc_ky_diem_norm] = {}
        self.diem[hoc_ky_diem_norm][ma_mon_hoc_norm] = float(diem_so)
        self.ngay_cap_nhat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True, f"Đã thêm điểm môn {ma_mon_hoc_norm} cho học kỳ {hoc_ky_diem_norm}."

    def sua_diem(self, hoc_ky_diem, ma_mon_hoc, diem_moi):
        if not (0 <= diem_moi <= 10):
            return False, "Điểm số mới phải từ 0 đến 10."
        hoc_ky_diem_norm = str(hoc_ky_diem).strip()
        ma_mon_hoc_norm = str(ma_mon_hoc).strip().upper()
        if hoc_ky_diem_norm in self.diem and ma_mon_hoc_norm in self.diem[hoc_ky_diem_norm]:
            self.diem[hoc_ky_diem_norm][ma_mon_hoc_norm] = float(diem_moi)
            self.ngay_cap_nhat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True, f"Đã cập nhật điểm môn {ma_mon_hoc_norm} trong học kỳ {hoc_ky_diem_norm}."
        return False, f"Không tìm thấy điểm môn {ma_mon_hoc_norm} trong học kỳ {hoc_ky_diem_norm} để sửa."

    def xoa_diem(self, hoc_ky_diem, ma_mon_hoc):
        hoc_ky_diem_norm = str(hoc_ky_diem).strip()
        ma_mon_hoc_norm = str(ma_mon_hoc).strip().upper()
        if hoc_ky_diem_norm in self.diem and ma_mon_hoc_norm in self.diem[hoc_ky_diem_norm]:
            del self.diem[hoc_ky_diem_norm][ma_mon_hoc_norm]
            if not self.diem[hoc_ky_diem_norm]: # Nếu học kỳ không còn môn nào
                del self.diem[hoc_ky_diem_norm]
            self.ngay_cap_nhat = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True, f"Đã xóa điểm môn {ma_mon_hoc_norm} trong học kỳ {hoc_ky_diem_norm}."
        return False, f"Không tìm thấy điểm môn {ma_mon_hoc_norm} trong học kỳ {hoc_ky_diem_norm} để xóa."

    def tinh_gpa(self, ds_mon_hoc_obj_dict, hoc_ky_filter=None): # Thêm hoc_ky_filter
        # ds_mon_hoc_obj_dict là {ma_mh: MonHoc_obj}
        # hoc_ky_filter: nếu được cung cấp, chỉ tính GPA cho học kỳ đó. Nếu None, tính GPA tích lũy.
        
        tong_diem_nhan_tin_chi = 0
        tong_so_tin_chi = 0
        co_diem_hop_le = False

        diem_can_tinh = {}
        hoc_ky_keys_to_process = []

        if hoc_ky_filter:
            hoc_ky_filter_norm = str(hoc_ky_filter).strip()
            if hoc_ky_filter_norm in self.diem:
                hoc_ky_keys_to_process.append(hoc_ky_filter_norm)
        else: # Tính GPA tích lũy
            hoc_ky_keys_to_process.extend(self.diem.keys())

        if not hoc_ky_keys_to_process and hoc_ky_filter : # Lọc theo kỳ cụ thể nhưng kỳ đó không có điểm / không tồn tại
            return 0.0, 0 # GPA, total_credits
        if not hoc_ky_keys_to_process and not hoc_ky_filter and not self.diem: # Tính tích lũy nhưng không có điểm nào
            return 0.0, 0 # GPA, total_credits

        for hoc_ky_key in hoc_ky_keys_to_process:
            diem_can_tinh = self.diem[hoc_ky_key]
            for ma_mh, diem_val in diem_can_tinh.items():
                ma_mh_norm = str(ma_mh).strip().upper()
                mon_hoc_obj = ds_mon_hoc_obj_dict.get(ma_mh_norm)
                if mon_hoc_obj and isinstance(mon_hoc_obj.so_tin_chi, int) and mon_hoc_obj.so_tin_chi > 0:
                    tong_diem_nhan_tin_chi += diem_val * mon_hoc_obj.so_tin_chi
                    tong_so_tin_chi += mon_hoc_obj.so_tin_chi
                    co_diem_hop_le = True

        if not co_diem_hop_le or tong_so_tin_chi == 0:
            return 0.0, 0 # GPA, total_credits
        
        gpa = tong_diem_nhan_tin_chi / tong_so_tin_chi
        return gpa, tong_so_tin_chi

    def to_dict(self):
        return {
            "ma_sv": self.ma_sv, # Thêm ma_sv để dễ dàng hơn khi lưu
            "ho_ten": self.ho_ten, "lop_hoc": self.lop_hoc, "truong": self.truong,
            "khoa": self.khoa, "hoc_ky_nhap_hoc": self.hoc_ky_nhap_hoc, "diem": self.diem, # Đổi tên
            "ngay_cap_nhat": self.ngay_cap_nhat
        }

    @classmethod
    def from_dict(cls, ma_sv, data):
        # Bỏ qua kiểm tra ma_sv ở đây nếu đã kiểm tra ở QuanLyDiem
        sv = cls(ma_sv, 
                 data["ho_ten"], 
                 data["lop_hoc"], 
                 data["truong"], 
                 data["khoa"], 
                 data.get("hoc_ky_nhap_hoc", "")) # Đổi tên và cung cấp giá trị mặc định
        sv.diem = data.get("diem", {})
        sv.ngay_cap_nhat = data.get("ngay_cap_nhat", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return sv