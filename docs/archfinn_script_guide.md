# 📘 ArchFinn Script Guide (DSL User Manual)

ArchFinn Script (đuôi `.afinn`) là Domain-Specific Language (DSL) được thiết kế để mô phỏng kịch bản tấn công và phòng thủ trong hệ thống CNTT. Tài liệu này hướng dẫn chi tiết cách viết, chạy và debug kịch bản.

---

## 🏗 Cấu trúc cơ bản
Một script `.afinn` bao gồm:

- **SCENARIO**: định nghĩa toàn bộ mô phỏng
- **STEP**: các bước tấn công/phòng thủ trong kịch bản
- **Properties**: tham số chi tiết của từng step

### Ví dụ skeleton
```afinn
SCENARIO "Tên kịch bản" {
    max_steps = 10
    tick_delay = 1.0

    STEP S1 {
        action = exploit
        attacker = hacker
        target = webserver
        method = sql_injection
        base_success = 0.6
        next = S2
    }

    STEP S2 {
        action = exfiltration
        attacker = hacker
        target = dbserver
        data_volume = 500
        base_success = 0.8
    }
}
```

---

## 🔑 Từ khóa & Thuộc tính

### SCENARIO
- `max_steps`: số bước tối đa trước khi dừng
- `tick_delay`: thời gian trễ giữa các bước (giây)

### STEP
Mỗi step có ID duy nhất (ví dụ `S1`, `S2`). Thuộc tính hỗ trợ:

| Thuộc tính       | Kiểu dữ liệu | Ý nghĩa |
|------------------|--------------|---------|
| `action`         | string       | Loại hành động (exploit, brute_force, exfiltration, v.v.) |
| `attacker`       | string       | Ai thực hiện step |
| `target`         | string       | Mục tiêu |
| `method`         | string       | Kỹ thuật cụ thể (sql_injection, phishing, …) |
| `base_success`   | float [0-1]  | Xác suất thành công cơ bản |
| `rate`           | float        | Tốc độ thực hiện |
| `detect_prob`    | float [0-1]  | Xác suất bị phát hiện |
| `on_success`     | Step ID      | Chuyển sang step nếu thành công |
| `on_fail`        | Step ID      | Chuyển sang step nếu thất bại |
| `on_detect`      | Step ID      | Chuyển sang step nếu bị phát hiện |
| `next`           | Step ID      | Bước tiếp theo mặc định |
| `data_volume`    | integer (MB) | Dữ liệu bị trích xuất |

---

## 📂 Ví dụ kịch bản đầy đủ
```afinn
SCENARIO "Multi-step Attack Simulation" {
    max_steps = 8
    tick_delay = 1.0

    STEP S1 {
        action = exploit
        attacker = hacker
        target = webserver
        method = sql_injection
        base_success = 0.7
        next = S2
    }

    STEP S2 {
        action = lateral_movement
        attacker = hacker
        target = dbserver
        method = stolen_credentials
        base_success = 0.5
        on_fail = S2_retry
        next = S3
    }

    STEP S2_retry {
        action = brute_force
        attacker = hacker
        target = dbserver
        method = password_guess
        base_success = 0.3
        next = S3
    }

    STEP S3 {
        action = exfiltration
        attacker = hacker
        target = dbserver
        data_volume = 1000
        base_success = 0.8
    }
}
```

---

## 🚀 Chạy script
```bash
archfinn myscenario.afinn --debug
```

### Ví dụ output
```
[t=00] 🚀 Running scenario: Multi-step Attack Simulation
[t=00] 🎯 Starting from step: S1
[t=01] ⚡ Exploit webserver via sql_injection: p=0.70 → ✅
[t=02] 🔄 Lateral movement to dbserver via stolen_credentials: p=0.50 → ❌
[t=02] ↩ Fallback to brute_force password_guess: p=0.30 → ✅
[t=03] 📦 Exfiltrating 1000 MB from dbserver → ✅
[t=03] 🏁 END: SUCCESS
```

---

## 🔍 Debug & Logging
- `--debug`: in cây AST sau khi parse
- Timeline log: hiển thị từng bước, xác suất thành công/thất bại
- Kết quả cuối: `SUCCESS`, `BLOCKED`, hoặc `DETECTED`

---

## 💡 Best Practices
- Luôn đặt `base_success` trong khoảng [0,1]
- Sử dụng `on_fail` để mô phỏng fallback attack
- Dùng `data_volume` để track dữ liệu bị mất
- Giữ tên step ngắn gọn (`S1`, `S2`) nhưng có logic

---

## 📌 Kết luận
ArchFinn Script cho phép bạn mô hình hóa kịch bản tấn công/phòng thủ nhanh chóng, dễ mở rộng và dễ debug. Việc hiểu rõ DSL này sẽ giúp viết kịch bản phong phú và thực tế hơn.

