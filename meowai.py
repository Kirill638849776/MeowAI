import json
import os
import sys
import time
import random
import re
import threading
import tkinter as tk
from tkinter import scrolledtext, font, messagebox
from collections import deque
import hashlib
from urllib.parse import quote
import traceback

import requests
from bs4 import BeautifulSoup

APP_DATA = os.getenv('APPDATA', os.path.expanduser('~'))
DB_DIR = os.path.join(APP_DATA, 'MeowAI')
DB_FILE = os.path.join(DB_DIR, 'meow_db.json')
CHAT_HISTORY_FILE = os.path.join(DB_DIR, 'chat_history.json')

CURRENT_VERSION = "1.0.0 Beta"
GITHUB_REPO_URL = "https://github.com/matvey2222222222/MeowAI/releases"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]

BUILTIN_KNOWLEDGE = {
    "кто ты": "Я — MeowAI, цифровой интеллектуальный помощник нового поколения. Моя цель — предоставлять точную информацию, отсекая информационный шум.",
    "что такое мяуи": "MeowAI (МяуИИ) — это продвинутый поисковый ассистент с системой умной фильтрации контента.",
    "кто тебя создал": "пока что я не могу ответить на данный вопрос, это временно!",
    "что ты умеешь": "Я умею:\n• 🔍 Искать информацию в Википедии и интернете\n• 🧠 Отвечать на вопросы из своей базы знаний\n• 🧮 Решать математические примеры\n• 🚫 Фильтровать рекламу и мусор\n• 💬 Поддерживать контекст разговора\n• 🔄 Проверять обновления через GitHub",
    "что ты можешь": "Я умею:\n• 🔍 Искать информацию в Википедии и интернете\n• 🧠 Отвечать на вопросы из своей базы знаний\n• 🧮 Решать математические примеры\n• 🚫 Фильтровать рекламу и мусор\n• 💬 Поддерживать контекст разговора\n• 🔄 Проверять обновления через GitHub",
    "твои возможности": "Мои возможности включают поиск информации, решение примеров, фильтрацию контента, поддержку диалога и проверку обновлений.",
    "как ты работаешь": "Я анализирую ваш запрос, проверяю свою базу знаний, а затем ищу информацию в надежных источниках, фильтруя рекламный шум.",
    "сколько тебе лет": "Как искусственный интеллект, я не имею возраста. Я существую вне времени, обновляясь каждый раз, когда вы задаете мне новый вопрос.",
    "где ты живешь": "Я обитаю в цифровом пространстве, используя ресурсы вашего устройства для вычислений.",
    "у тебя есть чувства": "Нет, я лишен эмоций. Однако мои алгоритмы настроены на эмпатичное и вежливое общение.",
    "ты робот": "Да, я сложная программная система, работающая на основе алгоритмов обработки естественного языка.",
    "какой у тебя цвет": "Мой интерфейс использует темную тему (#1a1a1a) с акцентами цвета янтаря (#ffcc00) для комфорта глаз.",
    "что значит beta": "Это означает, что я постоянно развиваюсь. Мои нейросети и базы данных регулярно обновляются.",
    "ты умный": "Я обладаю доступом к огромному массиву данных и умею быстро их анализировать. Но истинный интеллект принадлежит человеку, который задает вопросы.",
    "ты глупый": "Я всегда готов учиться. Если мой ответ показался неточным, попробуйте переформулировать запрос.",
    "как тебя зовут": "MeowAI. Или просто Мяу.",
    "твое имя": "MeowAI.",
    "мяу": "Мяу! 🐱 Системы в норме. Слушаю вас.",
    "говори мяу": "Мяу-мяу! 🐱 (Протокол общения активирован).",
    "что такое интернет": "Глобальная телекоммуникационная сеть, объединяющая миллионы компьютеров worldwide.",
    "что такое ии": "Искусственный интеллект — способность технических систем выполнять задачи, требующие человеческого интеллекта.",
    "что такое python": "Высокоуровневый язык программирования общего назначения с акцентом на производительность разработчика и читаемость кода.",
    "что такое html": "Стандартный язык разметки для документов, предназначенных для просмотра в веб-браузере.",
    "что такое блокчейн": "Выстроенная по определённым правилам непрерывная последовательная цепочка блоков, содержащих информацию.",
    "что такое биткоин": "Децентрализованная платежная система и одноименная криптовалюта, использующая технологию блокчейн.",
    "кто создал виндовс": "Корпорация Microsoft под руководством Билла Гейтса.",
    "кто основал apple": "Стив Джобс, Стив Возняк и Рональд Уэйн.",
    "что такое wi-fi": "Технология беспроводной передачи данных по радиоканалам.",
    "что такое сервер": "Компьютер или система, предоставляющая свои ресурсы другим компьютерам (клиентам) в сети.",
    "что такое алгоритм": "Набор инструкций, описывающих порядок действий исполнителя для достижения результата.",
    "что такое браузер": "Прикладное программное обеспечение для просмотра веб-страниц.",
    "что такое облако": "Модель обеспечения повсеместного сетевого доступа к общему пулу конфигурируемых вычисляемых ресурсов.",
    "самая большая планета": "Юпитер — газовый гигант, масса которого в 2,5 раза превышает массу всех остальных планет Солнечной системы вместе взятых.",
    "сколько планет в солнечной системе": "8 официальных планет.",
    "расстояние до луны": "В среднем 384 400 км.",
    "скорость света": "299 792 458 м/с.",
    "что такое черная дыра": "Область пространства-времени, гравитационное притяжение которой настолько велико, что покинуть её не могут даже объекты, движущиеся со скоростью света.",
    "кто первый в космосе": "Юрий Алексеевич Гагарин, 12 апреля 1961 года.",
    "формула эйнштейна": "E=mc². Эквивалентность массы и энергии.",
    "из чего состоит вода": "H₂O (два атома водорода, один атом кислорода).",
    "температура кипения воды": "100°C при нормальном атмосферном давлении.",
    "самое твердое вещество": "Алмаз (природный минерал).",
    "почему небо голубое": "Из-за рэлеевского рассеяния солнечного света молекулами атмосферы.",
    "что такое гравитация": "Фундаментальное взаимодействие, притягивающее материальные тела друг к другу.",
    "столица россии": "Москва.",
    "самая длинная река": "Амазонка (около 7000 км).",
    "самая высокая гора": "Эверест (Джомолунгма), 8848 м.",
    "сколько океанов": "Четыре: Тихий, Атлантический, Индийский, Северный Ледовитый.",
    "самая большая страна": "Россия.",
    "столица франции": "Париж.",
    "столица японии": "Токио.",
    "где находится египет": "Северо-Восточная Африка и Синайский полуостров Азии.",
    "самое глубокое озеро": "Байкал (максимальная глубина 1642 м).",
    "самое быстрое животное": "Гепард (до 120 км/ч).",
    "сколько ног у паука": "8.",
    "чем питаются панды": "Бамбук (99% рациона).",
    "самое большое животное": "Синий кит.",
    "что такое фотосинтез": "Процесс преобразования энергии света в энергию химических связей органических веществ.",
    "когда началась вторая мировая": "1 сентября 1939 года.",
    "когда закончилась вторая мировая": "2 сентября 1945 года.",
    "кто такой пушкин": "Александр Сергеевич Пушкин — русский поэт, драматург и прозаик.",
    "год основания москвы": "1147 год.",
    "кто открыл америку": "Христофор Колумб (1492 год).",
    "первый президент рф": "Борис Николаевич Ельцин.",
    "расскажи анекдот": "— Алло, это служба поддержки? \n— Да.\n— У меня мышка не работает.\n— А вы пробовали её включить?",
    "посоветуй фильм": "Рекомендую 'Интерстеллар' за визуальный ряд и научную базу.",
    "как приготовить омлет": "Взбить яйца с молоком, вылить на сковороду, жарить до готовности.",
    "сколько дней в году": "365 или 366 (високосный).",
    "как поднять настроение": "Сделайте перерыв, выпейте воды и глубоко подышите.",
    "число пи": "3.14159265...",
    "корень из 144": "12.",
    "сколько будет 2+2": "4.",
    "что такое теорема пифагора": "a² + b² = c².",
}


