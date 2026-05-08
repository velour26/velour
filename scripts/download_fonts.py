"""
Download Manrope and Cormorant Garamond font subsets from Google Fonts.

Since the site uses Russian (Cyrillic) text, this downloads BOTH the
'latin' and 'cyrillic' subsets for every weight/style so that all
characters render correctly with the chosen typefaces.

Generates static/css/fonts.css with proper unicode-range declarations.

Run once:  python scripts/download_fonts.py
Re-run any time to fill in missing files (skips existing ones).
"""
import os
import re
import urllib.request

BASE_DIR  = os.path.join(os.path.dirname(__file__), '..')
FONTS_DIR = os.path.join(BASE_DIR, 'static', 'fonts')
CSS_PATH  = os.path.join(BASE_DIR, 'static', 'css', 'fonts.css')
os.makedirs(FONTS_DIR, exist_ok=True)

UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/124.0.0.0 Safari/537.36'
)

# Subsets we want — covers Russian + Latin characters
WANTED_SUBSETS = {'latin', 'cyrillic'}

WEIGHT_LABEL = {
    '300': 'Light', '400': 'Regular', '500': 'Medium',
    '600': 'SemiBold', '700': 'Bold',
}

FONT_REQUESTS = [
    'https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&display=swap',
    'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap',
]


def fetch_text(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8')


def parse_faces(css):
    """
    Parse @font-face blocks annotated with /* subset */ comments.
    Returns list of dicts with: family, weight, style, subset,
                                 unicode_range, url, filename
    """
    # Split CSS into labelled segments
    # Each segment starts with an optional /* comment */ then @font-face {...}
    segments = re.split(r'(/\*[^*]*\*/)', css)
    current_subset = 'unknown'
    faces = []

    for part in segments:
        stripped = part.strip()
        if stripped.startswith('/*'):
            current_subset = stripped.strip('/* ').strip()
            continue
        if '@font-face' not in stripped:
            continue
        # Extract properties
        family_m  = re.search(r"font-family:\s*['\"]([^'\"]+)['\"]", stripped)
        style_m   = re.search(r'font-style:\s*(\w+)', stripped)
        weight_m  = re.search(r'font-weight:\s*(\d+)', stripped)
        url_m     = re.search(r'url\(([^)]+\.woff2)\)', stripped)
        range_m   = re.search(r'unicode-range:\s*([^\n;]+)', stripped)

        if not (family_m and weight_m and url_m):
            continue

        family_display = family_m.group(1)               # "Cormorant Garamond"
        family_slug    = family_display.replace(' ', '')  # "CormorantGaramond"
        style   = style_m.group(1) if style_m else 'normal'
        weight  = weight_m.group(1)
        url     = url_m.group(1)
        urange  = range_m.group(1).strip() if range_m else ''

        weight_label = WEIGHT_LABEL.get(weight, weight)
        if style == 'italic':
            style_suffix = '' if weight == '400' else weight_label
            name_base = f'{family_slug}-{style_suffix}Italic'
        else:
            name_base = f'{family_slug}-{weight_label}'

        filename = f'{name_base}-{current_subset}.woff2'

        faces.append({
            'family_display': family_display,
            'style':          style,
            'weight':         weight,
            'subset':         current_subset,
            'unicode_range':  urange,
            'url':            url,
            'filename':       filename,
        })

    return faces


# ── Fetch and parse CSS ──────────────────────────────────────────────────────
all_faces = []
for api_url in FONT_REQUESTS:
    label = api_url.split('family=')[1].split('&')[0]
    print(f'  fetching  {label} ...', end=' ', flush=True)
    try:
        css   = fetch_text(api_url)
        faces = parse_faces(css)
        # Keep only wanted subsets
        wanted = [f for f in faces if f['subset'] in WANTED_SUBSETS]
        all_faces.extend(wanted)
        print(f'{len(wanted)} face(s) (latin + cyrillic)')
    except Exception as e:
        print(f'FAILED: {e}')

print()

# ── Download missing woff2 files ─────────────────────────────────────────────
downloaded = []
for face in all_faces:
    dest = os.path.join(FONTS_DIR, face['filename'])
    if os.path.exists(dest):
        print(f'  skip      {face["filename"]}')
        downloaded.append(face)
        continue
    print(f'  download  {face["filename"]} ...', end=' ', flush=True)
    try:
        req = urllib.request.Request(face['url'], headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=20) as r, open(dest, 'wb') as f:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)
        print(f'OK  ({len(data):,} bytes)')
        downloaded.append(face)
    except Exception as e:
        print(f'FAILED: {e}')

# ── Generate fonts.css ───────────────────────────────────────────────────────
lines = [
    '/* ============================================================ */',
    '/*  Auto-generated by scripts/download_fonts.py — do not edit  */',
    '/*  Manrope + Cormorant Garamond — Latin & Cyrillic subsets     */',
    '/* ============================================================ */',
    '',
]
for face in downloaded:
    lines += [
        '@font-face {',
        f"  font-family: '{face['family_display']}';",
        f"  font-style: {face['style']};",
        f"  font-weight: {face['weight']};",
        '  font-display: swap;',
        f"  src: url('../fonts/{face['filename']}') format('woff2');",
    ]
    if face['unicode_range']:
        lines.append(f"  unicode-range: {face['unicode_range']};")
    lines += ['}', '']

with open(CSS_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'\n  fonts.css written  ({len(downloaded)} @font-face rules)')
print(f'Done. {len(downloaded)}/{len(all_faces)} font file(s) in static/fonts/')
