import ast
import datetime as dt
import json
import math
import operator
import os
import random
import re
import threading
import time
import traceback
import tkinter as tk
from collections import deque
from tkinter import font, messagebox, scrolledtext
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


# ============================================================
# MeowAI 2.0 — Smart Desktop Assistant
# No external GUI framework required: Tkinter + web APIs.
# ============================================================

APP_NAME = "MeowAI"
CURRENT_VERSION = "2.0.0"
APP_DATA = os.getenv("APPDATA", os.path.expanduser("~"))
DB_DIR = os.path.join(APP_DATA, "MeowAI")
DB_FILE = os.path.join(DB_DIR, "meow_db.json")
CHAT_HISTORY_FILE = os.path.join(DB_DIR, "chat_history.json")

GITHUB_REPO_URL = "https://github.com/matvey2222222222/MeowAI/releases"
WIKI_API = "https://ru.wikipedia.org/w/api.php"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
]

# ------------------------------------------------------------
# Built-in knowledge
# ------------------------------------------------------------

BUILTIN_KNOWLEDGE = {
    "кто ты": "Я MeowAI 2.0 — локальный интеллектуальный помощник с встроенной базой знаний, контекстом диалога, математическим движком и поиском актуальной информации.",
    "как тебя зовут": "Меня зовут MeowAI. Можно просто Мяу. 🐱",
    "твое имя": "MeowAI.",
    "кто тебя создал": "В этой версии информация об авторе не задана в конфигурации проекта.",
    "что ты умеешь": (
        "Я умею:\n"
        "• 🧠 искать ответы во встроенной базе знаний;\n"
        "• 🔎 искать дополнительную информацию в Википедии и интернете;\n"
        "• 🧮 решать арифметические выражения безопасным вычислителем;\n"
        "• 💬 учитывать последние сообщения разговора;\n"
        "• 💾 сохранять историю и локальные ответы;\n"
        "• 🕒 работать с датой и временем;\n"
        "• 🔄 проверять релизы проекта на GitHub."
    ),
    "что такое ии": "Искусственный интеллект — область компьютерных наук, занимающаяся созданием систем, способных выполнять задачи, обычно требующие интеллектуальной обработки информации.",
    "что такое python": "Python — высокоуровневый язык программирования общего назначения, известный читаемостью, большой экосистемой и широким применением в автоматизации, веб-разработке, анализе данных и ИИ.",
    "что такое html": "HTML — язык разметки, который описывает структуру веб-документа.",
    "что такое css": "CSS — язык таблиц стилей, используемый для оформления HTML-документов.",
    "что такое javascript": "JavaScript — язык программирования, широко используемый для интерактивности веб-страниц и приложений.",
    "что такое алгоритм": "Алгоритм — конечная последовательность понятных действий, которая приводит к решению задачи.",
    "что такое браузер": "Браузер — программа для открытия и взаимодействия с веб-страницами и веб-приложениями.",
    "что такое сервер": "Сервер — компьютер или программа, предоставляющая ресурсы и сервисы другим участникам сети.",
    "что такое wi-fi": "Wi‑Fi — семейство технологий беспроводной локальной сети, основанных на стандартах IEEE 802.11.",
    "что такое блокчейн": "Блокчейн — способ хранения данных в виде последовательности связанных блоков, защищённых криптографическими механизмами.",
    "самая большая планета": "Юпитер — крупнейшая планета Солнечной системы по массе и диаметру.",
    "сколько планет в солнечной системе": "В современной классификации Солнечная система имеет 8 планет.",
    "расстояние до луны": "Среднее расстояние от Земли до Луны — около 384 400 км.",
    "скорость света": "В вакууме скорость света равна 299 792 458 м/с.",
    "формула эйнштейна": "E = mc² — знаменитая формула эквивалентности массы и энергии.",
    "из чего состоит вода": "Молекула воды H₂O состоит из двух атомов водорода и одного атома кислорода.",
    "температура кипения воды": "При нормальном атмосферном давлении вода кипит примерно при 100 °C.",
    "почему небо голубое": "Главная причина — рэлеевское рассеяние солнечного света в атмосфере; коротковолновая часть видимого света рассеивается сильнее.",
    "что такое гравитация": "Гравитация — фундаментальное взаимодействие, связанное с массой и энергией; в общей теории относительности оно описывается геометрией пространства-времени.",
    "кто первый в космосе": "Юрий Алексеевич Гагарин совершил первый полёт человека в космос 12 апреля 1961 года.",
    "столица россии": "Москва.",
    "столица франции": "Париж.",
    "столица японии": "Токио.",
    "самая большая страна": "Россия — крупнейшее государство мира по площади территории.",
    "самая высокая гора": "Эверест (Джомолунгма) — высочайшая вершина Земли над уровнем моря.",
    "самое глубокое озеро": "Байкал — самое глубокое озеро мира; максимальная глубина составляет около 1642 м.",
    "самое большое животное": "Синий кит — крупнейшее из известных современных животных.",
    "самое быстрое животное": "Сапсан считается самым быстрым животным по скорости пикирования; у него зафиксированы скорости свыше 300 км/ч.",
    "сколько ног у паука": "У взрослых пауков 8 ног.",
    "чем питаются панды": "Большую часть рациона гигантской панды составляет бамбук, хотя биологически это всеядное животное.",
    "что такое фотосинтез": "Фотосинтез — процесс, при котором растения, водоросли и некоторые микроорганизмы используют световую энергию для синтеза органических веществ.",
    "когда началась вторая мировая": "В Европе Вторая мировая война началась 1 сентября 1939 года с нападения Германии на Польшу.",
    "когда закончилась вторая мировая": "Вторая мировая война завершилась в сентябре 1945 года; капитуляция Японии была подписана 2 сентября 1945 года.",
    "кто такой пушкин": "Александр Сергеевич Пушкин — русский поэт, драматург и прозаик, одна из ключевых фигур русской литературы.",
    "год основания москвы": "Традиционно основание Москвы связывают с 1147 годом — первым летописным упоминанием.",
    "число пи": "π ≈ 3.141592653589793.",
    "корень из 144": "√144 = 12.",
    "сколько дней в году": "Обычный год содержит 365 дней, високосный — 366.",
    "расскажи анекдот": "— Почему программист любит тёмную тему?\n— Потому что светлая тема показывает слишком много ошибок. 😸",
}

