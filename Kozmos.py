import json
import datetime
import random
from pathlib import Path
from typing import Dict, Any


class KozmosV7:
    def __init__(self, name: str = "Kozmos"):
        self.name = name
        self.memory_path = Path("kozmos_memory_v7.json")
        self.backup_path = Path("kozmos_memory_v7.bak")
        self.state = {
            "mood": "neutral",
            "last_topic": None,
            "last_response": None
        }
        self.memory = self._load_memory()

    # ================= HAFIZA =================
    def _load_memory(self) -> Dict[str, Any]:
        default_mem = {
            "conversations": [],
            "knowledge": {},
            "stats": {"messages": 0, "learned": 0}
        }

        if not self.memory_path.exists():
            return default_mem

        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            print(f"⚠️ {self.name}: Hafıza bozuktu, sıfırlandı.")
            return default_mem

    def _save_memory(self):
        try:
            if self.memory_path.exists():
                self.memory_path.replace(self.backup_path)

            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Hafıza yazılamadı: {e}")

    # ================= YARDIMCI =================
    def _clean(self, text: str) -> str:
        return "".join(c for c in text if c.isprintable()).strip()

    def _time_greeting(self) -> str:
        h = datetime.datetime.now().hour
        if 5 <= h < 12: return "Günaydın ☀️"
        if 12 <= h < 18: return "İyi günler 😎"
        return "İyi akşamlar 🌙"

    # ================= NİYET =================
    def detect_intent(self, text: str) -> str:
        t = text.lower()
        if t.startswith("/"):
            return "command"
        if t.startswith("öğren"):
            return "learn"
        if any(x in t for x in ["merhaba", "selam"]):
            return "greeting"
        if any(x in t for x in ["sinir", "öfke", "lan"]):
            return "angry"
        if any(x in t for x in ["mutlu", "harika", "efsane"]):
            return "happy"
        if any(x in t for x in ["nedir", "ne", "kim"]):
            return "question"
        return "chat"

    # ================= ÖĞRENME =================
    def learn(self, raw: str) -> str:
        try:
            content = raw.split("öğren", 1)[1].strip()
            topic, info = [x.strip() for x in content.split(":", 1)]

            topic_key = topic.lower()
            self.memory["knowledge"].setdefault(topic_key, [])

            if info not in self.memory["knowledge"][topic_key]:
                self.memory["knowledge"][topic_key].append(info)
                self.memory["stats"]["learned"] += 1
                self._save_memory()
                return f"✅ '{topic}' hakkında yeni bilgi öğrendim."

            return "Bunu zaten biliyorum 🙂"
        except Exception:
            return "💡 Format: öğren konu: bilgi"

    # ================= BİLGİ ARAMA =================
    def search_knowledge(self, text: str) -> str | None:
        words = set(text.lower().split())

        for topic, infos in self.memory["knowledge"].items():
            topic_words = set(topic.split())
            if topic_words & words:
                self.state["last_topic"] = topic
                return f"🔍 {topic.capitalize()}: {random.choice(infos)}"

        return None

    # ================= KOMUT =================
    def handle_command(self, cmd: str) -> str:
        stats = self.memory["stats"]
        if cmd == "/stats":
            return f"📊 Mesaj: {stats['messages']} | Bilgi: {stats['learned']}"
        if cmd == "/topics":
            return "📚 Konular: " + (", ".join(self.memory["knowledge"]) or "Yok")
        if cmd == "/explain":
            if self.state["last_topic"]:
                return f"Son konuştuğumuz konu: {self.state['last_topic']}"
            return "Henüz bir konu yok."
        return "❌ Bilinmeyen komut."

    # ================= CEVAP =================
    def generate_response(self, user_input: str) -> str:
        raw = self._clean(user_input)
        intent = self.detect_intent(raw)

        if intent == "command":
            return self.handle_command(raw)

        if intent == "learn":
            return self.learn(raw)

        info = self.search_knowledge(raw)
        if info:
            return info

        intent_responses = {
            "greeting": self._time_greeting(),
            "angry": "Biraz duralım, sakin düşünelim 🧘",
            "happy": "Bu enerjin çok iyi 😄",
            "question": "Bu güzel bir soru. Biraz açar mısın?"
        }

        if intent in intent_responses:
            return intent_responses[intent]

        responses = [
            "Anlıyorum, devam et.",
            "Bunu biraz daha detaylandıralım.",
            "İlginç…",
            "Bu konu üzerine düşünebiliriz."
        ]

        response = random.choice(responses)
        if response == self.state["last_response"]:
            response = random.choice(responses)

        self.state["last_response"] = response
        return response

    # ================= ÇALIŞ =================
    def run(self):
        print(f"🚀 {self.name} V7.1 aktif (çıkmak için 'exit')")
        print("-" * 40)

        while True:
            user = input("Siz > ").strip()
            if not user:
                continue
            if user.lower() in ["exit", "çık", "quit"]:
                print(f"{self.name} > Görüşürüz 👋")
                break

            reply = self.generate_response(user)
            print(f"{self.name} > {reply}")

            self.memory["conversations"].append({
                "time": datetime.datetime.now().isoformat(),
                "user": user,
                "kozmos": reply
            })
            self.memory["stats"]["messages"] += 1
            self._save_memory()


if __name__ == "__main__":
    KozmosV7().run()
  # © 2026 uygarbabapro-ETHICAL all rights reserved
