import json
import re
import os
from rapidfuzz import fuzz


def normalize_question(text):
    if not text:
        return ""
    text = str(text).strip()
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'[]?？,，.。!！:：;；""''「」《》()（）[【】、/|]', '', text)
    text = text.replace('〇', '零').replace('—', '-').replace('–', '-')
    return text.lower()


def clean_text(text):
    if not text:
        return ""
    text = str(text).strip()
    text = re.sub(r'\s+', '', text)
    return text


class QuestionMatcher:
    def __init__(self, questions_path=None):
        if questions_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            questions_path = os.path.join(base_dir, 'questions.json')
        self.questions_path = questions_path
        self.questions = {}
        self._load_questions()

    def _load_questions(self):
        try:
            with open(self.questions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.questions = data.get('questions', {})
            print(f"题库加载完成：共 {len(self.questions)} 道题目")
        except Exception as e:
            print(f"题库加载失败: {e}")
            self.questions = {}

    def match(self, question_text, threshold=70):
        if not question_text or not self.questions:
            return None

        q_norm = normalize_question(question_text)
        if not q_norm:
            return None

        if q_norm in self.questions:
            item = self.questions[q_norm]
            return {
                'question': item.get('question', ''),
                'answer': item.get('answer', ''),
                'confidence': 1.0,
                'match_type': 'exact'
            }

        best_score = 0
        best_key = None
        for key, item in self.questions.items():
            score = fuzz.ratio(q_norm, key)
            if score > best_score:
                best_score = score
                best_key = key

        if best_score >= threshold and best_key:
            item = self.questions[best_key]
            return {
                'question': item.get('question', ''),
                'answer': item.get('answer', ''),
                'confidence': best_score / 100.0,
                'match_type': 'fuzzy'
            }

        return None
