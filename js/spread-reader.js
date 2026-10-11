/* ==========================================================================
   MYTHOS SPREAD READER — 双页跨页杂志引擎
   · 骨架致敬 aifa.one：跨页开本 / running head / 页码 / 模块化块
   · 皮肤自成一格：宣纸 / 竖排刊名 / 朱砂印 / 汉字页码 / 水墨出血
   · 真 3D 物理翻页由 StPageFlip 驱动（纸张卷曲 + 中缝阴影 + 拖拽）
   ========================================================================== */

(function () {
  'use strict';

  /* ------------------------------------------------------------------ *
   * HELPERS
   * ------------------------------------------------------------------ */
  /* 配图分档：原图 2500x1400 PNG 单张 3~6MB，直接引用会拖垮首屏。
     统一走 optimize_images.py 生成的压缩版（th=480px / lg=1280px）。
     与 app.js 中的实现保持一致，这里自带一份以免加载顺序产生依赖。 */
  function mythImg(src, variant) {
    if (!src || typeof src !== 'string') return src;
    if (src.indexOf('illustrations/') === -1) return src;
    return src
      .replace(/illustrations\/([^/]+)$/, 'illustrations/' + variant + '/$1')
      .replace(/\.(png|jpe?g|webp)$/i, '.jpg');
  }

  const CN = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九'];

  function cnNum(n) {
    if (n < 10) return CN[n];
    if (n < 20) return '十' + (n % 10 ? CN[n % 10] : '');
    if (n < 100) return CN[Math.floor(n / 10)] + '十' + (n % 10 ? CN[n % 10] : '');
    return String(n);
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function el(tag, cls, html) {
    const d = document.createElement(tag);
    if (cls) d.className = cls;
    if (html != null) d.innerHTML = html;
    return d;
  }

  /* ------------------------------------------------------------------ *
   * STATE
   * ------------------------------------------------------------------ */
  const state = {
    article: null,
    geo: null,
    fontSize: parseInt(localStorage.getItem('myth_font_size') || '18', 10),
    flip: null,
    pageEls: [],
    chapterMap: [],   // [{label, pageIdx}]
    open: false,
    soundOn: localStorage.getItem('myth_sound') !== 'false'
  };

  /* ------------------------------------------------------------------ *
   * GEOMETRY
   * ------------------------------------------------------------------ */
  function computeGeometry() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const portrait = vw < 900;

    const availW = vw - (portrait ? 20 : 88);
    const availH = vh - (portrait ? 84 : 128);

    // 桌面：先按"双页跨页"反算单页宽
    let spreadH = Math.min(availH, 880);
    let pageH = spreadH;
    let pageW = pageH / 1.38;
    let spreadW = pageW * 2;
    if (!portrait) {
      if (spreadW > availW) { spreadW = availW; pageW = spreadW / 2; pageH = pageW * 1.38; spreadH = pageH; }
    } else {
      if (pageW > availW) { pageW = availW; pageH = pageW * 1.38; spreadH = pageH; spreadW = pageW; }
    }

    // 兜底夹取（单页尺寸）
    pageW = Math.max(300, Math.min(pageW, 620));
    pageH = Math.max(420, Math.min(pageH, 820));
    spreadW = portrait ? pageW : pageW * 2;
    spreadH = pageH;

    const padY = pageH < 580 ? 24 : (pageH < 720 ? 28 : 32);
    const padX = pageW < 380 ? 22 : (pageW < 520 ? 32 : 42);

    return {
      pageW: Math.round(pageW),
      pageH: Math.round(pageH),
      spreadW: Math.round(spreadW),
      spreadH: Math.round(spreadH),
      padY, padX,
      portrait,
      // 版心高 = 页高 - 上下页边距 - 页眉(26) - 页脚(27) - 2px 抗误差余量
      // （实测 folio-head≈26px / folio-foot≈27px；旧的 -27-26-8 会低估 8px，
      //   导致每页都凭空少排一行，累积成大面積留白）
      bodyH: Math.round(pageH - padY * 2 - 26 - 27 - 2),
      bodyW: Math.round(pageW - padX * 2)
    };
  }

  /* ------------------------------------------------------------------ *
   * MEASUREMENT（分页测高）
   * ------------------------------------------------------------------ */
  let measureEl = null;
  function getMeasure(w, fontSize) {
    if (!measureEl) {
      measureEl = el('div', 'sheet-body is-measure');
      document.body.appendChild(measureEl);
    }
    measureEl.style.width = w + 'px';
    measureEl.style.setProperty('--reader-font-size', fontSize + 'px');
    return measureEl;
  }

  function measureHTML(html, w, fontSize) {
    const m = getMeasure(w, fontSize);
    m.innerHTML = html;
    return m.getBoundingClientRect().height;
  }

  /** 把一段文字按可用高度切成两半（跨页续排），切不开则返回 null。
   *  二分找最长可容纳前缀，再回退到最近的句读标点，避免把句子拦腰截断。 */
  function splitParaAt(text, availH, bodyW, fontSize, isLead) {
    if (!text) return null;
    const cls = 'blk-para' + (isLead ? ' is-lead' : '');
    const heightOf = (n) =>
      measureHTML(`<p class="${cls}">${esc(text.slice(0, n))}</p>`, bodyW, fontSize);

    let lo = 1, hi = text.length, best = 0;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (heightOf(mid) <= availH) { best = mid; lo = mid + 1; }
      else { hi = mid - 1; }
    }
    if (best < 6) return null;

    // 回退到最近句读，最多回退 12 字
    const punct = '。！？；，、：”’）】》」』…—·';
    let cut = best;
    for (let k = best; k > best - 12 && k > 0; k--) {
      if (punct.indexOf(text[k - 1]) >= 0) { cut = k; break; }
    }
    if (cut < best * 0.55) cut = best;   // 回退过多就放弃回退

    return [text.slice(0, cut), text.slice(cut)];
  }

  /**
   * 把段落按可用高度贪心装箱成若干页。
   *
   * availH: 数字（所有页同一高度）或函数 (chunkIndex) => 该页正文可用高度。
   *
   * 关键：章节首页顶部有"幕次题头 + 大插画"占位，可用高度远小于续页；
   * 续页没有头块，应当吃满整个版心。若沿用首页的 remain，续页会大片留白。
   */
  function packParagraphs(paragraphs, availH, bodyW, fontSize) {
    if (!paragraphs || !paragraphs.length) return [[]];
    const limitOf = (typeof availH === 'function') ? availH : (() => availH);

    const out = [];
    let cur = [];
    let emitted = 0;   // 此前已装箱的段落数（用于判定"全章首段"）
    let ci = 0;        // 当前正在装的页序号（0 = 章节首页）

    for (let i = 0; i < paragraphs.length; i++) {
      const cand = cur.concat([paragraphs[i]]);
      const html = cand.map((t, j) => {
        const isLead = (emitted + j === 0);   // 仅整章第一段下沉
        return `<p class="blk-para${isLead ? ' is-lead' : ''}">${esc(t)}</p>`;
      }).join('');
      const h = measureHTML(html, bodyW, fontSize);

      if (h > limitOf(ci) && cur.length) {
        out.push(cur);
        emitted += cur.length;
        cur = [paragraphs[i]];
        ci++;
      } else {
        cur = cand;
      }
    }
    if (cur.length) out.push(cur);
    return out;
  }

  /* ------------------------------------------------------------------ *
   * FOLIO（页眉页脚）
   * ------------------------------------------------------------------ */
  function folioHead(article, side, extra) {
    const running = side === 'left'
      ? esc(article.category)
      : '《' + esc(article.cleanTitle) + '》';
    const fish = side === 'right' ? '<span class="folio-fishtail">□</span>' : '';
    return `<div class="folio-head">
        <span class="folio-running">${extra ? esc(extra) + ' · ' : ''}${running}</span>
        ${fish}
      </div>`;
  }

  function folioFoot(article, side, printed) {
    const cn = cnNum(printed);
    const arab = String(printed).padStart(2, '0');
    if (side === 'left') {
      return `<div class="folio-foot">
          <span>MYTHOS · ${esc(article.category)}</span>
          <span class="folio-num">${cn}<span class="arab">/${arab}</span></span>
        </div>`;
    }
    return `<div class="folio-foot">
        <span class="folio-num">${cn}<span class="arab">/${arab}</span></span>
        <span>神话 · MYTHOS</span>
      </div>`;
  }

  /* ------------------------------------------------------------------ *
   * PAGE BUILDERS
   * ------------------------------------------------------------------ */
  function buildFrontispiecePage(article) {
    const d = el('div', 'sheet sheet-frontispiece');
    d.dataset.density = 'soft';
    d.innerHTML = `
      <div class="inscr-wrap">
        <div class="inscr-mark">中 華 神 話 重 構</div>
        <div class="inscr-vertical" style="font-size:15px;line-height:2.1;letter-spacing:.28em;color:var(--ink-secondary);max-height:48%;border-right:none;padding:0;">
          MYTHOS RETOLD
        </div>
        <div class="inscr-source">独立数字文学杂志 · 共三十期</div>
        <div class="inscr-seal" style="margin-top:14px;">神</div>
      </div>
      <div class="folio-foot" style="justify-content:center;border-top:none;">
        <span>扉 页 · FRONTISPIECE</span>
      </div>`;
    return d;
  }

  function buildCoverPage(article) {
    const d = el('div', 'sheet sheet-cover');
    d.dataset.density = 'hard';
    d.innerHTML = `
      <img class="cover-art" src="${mythImg(article.coverImg, 'lg')}" alt="${esc(article.cleanTitle)}" decoding="async" />
      <div class="cover-scrim"></div>
      <div class="cover-vertical">中華神話重構</div>
      <div class="cover-inner">
        <div class="cover-top">
          <div class="cover-mast">
            <span class="cover-mast-seal">神</span>
            <span class="cover-mast-name">神話 · MYTHOS</span>
          </div>
          <div class="cover-issue">${esc(article.issueNumber)}</div>
        </div>
        <div class="cover-stack">
          <div class="cover-kicker">✦ ${esc(article.category)}</div>
          <h1 class="cover-headline">${esc(article.cleanTitle)}</h1>
          <p class="cover-deck">${esc(article.subtitle)}</p>
          <div class="cover-byline">
            <strong>${esc(article.author)}</strong>
            <span>${esc(article.authorTitle || '')}</span>
            <span>原典 ${esc(article.originalMyth)}</span>
            <span>${article.readMinutes} 分钟 · ${article.wordCount.toLocaleString()} 字</span>
          </div>
        </div>
      </div>`;
    return d;
  }

  function buildInscriptionPage(article) {
    const d = el('div', 'sheet sheet-inscription');
    d.dataset.density = 'hard';
    const quote = article.classicQuote || article.subtitle;
    d.innerHTML = `
      <div class="inscr-wrap">
        <div class="inscr-mark">原 典 題 記</div>
        <div class="inscr-vertical">${esc(quote)}</div>
        <div class="inscr-source">— ${esc(article.originalMyth)}</div>
        <div class="inscr-seal">典</div>
      </div>`;
    return d;
  }

  function buildColophonPage(article, nextArticle) {
    const d = el('div', 'sheet sheet-colophon');
    d.innerHTML = `
      <div class="colophon-wrap">
        <div class="colophon-seal">完</div>
        <div class="colophon-title">《${esc(article.cleanTitle)}》· 卷终</div>
        <div class="colophon-sub">${esc(article.issueNumber)} · ${esc(article.category)}</div>
        <div class="colophon-meta">
          <div><b>全文字数</b><span>${article.wordCount.toLocaleString()} 字</span></div>
          <div><b>阅读时长</b><span>约 ${article.readMinutes} 分钟</span></div>
          <div><b>原典考据</b><span>${esc(article.originalMyth)}</span></div>
          <div><b>文风定调</b><span>大白话打底，短句断得狠；叙述者冷、克制、却有体温。</span></div>
        </div>
        <div class="colophon-next">下期 · <span class="next-title">《${esc(nextArticle.cleanTitle)}》</span> ${esc(nextArticle.issueNumber)}</div>
      </div>`;
    return d;
  }

  function buildBackCoverPage(article) {
    const d = el('div', 'sheet sheet-back-cover');
    d.dataset.density = 'soft';
    d.innerHTML = `
      <div class="inscr-wrap" style="justify-content:center;">
        <div class="inscr-mark">全 卷 终</div>
        <div class="inscr-vertical" style="font-size:14px;line-height:2.2;letter-spacing:.32em;color:var(--ink-secondary);max-height:46%;border-right:none;padding:0;">
          END OF<br/>ISSUE
        </div>
        <div class="inscr-source">${esc(article.cleanTitle)} · ${esc(article.issueNumber)}</div>
        <div class="inscr-seal" style="margin-top:14px;">神</div>
      </div>
      <div class="folio-foot" style="justify-content:center;border-top:none;">
        <span>封 底 · BACK COVER</span>
      </div>`;
    return d;
  }

  /** 正文（幕次）分页 —— 核心
   *
   * 【全局流式排版】
   * 不再「一幕一幕各自装箱」，而是把所有幕摊平成一个连续的块序列逐块装页。
   * 只有当「幕次头块」会吊在页底（其后留不下 MIN_CARRY 正文）时才新起一页。
   *
   * 旧实现的问题：每一幕都从新页开始，且续页沿用被头块/插画扣减后的可用高度，
   * 导致上一幕尾部常常空掉 400~600px 就翻页，正文被切成碎片。
   */
  function buildContentPages(article, geo, startIndex) {
    const g = geo;
    const fs = state.fontSize;
    const chapterPages = article.pages.filter(p => p.type === 'chapter' || p.type === 'content');
    const out = [];

    const SAFE = 6;         // 抗亚像素 / 字体度量误差
    // 头块落在本页时，其后至少要保证的正文空间。
    // 定得太高（如 200）会让上一幕尾部空掉一大截才翻页；
    // 120 ≈ 3~4 行，既保证新幕不至于「开了个头就断」，也不至于留白刺眼。
    const MIN_CARRY = 120;
    // 页底剩余空间不小于这个值（约 3 行）时，才允许把一段拆开跨页；
    // 否则宁可整段挪走，免得页脚吊着一两个字的"孤儿残片"。
    const MIN_SPLIT = 100;

    // 「本幕未完 · 下页续」提示条实占高度（动态测量，不写死）
    const continueH = measureHTML(
      '<div class="blk-continue"><span>本幕未完 · 下页续</span><span class="arrow">→</span></div>',
      g.bodyW, fs
    ) || 34;

    /* ---------------- 1) 摊平成块序列 ---------------- */
    const blocks = [];

    chapterPages.forEach((ch) => {
      const paras = ch.paragraphs || [];
      if (!paras.length) return;

      // ---- 幕次头块：幕号 + 标题 + 引语 + 大插画 ----
      let headHTML = '';
      const chNo = ch.chapterIndex != null
        ? cnNum(ch.chapterIndex)
        : (String(ch.chapterTitle || '').replace(/\s/g, ''));

      headHTML += `<div class="blk-chapter">
          <div class="blk-chapter-no">${esc(chNo)}</div>
          <div class="blk-chapter-title">${esc(ch.chapterTitle || '')}</div>
          <div class="blk-chapter-rule"></div>
        </div>`;

      if (ch.pullQuote) {
        headHTML += `<div class="blk-deck">${esc(ch.pullQuote)}</div>`;
      }

      if (ch.inlineImg) {
        const imgH = Math.round(Math.min(g.bodyH * 0.44, 300));
        headHTML += `<div class="blk-image is-bleed">
            <div class="blk-image-frame" style="height:${imgH}px">
              <img src="${mythImg(ch.inlineImg, 'lg')}" alt="${esc(ch.imgCaption || ch.chapterTitle || '')}" loading="lazy" decoding="async" />
            </div>
            <div class="blk-image-caption">${esc(ch.imgCaption || '神话场景原画')}</div>
            <div class="blk-image-source">— 委托原画 · 中华神话重构系列</div>
          </div>`;
      }

      blocks.push({
        kind: 'head',
        html: headHTML,
        label: ch.chapterTitle || '',
        nextTitle: ch.nextChapterTitle || null
      });

      paras.forEach((t, j) => {
        blocks.push({
          kind: 'para',
          text: t,
          isLead: (j === 0),
          html: `<p class="blk-para${j === 0 ? ' is-lead' : ''}">${esc(t)}</p>`,
          isChapterLast: (j === paras.length - 1),
          nextTitle: ch.nextChapterTitle || null
        });
      });
    });

    if (!blocks.length) return out;

    /* ---------------- 2) 流式装页 ---------------- */
    const htmlOf = (arr) => arr.map(b => b.html).join('');
    // 「本幕未完」提示条改为浮在版心底部（不占文档流），所以装箱不必为它预留高度，
    // 正文可以直接吃满整个版心，多排约一行。
    const LIMIT = g.bodyH - SAFE;

    const pages = [];
    let cur = [];

    const flush = () => {
      if (!cur.length) return;
      const last = cur[cur.length - 1];
      pages.push({
        blocks: cur.slice(),
        endsChapter: !!(last && last.kind === 'para' && last.isChapterLast),
        nextTitle: last ? (last.nextTitle || null) : null
      });
      cur = [];
    };

    for (let i = 0; i < blocks.length; i++) {
      const b = blocks[i];

      // 头块不许吊在页底：装上它之后若留不下 MIN_CARRY 的正文，先翻页
      if (b.kind === 'head') {
        const roomAfter = g.bodyH - measureHTML(htmlOf(cur) + b.html, g.bodyW, fs);
        if (cur.length && roomAfter < MIN_CARRY) flush();
      }

      const h = measureHTML(htmlOf(cur) + b.html, g.bodyW, fs);
      if (cur.length && h > LIMIT) {
        // 整段塞不下时，若页底还剩得下一个像样的段落残片，就把这段拆开跨页续排，
        // 而不是整段甩到下一页、在本页留下大片空洞。
        if (b.kind === 'para') {
          const room = LIMIT - measureHTML(htmlOf(cur), g.bodyW, fs);
          if (room >= MIN_SPLIT) {
            const parts = splitParaAt(b.text, room, g.bodyW, fs, b.isLead);
            if (parts) {
              cur.push({
                kind: 'para', text: parts[0], isLead: b.isLead,
                html: `<p class="blk-para${b.isLead ? ' is-lead' : ''}">${esc(parts[0])}</p>`,
                isChapterLast: false, nextTitle: b.nextTitle
              });
              flush();
              // 剩下的半段留在原位，下一轮循环接着处理（必要时再拆）
              blocks.splice(i, 1, {
                kind: 'para', text: parts[1], isLead: false,
                html: `<p class="blk-para is-split-tail">${esc(parts[1])}</p>`,
                isChapterLast: b.isChapterLast, nextTitle: b.nextTitle
              });
              i--;
              continue;
            }
          }
        }
        flush();
      }

      cur.push(b);
    }
    flush();

    /* ---------------- 3) 渲染成页 ---------------- */
    let pageIdx = startIndex;
    let chapterSeq = 0;

    pages.forEach((pg) => {
      const d = el('div', 'sheet');
      const side = (pageIdx % 2 === 0) ? 'left' : 'right';
      const printed = pageIdx + 1;

      let body = '';
      let paraBuf = [];
      const flushPara = () => {
        if (!paraBuf.length) return;
        body += `<div class="blk-body">${paraBuf.join('')}</div>`;
        paraBuf = [];
      };

      pg.blocks.forEach((b) => {
        if (b.kind === 'head') {
          flushPara();
          body += b.html;
          state.chapterMap.push({
            label: b.label || ('第 ' + cnNum(chapterSeq + 1) + ' 幕'),
            pageIdx: pageIdx
          });
          chapterSeq++;
        } else {
          paraBuf.push(b.html);
        }
      });
      flushPara();

      // 续页 / 下一幕提示：浮在版心底部，只有剩余空间够时才挂，避免压住正文末行
      const usedH = measureHTML(body, g.bodyW, fs);
      const slack = g.bodyH - usedH;
      if (slack >= continueH + 10) {
        if (!pg.endsChapter) {
          body += `<div class="blk-continue"><span>本幕未完 · 下页续</span><span class="arrow">→</span></div>`;
        } else if (pg.nextTitle) {
          body += `<div class="blk-continue"><span>下一幕 · ${esc(pg.nextTitle)}</span><span class="arrow">→</span></div>`;
        }
      }

      // 栏外批注 / 卷末闲章 — 仅在真正稀疏的章节收尾页补白
      let marginal = '';
      if (pg.endsChapter && usedH / g.bodyH < 0.62) {
        const quotes = [
          { t: '论者不论', s: '《大荒经》残句' },
          { t: '后人哀之而不鉴之', s: '杜牧《阿房宫赋》' },
          { t: '天地不仁，以万物为刍狗', s: '《道德经》第五章' },
          { t: '神话是人类的童年日记', s: '—— 编者按' },
          { t: '黄河尚有澄清日', s: '民间谚' },
          { t: '上古之事不可考', s: '《史记·五帝本纪》' },
          { t: '若有人间天上', s: '《长恨歌》' },
          { t: '天若有情天亦老', s: '李贺《金铜仙人辞汉武》' }
        ];
        const seed = (pg.nextTitle || '').length + pg.blocks.length;
        const q = quotes[seed % quotes.length];
        marginal = `<aside class="blk-margin">
              <span class="m-glyph">注</span>
              <blockquote>${esc(q.t)}</blockquote>
              <cite>— ${esc(q.s)}</cite>
            </aside>`;
      }

      d.innerHTML =
        folioHead(article, side, '') +
        `<div class="sheet-body">${body}${marginal}</div>` +
        folioFoot(article, side, printed);

      out.push(d);
      pageIdx++;
    });

    return out;
  }

  /* ------------------------------------------------------------------ *
   * BUILD ALL
   * ------------------------------------------------------------------ */
  function buildAll(article) {
    const geo = state.geo;
    state.chapterMap = [];

    const idx = (window.MYTH_ARTICLES || []).findIndex(a => a.id === article.id);
    const next = (window.MYTH_ARTICLES || [])[(idx + 1) % (window.MYTH_ARTICLES || []).length] || article;

    const front = buildFrontispiecePage(article);      // index 0 (left)
    const cover = buildCoverPage(article);            // index 1 (right)
    const inscr = buildInscriptionPage(article);      // index 2 (left)
    const content = buildContentPages(article, geo, 3);
    const colo = buildColophonPage(article, next);
    const back = buildBackCoverPage(article);         // index N (right of last spread)

    const els = [front, cover, inscr].concat(content, [colo, back]);

    // 给每页钉死几何
    els.forEach(e => {
      e.style.setProperty('--page-w', geo.pageW + 'px');
      e.style.setProperty('--page-h', geo.pageH + 'px');
      e.style.setProperty('--page-pad-x', geo.padX + 'px');
      e.style.setProperty('--page-pad-y', geo.padY + 'px');
      e.style.setProperty('--reader-font-size', state.fontSize + 'px');
    });

    return els;
  }

  /* ------------------------------------------------------------------ *
   * BUILD SPREADS — 把扁平页两两配对成双页跨页容器
   * ------------------------------------------------------------------ */
  function buildSpreads(pageEls, geo) {
    const spreads = [];
    // 横屏：两页并一个跨页；竖屏（手机）：一页就是一个"跨页"，否则
    // 双栏 grid 会把单页挤成半宽，文字重排后高度暴涨、被 overflow 裁掉大半。
    const per = geo.portrait ? 1 : 2;

    for (let i = 0; i < pageEls.length; i += per) {
      const first = pageEls[i];
      const wrap = el('div', 'sheet-spread');
      wrap.style.setProperty('--page-w', geo.pageW + 'px');
      wrap.style.setProperty('--page-h', geo.pageH + 'px');
      wrap.style.setProperty('--spread-w', geo.spreadW + 'px');
      wrap.style.setProperty('--spread-h', geo.spreadH + 'px');

      if (geo.portrait) {
        wrap.classList.add('is-portrait');
        first.classList.add('is-spread-alone');
        first.style.gridColumn = '1 / -1';
        wrap.appendChild(first);
      } else {
        const right = pageEls[i + 1];
        if (right) {
          first.classList.add('is-spread-left');
          right.classList.add('is-spread-right');
          wrap.appendChild(first);
          wrap.appendChild(right);
        } else {
          first.classList.add('is-spread-alone');
          first.style.gridColumn = '1 / -1';
          wrap.appendChild(first);
        }
        const spine = el('div', 'spread-spine');
        wrap.appendChild(spine);
      }

      spreads.push(wrap);
    }
    return spreads;
  }

  /* ------------------------------------------------------------------ *
   * FLIP ENGINE
   * ------------------------------------------------------------------ */
  /** 取得（必要时重建）书容器。
   *  注意：StPageFlip 的 destroy() 内部会执行 `distElement.remove(); wrapper.remove()`，
   *  也就是把传进去的容器元素整个从 DOM 里删掉。
   *  若 rebuild 时直接用 getElementById 拿，第二次重建就会拿到 null，整本书消失（表现为空白）。 */
  function getBookEl(stage) {
    let bookEl = document.getElementById('myth-book');
    if (!bookEl) {
      bookEl = document.createElement('div');
      bookEl.id = 'myth-book';
      bookEl.className = 'myth-book';
      const anchor = document.getElementById('spine-gutter');
      if (anchor && anchor.parentNode === stage) stage.insertBefore(bookEl, anchor);
      else stage.appendChild(bookEl);
    }
    return bookEl;
  }

  function mountFlip(els) {
    const stage = document.getElementById('spread-stage');
    if (!stage) return;

    stage.style.setProperty('--page-w', state.geo.pageW + 'px');
    stage.style.setProperty('--page-h', state.geo.pageH + 'px');
    stage.style.setProperty('--spread-w', state.geo.spreadW + 'px');
    stage.style.setProperty('--spread-h', state.geo.spreadH + 'px');

    if (state.flip) { try { state.flip.destroy(); } catch (e) {} state.flip = null; }

    // 必须在 destroy() 之后取容器——它可能刚被 destroy 移除
    const bookEl = getBookEl(stage);
    bookEl.innerHTML = '';

    state.flip = new St.PageFlip(bookEl, {
      width: state.geo.spreadW,
      height: state.geo.spreadH,
      size: 'fixed',
      minWidth: 320,
      maxWidth: 1600,
      minHeight: 380,
      maxHeight: 1100,
      drawShadow: true,
      flippingTime: 820,
      usePortrait: true,        // 每"页"=一个双页跨页（始终单页显示 + 整页翻转）
      startZIndex: 10,
      autoSize: false,
      maxShadowOpacity: 0.5,
      showCover: false,
      mobileScrollSupport: false,
      swipeDistance: 26
    });

    state.flip.loadFromHTML(els);

    state.flip.on('flip', (e) => {
      playPageTurnSound();
      updatePageReadout();
      hideFlipHint();
    });
    state.flip.on('changeOrientation', () => {
      updatePageReadout();
    });

    // 桌面才显示书脊中缝
    const gutter = document.getElementById('spine-gutter');
    if (gutter) gutter.style.display = state.geo.portrait ? 'none' : 'block';

    updatePageReadout();
  }

  function updatePageReadout() {
    const f = state.flip;
    if (!f) return;
    const cur = f.getCurrentPageIndex() + 1;
    const total = f.getPageCount();
    const info = document.getElementById('spread-page-info');
    if (info) info.textContent = cur + ' / ' + total;

    const bar = document.getElementById('spread-progress-bar');
    if (bar) bar.style.width = (cur / total * 100) + '%';

    const prev = document.getElementById('spread-prev');
    const next = document.getElementById('spread-next');
    if (prev) prev.disabled = (cur <= 1);
    if (next) next.disabled = (cur >= total);
  }

  /* ------------------------------------------------------------------ *
   * SOUND
   * ------------------------------------------------------------------ */
  let audioCtx = null;
  function playPageTurnSound() {
    if (!state.soundOn) return;
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      if (!audioCtx) audioCtx = new AC();
      const ctx = audioCtx;
      const len = Math.floor(ctx.sampleRate * 0.17);
      const buf = ctx.createBuffer(1, len, ctx.sampleRate);
      const data = buf.getChannelData(0);
      for (let i = 0; i < len; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (len * 0.3));
      }
      const src = ctx.createBufferSource();
      src.buffer = buf;
      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(720, ctx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(180, ctx.currentTime + 0.17);
      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0.05, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.17);
      src.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
      src.start();
    } catch (e) {}
  }

  /* ------------------------------------------------------------------ *
   * FLIP HINT
   * ------------------------------------------------------------------ */
  function showFlipHint() {
    const h = document.getElementById('flip-hint');
    if (!h) return;
    h.classList.add('show');
    state._hintTimer = setTimeout(hideFlipHint, 5200);
  }
  function hideFlipHint() {
    const h = document.getElementById('flip-hint');
    if (h) h.classList.remove('show');
    if (state._hintTimer) { clearTimeout(state._hintTimer); state._hintTimer = null; }
  }

  /* ------------------------------------------------------------------ *
   * TOC
   * ------------------------------------------------------------------ */
  function renderTOC() {
    const list = document.getElementById('spread-toc-list');
    if (!list || !state.article) return;
    const rows = [{ label: '封面 · ' + state.article.cleanTitle, pageIdx: 0 },
                  { label: '题记 · 原典出处', pageIdx: 1 }]
      .concat(state.chapterMap.map(c => ({ label: c.label, pageIdx: c.pageIdx })));

    list.innerHTML = rows.map(r =>
      `<li class="toc-item" data-page="${r.pageIdx}"><span>${esc(r.label)}</span><span class="toc-item-page">P.${r.pageIdx + 1}</span></li>`
    ).join('');

    list.querySelectorAll('.toc-item').forEach(li => {
      li.onclick = () => {
        const p = parseInt(li.dataset.page, 10);
        if (state.flip) state.flip.turnToPage(p);
        closeTOC();
      };
    });
  }

  function openTOC() {
    const d = document.getElementById('spread-toc');
    const o = document.getElementById('spread-toc-overlay');
    if (d) d.classList.add('open');
    if (o) o.classList.add('open');
  }
  function closeTOC() {
    const d = document.getElementById('spread-toc');
    const o = document.getElementById('spread-toc-overlay');
    if (d) d.classList.remove('open');
    if (o) o.classList.remove('open');
  }

  /* ------------------------------------------------------------------ *
   * OPEN / CLOSE / REBUILD
   * ------------------------------------------------------------------ */
  function rebuild(keepPage) {
    if (!state.article) return;
    const target = keepPage != null
      ? keepPage
      : (state.flip ? state.flip.getCurrentPageIndex() : 0);

    state.geo = computeGeometry();
    state.pageEls = buildAll(state.article);
    const spreads = buildSpreads(state.pageEls, state.geo);
    mountFlip(spreads);
    renderTOC();

    if (target > 0 && state.flip && target < state.flip.getPageCount()) {
      try { state.flip.turnToPage(target); } catch (e) {}
    }
  }

  function openReader(articleId, page) {
    const article = (window.MYTH_ARTICLES || []).find(a => a.id === articleId);
    if (!article) return;

    state.article = article;
    state.open = true;

    const wrap = document.getElementById('spread-reader');
    if (wrap) wrap.classList.add('active');
    document.body.style.overflow = 'hidden';

    state.geo = computeGeometry();
    state.pageEls = buildAll(article);
    const spreads = buildSpreads(state.pageEls, state.geo);
    mountFlip(spreads);
    renderTOC();
    showFlipHint();

    if (page && page > 0 && state.flip && page < state.flip.getPageCount()) {
      setTimeout(() => { try { state.flip.turnToPage(page); } catch (e) {} }, 60);
    }

    history.pushState(null, '', '#reader=' + article.id + '&page=' + ((page || 0) + 1));
  }

  function closeReader() {
    if (!state.open) return;
    state.open = false;
    const wrap = document.getElementById('spread-reader');
    if (wrap) wrap.classList.remove('active');
    closeTOC();
    document.body.style.overflow = '';
    history.pushState(null, '', window.location.pathname);
  }

  /* ------------------------------------------------------------------ *
   * CONTROLS
   * ------------------------------------------------------------------ */
  function wireControls() {
    const on = (id, fn) => { const b = document.getElementById(id); if (b) b.onclick = fn; };

    on('spread-close', closeReader);
    on('spread-prev', () => state.flip && state.flip.flipPrev());
    on('spread-next', () => state.flip && state.flip.flipNext());
    on('spread-edge-prev', () => state.flip && state.flip.flipPrev());
    on('spread-edge-next', () => state.flip && state.flip.flipNext());
    on('spread-toc-btn', () => {
      const d = document.getElementById('spread-toc');
      if (d && d.classList.contains('open')) closeTOC(); else openTOC();
    });
    on('spread-toc-close', closeTOC);
    on('spread-toc-overlay', closeTOC);

    on('spread-font-dec', () => setFontSize(state.fontSize - 1));
    on('spread-font-inc', () => setFontSize(state.fontSize + 1));

    on('spread-sound', () => {
      state.soundOn = !state.soundOn;
      localStorage.setItem('myth_sound', String(state.soundOn));
      const b = document.getElementById('spread-sound');
      if (b) b.textContent = state.soundOn ? '🔊' : '🔇';
    });

    on('spread-full', () => {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {});
      else document.exitFullscreen().catch(() => {});
    });

    on('spread-share', () => {
      navigator.clipboard && navigator.clipboard.writeText(window.location.href);
      const b = document.getElementById('spread-share');
      if (b) { const old = b.innerHTML; b.innerHTML = '✓'; setTimeout(() => b.innerHTML = old, 1400); }
    });

    on('spread-bookmark', () => {
      if (window.MythApp && window.MythApp.toggleBookmark && state.article) {
        window.MythApp.toggleBookmark(state.article.id);
        syncBookmarkBtn();
      }
    });

    // 键盘
    window.addEventListener('keydown', (e) => {
      if (!state.open) return;
      if (e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault(); state.flip && state.flip.flipNext();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault(); state.flip && state.flip.flipPrev();
      } else if (e.key === 'Escape') {
        const d = document.getElementById('spread-toc');
        if (d && d.classList.contains('open')) closeTOC(); else closeReader();
      } else if (e.key.toLowerCase() === 't') {
        const d = document.getElementById('spread-toc');
        if (d && d.classList.contains('open')) closeTOC(); else openTOC();
      }
    });

    // 视窗变化 → 重新分页（防抖）
    let rt = null;
    window.addEventListener('resize', () => {
      if (!state.open) return;
      clearTimeout(rt);
      rt = setTimeout(() => rebuild(), 260);
    });
  }

  function setFontSize(v) {
    state.fontSize = Math.max(15, Math.min(26, v));
    localStorage.setItem('myth_font_size', String(state.fontSize));
    const cur = state.flip ? state.flip.getCurrentPageIndex() : 0;
    rebuild(cur);
  }

  function syncBookmarkBtn() {
    const b = document.getElementById('spread-bookmark');
    if (!b || !state.article) return;
    const saved = (JSON.parse(localStorage.getItem('myth_bookmarks') || '[]')).includes(state.article.id);
    b.innerHTML = `<svg viewBox="0 0 24 24" width="15" height="15" fill="${saved ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>`;
    b.style.color = saved ? 'var(--gold)' : '';
  }

  /* ------------------------------------------------------------------ *
   * BOOT
   * ------------------------------------------------------------------ */
  function init() {
    wireControls();
    const sb = document.getElementById('spread-sound');
    if (sb) sb.textContent = state.soundOn ? '🔊' : '🔇';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.MythSpread = {
    openReader, closeReader, rebuild, setFontSize,
    isOpen: () => state.open,
    getChapterMap: () => state.chapterMap,
    getPageCount: () => (state.flip ? state.flip.getPageCount() : 0),
    getCurrentPage: () => (state.flip ? state.flip.getCurrentPageIndex() : 0),
    flipNext: () => state.flip && state.flip.flipNext(),
    flipPrev: () => state.flip && state.flip.flipPrev(),
    getFlip: () => state.flip
  };

})();
