# Đặt tên file này là quan_ly_diem.py
import csv
import os
from datetime import datetime
from models import MonHoc, SinhVien # Import từ models.py

DATA_DIR = "data_ql_diem" # Thư mục lưu trữ dữ liệu
SV_FILE = os.path.join(DATA_DIR, "sinh_vien.csv")
MH_FILE = os.path.join(DATA_DIR, "mon_hoc.csv")
DIEM_FILE = os.path.join(DATA_DIR, "diem_sinh_vien.csv") # File riêng cho điểm

class QuanLyDiem:
    def __init__(self):
        self.danh_sach_sinh_vien = {}  # {ma_sv: SinhVienObject}
        self.danh_sach_mon_hoc = {}    # {ma_mh: MonHocObject}
        self._kiem_tra_tao_thu_muc_data()
        self.load_data_mh()
        self.load_data_sv() # Load SV trước
        self.load_data_diem() # Load điểm sau khi có SV và MH


    def _kiem_tra_tao_thu_muc_data(self):
        if not os.path.exists(DATA_DIR):
            try:
                os.makedirs(DATA_DIR)
            except OSError as e:
                print(f"Lỗi: không thể tạo thư mục {DATA_DIR}: {e}")
                # Có thể raise exception ở đây nếu thư mục là bắt buộc

    # --- Quản lý Môn học ---
    def load_data_mh(self):
        if not os.path.exists(MH_FILE):
            # Tạo file rỗng nếu chưa có
            with open(MH_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ma_mh', 'ten_mh', 'so_tin_chi'])
            return
        try:
            with open(MH_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try: # Sử dụng MonHoc từ models.py
                        ma_mh_val = str(row['ma_mh']).strip().upper()
                        ten_mh_val = str(row['ten_mh']).strip()
                        so_tin_chi_val = int(row['so_tin_chi'])
                        mon_hoc = MonHoc(ma_mh_val, ten_mh_val, so_tin_chi_val)
                        self.danh_sach_mon_hoc[mon_hoc.ma_mh] = mon_hoc
                    except ValueError as e:
                        print(f"Lỗi khi tải môn học (dòng {reader.line_num}): {row} - {e}. Bỏ qua.")
                    except KeyError as e:
                        print(f"Lỗi thiếu cột trong file mon_hoc.csv (dòng {reader.line_num}): {e}. Bỏ qua.")
        except FileNotFoundError:
            print(f"Thông báo: File {MH_FILE} không tồn tại. Sẽ tạo mới khi lưu.")
        except Exception as e:
            print(f"Lỗi không xác định khi tải dữ liệu môn học: {e}")

    def save_data_mh(self):
        try:
            with open(MH_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ma_mh', 'ten_mh', 'so_tin_chi'])
                for mon_hoc in self.danh_sach_mon_hoc.values():
                    writer.writerow([mon_hoc.ma_mh, mon_hoc.ten_mh, mon_hoc.so_tin_chi])
            return True, "Lưu dữ liệu môn học thành công."
        except Exception as e:
            return False, f"Lỗi khi lưu dữ liệu môn học: {e}"

    def them_mon_hoc(self, ma_mh, ten_mh, so_tin_chi_str):
        ma_mh_norm = str(ma_mh).strip().upper()
        if not ma_mh_norm or not str(ten_mh).strip() or not so_tin_chi_str.strip():
            return False, "Mã, tên môn học và số tín chỉ không được để trống."
        if ma_mh_norm in self.danh_sach_mon_hoc:
            return False, f"Mã môn học '{ma_mh_norm}' đã tồn tại."
        try:
            # Sử dụng MonHoc từ models.py
            ten_mh_strip = str(ten_mh).strip()
            so_tin_chi_int = int(so_tin_chi_str) # MonHoc constructor trong models.py sẽ validate
            mon_hoc = MonHoc(ma_mh_norm, ten_mh_strip, so_tin_chi_int)
            self.danh_sach_mon_hoc[mon_hoc.ma_mh] = mon_hoc
            self.save_data_mh()
            return True, f"Đã thêm môn học: {mon_hoc.ten_mh} ({mon_hoc.ma_mh})."
        except ValueError as e:
            return False, str(e)

    def sua_mon_hoc(self, ma_mh, ten_mh_moi, so_tin_chi_moi_str):
        ma_mh_norm = str(ma_mh).strip().upper()
        if not ma_mh_norm:
            return False, "Mã môn học không được để trống."
        if ma_mh_norm not in self.danh_sach_mon_hoc:
            return False, f"Mã môn học '{ma_mh_norm}' không tồn tại để sửa."

        mon_hoc_can_sua = self.danh_sach_mon_hoc[ma_mh_norm]
        try:
            ten_mh_moi_strip = str(ten_mh_moi).strip()
            if not ten_mh_moi_strip:
                return False, "Tên môn học mới không được để trống."
            
            so_tin_chi_moi = int(so_tin_chi_moi_str)
            if so_tin_chi_moi <=0:
                 return False, "Số tín chỉ mới phải là số dương."

            mon_hoc_can_sua.ten_mh = ten_mh_moi_strip
            mon_hoc_can_sua.so_tin_chi = so_tin_chi_moi
            self.save_data_mh()
            return True, f"Đã cập nhật môn học '{ma_mh_norm}'."
        except ValueError:
            return False, "Số tín chỉ mới không hợp lệ."
        except Exception as e:
            return False, f"Lỗi không xác định khi sửa môn học: {e}"


    def xoa_mon_hoc(self, ma_mh):
        ma_mh_norm = str(ma_mh).strip().upper()
        if ma_mh_norm not in self.danh_sach_mon_hoc:
            return False, f"Mã môn học '{ma_mh_norm}' không tồn tại."
        # Kiểm tra xem môn học có được sử dụng trong điểm của sinh viên nào không
        for sv in self.danh_sach_sinh_vien.values():
            for hoc_ky_data in sv.diem.values():
                if ma_mh_norm in hoc_ky_data:
                    return False, f"Không thể xóa môn '{ma_mh_norm}'. Môn học đã có điểm của sinh viên '{sv.ho_ten}'."
        del self.danh_sach_mon_hoc[ma_mh_norm]
        self.save_data_mh()
        return True, f"Đã xóa môn học '{ma_mh_norm}'."

    def lay_thong_tin_mon_hoc(self, ma_mh):
        return self.danh_sach_mon_hoc.get(str(ma_mh).strip().upper())

    def lay_tat_ca_mon_hoc(self): # GUI cần list of dicts
        return [{'ma_mh': mh.ma_mh, 'ten_mh': mh.ten_mh, 'so_tin_chi': mh.so_tin_chi}
                for mh in self.danh_sach_mon_hoc.values()]

    # --- Quản lý Sinh viên ---
    def load_data_sv(self):
        if not os.path.exists(SV_FILE):
            with open(SV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ma_sv', 'ho_ten', 'lop_hoc', 'truong', 'khoa', 'hoc_ky_nhap_hoc'])
            return
        try:
            with open(SV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try: # Sử dụng SinhVien từ models.py
                        # Đảm bảo các key trong row khớp với mong đợi của SinhVien constructor
                        sv_data_for_model = {
                            "ma_sv": str(row['ma_sv']).strip(),
                            "ho_ten": str(row['ho_ten']).strip(),
                            "lop_hoc": str(row['lop_hoc']).strip(),
                            "truong": str(row['truong']).strip(),
                            "khoa": str(row['khoa']).strip(),
                            "hoc_ky_nhap_hoc": str(row['hoc_ky_nhap_hoc']).strip() # Khớp với model
                        }
                        sv = SinhVien(**sv_data_for_model)
                        self.danh_sach_sinh_vien[sv.ma_sv] = sv
                    except ValueError as e:
                        print(f"Lỗi khi tải sinh viên (dòng {reader.line_num}): {row} - {e}. Bỏ qua.")
                    except KeyError as e:
                        print(f"Lỗi thiếu cột trong file sinh_vien.csv (dòng {reader.line_num}): {e}. Bỏ qua.")
        except FileNotFoundError:
             print(f"Thông báo: File {SV_FILE} không tồn tại. Sẽ tạo mới khi lưu.")
        except Exception as e:
            print(f"Lỗi không xác định khi tải dữ liệu sinh viên: {e}")

    def save_data_sv(self):
        try:
            with open(SV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ma_sv', 'ho_ten', 'lop_hoc', 'truong', 'khoa', 'hoc_ky_nhap_hoc'])
                for sv in self.danh_sach_sinh_vien.values():
                    writer.writerow([sv.ma_sv, sv.ho_ten, sv.lop_hoc, sv.truong, sv.khoa, sv.hoc_ky_nhap_hoc]) # sv.hoc_ky_nhap_hoc từ model
            return True, "Lưu dữ liệu sinh viên thành công."
        except Exception as e:
            return False, f"Lỗi khi lưu dữ liệu sinh viên: {e}"

    def them_sinh_vien(self, ma_sv, ho_ten, lop_hoc, truong, khoa, hoc_ky_nhap_hoc_param): # đổi tên param
        ma_sv_norm = str(ma_sv).strip()
        # Validate MSSV theo yêu cầu của GUI (9 chữ số)
        if not (ma_sv_norm.isdigit() and len(ma_sv_norm) == 9):
            return False, "Mã số sinh viên phải là 9 chữ số."
        if ma_sv_norm in self.danh_sach_sinh_vien:
            return False, f"Mã sinh viên '{ma_sv_norm}' đã tồn tại."
        try: # Sử dụng SinhVien từ models.py
            sv = SinhVien(ma_sv=ma_sv_norm, 
                          ho_ten=str(ho_ten).strip(), 
                          lop_hoc=str(lop_hoc).strip(), 
                          truong=str(truong).strip(), 
                          khoa=str(khoa).strip(), 
                          hoc_ky_nhap_hoc=str(hoc_ky_nhap_hoc_param).strip()) # Khớp với model
            self.danh_sach_sinh_vien[sv.ma_sv] = sv
            self.save_data_sv() # Lưu thông tin SV cơ bản
            return True, f"Đã thêm sinh viên: {sv.ho_ten} ({sv.ma_sv})."
        except ValueError as e:
            return False, str(e)

    # --- Quản lý Điểm ---
    def lay_tat_ca_sinh_vien(self): # GUI cần list of dicts
        return [{'ma_sv': sv.ma_sv, 'ho_ten': sv.ho_ten, 'lop_hoc': sv.lop_hoc,
                 'truong': sv.truong, 'khoa': sv.khoa, 'hoc_ky_nhap_hoc': sv.hoc_ky_nhap_hoc}
                for sv in self.danh_sach_sinh_vien.values()]

    def load_data_diem(self):
        if not os.path.exists(DIEM_FILE):
            with open(DIEM_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ma_sv', 'hoc_ky', 'ma_mh', 'diem_so'])
            return
        try:
            with open(DIEM_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        ma_sv = str(row['ma_sv']).strip()
                        hoc_ky = str(row['hoc_ky']).strip()
                        ma_mh = str(row['ma_mh']).strip().upper()
                        diem_so = float(row['diem_so'])

                        sv = self.danh_sach_sinh_vien.get(ma_sv)
                        mh = self.danh_sach_mon_hoc.get(ma_mh)

                        if sv and mh: # Chỉ thêm điểm nếu SV và MH hợp lệ
                            # Sử dụng sv.them_diem từ models.SinhVien
                            sv.them_diem(hoc_ky_diem=hoc_ky, ma_mon_hoc=ma_mh, diem_so=diem_so)
                        elif not sv:
                            print(f"Cảnh báo: Không tìm thấy SV '{ma_sv}' khi tải điểm cho môn '{ma_mh}'. Bỏ qua.")
                        elif not mh:
                             print(f"Cảnh báo: Không tìm thấy Môn học '{ma_mh}' khi tải điểm cho SV '{ma_sv}'. Bỏ qua.")

                    except ValueError:
                        print(f"Lỗi giá trị không hợp lệ trong file điểm (dòng {reader.line_num}): {row}. Bỏ qua.")
                    except KeyError as e:
                        print(f"Lỗi thiếu cột trong file diem_sinh_vien.csv (dòng {reader.line_num}): {e}. Bỏ qua.")
        except FileNotFoundError:
            print(f"Thông báo: File {DIEM_FILE} không tồn tại. Sẽ tạo mới khi lưu.")
        except Exception as e:
            print(f"Lỗi không xác định khi tải dữ liệu điểm: {e}")


    def save_data_diem(self):
        try:
            with open(DIEM_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ma_sv', 'hoc_ky', 'ma_mh', 'diem_so'])
                for sv_ma, sv_obj in self.danh_sach_sinh_vien.items():
                    for hoc_ky, diem_mon_hoc_dict in sv_obj.diem.items():
                        for ma_mh, diem_so in diem_mon_hoc_dict.items():
                            writer.writerow([sv_ma, hoc_ky, ma_mh, diem_so])
            return True, "Lưu dữ liệu điểm thành công."
        except Exception as e:
            return False, f"Lỗi khi lưu dữ liệu điểm: {e}"

    def nhap_diem(self, ma_sv, ma_mh, diem_so, hoc_ky_diem):
        ma_sv_norm = str(ma_sv).strip()
        ma_mh_norm = str(ma_mh).strip().upper()
        hoc_ky_diem_norm = str(hoc_ky_diem).strip()

        if not hoc_ky_diem_norm:
            return False, "Học kỳ nhập điểm không được để trống."
        sv = self.danh_sach_sinh_vien.get(ma_sv_norm)
        if not sv:
            return False, f"Không tìm thấy sinh viên với mã: {ma_sv_norm}."
        if ma_mh_norm not in self.danh_sach_mon_hoc:
            return False, f"Không tìm thấy môn học với mã: {ma_mh_norm}."

        # sv là đối tượng SinhVien từ models.py
        success, message = sv.them_diem(hoc_ky_diem=hoc_ky_diem_norm, ma_mon_hoc=ma_mh_norm, diem_so=diem_so)
        if success:
            self.save_data_diem() # Lưu lại toàn bộ file điểm
        return success, message

    def sua_diem(self, ma_sv, ma_mh, diem_moi, hoc_ky_diem):
        ma_sv_norm = str(ma_sv).strip()
        ma_mh_norm = str(ma_mh).strip().upper()
        hoc_ky_diem_norm = str(hoc_ky_diem).strip()

        if not hoc_ky_diem_norm:
            return False, "Học kỳ sửa điểm không được để trống."

        sv = self.danh_sach_sinh_vien.get(ma_sv_norm)
        if not sv:
            return False, f"Không tìm thấy sinh viên với mã: {ma_sv_norm}."
        # Không cần kiểm tra môn học tồn tại ở đây vì đang sửa điểm đã có
        # sv là đối tượng SinhVien từ models.py
        success, message = sv.sua_diem(hoc_ky_diem=hoc_ky_diem_norm, ma_mon_hoc=ma_mh_norm, diem_moi=diem_moi)
        if success:
            self.save_data_diem()
        return success, message

    def sua_sinh_vien(self, ma_sv, thong_tin_moi_dict):
        ma_sv_norm = str(ma_sv).strip()
        if not ma_sv_norm:
            return False, "Mã sinh viên không được để trống khi sửa."
        if ma_sv_norm not in self.danh_sach_sinh_vien:
            return False, f"Không tìm thấy sinh viên với mã '{ma_sv_norm}' để sửa."

        sv_can_sua = self.danh_sach_sinh_vien[ma_sv_norm]

        # Validate và cập nhật từng trường
        try:
            ho_ten_moi = str(thong_tin_moi_dict.get('ho_ten', sv_can_sua.ho_ten)).strip()
            lop_hoc_moi = str(thong_tin_moi_dict.get('lop_hoc', sv_can_sua.lop_hoc)).strip()
            truong_moi = str(thong_tin_moi_dict.get('truong', sv_can_sua.truong)).strip()
            khoa_moi = str(thong_tin_moi_dict.get('khoa', sv_can_sua.khoa)).strip()
            hoc_ky_nhap_hoc_moi = str(thong_tin_moi_dict.get('hoc_ky_nhap_hoc', sv_can_sua.hoc_ky_nhap_hoc)).strip()

            if not all([ho_ten_moi, lop_hoc_moi, truong_moi, khoa_moi, hoc_ky_nhap_hoc_moi]):
                return False, "Các thông tin (Họ tên, Lớp, Trường, Khoa, HK nhập học) không được để trống."

            sv_can_sua.ho_ten = ho_ten_moi
            sv_can_sua.lop_hoc = lop_hoc_moi
            sv_can_sua.truong = truong_moi
            sv_can_sua.khoa = khoa_moi
            sv_can_sua.hoc_ky_nhap_hoc = hoc_ky_nhap_hoc_moi
            sv_can_sua.ngay_cap_nhat = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Cập nhật ngày

            self.save_data_sv()
            return True, f"Đã cập nhật thông tin cho sinh viên '{ma_sv_norm}'."
        except Exception as e:
            return False, f"Lỗi không xác định khi cập nhật sinh viên: {e}"

    def xoa_sinh_vien(self, ma_sv):
        ma_sv_norm = str(ma_sv).strip()
        if ma_sv_norm not in self.danh_sach_sinh_vien:
            return False, f"Không tìm thấy sinh viên với mã '{ma_sv_norm}' để xóa."

        # Kiểm tra ràng buộc: Sinh viên có điểm không?
        if self.danh_sach_sinh_vien[ma_sv_norm].diem: # Nếu dict điểm không rỗng
            return False, f"Không thể xóa sinh viên '{ma_sv_norm}'. Sinh viên này đã có dữ liệu điểm."

        del self.danh_sach_sinh_vien[ma_sv_norm]
        self.save_data_sv()
        return True, f"Đã xóa sinh viên '{ma_sv_norm}'."

    def xoa_diem(self, ma_sv, ma_mh, hoc_ky_diem): # hoc_ky_diem là học kỳ của điểm đó
        ma_sv_norm = str(ma_sv).strip()
        ma_mh_norm = str(ma_mh).strip().upper()
        hoc_ky_diem_norm = str(hoc_ky_diem).strip()

        sv = self.danh_sach_sinh_vien.get(ma_sv_norm)
        if not sv:
            return False, f"Không tìm thấy sinh viên với mã: {ma_sv_norm}."
        # sv là đối tượng SinhVien từ models.py
        success, message = sv.xoa_diem(hoc_ky_diem=hoc_ky_diem_norm, ma_mon_hoc=ma_mh_norm)
        if success:
            self.save_data_diem()
        return success, message

    def lay_tat_ca_hoc_ky_da_nhap_diem(self):
        hoc_ky_set = set()
        for sv_obj in self.danh_sach_sinh_vien.values():
            if sv_obj.diem:
                for hoc_ky in sv_obj.diem.keys():
                    hoc_ky_set.add(hoc_ky)
        return sorted(list(hoc_ky_set))

    # --- Tìm kiếm và Báo cáo ---
    def tim_kiem_diem(self, ma_sv_filter=None, ma_mon_hoc_filter=None,
                      lop_hoc_filter=None, truong_filter=None, khoa_filter=None,
                      hoc_ky_filter=None): # hoc_ky_filter là học kỳ của điểm
        results = []
        for ma_sv, sv_obj in self.danh_sach_sinh_vien.items():
            if ma_sv_filter and ma_sv_filter.lower() not in sv_obj.ma_sv.lower():
                continue # Bỏ qua nếu mã SV không khớp (nếu có filter mã SV)
            if lop_hoc_filter and (not sv_obj.lop_hoc or lop_hoc_filter.lower() != sv_obj.lop_hoc.lower()):
                continue
            if truong_filter and (not sv_obj.truong or truong_filter.lower() != sv_obj.truong.lower()):
                continue
            if khoa_filter and (not sv_obj.khoa or khoa_filter.lower() != sv_obj.khoa.lower()):
                continue

            if not sv_obj.diem:
                if ma_mon_hoc_filter or hoc_ky_filter: # Nếu lọc theo môn hoặc kỳ mà SV ko có điểm thì bỏ qua
                    continue
                # Nếu chỉ lọc theo thông tin SV và SV không có điểm, vẫn có thể thêm SV vào kết quả (tùy yêu cầu)
                # Nếu muốn hiển thị SV dù không có điểm khi chỉ lọc theo thông tin SV:
                if not ma_mon_hoc_filter and not hoc_ky_filter: # Chỉ lọc theo thông tin SV
                    results.append({
                        'ma_sv': sv_obj.ma_sv, 'ho_ten': sv_obj.ho_ten,
                        'lop_hoc': sv_obj.lop_hoc, 'truong': sv_obj.truong, 'khoa': sv_obj.khoa,
                        'hoc_ky_diem': "N/A", 'mon_hoc': "Chưa có điểm", 
                        'ma_mon_hoc': "N/A", 'diem': ""
                    })
                continue # Bỏ qua xử lý điểm nếu SV không có điểm
                

            for hoc_ky_diem, diem_mon_hoc_dict in sv_obj.diem.items():
                if hoc_ky_filter and hoc_ky_filter.lower() != hoc_ky_diem.lower():
                    continue

                for ma_mh, diem_so in diem_mon_hoc_dict.items():
                    if ma_mon_hoc_filter and ma_mon_hoc_filter.lower() != ma_mh.lower():
                        continue

                    mon_hoc_obj = self.danh_sach_mon_hoc.get(str(ma_mh).strip().upper()) # Lấy MonHoc object
                    ten_mh_display = mon_hoc_obj.ten_mh if mon_hoc_obj else ma_mh

                    results.append({
                        'ma_sv': sv_obj.ma_sv,
                        'ho_ten': sv_obj.ho_ten,
                        'lop_hoc': sv_obj.lop_hoc,
                        'truong': sv_obj.truong,
                        'khoa': sv_obj.khoa,
                        'hoc_ky_diem': hoc_ky_diem, # Học kỳ của điểm số này
                        'mon_hoc': ten_mh_display, # Tên môn học
                        'ma_mon_hoc': ma_mh, # Mã môn học
                        'diem': diem_so
                    })
        # Sắp xếp kết quả (ví dụ theo mã SV, rồi học kỳ, rồi tên môn)
        results.sort(key=lambda x: (x['ma_sv'], x['hoc_ky_diem'], x['mon_hoc']))
        return results

    def xep_hang_sinh_vien(self, hoc_ky_xh=None): # hoc_ky_xh là học kỳ để tính GPA xếp hạng
        ranked_list = []
        for sv_ma, sv_obj in self.danh_sach_sinh_vien.items():
            gpa = 0.0
            hoc_ky_display_cho_xh = "Tích lũy"

            if hoc_ky_xh: # Xếp hạng theo GPA của một học kỳ cụ thể
                gpa_ky, _ = sv_obj.tinh_gpa(self.danh_sach_mon_hoc, hoc_ky_filter=hoc_ky_xh) # Sử dụng model.SinhVien.tinh_gpa
                gpa = gpa_ky
                hoc_ky_display_cho_xh = hoc_ky_xh
                # Chỉ thêm vào danh sách nếu SV có điểm trong học kỳ đó
                if hoc_ky_xh not in sv_obj.diem or not sv_obj.diem[hoc_ky_xh]:
                    continue # Bỏ qua SV này nếu không có điểm trong kỳ yêu cầu
            else: # Xếp hạng theo GPA tích lũy
                gpa_tl, _ = sv_obj.tinh_gpa(self.danh_sach_mon_hoc) # Sử dụng model.SinhVien.tinh_gpa (hoc_ky_filter=None)
                gpa = gpa_tl
                if not sv_obj.diem: # Nếu SV không có điểm nào thì GPA tích lũy là 0
                    gpa = 0.0

            ranked_list.append({
                'ma_sv': sv_obj.ma_sv,
                'ho_ten': sv_obj.ho_ten,
                'lop_hoc': sv_obj.lop_hoc,
                'truong': sv_obj.truong,
                'khoa': sv_obj.khoa,
                'gpa': gpa,
                'hoc_ky_xep_hang': hoc_ky_display_cho_xh # Học kỳ được dùng để tính GPA này
            })

        # Sắp xếp theo GPA giảm dần, sau đó theo họ tên tăng dần
        ranked_list.sort(key=lambda x: (-x['gpa'], x['ho_ten']))
        return ranked_list

    def xuat_bao_cao_lop(self, ten_lop_hoc):
        sinh_vien_trong_lop = [sv for sv in self.danh_sach_sinh_vien.values()
                               if sv.lop_hoc and sv.lop_hoc.lower() == ten_lop_hoc.lower()]

        if not sinh_vien_trong_lop:
            # Trả về None hoặc một dict chỉ rõ lớp không tìm thấy/rỗng
            # GUI đang kiểm tra if not bao_cao_data
            return None # Hoặc {'lop_hoc': ten_lop_hoc, 'so_sinh_vien': 0, 'danh_sach_sinh_vien': []}

        tong_gpa_tich_luy_lop = 0
        so_sv_co_diem_tl = 0
        danh_sach_sv_bao_cao = []

        for sv_obj in sinh_vien_trong_lop:
            gpa_tich_luy, tong_tc_tich_luy = sv_obj.tinh_gpa(self.danh_sach_mon_hoc) # GPA Tích lũy từ model
            if tong_tc_tich_luy > 0: # Chỉ tính vào TB lớp nếu SV có điểm
                tong_gpa_tich_luy_lop += gpa_tich_luy
                so_sv_co_diem_tl += 1

            diem_theo_hoc_ky_bao_cao = {}
            if sv_obj.diem:
                for hoc_ky, diem_mon_hoc_dict in sorted(sv_obj.diem.items()):
                    gpa_ky, _ = sv_obj.tinh_gpa(self.danh_sach_mon_hoc, hoc_ky_filter=hoc_ky) # GPA Học kỳ từ model
                    diem_theo_hoc_ky_bao_cao[hoc_ky] = {'_GPA_HOC_KY_': gpa_ky}
                    for ma_mh, diem_so in sorted(diem_mon_hoc_dict.items()):
                        mon_hoc = self.danh_sach_mon_hoc.get(ma_mh)
                        ten_mh_display = mon_hoc.ten_mh if mon_hoc else ma_mh
                        diem_theo_hoc_ky_bao_cao[hoc_ky][f"{ten_mh_display} ({ma_mh})"] = f"{diem_so:.1f}"
            
            danh_sach_sv_bao_cao.append({
                'ma_sv': sv_obj.ma_sv,
                'ho_ten': sv_obj.ho_ten,
                'lop_hoc': sv_obj.lop_hoc, # Thêm để GUI có thể dùng nếu cần
                'khoa': sv_obj.khoa,     # Thêm để GUI có thể dùng nếu cần
                'gpa_tich_luy': gpa_tich_luy,
                'diem_theo_hoc_ky': diem_theo_hoc_ky_bao_cao
            })
        
        # Sắp xếp danh sách SV trong báo cáo theo tên
        danh_sach_sv_bao_cao.sort(key=lambda x: x['ho_ten'])

        diem_trung_binh_lop_tich_luy = (tong_gpa_tich_luy_lop / so_sv_co_diem_tl) if so_sv_co_diem_tl > 0 else 0.0

        return {
            'lop_hoc': ten_lop_hoc, # Trả về tên lớp đã chuẩn hóa hoặc tên lớp gốc
            'so_sinh_vien': len(sinh_vien_trong_lop),
            'diem_trung_binh_lop_tich_luy': diem_trung_binh_lop_tich_luy,
            'danh_sach_sinh_vien': danh_sach_sv_bao_cao # Sẽ là list rỗng nếu SV trong lớp ko có điểm
        }

# Để chạy thử nghiệm độc lập (ví dụ)
if __name__ == '__main__':
    ql = QuanLyDiem()

    # Thử thêm môn học
    # ql.them_mon_hoc("IT001", "Nhập môn Lập trình", 3)
    # ql.them_mon_hoc("IT002", "Lập trình Hướng đối tượng", 3)
    # ql.them_mon_hoc("MA001", "Giải tích 1", 4)
    # print("--- Danh sách môn học ---")
    # for mh_dict in ql.lay_tat_ca_mon_hoc():
    #     print(mh_dict)

    # Thử thêm sinh viên
    # ql.them_sinh_vien("22520001", "Nguyễn Văn An", "IT01", "UIT", "CNPM", "HK1-2022")
    # ql.them_sinh_vien("22520002", "Trần Thị Bình", "IT01", "UIT", "CNPM", "HK1-2022")
    # print("\n--- Danh sách sinh viên ---")
    # for sv_ma, sv_obj in ql.danh_sach_sinh_vien.items():
    #     print(sv_obj)

    # Thử nhập điểm
    # ql.nhap_diem("22520001", "IT001", 8.5, "HK1-2022")
    # ql.nhap_diem("22520001", "MA001", 7.0, "HK1-2022")
    # ql.nhap_diem("22520001", "IT002", 9.0, "HK2-2022") # Học kỳ khác

    # ql.nhap_diem("22520002", "IT001", 9.5, "HK1-2022")
    # ql.nhap_diem("22520002", "MA001", 8.0, "HK1-2022")

    # print("\n--- Điểm của SV An ---")
    # sv_an = ql.danh_sach_sinh_vien.get("22520001")
    # if sv_an:
    #     print(sv_an.diem)
    #     gpa_hk1_an, _ = sv_an.tinh_gpa_hoc_ky("HK1-2022", ql.danh_sach_mon_hoc)
    #     gpa_tl_an, _ = sv_an.tinh_gpa_tich_luy(ql.danh_sach_mon_hoc)
    #     print(f"GPA HK1-2022 (An): {gpa_hk1_an:.2f}")
    #     print(f"GPA Tích lũy (An): {gpa_tl_an:.2f}")


    # print("\n--- Xếp hạng toàn trường (Tích lũy) ---")
    # xh_tl = ql.xep_hang_sinh_vien()
    # for sv_xh in xh_tl:
    #     print(f"{sv_xh['ho_ten']} ({sv_xh['ma_sv']}) - GPA {sv_xh['hoc_ky_xep_hang']}: {sv_xh['gpa']:.2f}")

    # print("\n--- Xếp hạng theo HK1-2022 ---")
    # xh_hk1 = ql.xep_hang_sinh_vien(hoc_ky_xh="HK1-2022")
    # for sv_xh_hk1 in xh_hk1:
    #      print(f"{sv_xh_hk1['ho_ten']} ({sv_xh_hk1['ma_sv']}) - GPA {sv_xh_hk1['hoc_ky_xep_hang']}: {sv_xh_hk1['gpa']:.2f}")


    # print("\n--- Báo cáo lớp IT01 ---")
    # bao_cao_it01 = ql.xuat_bao_cao_lop("IT01")
    # if bao_cao_it01:
    #     print(f"Lớp: {bao_cao_it01['lop_hoc']}, Số SV: {bao_cao_it01['so_sinh_vien']}")
    #     print(f"GPA TB Lớp (Tích lũy): {bao_cao_it01['diem_trung_binh_lop_tich_luy']:.2f}")
    #     for sv_data_bc in bao_cao_it01['danh_sach_sinh_vien']:
    #         print(f"  SV: {sv_data_bc['ho_ten']} - GPA TL: {sv_data_bc['gpa_tich_luy']:.2f}")
    #         for hk, diem_ky_data in sv_data_bc['diem_theo_hoc_ky'].items():
    #             print(f"    HK: {hk} - GPA Kỳ: {diem_ky_data.get('_GPA_HOC_KY_', 0.0):.2f}")
    #             for mon_display, diem_mh in diem_ky_data.items():
    #                 if mon_display != '_GPA_HOC_KY_':
    #                     print(f"      + {mon_display}: {diem_mh}")

    # print("\n--- Tìm kiếm ---")
    # kq_tim = ql.tim_kiem_diem(ma_sv_filter="22520001", hoc_ky_filter="HK1-2022")
    # # kq_tim = ql.tim_kiem_diem(lop_hoc_filter="IT01", ma_mon_hoc_filter="IT001")
    # for item in kq_tim:
    #     print(item)
    pass