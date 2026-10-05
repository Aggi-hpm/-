import re
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from rapidocr_onnxruntime import RapidOCR


def preprocess_question(img, scale=2.0, enhance_contrast=True, sharpen=True):
    if scale != 1.0:
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    if enhance_contrast:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.8)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 150 else 255, '1')
    img = img.convert('RGB')
    return img


def detect_question_lines(img):
    gray = img.convert('L')
    arr = np.array(gray)
    h, w = arr.shape
    row_white = np.sum(arr > 200, axis=1) / w
    threshold = 0.85
    in_text = False
    text_rows = []
    start = 0
    for i, ratio in enumerate(row_white):
        if ratio < threshold and not in_text:
            in_text = True
            start = i
        elif ratio >= threshold and in_text:
            in_text = False
            if i - start > 3:
                text_rows.append((start, i))
    if in_text and h - start > 3:
        text_rows.append((start, h))
    if len(text_rows) <= 1:
        return 'short', len(text_rows)
    gaps = []
    for i in range(1, len(text_rows)):
        gap = text_rows[i][0] - text_rows[i-1][1]
        gaps.append(gap)
    if gaps and max(gaps) > h * 0.15:
        return 'long', len(text_rows)
    return 'short' if len(text_rows) <= 2 else 'long', len(text_rows)


class OCREngine:
    def __init__(self, scale=2.0):
        self.scale = scale
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = RapidOCR()
            print("OCR引擎初始化成功 (RapidOCR)")
        except Exception as e:
            print(f"OCR引擎初始化失败: {e}")
            self.engine = None

    def is_ready(self):
        return self.engine is not None

    def recognize(self, image, scale=None):
        if not self.is_ready():
            return []
        if isinstance(image, str):
            img = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            img = image.convert('RGB') if image.mode != 'RGB' else image
        else:
            img = Image.fromarray(np.array(image)).convert('RGB')

        use_scale = scale if scale is not None else self.scale
        img = preprocess_question(img, scale=use_scale, enhance_contrast=True, sharpen=True)

        try:
            img_np = np.array(img)
            result, _ = self.engine(img_np)
            if result is None:
                return []
            scale_factor = use_scale
            restored = []
            for box, text, conf in result:
                restored_box = [[p[0] / scale_factor, p[1] / scale_factor] for p in box]
                restored.append([restored_box, text, conf])
            return restored
        except Exception as e:
            print(f"OCR识别出错: {e}")
            return []

    def detect_type(self, image):
        if isinstance(image, str):
            img = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            img = image.convert('RGB') if image.mode != 'RGB' else image
        else:
            img = Image.fromarray(np.array(image)).convert('RGB')
        q_type, line_count = detect_question_lines(img)
        return q_type, line_count

    def recognize_question(self, image, scale=None):
        results = self.recognize(image, scale=scale)
        if not results:
            return {'full_text': '', 'blocks': [], 'line_count': 0}

        blocks = []
        for box, text, conf in results:
            text_stripped = text.strip()
            if not text_stripped:
                continue
            if self._is_abcd_marker(text_stripped):
                continue
            if not self._has_chinese(text_stripped):
                continue
            center_x = sum(p[0] for p in box) / 4
            center_y = sum(p[1] for p in box) / 4
            blocks.append({
                'text': text_stripped,
                'center_x': center_x,
                'center_y': center_y,
                'confidence': conf,
                'box': box
            })

        if not blocks:
            return {'full_text': '', 'blocks': [], 'line_count': 0}

        blocks.sort(key=lambda b: (b['center_y'], b['center_x']))

        lines = []
        current_line = [blocks[0]]
        for b in blocks[1:]:
            if abs(b['center_y'] - current_line[0]['center_y']) < 20:
                current_line.append(b)
            else:
                current_line.sort(key=lambda x: x['center_x'])
                lines.append(current_line)
                current_line = [b]
        current_line.sort(key=lambda x: x['center_x'])
        lines.append(current_line)

        full_text = ''
        for line in lines:
            line_text = ''.join(b['text'] for b in line)
            full_text += line_text

        return {
            'full_text': full_text,
            'blocks': blocks,
            'line_count': len(lines)
        }

    def _has_chinese(self, text):
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def _is_abcd_marker(self, text):
        t = text.strip().upper()
        return bool(re.match(r'^[A-D][.．、:：]?$', t))
