# ĐỒ ÁN 1: XÂY DỰNG HỆ THỐNG PHÁT HIỆN GIAN LẬN GIAO DỊCH THẺ TÍN DỤNG

* **Nhóm thực hiện:** Nhóm 9
* **Thành viên:**
  1. Võ Văn Thuần
  2. Hoàng Minh Đức
  3. Trần Quốc Lộc
  4. Nguyễn Công Việt
  5. Hồ Gia Long

---


## 1. Bộ dữ liệu (Dataset: Credit Card Fraud Detection)

### 01. Nguồn dữ liệu (Source)
* **Link truy cập:** [Credit Card Fraud Detection - Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
* **Đơn vị cung cấp:** Machine Learning Group - Đại học ULB (Brussels) chia sẻ thông qua Kaggle.

### 02. Quy mô (Scale)
* **Dung lượng:** 150,83 MB (lưu trữ trong 1 file CSV duy nhất).
* **Số lượng bản ghi:** 284.807 giao dịch, trong đó có 492 giao dịch gian lận (chiếm tỷ lệ ~0,172%).

### 03. Cấu trúc dữ liệu (Schema)
Dataset bao gồm **31 trường dữ liệu** thuộc kiểu số (`Numeric/Double`):
* `Time`: Số giây trễ tính từ giao dịch đầu tiên trong tập dữ liệu.
* `V1` đến `V28`: 28 đặc trưng ẩn đã được biến đổi bằng thuật toán giảm chiều dữ liệu PCA nhằm bảo mật thông tin khách hàng.
* `Amount`: Số tiền của giao dịch.
* `Class`: Nhãn phân loại nhị phân (`0` = Giao dịch bình thường, `1` = Giao dịch gian lận).

### 04. Thời gian & Rủi ro dữ liệu (Time & Data Risks)
* **Thời gian thu thập:** Dữ liệu được thu thập trong vòng 2 ngày vào tháng 9 năm 2013.
* **Rủi ro dữ liệu:** Bộ dữ liệu gặp tình trạng mất cân bằng nghiêm trọng (Imbalanced Dataset), nhóm nhãn tích cực (gian lận) chỉ chiếm **0,172%** tổng số giao dịch.

### 05. Phương án dự phòng (Fallback Dataset)
* **Dataset thay thế:** [IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection)
* **Nguồn:** Dữ liệu công khai trên Kaggle năm 2019 của Tập đoàn Vesta.
* **Quy mô:** Dung lượng 1.35 GB, gồm 5 file chứa tổng cộng 871 trường dữ liệu.

---

## 2. Yêu cầu hệ thống (Requirements)

### Yêu cầu chức năng (Functional Requirements)
* **[FR1]** Tiếp nhận dữ liệu giao dịch thẻ tín dụng.
* **[FR2]** Làm sạch và tiền xử lý dữ liệu giao dịch.
* **[FR3]** Phân loại giao dịch: gian lận / không gian lận.
* **[FR4]** Phát hiện và cảnh báo các giao dịch có dấu hiệu bất thường.
* **[FR5]** Hiển thị số lượng và tỷ lệ giao dịch gian lận trên Dashboard.

### Yêu cầu phi chức năng (Non-Functional Requirements)
* **[NFR1 - Throughput]:** Hệ thống xử lý tối thiểu 100 giao dịch/giây.
* **[NFR2 - Processing Time]:** Trả về kết quả phát hiện trong tối đa 2 giây/giao dịch.
* **[NFR3 - Scalability]:** Có khả năng mở rộng lên tối thiểu 1.000 giao dịch/giây.

---

## 3. Kiến trúc hệ thống (Architecture v1)

### Luồng xử lý dữ liệu (Data Pipeline)
```text
[Source: File CSV] ──▶ [Ingest] ──▶ [Store] ──▶ [Process] ──▶ [Serve]
```
---

## 4. Rủi ro & Giải pháp (Risks & Mitigations)

| Rủi ro (Risk) | Giải pháp khắc phục (Mitigation) |
| :--- | :--- |
| **1. Mất cân bằng dữ liệu nghiêm trọng** (tỷ lệ gian lận chỉ 0,172% dễ làm mô hình thiên lệch). | • Sử dụng các thang đo đánh giá phù hợp như **Precision-Recall AUC**, **F1-Score** thay vì Accuracy.<br>• Áp dụng các kỹ thuật tái lấy mẫu để cân bằng dữ liệu như **SMOTE** (Oversampling) hoặc **Undersampling**. |
| **2. Khó giải thích mô hình** do các đặc trưng từ `V1`–`V28` đã bị ẩn danh hóa qua PCA. | • Tập trung phân tích sâu vào các trường dữ liệu tường minh (`Time`, `Amount`).<br>• Sử dụng biểu đồ phân phối (Distribution plots) cho các biến ẩn danh để trực quan hóa sự khác biệt hành vi giữa giao dịch hợp lệ và gian lận. |