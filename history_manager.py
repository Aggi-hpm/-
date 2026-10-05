import json
import os
import time
from datetime import datetime


class HistoryManager:
    def __init__(self, history_path=None):
        if history_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            history_path = os.path.join(base_dir, 'history.json')
        self.history_path = history_path
        self.records = []
        self.unmatched = []
        self._load()

    def _load(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.records = data.get('records', [])
                self.unmatched = data.get('unmatched', [])
            except Exception as e:
                print(f"历史记录加载失败: {e}")
                self.records = []
                self.unmatched = []

    def _save(self):
        try:
            if len(self.records) > 200:
                self.records = self.records[-200:]
            if len(self.unmatched) > 500:
                self.unmatched = self.unmatched[-500:]
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump({'records': self.records, 'unmatched': self.unmatched},
                          f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"历史记录保存失败: {e}")

    def add_record(self, question, answer, match_type, confidence, source='local', ocr_time=0):
        record = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': time.time(),
            'question': question,
            'answer': answer,
            'match_type': match_type,
            'confidence': confidence,
            'source': source,
            'ocr_time': ocr_time
        }
        self.records.append(record)
        self._save()
        return record

    def add_unmatched(self, question, ocr_text='', reason='not_found'):
        for item in self.unmatched:
            if item.get('question') == question:
                item['count'] = item.get('count', 0) + 1
                item['last_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self._save()
                return
        record = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'question': question,
            'ocr_text': ocr_text,
            'reason': reason,
            'count': 1
        }
        self.unmatched.append(record)
        self._save()

    def get_recent(self, count=20):
        return list(reversed(self.records[-count:]))

    def get_unmatched(self, count=50):
        sorted_list = sorted(self.unmatched, key=lambda x: x.get('count', 0), reverse=True)
        return sorted_list[:count]

    def clear_history(self):
        self.records = []
        self._save()

    def clear_unmatched(self):
        self.unmatched = []
        self._save()

    def export_unmatched(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("未匹配题目列表\n")
                f.write("=" * 60 + "\n\n")
                sorted_list = sorted(self.unmatched, key=lambda x: x.get('count', 0), reverse=True)
                for i, item in enumerate(sorted_list, 1):
                    f.write(f"{i}. [{item.get('count', 1)}次] {item['question']}\n")
                    if item.get('ocr_text'):
                        f.write(f"   OCR原文: {item['ocr_text']}\n")
                    f.write(f"   首次: {item['time']}  最近: {item.get('last_time', item['time'])}\n\n")
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
