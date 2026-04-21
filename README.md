# WortMeister — Ứng dụng Học Từ Vựng Tiếng Đức 🇩🇪

> **Personal Project** — German Vocabulary Learning App

WortMeister là ứng dụng web hỗ trợ tra cứu, phát âm và ghi nhớ từ vựng tiếng Đức cấp độ A1–B1 thông qua hệ thống **Spaced Repetition (SM-2)**, tìm kiếm **Autocomplete (Binary Search)**, kiểm tra bản dịch bằng **Regex**, và các tính năng mở rộng gồm **Article Drill**, **Context Analyzer**, và **Custom Text-to-Speech**. Hỗ trợ song ngữ Tiếng Việt / English.

---

## Kiến trúc hệ thống

```
┌──────────────────┐       HTTP/JSON        ┌──────────────────────┐
│   Web Frontend   │  ◄──────────────────►  │  FastAPI Backend     │
│  (HTML/CSS/JS)   │     fetch() calls      │  (Python + uvicorn)  │
└──────────────────┘                        └─────────┬────────────┘
                                                      │
                                          ┌───────────┴───────────┐
                                          │   In-Memory Store     │
                                          │   (loaded from JSON)  │
                                          └───────────────────────┘
```

## Tech Stack

| Layer     | Technology                                  |
|-----------|---------------------------------------------|
| Backend   | Python 3.10+, FastAPI, uvicorn              |
| Frontend  | HTML / Tailwind CSS / Vanilla JS            |
| Database  | In-memory (RAM), load từ `data.json`        |
| TTS       | `edge-tts` (Microsoft Edge TTS API)         |
| Algorithm | `bisect`, `heapq`, `re`, hash-based cache   |
| i18n      | Custom `data-i18n` + JS translation map     |

## Cấu trúc thư mục

```
DSA_BTL/
├── main.py              # FastAPI entrypoint (`uvicorn main:app`)
├── app/                 # Backend package theo kiến trúc service/controller
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   ├── domain.py
│   │   └── schemas.py
│   ├── routers/
│   │   └── api.py
│   ├── services/
│   │   ├── article_drill_service.py
│   │   ├── audio_service.py
│   │   ├── container.py
│   │   ├── context_analyzer_service.py
│   │   ├── search_service.py
│   │   ├── srs_service.py
│   │   ├── translation_service.py
│   │   └── vocabulary_store.py
│   ├── dependencies.py
│   └── factory.py
├── data.json            # Vocabulary dataset (597 từ A1, Goethe-Zertifikat, song ngữ VI/EN)
├── README.md            # Project Wiki (file này)
├── test_sync.py         # Script test tự động (local)
└── frontend/
    └── index.html       # SPA — Search, Flashcards, Translate, Drill, Context, Free TTS (i18n VI/EN)
```

## API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint                       | Mô tả                                           | Algorithm                         |
|--------|--------------------------------|--------------------------------------------------|-----------------------------------|
| GET    | `/api/search?q={prefix}&lang=` | Autocomplete từ vựng                             | `bisect_left`                     |
| GET    | `/api/next-card?lang=`         | Lấy flashcard cần ôn nhất                        | `heapq.heappop`                   |
| POST   | `/api/update-card`             | Cập nhật kết quả ôn tập (SM-2)                   | `heapq.heappush` + SM-2           |
| POST   | `/api/check-translation`       | Kiểm tra bản dịch tiếng Đức                      | `re.search`                       |
| GET    | `/api/audio?word={word}`       | Phát âm từ vựng (MP3)                            | `edge-tts` async + cache hash     |
| GET    | `/api/drill/next`              | Lấy câu hỏi phản xạ mạo từ/số nhiều              | `heapq.heappop`                   |
| POST   | `/api/drill/answer`            | Chấm câu trả lời drill và reschedule theo lỗi    | `heapq.heappush` + mistake weight |
| POST   | `/api/context/analyze`         | Phân tích đoạn văn và trả token match để highlight | regex tokenization + hash lookup  |
| POST   | `/api/audio/text`              | Tạo audio từ văn bản tự do                       | `edge-tts` async + cache hash     |
| GET    | `/api/audio/file/{filename}`   | Phục vụ file MP3 đã cache                        | file cache lookup                 |

> **`lang` parameter:** `vi` (mặc định — nghĩa tiếng Việt) hoặc `en` (nghĩa tiếng Anh).

<details>
<summary><strong>Chi tiết Request/Response</strong></summary>

### GET `/api/search?q=hau&lang=vi`
```json
// Response
{ "results": [{ "word": "Haus", "meaning": "ngôi nhà", "meaning_en": "house", "example": "...", "translation": "...", "level": "A1" }] }
```

