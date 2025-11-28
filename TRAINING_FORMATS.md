# Training Data Formats Guide

Hệ thống hỗ trợ upload training data với 5 định dạng khác nhau:

## 1. JSON Format

File mẫu: `sample.json`

```json
[
  {
    "user": "Xin chào",
    "bot": "Chào bạn! Tôi có thể giúp gì cho bạn?",
    "intent": "chao_hoi"
  },
  {
    "user": "Giá bao nhiêu?",
    "bot": "Giá dao động từ 100k-500k",
    "intent": "hoi_gia"
  }
]
```

**Đặc điểm:**
- Array của các object
- Bắt buộc: `user`, `bot`
- Tùy chọn: `intent`

---

## 2. CSV Format

File mẫu: `sample.csv`

```csv
user,bot,intent
Xin chào,Chào bạn! Tôi có thể giúp gì cho bạn?,chao_hoi
Giá sản phẩm bao nhiêu?,Giá dao động từ 100k-500k tùy loại,hoi_gia
```

**Đặc điểm:**
- Dòng đầu là header (tên cột)
- Hỗ trợ các tên cột: `user/User/question/Question`, `bot/Bot/answer/Answer`, `intent/Intent/category/Category`
- Phân tách bằng dấu phẩy

---

## 3. Plain Text Format

File mẫu: `sample.txt`

### Format 1: User/Bot/Intent
```
User: Xin chào
Bot: Chào bạn! Tôi có thể giúp gì cho bạn?
Intent: chao_hoi

User: Giá bao nhiêu?
Bot: Giá dao động từ 100k-500k
Intent: hoi_gia
```

### Format 2: Q/A/#intent
```
Q: Làm sao liên hệ?
A: Bạn có thể gọi 0123456789
#lien_he

Q: Tính năng gì?
A: Chúng tôi có 3 tính năng chính
#tinh_nang
```

### Format 3: Alternate lines
```
Xin chào
Chào bạn! Tôi có thể giúp gì cho bạn?
---
Giá bao nhiêu?
Giá dao động từ 100k-500k
---
```

**Đặc điểm:**
- Dòng trống hoặc `---` để ngăn cách các cặp hội thoại
- Nếu không có intent, hệ thống sẽ tự động detect
- Hỗ trợ multi-line cho câu trả lời dài

**Auto-detect intent patterns:**
- `chao_hoi`: chào, hi, hello
- `hoi_gia`: giá, bao nhiêu, tiền, chi phí
- `lien_he`: liên hệ, số điện thoại, email, địa chỉ
- `tinh_nang`: tính năng, chức năng, làm gì
- `cam_on`: cảm ơn, thanks
- `tam_biet`: tạm biệt, bye

---

## 4. YAML Format (Rasa NLU)

File mẫu: `sample.yml`

```yaml
nlu:
- intent: chao_hoi
  examples: |
    - xin chào
    - chào bạn
    - hi
    - hello

- intent: hoi_gia
  examples: |
    - giá bao nhiêu
    - giá sản phẩm
    - bao nhiêu tiền
```

**Đặc điểm:**
- Format chuẩn của Rasa NLU
- Mỗi intent có nhiều examples
- Bot response sẽ được tạo tự động: `"Response for {intent}"`
- Hỗ trợ entity annotations: `[text](entity_name)` (sẽ được remove khi parse)

---

## 5. Markdown Format (Rasa 2.x)

File mẫu: `sample.md`

```markdown
## intent:chao_hoi
- xin chào
- chào bạn
- hi
- hello

## intent:hoi_gia
- giá bao nhiêu
- giá sản phẩm
- bao nhiêu tiền
```

**Đặc điểm:**
- Format của Rasa 2.x
- Header: `## intent:intent_name`
- Examples bắt đầu bằng `-`
- Bot response tự động: `"Response for {intent}"`
- Hỗ trợ entity annotations

---

## Upload Instructions

1. Vào trang **Training Data**
2. Chọn bot cần upload data
3. Click **Upload Training Data**
4. Chọn file với 1 trong 5 format trên
5. Hệ thống tự động detect format và parse

**Tùy chọn nâng cao:**
- Thêm `?use_intelligent_classification=true` vào URL để sử dụng Rasa NLU phân loại intent
- Ví dụ: `POST /bots/10/training/upload?use_intelligent_classification=true`

**Lưu ý:**
- File phải encode UTF-8
- YAML/Markdown chỉ có user examples, cần thêm bot response sau
- Sau khi upload, nhớ click **Train** để train model mới
- Nếu bot đã có model trained, có thể dùng intelligent classification để tự động phân loại intent chính xác hơn

---

## Intelligent Intent Classification

Hệ thống hỗ trợ 2 phương pháp phân loại intent:

### 1. **Regex-based (Mặc định)**
- Dùng pattern matching đơn giản
- Nhanh, không cần model
- Độ chính xác vừa phải (~70-80%)

### 2. **Rasa NLU-based (Khuyến nghị)**
- Sử dụng model Rasa đã train của bot
- Hiểu ngữ cảnh và ngữ nghĩa
- Độ chính xác cao (~90-95%)
- Cần bot đã có model trained trước

**Cách dùng:**
```bash
# Upload với intelligent classification
curl -X POST "http://localhost:8000/bots/10/training/upload?use_intelligent_classification=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@no_intent.txt"
```

**So sánh:**

| Phương pháp | Tốc độ | Độ chính xác | Yêu cầu |
|-------------|--------|--------------|---------|
| Regex | Rất nhanh | 70-80% | Không |
| Rasa NLU | Nhanh | 90-95% | Model trained |

---

## Auto Format Detection

Hệ thống tự động detect format dựa trên:

1. **Extension**: `.json`, `.csv`, `.yml`, `.yaml`, `.txt`, `.md`
2. **Content sniffing** nếu extension không rõ:
   - `[` hoặc `{` → JSON
   - `nlu:` hoặc `intent:` → YAML
   - `##` + `intent:` → Markdown
   - Có `,` và `\n` → CSV
   - Còn lại → TXT

---

## Examples trong project

Xem folder `test_data/` để tham khảo các file mẫu:
- `sample.json` - JSON format
- `sample.csv` - CSV format
- `sample.txt` - Plain text format
- `sample.yml` - YAML format
- `sample.md` - Markdown format