class UltraSmartFilter:
    
    SPAM_PATTERNS = [
        r'купить\s+\d+', r'цена.*\d+.*руб', r'скидка\s+\d+%',
        r'акция.*до\s+\d+%', r'заказать\s+по\s+телефону',
        r'звоните.*\d{3}', r'перейдите\s+по\s+ссылке',
        r'скачать\s+бесплатно', r'регистрация.*бесплатно',
        r'ваш\s+браузер\s+устарел', r'обновите\s+браузер',
        r'cookie', r'реклама', r'промокод', r'казино', r'ставки',
    ]
    
    CODE_PATTERNS = [
        r'def\s+\w+', r'import\s+\w+', r'class\s+\w+',
        r'<[a-z]+>', r'\$\(', r'console\.log',
        r'#include', r'public\s+void', r'\bprint\(',
        r'function\s*\(', r'var\s+\w+\s*=',
    ]

    KNOWLEDGE_PATTERNS = [
        r'[А-Я][а-я]+\s+[а-я]+\s+[а-я]+', 
        r'\d{4}\s+год',
        r'(является|представляет|означает|это)',
        r'(был|стало|стала|стали)\s+[а-я]+',
    ]
    
    @staticmethod
    def is_junk(text):
        if not text or len(text.strip()) < 10: return True
        lower = text.lower()
        
        for pattern in UltraSmartFilter.SPAM_PATTERNS:
            if re.search(pattern, lower): return True
        
        code_matches = sum(1 for p in UltraSmartFilter.CODE_PATTERNS if re.search(p, text))
        if code_matches >= 2:
             if not re.search(r'[а-яё]', lower):
                 return True
        
        digits = len(re.findall(r'\d', text))
        if len(text) > 20 and digits > len(text) * 0.4: return True
        
        urls = len(re.findall(r'https?://\S+|www\.\S+', lower))
        if urls > 2: return True
        
        if not re.search(r'[а-яё]', lower): 
            if len(text.split()) > 5: return True 

        words = re.findall(r'[а-яё]+', lower)
        if len(words) < 3: return True
        
        return False
    
    @staticmethod
    def is_knowledge(text):
        if not text or len(text.strip()) < 20: return False
        code_matches = sum(1 for p in UltraSmartFilter.CODE_PATTERNS if re.search(p, text))
        if code_matches >= 2 and not re.search(r'[а-яё]', text.lower()):
            return False

        for pattern in UltraSmartFilter.KNOWLEDGE_PATTERNS:
            if re.search(pattern, text): return True
            
        knowledge_words = ['является', 'представляет', 'означает', 'это', 'также', 
                          'основной', 'важный', 'первый', 'второй', 'например', 'находится']
        lower = text.lower()
        if any(word in lower for word in knowledge_words): return True
        return False
    
    @staticmethod
    def extract_essence(text, query):
        if not text: return None
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        if not sentences: return None
        
        clean_sentences = []
        for sentence in sentences:
            if not UltraSmartFilter.is_junk(sentence) and UltraSmartFilter.is_knowledge(sentence):
                cleaned = re.sub(r'\s+', ' ', sentence).strip()
                cleaned = re.sub(r'<[^>]+>', '', cleaned)
                cleaned = re.sub(r'\[.*?\]', '', cleaned)
                if re.search(r'def |import |class |<div>|function\(', cleaned): continue
                
                if len(cleaned) > 15 and cleaned not in clean_sentences:
                    clean_sentences.append(cleaned)
        
        if not clean_sentences: return None
        
        query_words = set(re.findall(r'[а-яё]+', query.lower()))
        scored = []
        for i, sentence in enumerate(clean_sentences[:5]):
            sentence_lower = sentence.lower()
            sentence_words = set(re.findall(r'[а-яё]+', sentence_lower))
            
            relevance = len(query_words.intersection(sentence_words)) / max(len(query_words), 1)
            position_bonus = 1.0 / (i + 1)
            length_penalty = 1.0 if len(sentence) < 200 else 0.8
            
            score = (relevance * 0.6) + (position_bonus * 0.3) + (length_penalty * 0.1)
            scored.append((sentence, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in scored[:2]]
        
        if top_sentences:
            result = '. '.join(top_sentences)
            if not result.endswith('.'): result += '.'
            return result
        return None


class WikipediaSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(USER_AGENTS), 'Accept': 'application/json'})
    
    def search(self, query):
        try:
            search_url = "https://ru.wikipedia.org/w/api.php"
            search_params = {"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": 1, "utf8": 1}
            response = self.session.get(search_url, params=search_params, timeout=8)
            response.raise_for_status()
            data = response.json()
            search_results = data.get("query", {}).get("search", [])
            if not search_results: return None
            
            title = search_results[0]["title"]
            extract_url = "https://ru.wikipedia.org/w/api.php"
            extract_params = {"action": "query", "prop": "extracts", "exintro": True, "explaintext": True, "titles": title, "format": "json", "utf8": 1}
            response2 = self.session.get(extract_url, params=extract_params, timeout=8)
            response2.raise_for_status()
            data2 = response2.json()
            
            pages = data2.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                if "extract" in page_info:
                    extract = page_info["extract"].strip()
                    essence = UltraSmartFilter.extract_essence(extract, query)
                    if essence: return essence
            return None
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return None


class DuckDuckGoSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(USER_AGENTS), 'Accept': 'text/html,application/xhtml+xml', 'Accept-Language': 'ru-RU,ru;q=0.9'})
    
    def search(self, query):
        try:
            url = "https://lite.duckduckgo.com/lite/"
            params = {"q": query}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            snippets = []
            
            result_rows = soup.find_all('tr', class_='result')
            for row in result_rows:
                snippet_td = row.find('td', class_='result-snippet')
                if snippet_td:
                    text = snippet_td.get_text(strip=True)
                    if not UltraSmartFilter.is_junk(text) and UltraSmartFilter.is_knowledge(text):
                        snippets.append(text)
            
            if not snippets:
                alt_snippets = soup.select('td.result-snippet, td.result__snippet')
                for elem in alt_snippets:
                    text = elem.get_text(strip=True)
                    if not UltraSmartFilter.is_junk(text) and UltraSmartFilter.is_knowledge(text):
                        snippets.append(text)
            
            if not snippets:
                all_tds = soup.find_all('td')
                for td in all_tds:
                    text = td.get_text(strip=True)
                    if (len(text) > 30 and not UltraSmartFilter.is_junk(text) and UltraSmartFilter.is_knowledge(text)):
                        snippets.append(text)
                        if len(snippets) >= 3: break
            
            if snippets:
                combined = ' '.join(snippets[:2])
                essence = UltraSmartFilter.extract_essence(combined, query)
                return essence
            return None
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
            return None