ALIASES = {
    "что такое искусственный интеллект": "что такое ии",
    "что такое искусственный интелект": "что такое ии",
    "кто ты такой": "кто ты",
    "как тебя зовут": "как тебя зовут",
    "сколько планет": "сколько планет в солнечной системе",
    "планеты солнечной системы": "сколько планет в солнечной системе",
    "луна": "расстояние до луны",
    "скорость света": "скорость света",
    "пи": "число пи",
}


# ------------------------------------------------------------
# Utility / safe math
# ------------------------------------------------------------

class SafeMath:
    BINOPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
    NAMES = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }
    FUNCS = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "abs": abs,
        "round": round,
    }

    @classmethod
    def evaluate_node(cls, node):
        if isinstance(node, ast.Expression):
            return cls.evaluate_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in cls.BINOPS:
            left = cls.evaluate_node(node.left)
            right = cls.evaluate_node(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("слишком большая степень")
            return cls.BINOPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls.UNARY:
            return cls.UNARY[type(node.op)](cls.evaluate_node(node.operand))
        if isinstance(node, ast.Name) and node.id in cls.NAMES:
            return cls.NAMES[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in cls.FUNCS:
            args = [cls.evaluate_node(x) for x in node.args]
            return cls.FUNCS[node.func.id](*args)
        raise ValueError("недопустимое выражение")

    @classmethod
    def solve(cls, text):
        candidate = text.lower().strip()
        candidate = re.sub(r"^(посчитай|вычисли|сколько будет|реши)\s+", "", candidate)
        candidate = candidate.replace("^", "**").replace("×", "*").replace("÷", "/")
        if not re.fullmatch(r"[0-9a-z_+\-*/().,\s%*]+", candidate):
            return None
        if not re.search(r"\d", candidate):
            return None
        candidate = candidate.replace(",", ".")
        try:
            tree = ast.parse(candidate, mode="eval")
            result = cls.evaluate_node(tree)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"🧮 Результат: {result}"
        except Exception:
            return None


# ------------------------------------------------------------
# Search
# ------------------------------------------------------------

class WebSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7",
        })

    def wikipedia(self, query):
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 3,
                "utf8": 1,
            }
            r = self.session.get(WIKI_API, params=params, timeout=7)
            r.raise_for_status()
            results = r.json().get("query", {}).get("search", [])
            if not results:
                return None

            title = results[0]["title"]
            params = {
                "action": "query",
                "prop": "extracts|info",
                "exintro": True,
                "explaintext": True,
                "inprop": "url",
                "titles": title,
                "format": "json",
                "utf8": 1,
            }
            r = self.session.get(WIKI_API, params=params, timeout=7)
            r.raise_for_status()
            pages = r.json().get("query", {}).get("pages", {})
            page = next(iter(pages.values()), {})
            extract = re.sub(r"\s+", " ", page.get("extract", "")).strip()
            if not extract:
                return None
            return {
                "source": "Википедия",
                "title": title,
                "text": extract[:1400],
                "url": page.get("fullurl", ""),
            }
        except Exception:
            return None

    def duckduckgo(self, query):
        try:
            r = self.session.get(
                "https://lite.duckduckgo.com/lite/",
                params={"q": query},
                timeout=8,
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            rows = soup.select("tr")
            snippets = []
            for row in rows:
                text = row.get_text(" ", strip=True)
                if len(text) >= 80 and query.lower().split()[0] in text.lower():
                    snippets.append(text)
                if len(snippets) >= 3:
                    break
            if not snippets:
                return None
            return {
                "source": "DuckDuckGo",
                "title": "Результаты поиска",
                "text": " ".join(snippets)[:1600],
                "url": "",
            }
        except Exception:
            return None


# ------------------------------------------------------------
# Smart engine
# ------------------------------------------------------------

class SmartAnswerEngine:
    def __init__(self):
        self.web = WebSearch()
        self.context = deque(maxlen=8)
        self.learned = {}

    @staticmethod
    def normalize(text):
        text = text.lower().strip()
        text = re.sub(r"[?!.,:;]+$", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def remember(self, query, answer):
        self.context.append({"q": query, "a": answer})

    def context_query(self, query):
        q = self.normalize(query)
        pronouns = (
            "он", "она", "они", "это", "этот", "эта", "там", "тогда",
            "подробнее", "подробней", "расскажи еще", "а почему", "а как",
            "а где", "а когда", "что насчет этого",
        )
        if self.context and any(q.startswith(x) or f" {x}" in q for x in pronouns):
            previous = self.context[-1]["q"]
            return f"{previous}. {query}"
        return None

    def builtin(self, query):
        q = self.normalize(query)
        q = ALIASES.get(q, q)

        if q in BUILTIN_KNOWLEDGE:
            return BUILTIN_KNOWLEDGE[q]

        # Exact key phrase inside a longer request.
        matches = [(k, v) for k, v in BUILTIN_KNOWLEDGE.items() if k in q]
        if matches:
            matches.sort(key=lambda x: len(x[0]), reverse=True)
            return matches[0][1]

        # Lightweight word-overlap retrieval.
        query_words = set(re.findall(r"[а-яёa-z0-9]+", q))
        best = None
        best_score = 0.0
        for key, value in BUILTIN_KNOWLEDGE.items():
            key_words = set(re.findall(r"[а-яёa-z0-9]+", key))
            if not key_words:
                continue
            score = len(query_words & key_words) / len(key_words)
            if score > best_score:
                best_score = score
                best = value
        return best if best_score >= 0.65 else None

    def learn_from_local(self, query):
        q = self.normalize(query)
        if q in self.learned:
            return self.learned[q]
        return None

    def answer(self, query):
        math_answer = SafeMath.solve(query)
        if math_answer:
            self.remember(query, math_answer)
            return math_answer

        q = self.context_query(query) or query

        local = self.learn_from_local(query)
        if local:
            answer = f"🧠 Из локальной памяти:\n{local}"
            self.remember(query, answer)
            return answer

        builtin = self.builtin(q)
        if builtin:
            answer = f"🧠 Из базы знаний:\n{builtin}"
            self.remember(query, answer)
            return answer

        wiki = self.web.wikipedia(q)
        if wiki:
            answer = f"📚 {wiki['title']}\n\n{wiki['text']}"
            self.remember(query, answer)
            return answer

        ddg = self.web.duckduckgo(q)
        if ddg:
            answer = f"🔎 {ddg['title']}\n\n{ddg['text']}"
            self.remember(query, answer)
            return answer

        return None


# ------------------------------------------------------------
# Persistence
# ------------------------------------------------------------

class ChatHistory:
    def __init__(self, path):
        self.path = path
        self.history = []
        self.load()

    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.history = data[-200:]
        except Exception:
            self.history = []

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.history[-200:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add(self, role, content):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
        })
        self.history = self.history[-200:]
        self.save()

    def clear(self):
        self.history = []
        self.save()


# ------------------------------------------------------------
# Main UI
# ------------------------------------------------------------

class MeowAIApp:
    BG = "#0b0f14"
    PANEL = "#111821"
    PANEL2 = "#151e29"
    INPUT = "#0f1720"
    TEXT = "#e8eef7"
    MUTED = "#7f8b9b"
    ACCENT = "#ffd166"
    ACCENT2 = "#67e8f9"
    GREEN = "#62e884"
    RED = "#ff6b6b"
    BORDER = "#243141"

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {CURRENT_VERSION}")
        self.root.geometry("1050x720")
        self.root.minsize(800, 580)
        self.root.configure(bg=self.BG)

        os.makedirs(DB_DIR, exist_ok=True)

        self.engine = SmartAnswerEngine()
        self.history = ChatHistory(CHAT_HISTORY_FILE)
        self.local_db = self.load_db()

        self.font_ui = ("Segoe UI", 10)
        self.font_body = ("Segoe UI", 11)
        self.font_small = ("Segoe UI", 9)
        self.font_title = ("Segoe UI Semibold", 18)

        self.setup_ui()
        self.load_history_to_ui()
        self.show_welcome()

    def load_db(self):
        try:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
        except Exception:
            pass
        return {}

    def save_db(self):
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.local_db, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.PANEL, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=self.PANEL)
        brand.pack(side="left", padx=22)

        tk.Label(
            brand, text="🐱", bg=self.PANEL, fg=self.ACCENT,
            font=("Segoe UI Emoji", 25)
        ).pack(side="left", padx=(0, 10))

        title_box = tk.Frame(brand, bg=self.PANEL)
        title_box.pack(side="left", pady=8)
        tk.Label(
            title_box, text="MeowAI", bg=self.PANEL, fg=self.TEXT,
            font=self.font_title
        ).pack(anchor="w")
        tk.Label(
            title_box, text=f"SMART ASSISTANT  •  v{CURRENT_VERSION}",
            bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        self.status = tk.Label(
            header, text="● ONLINE", bg=self.PANEL, fg=self.GREEN,
            font=("Segoe UI", 9, "bold")
        )
        self.status.pack(side="right", padx=24)

        # Main
        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=16, pady=14)

        # Side panel
        side = tk.Frame(
            main, bg=self.PANEL, width=205,
            highlightbackground=self.BORDER, highlightthickness=1
        )
        side.pack(side="left", fill="y", padx=(0, 12))
        side.pack_propagate(False)

        tk.Label(
            side, text="ВОЗМОЖНОСТИ", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=16, pady=(18, 10))

        features = [
            ("🧠", "База знаний"),
            ("🔎", "Веб-поиск"),
            ("🧮", "Математика"),
            ("💬", "Контекст"),
            ("💾", "Память"),
            ("🕒", "Дата и время"),
        ]
        for icon, text in features:
            row = tk.Frame(side, bg=self.PANEL)
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(row, text=icon, bg=self.PANEL, fg=self.TEXT,
                     font=("Segoe UI Emoji", 12)).pack(side="left", padx=6, pady=5)
            tk.Label(row, text=text, bg=self.PANEL, fg=self.TEXT,
                     font=self.font_ui).pack(side="left")

        tk.Label(
            side, text="БЫСТРЫЕ КОМАНДЫ", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=16, pady=(22, 8))

        for label, command in [
            ("🧹 Очистить чат", self.clear_chat),
            ("🕒 Текущее время", lambda: self.ask("который сейчас час")),
            ("🧮 Калькулятор", lambda: self.ask("2 + 2 * 10")),
            ("🔄 Проверить обновления", self.check_updates),
        ]:
            self.side_button(side, label, command)

        # Chat area
        center = tk.Frame(main, bg=self.BG)
        center.pack(side="left", fill="both", expand=True)

        chat_panel = tk.Frame(
            center, bg=self.PANEL,
            highlightbackground=self.BORDER, highlightthickness=1
        )
        chat_panel.pack(fill="both", expand=True)

        self.chat = scrolledtext.ScrolledText(
            chat_panel, wrap=tk.WORD,
            bg=self.PANEL, fg=self.TEXT,
            insertbackground=self.TEXT,
            selectbackground="#30445a",
            relief="flat", borderwidth=0,
            padx=22, pady=18,
            font=self.font_body
        )
        self.chat.pack(fill="both", expand=True)
        self.chat.configure(state="disabled")

        self.chat.tag_config("user_name", foreground=self.ACCENT2,
                             font=("Segoe UI Semibold", 10))
        self.chat.tag_config("ai_name", foreground=self.ACCENT,
                             font=("Segoe UI Semibold", 10))
        self.chat.tag_config("system", foreground=self.MUTED,
                             font=self.font_small)
        self.chat.tag_config("body", foreground=self.TEXT, font=self.font_body)
        self.chat.tag_config("error", foreground=self.RED, font=self.font_body)
        self.chat.tag_config("divider", foreground=self.BORDER)

        # Composer
        composer = tk.Frame(center, bg=self.BG)
        composer.pack(fill="x", pady=(10, 0))

        input_panel = tk.Frame(
            composer, bg=self.INPUT,
            highlightbackground=self.BORDER, highlightthickness=1
        )
        input_panel.pack(fill="x")

        self.input = tk.Text(
            input_panel, height=3, wrap=tk.WORD,
            bg=self.INPUT, fg=self.TEXT,
            insertbackground=self.ACCENT,
            relief="flat", borderwidth=0,
            padx=14, pady=12, font=self.font_body
        )
        self.input.pack(side="left", fill="both", expand=True)
        self.input.bind("<Return>", self.on_enter)

        send = tk.Button(
            input_panel, text="➤", command=self.send,
            bg=self.ACCENT, fg="#17120a",
            activebackground="#ffe39a", activeforeground="#17120a",
            relief="flat", borderwidth=0,
            font=("Segoe UI", 16, "bold"),
            cursor="hand2", width=4
        )
        send.pack(side="right", padx=8, pady=8, fill="y")

        tk.Label(
            composer,
            text="Enter — отправить   •   Ctrl+Enter — новая строка   •   Ответы сохраняются локально",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(5, 0))

    def side_button(self, parent, text, command):
        btn = tk.Button(
            parent, text=text, command=command,
            anchor="w", bg=self.PANEL2, fg=self.TEXT,
            activebackground="#223143", activeforeground=self.ACCENT,
            relief="flat", borderwidth=0,
            font=self.font_small, cursor="hand2",
            padx=10, pady=7
        )
        btn.pack(fill="x", padx=10, pady=2)

    def write(self, sender, text, kind="ai"):
        self.chat.configure(state="normal")
        if sender == "Ты":
            self.chat.insert("end", "YOU  ", "user_name")
        elif sender == "MeowAI":
            self.chat.insert("end", "MEOWAI  ", "ai_name")
        else:
            self.chat.insert("end", "SYSTEM  ", "system")
        self.chat.insert("end", text + "\n", "body" if kind != "error" else "error")
        self.chat.insert("end", "────────────────────────────────────────\n", "divider")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def show_welcome(self):
        if not self.history.history:
            self.write(
                "MeowAI",
                "Привет! Я MeowAI 2.0 🐱\n\n"
                "Я стал умнее: лучше ищу знания, понимаю короткие продолжения диалога, "
                "умею считать выражения и сохраняю историю.\n\n"
                "Попробуй: «что такое нейросеть», «кто такой Гагарин», "
                "«sqrt(144) + 5» или «расскажи подробнее».",
            )

    def load_history_to_ui(self):
        if not self.history.history:
            return
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        for item in self.history.history[-30:]:
            sender = "Ты" if item.get("role") == "user" else "MeowAI"
            self.write(sender, item.get("content", ""))

    def on_enter(self, event):
        if event.state & 0x4:
            return
        self.send()
        return "break"

    def ask(self, text):
        self.input.delete("1.0", "end")
        self.input.insert("1.0", text)
        self.send()

    def send(self):
        query = self.input.get("1.0", "end").strip()
        if not query:
            return

        self.input.delete("1.0", "end")
        self.write("Ты", query)
        self.history.add("user", query)

        low = query.lower().strip()
        if low in {"выход", "exit", "quit"}:
            self.write("MeowAI", "До встречи! 🐱")
            self.root.after(600, self.root.destroy)
            return

        if low in {"очистить", "clear", "очистить чат"}:
            self.clear_chat()
            return

        if low in {"время", "который час", "который сейчас час", "дата", "сегодня"}:
            now = dt.datetime.now()
            answer = f"🕒 Сейчас {now:%H:%M:%S}, {now:%d.%m.%Y}."
            self.write("MeowAI", answer)
            self.history.add("assistant", answer)
            return

        self.status.configure(text="● THINKING...", fg=self.ACCENT)
        self.write("MeowAI", "🤔 Анализирую запрос…")
        threading.Thread(target=self.process, args=(query,), daemon=True).start()

    def process(self, query):
        try:
            # Remove temporary thinking line by leaving it as a visible activity record.
            answer = self.engine.answer(query)

            if answer:
                # Save useful answers for later local retrieval.
                key = SmartAnswerEngine.normalize(query)
                self.local_db[key] = answer
                if len(self.local_db) > 300:
                    self.local_db = dict(list(self.local_db.items())[-300:])
                self.save_db()

                self.root.after(0, lambda: self.finish_answer(answer))
            else:
                fallback = (
                    "Я пока не нашёл достаточно уверенного ответа.\n\n"
                    "Попробуй уточнить тему, добавить имя/термин или задать вопрос "
                    "другими словами."
                )
                self.root.after(0, lambda: self.finish_answer(fallback))
        except Exception as exc:
            traceback.print_exc()
            self.root.after(
                0,
                lambda: self.finish_answer(f"❌ Ошибка обработки: {exc}", error=True)
            )

    def finish_answer(self, answer, error=False):
        self.write("MeowAI", answer, "error" if error else "ai")
        self.history.add("assistant", answer)
        self.status.configure(text="● ONLINE", fg=self.GREEN)

    def clear_chat(self):
        self.history.clear()
        self.engine.context.clear()
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.write("MeowAI", "Чат очищен. Готов к новому разговору. 🐱")

    def check_updates(self):
        self.status.configure(text="● CHECKING...", fg=self.ACCENT)
        self.write("SYSTEM", "Проверяю последнюю версию на GitHub…")
        threading.Thread(target=self._update_thread, daemon=True).start()

    def _update_thread(self):
        try:
            r = requests.get(
                "https://api.github.com/repos/matvey2222222222/MeowAI/releases",
                headers={"Accept": "application/vnd.github+json"},
                timeout=8,
            )
            r.raise_for_status()
            releases = r.json()
            if not releases:
                result = "На GitHub пока нет опубликованных релизов."
            else:
                latest = releases[0]
                tag = latest.get("tag_name", "unknown")
                url = latest.get("html_url", GITHUB_REPO_URL)
                result = f"Последний релиз: {tag}\n{url}"
        except Exception as exc:
            result = f"Не удалось проверить GitHub: {exc}"

        self.root.after(0, lambda: self._update_done(result))

    def _update_done(self, result):
        self.status.configure(text="● ONLINE", fg=self.GREEN)
        self.write("SYSTEM", result)


def main():
    root = tk.Tk()
    app = MeowAIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
