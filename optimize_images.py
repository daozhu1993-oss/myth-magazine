#!/usr/bin/env python3
"""
批量压缩《神话》杂志配图。

原图问题：2500x1400 的 PNG，单张 3~6MB，共 154MB。
首页一次渲染 30 张封面卡 => 浏览器要下 53MB，全部卡在 pending。

产出两档：
  th/<name>.jpg   宽 480  用作首页网格卡片缩略图（目标 30~60KB）
  lg/<name>.jpg   宽 1280 用作 hero / 阅读器封面大图（目标 150~300KB）

原图保留不动，仅新增压缩版，页面改为引用压缩版。
"""
import os
import sys
import glob
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

ROOT = '/Users/gx/.gemini/antigravity/scratch/myth-magazine'
SRC_DIR = os.path.join(ROOT, 'assets/illustrations')
TH_DIR = os.path.join(SRC_DIR, 'th')
LG_DIR = os.path.join(SRC_DIR, 'lg')

PROFILES = [
    (TH_DIR, 480, 80),
    (LG_DIR, 1280, 82),
]


def human(n):
    return '%.1f KB' % (n / 1024) if n < 1024 * 1024 else '%.2f MB' % (n / 1024 / 1024)


def make(src):
    name = os.path.basename(src)
    stem = os.path.splitext(name)[0]
    out = []
    try:
        with Image.open(src) as im:
            im.load()
            # PNG 可能带 alpha / 调色板，统一转 RGB 才能存 JPEG
            if im.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', im.size, (247, 245, 241))  # 宣纸底色
                rgba = im.convert('RGBA')
                bg.paste(rgba, mask=rgba.split()[-1])
                im = bg
            elif im.mode != 'RGB':
                im = im.convert('RGB')

            orig_w, orig_h = im.size
            osize = os.path.getsize(src)

            for dst_dir, target_w, quality in PROFILES:
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, stem + '.jpg')
                # 不放大，只缩小
                w = min(target_w, orig_w)
                if w == orig_w:
                    resized = im
                else:
                    h = round(orig_h * w / orig_w)
                    resized = im.resize((w, h), Image.LANCZOS)
                resized.save(
                    dst, 'JPEG',
                    quality=quality,
                    optimize=True,
                    progressive=True,
                    subsampling=2 if w <= 640 else 0,
                )
                out.append((dst, os.path.getsize(dst)))
        return (name, orig_w, orig_h, osize, out, None)
    except Exception as e:
        return (name, 0, 0, 0, [], str(e))


def main():
    srcs = sorted(glob.glob(os.path.join(SRC_DIR, '*.*')))
    srcs = [s for s in srcs if os.path.isfile(s)
            and os.path.splitext(s)[1].lower() in ('.png', '.jpg', '.jpeg', '.webp')]
    print('待处理图片: %d 张' % len(srcs))

    total_before = sum(os.path.getsize(s) for s in srcs)
    total_after = 0
    errors = []

    with ProcessPoolExecutor(max_workers=6) as ex:
        for name, w, h, osize, outs, err in ex.map(make, srcs):
            if err:
                errors.append((name, err))
                print('  ❌ %-22s %s' % (name, err))
                continue
            sizes = ' '.join('%s=%s' % (os.path.basename(os.path.dirname(d)), human(sz)) for d, sz in outs)
            total_after += sum(sz for _, sz in outs)
            print('  ✅ %-22s %dx%d  %8s  ->  %s' % (name, w, h, human(osize), sizes))

    print('\n' + '=' * 62)
    print('原图合计 : %s  (%d 张)' % (human(total_before), len(srcs)))
    print('压缩版合计: %s  (th + lg 两档)' % human(total_after))
    print('总体压缩率: %.1f%%  (体积降到原来的 %.2f%%)' % (
        (1 - total_after / total_before) * 100, total_after / total_before * 100))
    if errors:
        print('\n失败 %d 张:' % len(errors))
        for n, e in errors[:10]:
            print('  ', n, e)
    print('=' * 62)


if __name__ == '__main__':
    main()
