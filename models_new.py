"""Data models for the application."""
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
from constants_new import Validation

@dataclass
class MonHoc:
    ma_mh: str
    ten_mh: str
    so_tin_chi: int

    def __post_init__(self):
        """Validate attributes after initialization."""
        if not isinstance(self.so_tin_chi, int):
            self.so_tin_chi = int(self.so_tin_chi)
        if not Validation.MIN_TIN_CHI <= self.so_tin_chi <= Validation.MAX_TIN_CHI:
            raise ValueError(f"Số tín chỉ phải từ {Validation.MIN_TIN_CHI} đến {Validation.MAX_TIN_CHI}")

@dataclass
class SinhVien:
    ma_sv: str
    ho_ten: str
    lop_hoc: str
    truong: str 
    khoa: str
    hoc_ky_nhap_hoc: str
    diem: Dict[str, Dict[str, float]] = field(default_factory=dict)
    ngay_cap_nhat: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __post_init__(self):
        """Validate attributes after initialization."""
        if not self.ma_sv:
            raise ValueError("Mã SV không được để trống.")
        if not len(self.ma_sv) == Validation.MIN_MA_SV_LENGTH:
            raise ValueError(f"Mã SV phải có {Validation.MIN_MA_SV_LENGTH} ký tự.")
        if not self.ma_sv.isdigit():
            raise ValueError("Mã SV chỉ được chứa chữ số.")

    def them_diem(self, ma_mon: str, diem: float, hoc_ky: str) -> None:
        """Thêm điểm cho một môn học."""
        if not Validation.MIN_DIEM <= diem <= Validation.MAX_DIEM:
            raise ValueError(f"Điểm phải từ {Validation.MIN_DIEM} đến {Validation.MAX_DIEM}")
        
        if hoc_ky not in self.diem:
            self.diem[hoc_ky] = {}
        self.diem[hoc_ky][ma_mon] = diem
        self.ngay_cap_nhat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def xoa_diem(self, ma_mon: str, hoc_ky: str) -> bool:
        """Xóa điểm của một môn học."""
        if hoc_ky in self.diem and ma_mon in self.diem[hoc_ky]:
            del self.diem[hoc_ky][ma_mon]
            if not self.diem[hoc_ky]:  # If no more grades in semester
                del self.diem[hoc_ky]
            self.ngay_cap_nhat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        return False

    def tinh_diem_trung_binh(self, hoc_ky: Optional[str] = None) -> float:
        """Tính điểm trung bình của sinh viên."""
        if not self.diem:
            return 0.0

        if hoc_ky:  # Tính GPA cho một học kỳ cụ thể
            if hoc_ky not in self.diem:
                return 0.0
            diem_list = list(self.diem[hoc_ky].values())
            return sum(diem_list) / len(diem_list) if diem_list else 0.0
        else:  # Tính GPA tích lũy
            all_grades = []
            for semester_grades in self.diem.values():
                all_grades.extend(list(semester_grades.values()))
            return sum(all_grades) / len(all_grades) if all_grades else 0.0

    def to_dict(self) -> dict:
        """Convert object to dictionary for serialization."""
        return {
            "ma_sv": self.ma_sv,
            "ho_ten": self.ho_ten,
            "lop_hoc": self.lop_hoc,
            "truong": self.truong,
            "khoa": self.khoa,
            "hoc_ky_nhap_hoc": self.hoc_ky_nhap_hoc,
            "diem": self.diem,
            "ngay_cap_nhat": self.ngay_cap_nhat
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SinhVien':
        """Create object from dictionary."""
        return cls(**data)
