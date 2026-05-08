import os
import sys
import csv
import time
import urllib.request

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH   = os.path.join(BASE_DIR, 'wb_articles.csv')
IMAGES_DIR = os.path.join(BASE_DIR, 'seed_data', 'images')
MAX_PHOTOS = 5

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

def get_basket_list(nm_id: int):
    """Генерирует приоритетный список корзин. Сначала расчетная, потом остальные."""
    vol = nm_id // 100_000
    # Формула WB для новых артикулов
    if vol <= 143: b = 1
    elif vol <= 287: b = 2
    elif vol <= 431: b = 3
    elif vol <= 719: b = 4
    elif vol <= 1007: b = 5
    elif vol <= 1061: b = 6
    elif vol <= 1115: b = 7
    elif vol <= 1169: b = 8
    elif vol <= 1313: b = 9
    elif vol <= 1601: b = 10
    elif vol <= 1655: b = 11
    elif vol <= 1919: b = 12
    elif vol <= 2045: b = 13
    elif vol <= 2189: b = 14
    elif vol <= 2405: b = 15
    elif vol <= 2621: b = 16
    elif vol <= 2837: b = 17
    elif vol <= 3053: b = 18
    elif vol <= 3269: b = 19
    elif vol <= 3485: b = 20
    elif vol <= 3701: b = 21
    elif vol <= 3917: b = 22
    elif vol <= 4133: b = 23
    elif vol <= 4349: b = 24
    elif vol <= 4565: b = 25
    else: b = 21 + (vol - 3486) // 216
    
    calculated = int(b)
    # Создаем список: расчетная корзина, потом все остальные от 01 до 65 для страховки
    baskets = [calculated]
    for x in range(1, 66):
        if x not in baskets:
            baskets.append(x)
    return [str(x).zfill(2) for x in baskets]

def download_image(basket, vol, part, nm_id, photo_idx):
    url = f'https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{nm_id}/images/big/{photo_idx}.webp'
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=2) as r:
            if r.status == 200:
                data = r.read()
                if len(data) > 1000: return data
    except:
        pass
    return None

if __name__ == "__main__":
    if not os.path.exists(CSV_PATH):
        print(f"Файл {CSV_PATH} не найден")
        sys.exit(1)

    rows = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            our, wb = row.get('our_article', '').strip(), row.get('wb_article', '').strip()
            if our and wb: rows.append((our, int(wb)))

    print(f'Обработка {len(rows)} товаров...')

    for idx, (our_art, nm_id) in enumerate(rows, 1):
        folder = os.path.join(IMAGES_DIR, our_art)
        os.makedirs(folder, exist_ok=True)

        # Если файл уже есть, пропускаем
        if os.path.exists(os.path.join(folder, '01.jpg')):
            print(f'[{idx:3d}/{len(rows)}] {our_art:10} - уже загружен')
            continue

        vol = nm_id // 100_000
        part = nm_id // 1_000
        
        found_basket = None
        baskets_to_check = get_basket_list(nm_id)
        
        # Ищем корзину (проверяем только 1-е фото)
        for b in baskets_to_check:
            img_data = download_image(b, vol, part, nm_id, 1)
            if img_data:
                found_basket = b
                with open(os.path.join(folder, '01.jpg'), 'wb') as f:
                    f.write(img_data)
                break
        
        if found_basket:
            results = ["01:OK"]
            for p in range(2, MAX_PHOTOS + 1):
                img_data = download_image(found_basket, vol, part, nm_id, p)
                if img_data:
                    with open(os.path.join(folder, f'{p:02d}.jpg'), 'wb') as f:
                        f.write(img_data)
                    results.append(f"{p:02d}:OK")
                else:
                    break
            print(f'[{idx:3d}/{len(rows)}] {our_art:10} (wb:{nm_id:<10}): Найдено в корзине {found_basket} | {len(results)} фото')
        else:
            print(f'[{idx:3d}/{len(rows)}] {our_art:10} (wb:{nm_id:<10}): !!! НЕ НАЙДЕНО (проверено 65 корзин) !!!')

    print("\nГотово!")