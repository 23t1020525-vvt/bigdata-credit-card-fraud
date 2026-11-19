# CHECKPOINT 2: Environment → Ingestion → Raw Storage
**Đề tài:** Phát hiện gian lận thẻ tín dụng
**Nhóm:** Nhóm 9  
**Thành viên:** Đức, Thuần, Lộc , Việt , Long 

---
## 1. Cấu trúc thư mục

```text
bigdata-credit-card-fraud/
└── DoAn_2/
    ├── data/
    │   ├── raw/
    │   │   └── credit_card_transactions/
    │   │       └── ingest_date=2026-11-12/
    │   │           └── run_<TIMESTAMP>/
    │   │               └── raw_transactions.csv  # Raw storage preserved
    │   └── source_input/
    │       └── creditcard.csv          # File nguồn gốc từ Kaggle (284,807 records)
    ├── logs/
    │   ├── env_check.txt               # Bằng chứng Smoke Test môi trường
    │   └── ingest_credit_card.log      # Log thực thi Ingestion Pipeline
    ├── metadata/
    │   └── manifests/
    │       ├── manifest_run_20261112_122401.json # File lưu vết SHA-256, count, status
    │       ├── manifest_run_20261112_122512.json
    │       └── manifest_run_20261112_123623.json
    ├── src/
    │   ├── env_check.py                # Script kiểm tra Smoke Test
    │   └── ingest_credit_card.py       # Script nạp dữ liệu & kiểm tra Quality Gate
    ├── DoAn_2.md                       # Tài liệu/Báo cáo đồ án 2
    └── requirements.txt                # Khai báo phụ thuộc (pyspark==4.2.0, v.v.)
```

---

- `src/`: Chứa mã nguồn kiểm tra môi trường và nạp dữ liệu.
- `data/raw/`: Chứa dữ liệu gốc theo phân vùng `ingest_date` và `run_id`.
- `logs/`: Lưu trữ file log quá trình chạy.
- `metadata/manifests/`: Lưu vết manifest (JSON) phục vụ kiểm tra provenance.

## 2. Yêu cầu Môi trường
- Python 3.10+
- PySpark 3.5+ / 4.x
- Java JDK 11 hoặc cao hơn

## 3.Nguồn dữ liệu (Data Source & Provenance)
* **Bộ dữ liệu gốc:** Credit Card Fraud Detection Dataset (Kaggle).
* **Nguồn dữ liệu gốc (URL):** [https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
* **Vị trí tệp nguồn local:** `data/source_input/creditcard.csv`
* **Mô tả:** Tập dữ liệu bao gồm các giao dịch thẻ tín dụng của chủ thẻ Châu Âu thực hiện trong tháng 09/2013. Tập dữ liệu gồm **284,807 bản ghi**, trong đó có **492 giao dịch gian lận** (`Class = 1`, chiếm tỉ lệ cực nhỏ ~0.172% -> bài toán Class Imbalance).

---

*Kỳ vọng Output:*
```text
Starting Spark Environment Smoke Test...

========================================
ENVIRONMENT SMOKE TEST: PASS
Python Version: 3.12.5
Spark Version : 4.2.0
Test Execution: Processed 2 records successfully
========================================
```

## 3. HƯỚNG DẪN THAO TÁC TERMINAL & MÔI TRƯỜNG (WINDOWS POWERSHELL)

### 1. Khởi tạo và kích hoạt môi trường ảo (`.venv`)
Đảm bảo đứng đúng thư mục chứa mã nguồn dự án (`DoAn_2`) trước khi thao tác:

```powershell
# 1. Di chuyển vào thư mục dự án
cd DoAn_2

# 2. Tạo môi trường ảo (nếu chưa có)
python -m venv .venv

# 3. Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1

# (Tùy chọn) Nếu PowerShell chặn chạy script, chạy lệnh sau rồi kích hoạt lại:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Cài đặt thư viện và chạy kiểm tra Pipeline

```powershell
# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Chạy kiểm tra môi trường Spark
python src/env_check.py

# Chạy nạp dữ liệu thô
python src/ingest_credit_card.py
```

**Sản phẩm đầu ra (Artifacts) được sinh ra:**
1. **Raw Storage:** `data/raw/credit_card_transactions/ingest_date=YYYY-MM-DD/run_<TIMESTAMP>/raw_transactions.csv`
2. **Manifest File:** `metadata/manifests/manifest_run_<TIMESTAMP>.json` (Chứa thông số 284,807 bản ghi, mã băm SHA-256, dung lượng file, và status `"SUCCESS"`).
3. **Execution Log:** `logs/ingest_credit_card.log`

---
