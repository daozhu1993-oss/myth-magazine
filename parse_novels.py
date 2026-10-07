import os
import zipfile
import xml.etree.ElementTree as ET
import json
import re

desktop_path = '/Users/gx/Desktop/神话改编系列'
output_dir = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/data'
os.makedirs(output_dir, exist_ok=True)

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            paragraphs = []
            for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
                if texts:
                    t = ''.join(texts).strip()
                    if t:
                        paragraphs.append(t)
            return paragraphs
    except Exception as e:
        print(f"Error reading docx {path}: {e}")
        return []

def read_md(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines
    except Exception as e:
        print(f"Error reading md {path}: {e}")
        return []

categories_map = {
    '创世与洪荒': ['女娲', '混沌之死', '神农', '大禹', '仓颉造字'],
    '反叛与神罚': ['刑天舞干戚', '共工', '不周', '后羿', '夸父', '精卫', '扑通', '哪吒', '愚公移山'],
    '人间与执念': ['孟姜女', '尾生抱柱', '伯牙子期', '化蝶', '雷峰塔', '织女', '妲己'],
    '志怪与幽冥': ['画皮', '聂小倩', '孟婆', '钟馗嫁妹', '八仙'],
    '幻化与器物': ['莫邪', '梦蝶', '烂柯', '黄粱一梦', '点睛', '白水素女']
}

def get_category(filename):
    for cat, list_titles in categories_map.items():
        for t in list_titles:
            if t in filename:
                return cat
    return '神话新编'

files = sorted(os.listdir(desktop_path))
articles = []
issue_no = 1

# Filter out non-novel files
for f in files:
    if f.startswith('.') or f.endswith(('.png', '.xlsx', '.log')):
        continue
    if f in ['文风范例.md', '项目交接_handoff.md']:
        continue
    if not (f.endswith('.docx') or f.endswith('.md')):
        continue
        
    full_path = os.path.join(desktop_path, f)
    if f.endswith('.docx'):
        paras = read_docx(full_path)
    else:
        paras = read_md(full_path)
        
    if not paras:
        continue
        
    clean_name = f.replace('.docx', '').replace('.md', '').replace('_v1', '').replace('_v2', '').replace('`', '')
    
    # Title resolution
    display_title = clean_name
    body_paras = paras
    
    # Check if first paragraph is a title
    first_p = paras[0].lstrip('#').strip()
    if len(first_p) < 30 and ('·' in first_p or '《' in first_p or clean_name in first_p or len(first_p) < 15):
        display_title = first_p
        body_paras = paras[1:]
        
    total_words = sum(len(p) for p in body_paras)
    if total_words < 100:
        continue
        
    # Extract compelling excerpt / summary
    summary = ""
    for p in body_paras:
        p_clean = p.strip()
        if len(p_clean) > 30 and not p_clean.startswith(('一、', '二、', '1.', '写作阐述', '#', '>')):
            summary = p_clean[:140] + ('...' if len(p_clean) > 140 else '')
            break
    if not summary and body_paras:
        summary = body_paras[0][:140]
        
    category = get_category(f)
    
    # Parse chapters/sections
    chapters = []
    curr_chapter = {'title': '开篇', 'paragraphs': []}
    chapter_num_pattern = re.compile(r'^(第[一二三四五六七八九十百]+[章回节]|一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|十一、|十二、|\d+[\.、])\s*(.*)')
    
    for p in body_paras:
        p_str = p.strip()
        if chapter_num_pattern.match(p_str):
            if curr_chapter['paragraphs']:
                chapters.append(curr_chapter)
            curr_chapter = {'title': p_str, 'paragraphs': []}
        else:
            curr_chapter['paragraphs'].append(p_str)
            
    if curr_chapter['paragraphs'] or curr_chapter['title']:
        chapters.append(curr_chapter)
        
    # Key quote / pull quote extraction
    pull_quote = ""
    for p in body_paras:
        if 15 <= len(p) <= 60 and not p.startswith(('一、', '二、', '三、', '第')):
            pull_quote = p
            break
    if not pull_quote:
        pull_quote = summary[:50]

    article_obj = {
        'id': f'issue-{issue_no:03d}',
        'slug': f'issue-{issue_no:03d}',
        'issueNumber': f'No. {issue_no:03d}',
        'title': display_title,
        'category': category,
        'author': 'GX',
        'authorTitle': '神话重构作者 · 独立作家',
        'wordCount': total_words,
        'readMinutes': max(3, round(total_words / 350)),
        'summary': summary,
        'pullQuote': pull_quote,
        'date': f'2026-10-{issue_no:02d}' if issue_no <= 31 else f'2026-11-{(issue_no-30):02d}',
        'chapters': chapters,
        'fullParagraphs': body_paras
    }
    articles.append(article_obj)
    issue_no += 1

print(f"Successfully processed {len(articles)} myth novels!")
output_path = os.path.join(output_dir, 'articles.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"Saved to {output_path}")
