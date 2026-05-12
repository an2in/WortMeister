"""
WortMeister — Local Test Script
================================
Checks all 5 API endpoints on a running server.

Usage:
    1. Start the server:  uvicorn main:app --reload --port 8000
    2. Run the tests:     python test_sync.py
"""

import json
import sys
import urllib.request
import urllib.error

API = "http://localhost:8000"
passed = 0
failed = 0


def test(name: str, ok: bool, detail: str = ""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name} — {detail}")


def get(path: str) -> dict:
    with urllib.request.urlopen(f"{API}{path}") as r:
        return json.loads(r.read())


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{API}{path}", data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get_raw(path: str):
    return urllib.request.urlopen(f"{API}{path}")


# ─── Tests ────────────────────────────────────────────────────────────────────

print("\n🧪 WortMeister Test Suite\n" + "=" * 40)

# 1. Search (Vietnamese)
print("\n📖 Search API")
try:
    data = get("/api/search?q=hau&lang=vi")
    results = data.get("results", [])
    test("search_vi: returns results", len(results) > 0, "No results")
    if results:
        test("search_vi: first result is 'Haus'", results[0]["word"] == "Haus",
             f"Got '{results[0]['word']}'")
        test("search_vi: meaning is Vietnamese", "nhà" in results[0]["meaning"],
             f"Got '{results[0]['meaning']}'")
except Exception as e:
    test("search_vi", False, str(e))

# 2. Search (English)
try:
    data = get("/api/search?q=hau&lang=en")
    results = data.get("results", [])
    test("search_en: returns results", len(results) > 0, "No results")
    if results:
        test("search_en: meaning is English", results[0]["meaning"] == "house",
             f"Got '{results[0]['meaning']}'")
except Exception as e:
    test("search_en", False, str(e))

# 3. Next Card
print("\n🃏 Flashcard API")
try:
    data = get("/api/next-card?lang=vi")
    test("next_card: has 'word'", "word" in data, "Missing 'word'")
    test("next_card: has 'meaning'", "meaning" in data, "Missing 'meaning'")
    test("next_card: has 'level'", "level" in data, "Missing 'level'")
    card_word = data.get("word", "")
except Exception as e:
    test("next_card", False, str(e))
    card_word = ""

# 4. Update Card
try:
    if card_word:
        data = post("/api/update-card", {"word": card_word, "quality": 4})
        test("update_card: success=true", data.get("success") is True,
             f"success={data.get('success')}")
        test("update_card: has new_interval", "new_interval" in data,
             "Missing 'new_interval'")
        test("update_card: has message", "message" in data, "Missing 'message'")
    else:
        test("update_card", False, "Skipped — no card_word from next_card")
except Exception as e:
    test("update_card", False, str(e))

# 5. Check Translation
print("\n✍️  Translation API")
try:
    data = post("/api/check-translation", {
        "target_word": "Haus",
        "user_sentence": "Das ist mein Haus.",
    })
    test("check_translation: correct=true", data.get("correct") is True,
         f"correct={data.get('correct')}")
    test("check_translation: has feedback", "feedback" in data, "Missing 'feedback'")
except Exception as e:
    test("check_translation", False, str(e))

try:
    data = post("/api/check-translation", {
        "target_word": "Haus",
        "user_sentence": "Ich lerne Deutsch.",
    })
    test("check_translation: wrong → correct=false", data.get("correct") is False,
         f"correct={data.get('correct')}")
except Exception as e:
    test("check_translation_wrong", False, str(e))

# 6. Audio
print("\n🔊 Audio API")
try:
    resp = get_raw("/api/audio?word=Hallo")
    test("audio: status 200", resp.status == 200, f"Status {resp.status}")
    ctype = resp.headers.get("content-type", "")
    test("audio: content-type is audio", "audio" in ctype, f"Got '{ctype}'")
    body = resp.read()
    test("audio: body > 0 bytes", len(body) > 0, "Empty body")
except Exception as e:
    test("audio", False, str(e))

# ─── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'=' * 40}")
print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
if failed == 0:
    print("🎉 ALL TESTS PASSED")
    sys.exit(0)
else:
    print("⚠️  SOME TESTS FAILED")
    sys.exit(1)