### GET `/api/next-card?lang=en`
```json
// Response
{ "word": "lernen", "meaning": "to learn, to study", "meaning_en": "to learn, to study", "example": "...", "translation": "...", "level": "A1", "interval": 1.0, "repetitions": 0, "easiness": 2.5, "due": 1712700000.0 }
```

### POST `/api/update-card`
```json
// Request
{ "word": "lernen", "quality": 4 }
// Response
{ "success": true, "word": "lernen", "new_interval": 6.0, "new_due": "2026-04-16 23:00", "message": "Next review in 6.0 day(s)" }
```

### POST `/api/check-translation`
```json
// Request
{ "target_word": "Haus", "user_sentence": "Das ist mein Haus." }
// Response
{ "correct": true, "target_word": "Haus", "feedback": "✅ Richtig! ..." }
```

### GET `/api/audio?word=Hallo`
→ Returns `audio/mpeg` file (MP3).

### GET `/api/drill/next`
```json
// Response
{ "word": "Abfahrt", "article_options": ["der", "die", "das"], "attempts": 0, "mistakes": 0, "hint": "Plural begins with: Ab..." }
```

### POST `/api/drill/answer`
```json
// Request
{ "word": "Abfahrt", "article": "die", "plural": "Abfahrten" }
// Response
{ "word": "Abfahrt", "article_correct": true, "plural_correct": false, "correct": false, "expected_article": "die", "expected_plural": "Abfahrte (auto)", "message": "Incorrect. This noun will appear more frequently.", "next_due_in_minutes": 3.0, "attempts": 1, "mistakes": 1 }
```

### POST `/api/context/analyze`
```json
// Request
{ "text": "Das Haus und die Adresse sind hier.", "lang": "vi" }
// Response
{ "text": "Das Haus und die Adresse sind hier.", "matches": [{ "word": "Haus", "start": 4, "end": 8, "meaning": "ngôi nhà", "meaning_en": "house", "example": "...", "article": "das" }] }
```

### POST `/api/audio/text`
```json
// Request
{ "text": "Guten Morgen zusammen" }
// Response
{ "text": "Guten Morgen zusammen", "audio_url": "/api/audio/file/<md5>.mp3" }
```

</details>

## Hướng dẫn chạy

### 1. Cài đặt thư viện

```bash
pip install fastapi uvicorn edge-tts
```

### 2. Chạy server

```bash
cd DSA_BTL
uvicorn main:app --reload --port 8000
```

