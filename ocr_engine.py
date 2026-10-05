import re
import numpy as np
from PIL import Image, ImageEnhance
from rapidocr_onnxruntime import RapidOCR


def preprocess_question(img, scale=1.5):
    if scale != 1.0:
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.BILINEAR)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    return img.convert('RGB')


class OCREngine:
    def __init__(self, scale=1.5):
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

    def recognize_question(self, image, scale=None):
        if not self.is_ready():
            return {'full_text': '', 'blocks': [], 'line_count': 0}
        if isinstance(image, str):
            img = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            img = image.convert('RGB') if image.mode != 'RGB' else image
        else:
            img = Image.fromarray(np.array(image)).convert('RGB')

        use_scale = scale if scale is not None else self.scale
        img = preprocess_question(img, scale=use_scale)

        try:
            result, _ = self.engine(np.array(img))
            if not result:
                return {'full_text': '', 'blocks': [], 'line_count': 0}

            blocks = []
            for box, text, conf in result:
                text_stripped = text.strip()
                if not text_stripped:
                    continue
                if re.match(r'^[A-D][.．、:：]?$', text_stripped.upper()):
                    continue
                if not re.search(r'[\u4e00-\u9fff]', text_stripped):
                    continue
                center_y = (box[0][1] + box[2][1]) / 2
                center_x = (box[0][0] + box[2][0]) / 2
                blocks.append({
                    'text': text_stripped,
                    'center_x': center_x,
                    'center_y': center_y,
                    'confidence': conf
                })

            if not blocks:
                return {'full_text': '', 'blocks': [], 'line_count': 0}

            blocks.sort(key=lambda b: (b['center_y'], b['center_x']))

            lines = []
            current_line = [blocks[0]]
            for b in blocks[1:]:
                if abs(b['center_y'] - current_line[0]['center_y']) < 25:
                    current_line.append(b)
                else:
                    current_line.sort(key=lambda x: x['center_x'])
                    lines.append(current_line)
                    current_line = [b]
            current_line.sort(key=lambda x: x['center_x'])
            lines.append(current_line)

            full_text = ''.join(''.join(b['text'] for b in line) for line in lines)

            return {
                'full_text': full_text,
                'blocks': blocks,
                'line_count': len(lines)
            }
        except Exception as e:
            print(f"OCR识别出错: {e}")
            return {'full_text': '', 'blocks': [], 'line_count': 0}
