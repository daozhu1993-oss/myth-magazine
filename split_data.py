#!/usr/bin/env python3
"""
把 refined_articles.json 拆成：
  data/meta.js                  首页元数据列表（~15KB；首页/网格/书架只读这个）
  data/content/<id>.json        每篇正文（~30KB；阅读器按需 fetch）

原 data.js 是 1.0MB，把 30 篇正文拖垮首屏。Cloudflare 把每个请求都回源到 GitHub Pages，
30 张图 + 1MB JS 同时拉，浏览器 6 条并发要等 60s+ 才能看到正文。
"""
import json
import os
import re

ROOT = '/Users/gx/.gemini/antigravity/scratch/myth-magazine'
SRC = os.path.join(ROOT, 'data/refined_articles.json')
OUT_DIR = os.path.join(ROOT, 'data')
CONTENT_DIR = os.path.join(OUT_DIR, 'content')

# 首页/网格/书架需要的字段（其余拆走）
META_FIELDS = [
    'id', 'issueNumber', 'cleanTitle', 'subtitle', 'category',
    'originalMyth', 'author', 'authorTitle', 'readMinutes',
    'wordCount', 'coverImg'
]


def main():
    data = json.load(open(SRC, encoding='utf-8'))

    meta = []
    os.makedirs(CONTENT_DIR, exist_ok=True)
    for a in data:
        m = {k: a.get(k) for k in META_FIELDS}
        meta.append(m)
        # 单篇正文
        full = {k: v for k, v in a.items() if k not in META_FIELDS}
        # chapters 与 fullParagraphs 同源，pages 是渲染时算的，存 chapter/paragraphs 即可
        cid = a['id']
        with open(os.path.join(CONTENT_DIR, cid + '.json'), 'w', encoding='utf-8') as f:
            json.dump(full, f, ensure_ascii=False, separators=(',', ':'))

    # 生成 meta.js
    meta_js_path = os.path.join(OUT_DIR, 'meta.js')
    with open(meta_js_path, 'w', encoding='utf-8') as f:
        f.write('/* Auto-generated: 首页元数据（不含正文）*/\n')
        f.write('window.MYTH_META = ')
        json.dump(meta, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')

    # 体积统计
    meta_size = os.path.getsize(meta_js_path)
    sizes = []
    for a in data:
        p = os.path.join(CONTENT_DIR, a['id'] + '.json')
        sizes.append((a['id'], os.path.getsize(p)))
    total_content = sum(s for _, s in sizes)
    print('首页 meta.js : %7d B (%.1f KB)   30 篇元数据' % (meta_size, meta_size / 1024))
    print('正文合计     : %7d B (%.1f KB)   30 篇 × %.1f KB/篇' % (
        total_content, total_content / 1024, total_content / 30 / 1024))
    print('优化前       : %7d B (%.1f KB)   js/data.js 单文件' % (
        os.path.getsize(os.path.join(ROOT, 'js/data.js')),
        os.path.getsize(os.path.join(ROOT, 'js/data.js')) / 1024))
    print('  ↓ 首页首屏下载从 %.1f KB → %.1f KB（节省 %.0f%%）' % (
        os.path.getsize(os.path.join(ROOT, 'js/data.js')) / 1024,
        meta_size / 1024,
        (1 - meta_size / os.path.getsize(os.path.join(ROOT, 'js/data.js'))) * 100))


if __name__ == '__main__':
    main()