Server chạy tại: [http://localhost:8000](http://localhost:8000)  
API Docs (tự động): [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Mở frontend

Truy cập [http://localhost:8000](http://localhost:8000) trên trình duyệt.  
Bấm nút **VI ↔ EN** ở góc trên bên phải để chuyển ngôn ngữ giao diện.

## Hướng dẫn Test (Local)

### Test tự động — `test_sync.py`

Script kiểm tra 5 endpoint nền tảng trên server đang chạy:

```bash
# Terminal 1: Khởi động server
uvicorn main:app --reload --port 8000

# Terminal 2: Chạy test
python test_sync.py
```

**Nội dung test:**

| Test                     | Kiểm tra                                              |
|--------------------------|-------------------------------------------------------|
| `test_search_vi`         | Search "hau" → trả về "Haus" (meaning = "ngôi nhà")  |
| `test_search_en`         | Search "hau" + lang=en → meaning = "house"            |
| `test_next_card`         | Lấy flashcard từ heap → trả về word, meaning, level   |
| `test_update_card`       | Rate quality=4 → trả về new_interval, success=true    |
| `test_check_translation` | "Das ist mein Haus." chứa "Haus" → correct=true       |
| `test_audio`             | `/api/audio?word=Hallo` → status 200, content-type=audio |

### Test thủ công — `curl`

```bash
# Search (Vietnamese)
curl "http://localhost:8000/api/search?q=hau&lang=vi"

# Search (English)
curl "http://localhost:8000/api/search?q=hau&lang=en"

# Flashcard
curl "http://localhost:8000/api/next-card?lang=vi"

# Update card
curl -X POST "http://localhost:8000/api/update-card" \
  -H "Content-Type: application/json" \
  -d '{"word": "Haus", "quality": 4}'

# Check translation
curl -X POST "http://localhost:8000/api/check-translation" \
  -H "Content-Type: application/json" \
  -d '{"target_word": "Haus", "user_sentence": "Das ist mein Haus."}'

# Audio
curl -o test.mp3 "http://localhost:8000/api/audio?word=Hallo"
```

### Test frontend — Trình duyệt

1. Mở `http://localhost:8000` → kiểm tra tab **Search** (gõ "hau" → "Haus" xuất hiện)
2. Chuyển tab **Flashcards** → lật thẻ, bấm đánh giá 0-5
3. Chuyển tab **Translate** → nhập câu tiếng Đức, bấm "Kiểm tra"
4. Chuyển tab **Article Drill** → chọn mạo từ + nhập plural, xác nhận feedback và countdown 30s
5. Chuyển tab **Context** → dán đoạn văn tiếng Đức, bấm Analyze, kiểm tra highlight + danh sách match
6. Chuyển tab **Free TTS** → nhập đoạn văn bản, bấm Generate Audio, kiểm tra player phát được
7. Bấm toggle **VI ↔ EN** → toàn bộ UI chuyển ngôn ngữ

### Test nhanh các endpoint mới (`curl`)

```bash
# Drill next
curl "http://localhost:8000/api/drill/next"

# Drill answer
curl -X POST "http://localhost:8000/api/drill/answer" \
  -H "Content-Type: application/json" \
  -d '{"word": "Abfahrt", "article": "die", "plural": "Abfahrten"}'

# Context analyzer
curl -X POST "http://localhost:8000/api/context/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Das Haus und die Adresse sind hier.", "lang": "vi"}'

# Free text TTS
curl -X POST "http://localhost:8000/api/audio/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Guten Morgen zusammen"}'
```

## Roadmap & Tiến độ

### Phase 1 — Cài đặt môi trường ✅
- [x] Cài Python 3.10+, pip
- [x] Cài thư viện: `fastapi`, `uvicorn`, `edge-tts`

### Phase 2 — Code Backend ✅
- [x] Chuẩn bị dataset `data.json` (597 từ A1, Goethe-Zertifikat)
- [x] Implement FastAPI backend + refactor sang kiến trúc service/controller
- [x] Endpoint `/api/search` — bisect autocomplete + `?lang=vi|en`
- [x] Endpoint `/api/next-card` + `/api/update-card` — heapq SRS + `?lang=vi|en`
- [x] Endpoint `/api/check-translation` — regex
- [x] Endpoint `/api/audio` — edge-tts
- [x] Endpoint `/api/drill/next` + `/api/drill/answer` — article/plural reflex mode
- [x] Endpoint `/api/context/analyze` — context analyzer
- [x] Endpoint `/api/audio/text` + `/api/audio/file/{filename}` — custom text-to-speech

### Phase 3 — Build UI ✅
- [x] Tạo giao diện bằng Google Stitch
- [x] Kết nối frontend với backend API (fetch)
- [x] Hệ thống i18n — toggle VI ↔ EN toàn bộ UI
- [x] Thêm tab mới: Article Drill, Context, Free TTS
- [x] UX Article Drill: feedback hiển thị tối thiểu 30s + countdown vòng tròn

### Phase 4 — Tích hợp & Hoàn thiện ✅
- [x] Test end-to-end các tính năng nền tảng
- [x] Smoke test các endpoint mở rộng (drill/context/free-tts)
- [x] Cập nhật tài liệu kỹ thuật thuật toán (`docs/technical_algorithm_report.md`)

### Phase 5 — Mở rộng
- [ ] Mở rộng dataset (1000+ từ vựng)
- [x] **Chế độ phản xạ Mạo từ (Der/Die/Das) & Số nhiều**
- [x] **Trợ lý đọc hiểu (Context Analyzer)**
- [x] **Công cụ Đọc văn bản tự do (Custom Text-to-Speech)**
- [ ] Viết báo cáo đồ án
- [ ] Deploy (tuỳ chọn)

---

*WortMeister — Wort (từ) + Meister (bậc thầy)*

> **Về việc sử dụng emoji trong README:** Có thể bạn đang nghĩ *"File này có emoji, chắc AI viết. Xóa emoji đi rồi push"*. Đúng rồi đấy :DDD. Tôi có sửa file cho đúng thông tin rồi, còn emoji thì tôi vẫn giữ lại 🐧​. Thực ra, việc sử dụng emoji trong văn bản **hoàn toàn có cơ sở khoa học**. Nghiên cứu của Boutet et al. (2021, *Computers in Human Behavior*) chỉ ra rằng positive emoji giúp người đọc cảm nhận người viết *thân thiện hơn* và xử lý thông tin *nhanh hơn*. Huh (2025, *PLOS One*) bổ sung: emoji tăng cảm giác *gần gũi* và *dễ mến* — bất kể đó là mặt cười hay cây xương rồng 🌵. Khalid (2024) còn phát hiện positive emoji *khuếch đại* cảm xúc tích cực trong văn bản. Nói cách khác, README không có emoji giống như phở không có rau — ăn được, nhưng buồn. Tất nhiên, *nhiều quá thì lố*, nên file này chỉ rắc emoji ở những chỗ thật sự cần thiết. Bạn đọc đến đây nghĩa là emoji đã hoàn thành nhiệm vụ của nó rồi 😄
