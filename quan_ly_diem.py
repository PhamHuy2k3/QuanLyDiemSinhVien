import json
import os # Để kiểm tra file tồn tại
import datetime # Để lấy thời gian hiện tại cho việc cập nhật
from models import SinhVien, MonHoc # Import các lớp mới

class QuanLyDiem:
    def __init__(self):
        self.danh_sach_sinh_vien = {} # Sẽ lưu {ma_sv: SinhVien_obj}
        self.danh_sach_mon_hoc = {} # Sẽ lưu {ma_mh: MonHoc_obj}
        self.data_file_sv = "du_lieu_diem.json"
        self.data_file_mh = "du_lieu_mon_hoc.json"
        self.load_data_sv()
        self.load_data_mh()

    def load_data_sv(self):
        """Tải dữ liệu sinh viên từ file JSON."""
        if os.path.exists(self.data_file_sv):
            try:
                with open(self.data_file_sv, 'r', encoding='utf-8') as f:
                    sinh_vien_data_raw = json.load(f)
                    for ma_sv, data in sinh_vien_data_raw.items():
                        try:
                            self.danh_sach_sinh_vien[ma_sv] = SinhVien.from_dict(ma_sv, data)
                        except ValueError as ve:
                            print(f"Lỗi khi tạo đối tượng SinhVien cho {ma_sv}: {ve}. Bỏ qua sinh viên này.")
                print(f"Đã tải dữ liệu sinh viên từ {self.data_file_sv}")
            except json.JSONDecodeError:
                print(f"Lỗi: File {self.data_file_sv} không chứa JSON hợp lệ. Bắt đầu với dữ liệu rỗng.")
                self.danh_sach_sinh_vien = {} 
            except Exception as e:
                print(f"Lỗi không xác định khi tải dữ liệu SV: {e}. Bắt đầu với dữ liệu rỗng.")
                self.danh_sach_sinh_vien = {}
        else:
            print(f"Thông báo: File {self.data_file_sv} không tìm thấy. Sẽ tạo file mới khi lưu dữ liệu.")
            self.danh_sach_sinh_vien = {} 

    def save_data_sv(self):
        """Lưu dữ liệu sinh viên hiện tại vào file JSON."""
        try:
            with open(self.data_file_sv, 'w', encoding='utf-8') as f:
                data_to_save = {ma_sv: sv_obj.to_dict() for ma_sv, sv_obj in self.danh_sach_sinh_vien.items()}
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu sinh viên vào {self.data_file_sv}: {e}")

    def load_data_mh(self):
        """Tải dữ liệu môn học từ file JSON."""
        if os.path.exists(self.data_file_mh):
            try:
                with open(self.data_file_mh, 'r', encoding='utf-8') as f:
                    mon_hoc_data_raw = json.load(f)
                    for ma_mh, data in mon_hoc_data_raw.items():
                        try:
                            self.danh_sach_mon_hoc[ma_mh] = MonHoc.from_dict(ma_mh, data)
                        except ValueError as ve:
                             print(f"Lỗi khi tạo đối tượng MonHoc cho {ma_mh}: {ve}. Bỏ qua môn học này.")
                print(f"Đã tải dữ liệu môn học từ {self.data_file_mh}")
            except json.JSONDecodeError:
                print(f"Lỗi: File {self.data_file_mh} không chứa JSON hợp lệ. Bắt đầu với dữ liệu môn học rỗng.")
                self.danh_sach_mon_hoc = {}
            except Exception as e:
                print(f"Lỗi không xác định khi tải dữ liệu MH: {e}. Bắt đầu với dữ liệu môn học rỗng.")
                self.danh_sach_mon_hoc = {}
        else:
            print(f"Thông báo: File {self.data_file_mh} không tìm thấy. Sẽ tạo file mới khi lưu dữ liệu.")
            self.danh_sach_mon_hoc = {}
        
        # Nếu sau khi tải, self.danh_sach_mon_hoc vẫn rỗng, thêm các môn học mặc định
        if not self.danh_sach_mon_hoc:
            print("Dữ liệu môn học rỗng. Thêm các môn học mặc định...")
            default_subjects = {
                "CS101": {"ten_mh": "Lập Trình Hướng Đối Tượng", "so_tin_chi": 3},
                "WD102": {"ten_mh": "Thiết Kế Web", "so_tin_chi": 3},
                "DB103": {"ten_mh": "Cơ Sở Dữ Liệu", "so_tin_chi": 3},
                "JS201": {"ten_mh": "Java Spring", "so_tin_chi": 4},
                "MA100": {"ten_mh": "Toán Rời Rạc", "so_tin_chi": 2} # Thêm cả Toán Rời Rạc nếu cần
            }
            for ma_mh, data in default_subjects.items():
                self.danh_sach_mon_hoc[ma_mh] = MonHoc.from_dict(ma_mh, data)
            self.save_data_mh() # Lưu lại các môn học mặc định này
            print(f"Đã thêm và lưu {len(self.danh_sach_mon_hoc)} môn học mặc định vào {self.data_file_mh}.")


    def save_data_mh(self):
        """Lưu dữ liệu môn học hiện tại vào file JSON."""
        try:
            with open(self.data_file_mh, 'w', encoding='utf-8') as f:
                data_to_save = {ma_mh: mh_obj.to_dict() for ma_mh, mh_obj in self.danh_sach_mon_hoc.items()}
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu môn học vào {self.data_file_mh}: {e}")

    def _lay_thoi_gian_hien_tai_str(self):
        """Trả về chuỗi thời gian hiện tại theo định dạng mong muốn."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def them_sinh_vien(self, ma_sv, ho_ten, lop_hoc, truong, khoa):
        if ma_sv in self.danh_sach_sinh_vien:
            return "Mã số sinh viên đã tồn tại!"
        try:
            sv_moi = SinhVien(ma_sv, ho_ten, lop_hoc, truong, khoa)
            self.danh_sach_sinh_vien[ma_sv] = sv_moi
            self.save_data_sv()
            return "Thêm sinh viên thành công."
        except ValueError as e:
            return str(e)

    def them_mon_hoc(self, ma_mh, ten_mh, so_tin_chi):
        """Thêm một môn học mới vào hệ thống."""
        if ma_mh in self.danh_sach_mon_hoc:
            return f"Mã môn học '{ma_mh}' đã tồn tại."
        try:
            mh_moi = MonHoc(ma_mh, ten_mh, so_tin_chi)
            self.danh_sach_mon_hoc[ma_mh] = mh_moi
            self.save_data_mh()
            return f"Thêm môn học '{ten_mh}' ({ma_mh}) thành công."
        except ValueError as e:
            return str(e)

    def lay_thong_tin_mon_hoc(self, ma_mh):
        """Lấy thông tin chi tiết của một môn học dựa trên mã môn học."""
        return self.danh_sach_mon_hoc.get(ma_mh) # Trả về đối tượng MonHoc

    def lay_tat_ca_mon_hoc(self):
        """Trả về danh sách các môn học (mã, tên, tín chỉ) để hiển thị trên GUI."""
        return [{"ma_mh": mh_obj.ma_mh, "ten_mh": mh_obj.ten_mh, "so_tin_chi": mh_obj.so_tin_chi} 
                for mh_obj in self.danh_sach_mon_hoc.values()]

    def nhap_diem(self, ma_sv, ma_mon_hoc, diem): # Thay mon_hoc bằng ma_mon_hoc
        sv_obj = self.danh_sach_sinh_vien.get(ma_sv)
        if not sv_obj:
            return "Sinh viên không tồn tại."
        
        mon_hoc_obj = self.danh_sach_mon_hoc.get(ma_mon_hoc)
        if not mon_hoc_obj:
            return "Mã môn học không tồn tại trong danh sách môn học quản lý."
        
        try:
            sv_obj.them_diem(mon_hoc_obj, diem)
            self.save_data_sv() 
            return True
        except (ValueError, TypeError) as e:
            return str(e)

    def xem_diem(self, ma_sv):
        """Trả về dữ liệu của một sinh viên, bao gồm cả thông tin và điểm."""
        sv_obj = self.danh_sach_sinh_vien.get(ma_sv)
        if not sv_obj:
            return None
        
        # Chuyển đổi điểm từ {ma_mh: diem} sang {ten_mh: diem} để hiển thị
        diem_hien_thi = {}
        if sv_obj.diem:
            for ma_mh, diem_val in sv_obj.diem.items():
                mon_hoc_obj_temp = self.lay_thong_tin_mon_hoc(ma_mh) # Lấy đối tượng MonHoc
                # Sử dụng tên môn học từ dữ liệu quản lý, fallback là mã MH nếu không tìm thấy
                ten_mh_display = mon_hoc_obj_temp.ten_mh if mon_hoc_obj_temp else ma_mh 
                diem_hien_thi[ten_mh_display] = diem_val
        
        # Tạo bản sao của sv_data và thay thế 'diem' bằng phiên bản đã chuyển đổi
        sv_data_display = {
            "ma_sv": sv_obj.ma_sv, # Thêm ma_sv nếu GUI cần
            "ho_ten": sv_obj.ho_ten,
            "lop_hoc": sv_obj.lop_hoc,
            "truong": sv_obj.truong,
            "khoa": sv_obj.khoa,
            "ngay_cap_nhat": sv_obj.ngay_cap_nhat 
        }
        sv_data_display['diem'] = diem_hien_thi
        return sv_data_display


    def xoa_diem(self, ma_sv, ma_mon_hoc_can_xoa): # Cần truyền ma_mon_hoc_can_xoa
        sv_obj = self.danh_sach_sinh_vien.get(ma_sv)
        if sv_obj and ma_mon_hoc_can_xoa in sv_obj.diem:
            del sv_obj.diem[ma_mon_hoc_can_xoa]
            sv_obj.ngay_cap_nhat = self._lay_thoi_gian_hien_tai_str()
            self.save_data_sv()
            return True
        return False

    def sua_diem(self, ma_sv, ma_mon_hoc, diem_moi): # Cần truyền ma_mon_hoc
        sv_obj = self.danh_sach_sinh_vien.get(ma_sv)
        mon_hoc_obj = self.danh_sach_mon_hoc.get(ma_mon_hoc)

        if sv_obj and mon_hoc_obj and ma_mon_hoc in sv_obj.diem:
            try:
                # Validate điểm mới trước khi gán
                if not (0 <= diem_moi <= 10):
                    return "Điểm mới phải từ 0 đến 10." # Hoặc raise ValueError
                sv_obj.diem[ma_mon_hoc] = diem_moi # Hoặc sv_obj.them_diem(mon_hoc_obj, diem_moi) nếu muốn cập nhật ngày
                sv_obj.ngay_cap_nhat = self._lay_thoi_gian_hien_tai_str()
                self.save_data_sv()
                return True
            except ValueError as e:
                return str(e)
        return False

    def _tinh_gpa(self, ma_sv):
        sv_obj = self.danh_sach_sinh_vien.get(ma_sv)
        if not sv_obj:
            return 0.0
        return sv_obj.tinh_gpa(self.danh_sach_mon_hoc)

    def tim_kiem_diem(self, ma_sv=None, ma_mon_hoc_tim=None, lop_hoc=None, truong=None, khoa=None): # mon_hoc -> ma_mon_hoc_tim
        results = []
        for msv_key, sv_obj in self.danh_sach_sinh_vien.items():
            # Kiểm tra khớp tiêu chí
            match_msv = (not ma_sv or msv_key == ma_sv)
            match_lop = (not lop_hoc or sv_obj.lop_hoc.lower() == lop_hoc.lower())
            match_truong = (not truong or sv_obj.truong.lower() == truong.lower())
            match_khoa = (not khoa or sv_obj.khoa.lower() == khoa.lower())

            if match_msv and match_lop and match_truong and match_khoa:
                if ma_mon_hoc_tim: # Tìm cụ thể theo mã môn học
                    # Kiểm tra xem sinh viên có điểm cho mã môn học này không
                    if ma_mon_hoc_tim in sv_obj.diem:
                        mon_hoc_obj_tim = self.lay_thong_tin_mon_hoc(ma_mon_hoc_tim)
                        ten_mh_display = mon_hoc_obj_tim.ten_mh if mon_hoc_obj_tim else ma_mon_hoc_tim
                        results.append({
                            'ma_sv': msv_key,
                            'ho_ten': sv_obj.ho_ten,
                            'lop_hoc': sv_obj.lop_hoc,
                            'truong': sv_obj.truong,
                            'khoa': sv_obj.khoa,
                            'mon_hoc': ten_mh_display, # Hiển thị tên môn
                            'diem': sv_obj.diem[ma_mon_hoc_tim]
                        })
                else: # Không tìm theo môn cụ thể, lấy tất cả điểm của SV khớp các tiêu chí khác
                    if sv_obj.diem:
                        for ma_mh_sv, diem_val_sv in sv_obj.diem.items():
                            mon_hoc_obj_sv = self.lay_thong_tin_mon_hoc(ma_mh_sv)
                            ten_mh_display_sv = mon_hoc_obj_sv.ten_mh if mon_hoc_obj_sv else ma_mh_sv
                            results.append({
                                'ma_sv': msv_key,
                                'ho_ten': sv_obj.ho_ten,
                                'lop_hoc': sv_obj.lop_hoc,
                                'truong': sv_obj.truong,
                                'khoa': sv_obj.khoa,
                                'mon_hoc': ten_mh_display_sv, # Hiển thị tên môn
                                'diem': diem_val_sv
                            })
                    elif ma_sv: # Nếu tìm theo mã SV (match_msv=True) và SV đó chưa có điểm nào
                                # nhưng các tiêu chí khác (lớp, trường, khoa) cũng phải khớp nếu được cung cấp
                                # Điều kiện này có vẻ hơi thừa nếu đã có if info.get('diem') ở trên
                                # Tuy nhiên, nếu muốn hiển thị SV dù chưa có điểm khi tìm theo mã SV cụ thể
                                # và các tiêu chí khác (lớp, trường, khoa) cũng khớp thì có thể giữ lại.
                                # Để đơn giản, nếu không có môn học cụ thể, chỉ trả về SV có điểm.
                                # Nếu muốn trả về SV dù không có điểm khi tìm theo mã SV, cần logic riêng.
                        # Xử lý trường hợp tìm theo mã SV và SV không có điểm
                        results.append({
                                    'ma_sv': msv_key,
                                    'ho_ten': sv_obj.ho_ten,
                                    'lop_hoc': sv_obj.lop_hoc,
                                    'truong': sv_obj.truong,
                                    'khoa': sv_obj.khoa,
                                    'mon_hoc': 'Chưa có điểm',
                                    'diem': ''
                                })
        return results

    def xep_hang_sinh_vien(self):
        ranked_list = []
        # Chỉ xếp hạng những SV có dữ liệu điểm và GPA > 0 (do _tinh_gpa trả về 0.0 nếu không có điểm/tín chỉ)
        for ma_sv_key, sv_obj in self.danh_sach_sinh_vien.items():
            if sv_obj.diem: 
                gpa = self._tinh_gpa(ma_sv_key)
                ranked_list.append({
                    'ma_sv': ma_sv_key,
                    'ho_ten': sv_obj.ho_ten,
                    'lop_hoc': sv_obj.lop_hoc,
                    'truong': sv_obj.truong,
                    'khoa': sv_obj.khoa,
                    'gpa': gpa
                })
        
        # Sắp xếp theo GPA giảm dần, sau đó theo mã SV tăng dần nếu GPA bằng nhau
        ranked_list.sort(key=lambda x: (-x['gpa'], x['ma_sv']))
        return ranked_list

    def xuat_bao_cao_lop(self, lop_hoc_can_tim):
        sv_trong_lop_co_diem = []
        tong_sv_thuoc_lop_trong_he_thong = 0
        
        for ma_sv_key, sv_obj in self.danh_sach_sinh_vien.items():
            if sv_obj.lop_hoc.lower() == lop_hoc_can_tim.lower():
                tong_sv_thuoc_lop_trong_he_thong += 1
                if sv_obj.diem: 
                    gpa_sv = self._tinh_gpa(ma_sv_key)
                    
                    # Chuyển đổi bảng điểm chi tiết sang tên môn học
                    bang_diem_chi_tiet_display = {}
                    for ma_mh_bd, diem_bd in sv_obj.diem.items():
                        mon_hoc_obj_bd = self.lay_thong_tin_mon_hoc(ma_mh_bd)
                        ten_mh_bd_display = mon_hoc_obj_bd.ten_mh if mon_hoc_obj_bd else ma_mh_bd
                        bang_diem_chi_tiet_display[ten_mh_bd_display] = diem_bd

                    sv_trong_lop_co_diem.append({
                        'ma_sv': ma_sv_key,
                        'ho_ten': sv_obj.ho_ten,
                        'truong': sv_obj.truong,
                        'khoa': sv_obj.khoa,
                        'bang_diem': bang_diem_chi_tiet_display, # Đã chuyển sang tên môn
                        'diem_trung_binh': gpa_sv
                    })

        # Nếu lớp không có sinh viên nào trong hệ thống (dựa trên kiểm tra của GUI)
        # Hàm này sẽ được gọi khi GUI đã xác nhận lớp có tồn tại (có ít nhất 1 sv thuộc lớp)
        # Nên tong_sv_thuoc_lop_trong_he_thong >= 0
        
        diem_tb_lop = 0.0
        if sv_trong_lop_co_diem: # Tính GPA của lớp nếu có SV có điểm
            tong_gpa_sv_co_diem = sum(sv['diem_trung_binh'] for sv in sv_trong_lop_co_diem)
            diem_tb_lop = tong_gpa_sv_co_diem / len(sv_trong_lop_co_diem)
        
        return {
            "lop_hoc": lop_hoc_can_tim, # Trả về tên lớp đã chuẩn hóa (có thể viết hoa chữ cái đầu)
            "so_sinh_vien": tong_sv_thuoc_lop_trong_he_thong, # Tổng SV thuộc lớp này trong hệ thống
            "diem_trung_binh_lop": diem_tb_lop, # GPA của lớp, tính trên SV có điểm
            "danh_sach_sinh_vien": sv_trong_lop_co_diem # Danh sách SV có điểm của lớp đó
        }