# Kế Hoạch Thực Hiện Lab: CI/CD cho AI Systems

Tài liệu này hướng dẫn chi tiết từng bước để hoàn thành bài lab MLOps, từ thực nghiệm cục bộ đến triển khai liên tục trên Cloud.

## 📋 Giai Đoạn Chuẩn Bị

- [ ] **Khởi tạo Repo:** Tạo một repository GitHub mới và clone về máy.
- [ ] **Môi trường Python:** Tạo venv và cài đặt thư viện.
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- [ ] **Khởi tạo Dữ liệu:** Chạy script tạo dữ liệu mẫu.
  ```bash
  python generate_data.py
  ```
- [ ] **Cấu hình .gitignore:** Đảm bảo các file nhạy cảm và dữ liệu lớn không bị commit.

---

## 🧪 Bước 1: Thực Nghiệm Cục Bộ & MLflow Tracking

Mục tiêu: Tìm bộ siêu tham số (hyperparameters) tốt nhất.

- [ ] **Cấu hình MLflow:** Thiết lập biến môi trường để lưu tracking cục bộ.
  ```bash
  export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
  ```
- [ ] **Thiết lập `params.yaml`:** Khai báo các tham số ban đầu cho RandomForest.
- [ ] **Hoàn thiện `src/train.py`:** 
  - Đọc dữ liệu từ `data/train_phase1.csv` và `data/eval.csv`.
  - Sử dụng `mlflow.start_run()` để log params và metrics (`accuracy`, `f1_score`).
  - Lưu mô hình vào `models/model.pkl` và metrics vào `outputs/metrics.json`.
- [ ] **Chạy thí nghiệm:** Thực hiện ít nhất 3 lần chạy với các bộ tham số khác nhau trong `params.yaml`.
- [ ] **Phân tích kết quả:** Mở `mlflow ui`, so sánh và chọn bộ tham số tốt nhất cập nhật lại vào `params.yaml`.

---

## 🚀 Bước 2: Pipeline CI/CD Tự Động

Mục tiêu: Tự động hóa quy trình Kiểm thử -> Huấn luyện -> Đánh giá -> Triển khai.

### 2.1 Cấu Hình Cloud & DVC
- [ ] **Tạo Storage Bucket:** Tạo Bucket trên GCP (GCS), AWS (S3) hoặc Azure.
- [ ] **Tạo Service Account:** Cấp quyền `Storage Object Admin` và tải file `sa-key.json`.
- [ ] **Khởi tạo DVC:**
  - `dvc init`
  - `dvc remote add -d myremote gs://<your-bucket>/dvc`
  - `dvc remote modify myremote credentialpath sa-key.json`
- [ ] **Quản lý dữ liệu:** `dvc add data/*.csv` và `dvc push`.

### 2.2 Triển Khai Server (Serving)
- [ ] **Tạo VM:** Khởi tạo máy chủ ảo (GCE/EC2) và mở cổng 8000.
- [ ] **Hoàn thiện `src/serve.py`:** Viết API FastAPI với các endpoint `/health` và `/predict`.
- [ ] **Cấu hình Systemd:** Tạo service `mlops-serve.service` trên VM để tự động chạy API.

### 2.3 Thiết Lập GitHub Actions
- [ ] **SSH Key:** Tạo cặp khóa SSH để GitHub Actions có thể truy cập VM.
- [ ] **GitHub Secrets:** Thêm 5 secrets: `CLOUD_CREDENTIALS`, `CLOUD_BUCKET`, `VM_HOST`, `VM_USER`, `VM_SSH_KEY`.
- [ ] **Viết Unit Test:** Hoàn thiện `tests/test_train.py` để kiểm tra logic huấn luyện.
- [ ] **Xây dựng Workflow:** Hoàn thiện `.github/workflows/mlops.yml` với 4 jobs:
  1. **Test:** Chạy pytest.
  2. **Train:** Pull dữ liệu DVC, huấn luyện, log metrics, upload model lên Cloud.
  3. **Eval:** Kiểm tra nếu `accuracy >= 0.70` mới cho phép đi tiếp.
  4. **Deploy:** SSH vào VM, restart service và kiểm tra health check.

---

## 🔄 Bước 3: Huấn Luyện Liên Tục (Retraining)

Mục tiêu: Kiểm tra khả năng tự động cập nhật khi có dữ liệu mới.

- [ ] **Bổ sung dữ liệu:** Chạy `python add_new_data.py` để tăng kích thước tập train.
- [ ] **Cập nhật DVC:**
  ```bash
  dvc add data/train_phase1.csv
  dvc push
  ```
- [ ] **Kích hoạt Pipeline:**
  ```bash
  git add data/train_phase1.csv.dvc
  git commit -m "data: cập nhật dữ liệu mới cho phase 3"
  git push origin main
  ```
- [ ] **Kiểm chứng:** Theo dõi GitHub Actions tự động chạy lại và kiểm tra API trên VM đã cập nhật mô hình mới chưa.

---

## 🌟 Thử Thách Nâng Cao (Bonus)
- [ ] **Bonus 1:** Kết nối MLflow với DagsHub để xem tracking online.
- [ ] **Bonus 2:** Thử nghiệm thêm các thuật toán khác (Logistic Regression, v.v.).
- [ ] **Bonus 3:** Tự động tạo báo cáo `report.txt` (confusion matrix) sau khi train.
- [ ] **Bonus 4:** Chỉ deploy nếu mô hình mới tốt hơn mô hình cũ.
- [ ] **Bonus 5:** Kiểm tra lệch lạc dữ liệu (Data Drift/Distribution check).

---

## 📝 Yêu Cầu Nộp Bài
1. Link GitHub Repository.
2. Ảnh chụp màn hình MLflow UI (3+ runs).
3. Ảnh chụp màn hình GitHub Actions (4 jobs xanh).
4. Kết quả `curl` từ IP của VM (`/health` và `/predict`).
5. Báo cáo ngắn về siêu tham số và khó khăn gặp phải.
