import json
import os


DEFAULT_CONFIG = {
    'question_region': {'x': 300, 'y': 200, 'w': 1320, 'h': 80},
    'question_region_long': {'x': 300, 'y': 180, 'w': 1320, 'h': 140},
    'answer_region': {'x': 300, 'y': 400, 'w': 1320, 'h': 60},
    'use_auto_detect': True,
    'ocr_scale': 2.0,
    'match_threshold': 70,
    'hotkey': 'F8',
    'always_on_top': True,
    'font_size': 18,
    'auto_recognize': False,
    'auto_interval': 1.5,
    'auto_change_threshold': 0.3,
    'enable_web_search': True,
    'enable_doubao_search': True,
    'search_on_unmatched': True,
    'record_history': True,
    'record_unmatched': True,
    'show_overlay': True,
    'auto_change_threshold': 0.3,
}


class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config.json')
        self.config_path = config_path
        self.config = {}
        self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                for key, val in DEFAULT_CONFIG.items():
                    if key not in self.config:
                        self.config[key] = val
                print(f"配置已加载: {self.config_path}")
            except Exception as e:
                print(f"配置加载失败: {e}")
                self.config = dict(DEFAULT_CONFIG)
        else:
            self.config = dict(DEFAULT_CONFIG)
            self.save()

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"配置保存失败: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def get_region(self, name):
        region = self.config.get(name, {})
        if region and all(k in region for k in ['x', 'y', 'w', 'h']):
            return (region['x'], region['y'], region['w'], region['h'])
        return None

    def set_region(self, name, x, y, w, h):
        self.config[name] = {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}
        self.save()