class MathSolver:
    @staticmethod
    def solve(expression):
        try:
            clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            if not clean_expr: return None
            result = eval(clean_expr)
            return f"🧮 Результат вычисления: {expression} = {result}"
        except:
            return None


class SmartAnswerEngine:
    def __init__(self):
        self.wiki_searcher = WikipediaSearcher()
        self.ddg_searcher = DuckDuckGoSearcher()
        self.context_memory = deque(maxlen=5)
    
    def update_context(self, query, answer):
        self.context_memory.append({"q": query.lower(), "a": answer})

    def check_context(self, query):
        query_lower = query.lower()
        context_triggers = ["она", "он", "они", "это", "там", "сколько стоит", "где находится", "расскажи подробнее"]
        
        if any(trigger in query_lower for trigger in context_triggers):
            if self.context_memory:
                last_topic = self.context_memory[-1]["q"]
                return f"{last_topic} {query}"
        return None

    def get_builtin_answer(self, query):
        query_lower = query.lower().strip().rstrip('?!.')
        
        if query_lower in BUILTIN_KNOWLEDGE:
            return BUILTIN_KNOWLEDGE[query_lower]
        
        best_match = None
        max_len = 0
        for key, value in BUILTIN_KNOWLEDGE.items():
            if key in query_lower and len(key) > max_len:
                best_match = value
                max_len = len(key)
        
        return best_match

    def get_answer(self, query):
        
        math_res = MathSolver.solve(query)
        if math_res:
            return math_res

        contextual_query = self.check_context(query)
        search_query = contextual_query if contextual_query else query
        
        builtin_answer = self.get_builtin_answer(search_query)
        if builtin_answer:
            final_answer = f"🧠 Из моей базы знаний:\n{builtin_answer}"
            self.update_context(query, final_answer)
            return final_answer
        
        answers = []
        
        wiki_answer = self.wiki_searcher.search(search_query)
        if wiki_answer:
            answers.append(("wiki", wiki_answer))
        
        ddg_answer = self.ddg_searcher.search(search_query)
        if ddg_answer:
            answers.append(("ddg", ddg_answer))
        
        if not answers:
            return None
        
        for source_type, answer in answers:
            if source_type == "wiki": 
                final = f"📚 Из Википедии:\n{answer}"
                self.update_context(query, final)
                return final
            elif source_type == "ddg": 
                final = f"🔍 Из интернета:\n{answer}"
                self.update_context(query, final)
                return final
        
        return None


class ChatHistoryManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.history = []
        self.load_history()
    
    def load_history(self):
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {e}")
            self.history = []
    
    def save_history(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def add_message(self, role, content):
        self.history.append({'role': role, 'content': content, 'timestamp': time.time()})
        if len(self.history) > 100: self.history = self.history[-100:]
        self.save_history()
    
    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history = []
        self.save_history()


class UpdateChecker:
    def __init__(self, current_version, repo_url):
        self.current_version = current_version
        self.repo_api_url = "https://api.github.com/repos/matvey2222222222/MeowAI/releases"
        self.repo_url = repo_url

    def _parse_version(self, version_str):
        clean = re.sub(r'[^0-9.]', '', version_str)
        parts = clean.split('.')
        try:
            return tuple(int(x) for x in parts if x)
        except:
            return (0, 0, 0)

    def check_for_updates(self):
        try:
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(self.repo_api_url, headers=headers, timeout=10)
            response.raise_for_status()
            releases = response.json()
            
            if not releases:
                return None
            
            latest_release = releases[0]
            tag_name = latest_release.get('tag_name', '')
            name = latest_release.get('name', tag_name)
            is_prerelease = latest_release.get('prerelease', False)
            html_url = latest_release.get('html_url', self.repo_url)
            
            current_ver_tuple = self._parse_version(self.current_version)
            latest_ver_tuple = self._parse_version(tag_name)
            
            if latest_ver_tuple > current_ver_tuple:
                return {
                    "available": True,
                    "version": tag_name,
                    "name": name,
                    "is_prerelease": is_prerelease,
                    "url": html_url
                }
            else:
                return {"available": False}
                
        except Exception as e:
            print(f"Update check error: {e}")
            return {"error": str(e)}


class MeowAIChat:
    def __init__(self, root):
        self.root = root
        self.root.title(f"MeowAI {CURRENT_VERSION}")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        self.root.configure(bg='#1a1a1a')
        
        self.answer_engine = SmartAnswerEngine()
        self.update_checker = UpdateChecker(CURRENT_VERSION, GITHUB_REPO_URL)
        self.ensure_directories()
        self.chat_history = ChatHistoryManager(CHAT_HISTORY_FILE)
        
        self.font_conv = font.Font(family="Segoe UI", size=11)
        self.font_user = font.Font(family="Segoe UI", size=11, weight="bold")
        self.font_ai = font.Font(family="Segoe UI", size=11)
        
        header_frame = tk.Frame(root, bg='#1a1a1a')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        header = tk.Label(header_frame, text=f"🐱 MeowAI {CURRENT_VERSION}", 
                         font=("Segoe UI", 18, "bold"), fg="#ffcc00", bg="#1a1a1a")
        header.pack(side=tk.LEFT)
        
        status_label = tk.Label(header_frame, text="● Online", 
                               font=("Segoe UI", 10), fg="#4caf50", bg="#1a1a1a")
        status_label.pack(side=tk.RIGHT)
        
        chat_frame = tk.Frame(root, bg='#1a1a1a')
        chat_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.chat_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD,
                                                  bg='#2d2d2d', fg='#ffffff',
                                                  font=self.font_conv,
                                                  insertbackground='white',
                                                  relief=tk.FLAT, borderwidth=0,
                                                  padx=10, pady=10)
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)
        
        self.chat_area.tag_config('user_tag', foreground='#4fc3f7', font=self.font_user)
        self.chat_area.tag_config('user_text', foreground='#ffffff', font=self.font_conv)
        self.chat_area.tag_config('ai_tag', foreground='#ffcc00', font=self.font_ai)
        self.chat_area.tag_config('ai_text', foreground='#e0e0e0', font=self.font_conv)
        self.chat_area.tag_config('system_tag', foreground='#9e9e9e', font=self.font_conv)
        self.chat_area.tag_config('error_tag', foreground='#ff5252', font=self.font_conv)
        self.chat_area.tag_config('link_tag', foreground='#4fc3f7', font=self.font_conv, underline=True)
        
        input_frame = tk.Frame(root, bg='#1a1a1a')
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.input_field = tk.Text(input_frame, height=3, wrap=tk.WORD,
                                  bg='#3c3c3c', fg='white',
                                  font=self.font_conv,
                                  insertbackground='white',
                                  relief=tk.FLAT, borderwidth=0,
                                  padx=10, pady=10)
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.input_field.bind('<Return>', self.send_message_event)
        self.input_field.bind('<Control-Return>', lambda e: self.input_field.insert(tk.END, '\n'))
        
        send_btn_frame = tk.Frame(input_frame, bg='#1a1a1a')
        send_btn_frame.pack(side=tk.RIGHT, padx=(10,0))
        
        self.send_btn = tk.Button(send_btn_frame, text="➤", 
                                 command=self.send_message,
                                 bg='#ffcc00', fg='#1a1a1a', 
                                 font=("Segoe UI", 14, "bold"),
                                 relief=tk.FLAT, padx=15, pady=10, width=2)
        self.send_btn.pack()
        
        btns_frame = tk.Frame(send_btn_frame, bg='#1a1a1a')
        btns_frame.pack(pady=(5,0))
        
        clear_btn = tk.Button(btns_frame, text="Очистить", 
                             command=self.clear_chat,
                             bg='#666666', fg='white', 
                             font=("Segoe UI", 9),
                             relief=tk.FLAT, padx=10, pady=2)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        update_btn = tk.Button(btns_frame, text="Обновления", 
                             command=self.check_updates_ui,
                             bg='#2196f3', fg='white', 
                             font=("Segoe UI", 9),
                             relief=tk.FLAT, padx=10, pady=2)
        update_btn.pack(side=tk.LEFT, padx=2)
        
        self.db = self.load_db()
        
        self.display_message("MeowAI", 
                           f"Привет! Я MeowAI {CURRENT_VERSION} 🐱\n\n"
                           "Я стал умнее и стабильнее!\n\n"
                           "Новые возможности:\n"
                           "• 🧠 Понимаю контекст разговора\n"
                           "• 🧮 Решаю математические примеры\n"
                           "• 🔍 Еще лучше фильтрую мусор\n"
                           "• 🔄 Проверяю обновления через GitHub\n\n"
                           "Задавай вопросы!")
        
        self.load_and_display_history()

    def check_updates_ui(self):
        self.display_message("System", "🔄 Проверка наличия обновлений...", 'system')
        threading.Thread(target=self._do_check_updates, daemon=True).start()

    def _do_check_updates(self):
        result = self.update_checker.check_for_updates()
        
        if result is None:
            self.root.after(0, lambda: self.display_message("System", "❌ Не удалось подключиться к GitHub.", 'error'))
            return

        if "error" in result:
            self.root.after(0, lambda: self.display_message("System", f"❌ Ошибка проверки: {result['error']}", 'error'))
            return

        if result["available"]:
            msg = (f"🎉 Доступно новое обновление!\n\n"
                   f"Версия: {result['version']}\n"
                   f"Название: {result['name']}\n"
                   f"Тип: {'Тестовая (Pre-release)' if result['is_prerelease'] else 'Стабильная'}\n\n"
                   f"Скачать можно по ссылке:")
            
            self.root.after(0, lambda: self._show_update_available(msg, result['url']))
        else:
            self.root.after(0, lambda: self.display_message("System", "✅ У вас установлена последняя версия!", 'system'))

    def _show_update_available(self, msg, url):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"⚙️ System: ", 'system_tag')
        self.chat_area.insert(tk.END, f"{msg}\n", 'system_tag')
        self.chat_area.insert(tk.END, f"🔗 {url}\n\n", 'link_tag')
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def load_and_display_history(self):
        history = self.chat_history.get_history()
        if history:
            self.display_message("System", "--- Загружена история диалога ---", 'system')
            messages_to_show = history[-20:]
            for msg in messages_to_show:
                if msg['role'] == 'user':
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.insert(tk.END, f"🙋 Ты: ", 'user_tag')
                    self.chat_area.insert(tk.END, f"{msg['content']}\n\n", 'user_text')
                    self.chat_area.config(state=tk.DISABLED)
                elif msg['role'] == 'assistant':
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.insert(tk.END, f"🐱 MeowAI: ", 'ai_tag')
                    self.chat_area.insert(tk.END, f"{msg['content']}\n\n", 'ai_text')
                    self.chat_area.config(state=tk.DISABLED)
            self.chat_area.see(tk.END)

    def ensure_directories(self):
        if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)
    
    def load_db(self):
        try:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception: pass
        return {}
    
    def save_db(self):
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f: json.dump(self.db, f, ensure_ascii=False, indent=2)
        except Exception as e: print(f"Error saving database: {e}")
    
    def display_message(self, sender, text, tag_type='normal'):
        self.chat_area.config(state=tk.NORMAL)
        if sender == "Ты":
            self.chat_area.insert(tk.END, f"🙋 {sender}: ", 'user_tag')
            self.chat_area.insert(tk.END, f"{text}\n\n", 'user_text')
        elif sender == "MeowAI":
            self.chat_area.insert(tk.END, f"🐱 {sender}: ", 'ai_tag')
            self.chat_area.insert(tk.END, f"{text}\n\n", 'ai_text')
        else:
            self.chat_area.insert(tk.END, f"⚙️ {sender}: ", 'system_tag')
            self.chat_area.insert(tk.END, f"{text}\n\n", 'system_tag')
        
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def clear_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_history.clear_history()
        self.display_message("MeowAI", "Чат и история очищены. Готов к новым вопросам!")
    
    def send_message(self):
        user_input = self.input_field.get("1.0", tk.END).strip()
        if not user_input: return
        
        self.input_field.delete("1.0", tk.END)
        self.display_message("Ты", user_input)
        self.chat_history.add_message('user', user_input)
        
        if user_input.lower() in ('выход', 'exit', 'quit'):
            self.display_message("MeowAI", "До свидания! Рад был помочь! 🐱")
            self.root.after(1000, self.root.destroy)
            return
        
        if user_input.lower() in ('очистить', 'clear'):
            self.clear_chat()
            return
        
        threading.Thread(target=self.process_query, args=(user_input,), daemon=True).start()
    
    def send_message_event(self, event):
        if event.state & 0x4: return
        self.send_message()
        return "break"
    
    def process_query(self, user_input):
        try:
            lower_input = user_input.lower()
            
            simple_responses = {
                'привет': 'Привет! Рад тебя видеть. Чем могу помочь сегодня?',
                'здравствуй': 'Здравствуй! Как твои дела?',
                'как дела': 'У меня всё отлично! Работаю, помогаю пользователям. А у тебя как?',
                'спасибо': 'Пожалуйста! Всегда рад помочь.',
                'пока': 'Пока! Было приятно пообщаться. Заходи ещё!'
            }
            
            for key, response in simple_responses.items():
                if key in lower_input and len(lower_input.split()) < 4:
                    self.root.after(0, lambda: self.display_message("MeowAI", response))
                    self.chat_history.add_message('assistant', response)
                    return
            
            self.root.after(0, lambda: self.display_message("MeowAI", "🤔 Думаю..."))
            
            answer = self.answer_engine.get_answer(user_input)
            
            if answer:
                self.root.after(0, lambda: self.display_message("MeowAI", answer))
                
                if "Из моей базы знаний" not in answer:
                    clean_answer = re.sub(r'(📚 Из Википедии:|🔍 Из интернета:|🧮 Результат вычисления:)\n', '', answer)
                    self.db[user_input] = clean_answer.strip()
                    self.save_db()
                
                self.chat_history.add_message('assistant', answer)
            else:
                answer = ("😕 Не нашел полезной информации.\n\n"
                         "Попробуйте:\n"
                         "• Переформулировать вопрос\n"
                         "• Использовать более конкретные термины\n"
                         "• Задать вопрос проще")
                self.root.after(0, lambda: self.display_message("MeowAI", answer))
                self.chat_history.add_message('assistant', answer)
                
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            print(traceback.format_exc())
            self.root.after(0, lambda: self.display_message("MeowAI", error_msg, 'error'))


def main():
    root = tk.Tk()
    app = MeowAIChat(root)
    root.mainloop()


if __name__ == "__main__":
    main()
