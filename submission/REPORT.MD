# BÁO CÁO KẾT QUẢ LAB DAY 21: MLOPS PIPELINE

## 1. Lựa chọn mô hình và Siêu tham số (Bước 1)
Trong quá trình thực hiện, tôi đã thử nghiệm 3 cấu hình mô hình khác nhau:

Lần 1 (Random Forest): Acc ~0.68.
Lần 2 (Logistic Regression): Acc ~0.65.
Lần 3 (Gradient Boosting): Sử dụng bộ tham số tối ưu sau khi có dữ liệu mới ở Bước 3.
model_type: gradient_boosting
n_estimators: 300
max_depth: 6
min_samples_split: 5
Lý do lựa chọn: Sau khi thêm dữ liệu mới bằng lệnh add_new_data.py, độ phức tạp của tập dữ liệu tăng lên. Việc sử dụng Gradient Boosting với số lượng cây lớn (300) và độ sâu tăng lên (6) giúp mô hình học được các ranh giới quyết định chi tiết hơn, từ đó đưa Accuracy vượt ngưỡng 70% (đạt khoảng 72-74% tùy lần chạy).

## 2. Phân tích Độ lệch dữ liệu (Bonus 5)
Hệ thống cảnh báo tự động đã ghi nhận sự mất cân bằng nhẹ trong tập huấn luyện:

Class 1: ~43.5%
Class 0: ~36.8%
Class 2: ~19.6% Mặc dù lớp 2 có tỷ lệ thấp nhất nhưng vẫn trên ngưỡng 10%, do đó mô hình vẫn có đủ dữ liệu để học mà không gây ra lỗi nghiêm trọng về bias.

## 3. Khó khăn và Giải quyết
Lỗi xác thực Workflow: Ban đầu tôi không thể push file lên thư mục .github/workflows do quyền Token. Giải quyết: Tôi đã tự push thủ công bằng Terminal trên máy local để kích hoạt Pipeline.

Lỗi Service trên EC2: Máy ảo không tự khởi động được do sai đường dẫn Python. Giải quyết: Đã cập nhật lại file mlops-serve.service với đường dẫn chính xác là /usr/bin/python3.

Lỗi DagsHub Authorization: Thư viện dagshub.init yêu cầu xác thực tương tác trong CI. Giải quyết: Chuyển sang cấu hình MLflow chuẩn thông qua 3 biến môi trường (Secrets) để Pipeline chạy tự động 100%.

Hạ cấp hiệu suất ở Bước 3: Khi thêm dữ liệu mới, Accuracy bị giảm. Giải quyết: Đã tinh chỉnh siêu tham số và áp dụng cơ chế Rollback (Bonus 4) để đảm bảo chỉ deploy bản có hiệu suất tốt hơn.

## 4. Kết luận
Toàn bộ hệ thống MLOps đã được thiết lập hoàn chỉnh, từ việc quản lý dữ liệu bằng DVC, theo dõi thí nghiệm bằng MLflow/DagsHub, đến việc tự động kiểm tra và Deploy lên AWS EC2 thông qua GitHub Actions.