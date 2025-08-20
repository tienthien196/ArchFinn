# ArchFinn Engine – Tài liệu mở

> **Where Ideas Become Architectures**

Tài liệu này mô tả toàn diện dự án **ArchFinn Engine**: kiến trúc, mô-đun, DSL, cách vận hành, CLI/SDK, ví dụ, mở rộng, kiểm thử, và lộ trình phát triển. Nội dung hướng đến người dùng cuối **và** contributor mã nguồn mở.

---

## Mục lục
1. [Giới thiệu nhanh](#giới-thiệu-nhanh)
2. [Kiến trúc tổng thể](#kiến-trúc-tổng-thể)
3. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
4. [Ngôn ngữ ArchFinn Script (DSL)](#ngôn-ngữ-archfinn-script-dsl)
5. [Parser (Lark) & Transformer](#parser-lark--transformer)
6. [Engine Runtime](#engine-runtime)
7. [CLI](#cli)
8. [SDK (Python API)](#sdk-python-api)
9. [Ví dụ kịch bản](#ví-dụ-kịch-bản)
10. [Mở rộng & Phát triển](#mở-rộng--phát-triển)
11. [Kiểm thử & Gỡ lỗi](#kiểm-thử--gỡ-lỗi)
12. [Lộ trình (Roadmap)](#lộ-trình-roadmap)
13. [License](#license)
14. [Đóng góp](#đóng-góp)

---

## Giới thiệu nhanh
**ArchFinn Engine** là một **script engine** mô phỏng kịch bản tấn công/phòng thủ trong kiến trúc hệ thống thông qua một DSL gọn nhẹ (
**.afinn**). Công cụ cung cấp:
- **CLI** để chạy kịch bản.
- **Parser** dựa trên **Lark** để sinh **AST**.
- **Runtime/Engine** tối giản để thực thi *step* (exploit, move_lateral, exfiltrate) với xác suất, phát hiện, và kết thúc kịch bản.
- **SDK** Python để nhúng engine vào ứng dụng khác.

> Trạng thái hiện tại: Engine đã chạy được **SCENARIO/SIMULATION** với **timeline** và các **STEP**; phần **STRUCTURE/BEHAVIOR** đã có trong DSL nhưng chưa được gắn hoàn chỉnh vào runtime.

---

## Kiến trúc tổng thể
```mermaid
flowchart LR
    A[CLI (archfinn)] -->|đọc .afinn| B[Parser (Lark)]
    B -->|AST| C[Engine Runtime]
    C -->|logs/events| D[Console Output]
    E[SDK (Python)] -->|parse/run| B
    E -->|run_scenario| C

    subgraph Parser
      B1[grammar.py]-->B2[parser.py]
      B2-->B3[ast.py]
    end

    subgraph Engine
      C1[core/engine.py]
      C2[core/model.py]
      C3[core/runtime.py]
      C1-->C2
      C1-->C3
    end
```

**Luồng chính:**
1. `archfinn <file.afinn>` → CLI đọc tệp.
2. `parser` (Lark) parse DSL → sinh **AST** (`Scenario`, `ScenarioStep`, ...).
3. `run_scenario` trong `core/engine.py` thực thi từng step theo **timeline** và tham số.
4. In **log** theo tick, kết quả cuối (END), và các sự kiện (events).

---

## Cấu trúc thư mục
```
archfinn/
├─ cli/
│  └─ main.py                # Entry CLI
├─ core/
│  ├─ engine.py              # Runtime chính (run_scenario)
│  ├─ model.py               # Dataclass mô tả Node/Edge/Control...
│  └─ runtime.py             # EventBus, SimulationContext (tiềm năng)
├─ parser/
│  ├─ ast.py                 # AST dataclass (Scenario, ScenarioStep...)
│  ├─ grammar.py             # Lark grammar (DSL)
│  └─ parser.py              # Khởi tạo Lark+Transformer
├─ sdk/
│  └─ api.py                 # load/run/export API
├─ stdlib/
│  └─ cloud/controls.afinn   # Ví dụ DSL tiêu chuẩn
└─ utils/
   └─ graph.py               # (placeholder)
```

Các tệp khác:
- `pyproject.toml`: cấu hình build & console_scripts (`archfinn = archfinn.cli.main:main`).
- `examples/demo.afinn`, `test.afinn`: kịch bản mẫu.

---

## Ngôn ngữ ArchFinn Script (DSL)
### Header
```afinn
ARCHFINN "v1.0"
```

### Khối SIMULATION/SCENARIO
`SIMULATION` và `SCENARIO` tương đương trong parser, cùng chứa `timeline` và `STEP`.

```afinn
SIMULATION "Test Attack Path" {
    timeline = {
        max_steps = 10,
        tick_delay = 1.0
    }

    STEP S1 { ... }
    STEP S2 { ... }
}
```

### Timeline
- `max_steps` *(NUMBER)*: số vòng lặp tối đa.
- `tick_delay` *(NUMBER)*: độ trễ mỗi tick (giây).

### STEP
Các thuộc tính hợp lệ trong `STEP` (đã được grammar hỗ trợ):
- `action` *(STRING | IDENT)* – tên hành động: `exploit`, `move_lateral`, `exfiltrate` (engine hiện hỗ trợ 3 loại này).
- `attacker` *(value)* – nhãn/tác nhân.
- `target` *(value)* – đích tấn công.
- `type` *(value)* – loại khai thác/phương thức.
- `base_success` *(NUMBER)* – xác suất cơ bản thành công.
- `from`, `to` *(value)* – nguồn/đích cho di chuyển ngang.
- `method` *(value)* – phương thức (tuỳ chọn).
- `rate` *(value)* – tốc độ (tuỳ chọn).
- `detect_prob` *(NUMBER)* – xác suất bị phát hiện (dùng trong `exfiltrate`).
- `data_volume` *(NUMBER)* – dung lượng dữ liệu (MB) dùng khi `exfiltrate`.
- `on_success` *(jump_target)* – nhảy khi thành công.
- `on_fail` *(jump_target)* – nhảy khi thất bại.
- `on_detect` *(jump_target)* – nhảy khi bị phát hiện.
- `next` *(jump_target)* – nhảy tiếp theo (tuỳ chọn chung).

**jump_target** có 2 dạng:
```afinn
on_success = goto:S2
on_fail    = end:blocked
on_detect  = end:alert_triggered
```

### Giá trị (value)
- `STRING`: chuỗi trong `"..."`.
- `NUMBER`: `123` hoặc `12.34`.
- `IDENT`: định danh `a_z`, `A_Z`, số, `_` hoặc `-` (không bắt đầu bằng số).
- List: `[ value, value, ... ]`.

### (Tuỳ chọn) META / STRUCTURE / BEHAVIOR
Ngôn ngữ hỗ trợ thêm các khối sau (parser hiểu, engine sẽ mở rộng tích hợp dần):
- `META { author = "...", version = "...", ... }`
- `STRUCTURE { NODE ..., EDGE ... }`
- `BEHAVIOR { CONTROL ..., VULN ..., DETECTOR ..., RESPONSE ..., ACTOR ... }`

---

## Parser (Lark) & Transformer
- **Grammar**: `archfinn/parser/grammar.py` – cú pháp DSL bằng Lark (LALR).
- **Transformer**: `archfinn/parser/parser.py` → `AfinnTransformer` chuyển cây parse thành **AST dataclass** (`Scenario`, `ScenarioStep`, ...).

Điểm nổi bật:
- Hỗ trợ cả `SCENARIO` và `SIMULATION` (cùng trả về `Scenario`).
- `timeline = { ... }` → dict.
- `STEP` → `ScenarioStep(id, action, params)`; mọi thuộc tính (ngoài `action`) nằm trong `params`.
- **Sửa lỗi đã biết**: Thuộc tính `data_volume` phải có trong rule `step` (đã thêm vào `grammar.py`). Khuyến nghị rút gọn rule:

```lark
# Khuyến nghị:
step: "STEP" IDENT "{" step_prop* "}"
```

Nhờ vậy, khi thêm property mới, chỉ cần khai báo `*_prop` + Transformer, không quên sửa danh sách trong `step`.

---

## Engine Runtime
Tệp: `archfinn/core/engine.py`

### Trạng thái & log
- `ArchState`: giữ `nodes`, `edges`, `controls`, `events`, `logs`, `tick`, `rng`.
- `state.log(...)`: in log với tiền tố `[t=<tick>]`.

### Xác suất & kiểm soát
- `eval_prob(state, kind, target/path, base_p, context)`
  - Tính `p = base_p * (1 - p_block) * context`.
  - `p_block` dựa trên hiệu quả kiểm soát của `nodes` hoặc `path` (nếu có). Hiện `controls` chưa được nạp từ DSL vào `state` ở CLI, nhưng cơ chế đã sẵn sàng.

### Vòng chạy `run_scenario(state, scenario)`
- Đọc `timeline.max_steps`, `timeline.tick_delay`.
- Bắt đầu từ step đầu tiên.
- **Hỗ trợ action**:
  1. `exploit`
     - Tham số: `target`, `type`, `base_success`.
     - Quyết định thành công bằng RNG; nhảy `on_success`/`on_fail`.
  2. `move_lateral`
     - Tham số: `from`, `to`, `type`, `base_success`.
     - Xác suất xét theo `path=[from,to]`.
  3. `exfiltrate`
     - Tham số: `detect_prob`, `data_volume`, `on_detect`, `on_success`.
     - Nếu bị phát hiện: emit event `ALERT.EXFIL` và nhảy `on_detect` (thường `end:*`).
     - Nếu không: nhảy `on_success` (có thể `goto` hoặc `end`).

> Nếu không có nhảy hợp lệ sau một action → kết thúc sớm với log `No valid transition found`.

### Ngẫu nhiên & seed
- RNG: `state.rng` (mặc định seed 1337). CLI cho phép đổi seed (`--seed`).

---

## CLI
Tệp: `archfinn/cli/main.py`

### Sử dụng
```bash
archfinn <file.afinn> [--scenario NAME] [--debug] [--seed INT] [--quiet]
```

**Tuỳ chọn**
- `--scenario, -s`: chọn scenario theo tên.
- `--debug, -d`: in thêm thông tin debug/trace khi lỗi parse/runtime.
- `--seed`: thiết lập seed RNG.
- `--quiet, -q`: chỉ in kết quả ngắn gọn.

**Ví dụ**
```bash
archfinn test.afinn --debug
archfinn examples/demo.afinn --seed 42
```

---

## SDK (Python API)
Tệp: `archfinn/sdk/api.py`

### API chính
- `load(path) -> {ast, source, path}`
- `run(path, scenario_name=None) -> result`
- `export(path, format="json")`

**Ví dụ**
```python
from archfinn.sdk.api import load, run, export

info = load("test.afinn")
print(info["ast"])           # Xem AST

res = run("test.afinn")      # Chạy scenario đầu tiên
print(res["result"], res["events"])  # Kết quả & sự kiện

print(export("test.afinn", "json"))  # Xuất JSON đơn giản
```

---

## Ví dụ kịch bản
### 1) Kịch bản tối thiểu
```afinn
ARCHFINN "v1.0"
SIMULATION "Minimal" {
  STEP S1 {
    action = exploit
    target = webserver
    type = sql_injection
    base_success = 0.6
    on_success = end:ok
    on_fail = end:blocked
  }
}
```

### 2) Kịch bản nhiều bước (có nhánh retry & exfiltrate)
```afinn
ARCHFINN "v1.0"
SIMULATION "Multi-step" {
  timeline = {
    max_steps = 12,
    tick_delay = 1.0
  }

  STEP S1 {
    action = exploit
    target = webserver
    type = sql_injection
    base_success = 0.7
    on_success = goto:S2
    on_fail = end:initial_blocked
  }

  STEP S2 {
    action = move_lateral
    from = webserver
    to = dbserver
    type = ssh
    base_success = 0.5
    on_success = goto:S3
    on_fail = goto:S2_retry
  }

  STEP S2_retry {
    action = move_lateral
    from = webserver
    to = dbserver
    type = ssh
    base_success = 0.3
    on_success = goto:S3
    on_fail = end:movement_failed
  }

  STEP S3 {
    action = exfiltrate
    detect_prob = 0.5
    data_volume = 1000
    on_success = end:exfil_success
    on_detect = end:alert_triggered
  }
}
```

---

## Mở rộng & Phát triển
### Thêm thuộc tính mới cho STEP
1. **Grammar** (`grammar.py`): khai báo `*_prop` mới và thêm vào `step_prop`.
2. **Rule step**: khuyến nghị sử dụng `step_prop*` để không cần liệt kê thủ công.
3. **Transformer** (`parser.py`): thêm phương thức `def <name>_prop(self, args): return ("<name>", args[0])`.
4. **Engine** (`engine.py`): đọc từ `step.params.get("<name>")` và xử lý.

**Ví dụ**: thêm `stealth` (0..1)
```lark
stealth_prop: "stealth" "=" NUMBER
step_prop: ... | stealth_prop
```
```python
def stealth_prop(self, args):
    return ("stealth", args[0])
```
Trong `eval_prob(...)` thêm tham số `context=1.0 - stealth` (ví dụ) hoặc viết logic riêng trong action.

### Thêm action mới
- Không cần sửa grammar (giá trị `action` là tự do). Chỉ cần:
  - Thêm case trong `run_scenario` (`elif action == "scan": ...`).
  - Định nghĩa tham số cần thiết và cách nhảy (`on_success`/`on_fail`/`next`).

### Kết nối STRUCTURE/BEHAVIOR vào Engine
- Nạp `NODE`/`EDGE`/`CONTROL` từ DSL vào `ArchState`.
- Tính `state.controls` từ `CONTROL.effectiveness`.
- Gắn `node.controls` đúng với từng node để `eff_node` phát huy hiệu quả.

**Gợi ý skeleton**
```python
# Sau khi parse, duyệt AST để dựng state.nodes/state.controls
state = ArchState(nodes={}, edges=[], controls={})
# state.nodes["webserver"] = Node(..., controls=["WAF"])
# state.controls["WAF"] = {"effectiveness": {"sql_injection": 0.4}}
```

### Logging nâng cao
- Ghi log `data_volume` khi exfiltrate thành công/thất bại.
- Cho phép log ra file (`--log-file`).

---

## Kiểm thử & Gỡ lỗi
### Lỗi parse thường gặp
- **Unexpected token**: thuộc tính chưa có trong grammar `step` (ví dụ `data_volume` trước đây). → Thêm vào grammar hoặc dùng `step_prop*`.
- **AST is None / No valid scenario**: tệp không có `SCENARIO/SIMULATION` hợp lệ.

### Bật debug
```bash
archfinn test.afinn --debug
```
- In traceback parse/runtime khi lỗi.

### Tái lập kết quả
- Dùng `--seed <int>` để cố định RNG.

---

## Lộ trình (Roadmap)
- [ ] Kết nối đầy đủ `STRUCTURE/BEHAVIOR` vào runtime (Node/Edge/Control/VULN/DETECTOR/RESPONSE/ACTOR).
- [ ] Hệ thống **detector/response** theo event bus (phát hiện → phát sự kiện → hành động phản ứng).
- [ ] Bộ sinh **báo cáo** (JSON/Markdown/HTML) & exporter chi tiết.
- [ ] Tích hợp **networkx** để mô phỏng đồ thị tấn công.
- [ ] Ứng dụng **FastAPI/Streamlit** làm UI demo.
- [ ] Test suite (pytest) và CI.

---

## License
Hiện repo **chưa có** file `LICENSE`. Để mở nguồn hoàn toàn, bạn có thể chọn:
- **MIT** – ngắn gọn, linh hoạt.
- **Apache-2.0** – kèm điều khoản bằng sáng chế.
- **BSD-3-Clause** – tương tự MIT, ràng buộc attribution.

> Khuyến nghị: thêm file `LICENSE` vào gốc dự án và ghi rõ trong `pyproject.toml`.

---

## Đóng góp
- Fork → tạo nhánh → commit theo chuẩn → PR.
- Mở issue với template: *Mô tả*, *Cách tái hiện*, *Kỳ vọng*, *Log/Traceback*.
- Code style: Python ≥3.8, giữ kiểu dataclass & typing như hiện tại.

**Liên hệ/Thanks**: ArchFinn Team.

---

> *Tài liệu này có thể dùng làm README.md cho repo. Nếu cần mình xuất bản bản tiếng Anh/đa ngôn ngữ, hoặc sinh tự động từ nội dung hiện tại, hãy ping mình.*

