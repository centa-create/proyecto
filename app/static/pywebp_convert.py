# Script para convertir imágenes JPG/PNG a WebP en static/product_images y static/review_images
import os
from PIL import Image

def convert_to_webp(folder):
    for fname in os.listdir(folder):
        if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(folder, fname)
            img = Image.open(path).convert('RGB')
            webp_path = os.path.splitext(path)[0] + '.webp'
            img.save(webp_path, 'webp', quality=85)
            print(f'Convertido: {fname} -> {os.path.basename(webp_path)}')

if __name__ == '__main__':
    for sub in ['product_images', 'review_images']:
        folder = os.path.join(os.path.dirname(__file__), sub)
        if os.path.exists(folder):
            convert_to_webp(folder)
