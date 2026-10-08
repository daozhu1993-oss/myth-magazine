# 《神话》· MYTHOS 独立文学杂志项目交接与二次优化方案 (Handover Document)

> **交接对象**：Workbuddy / 前端架构师 / 交互体验主理人  
> **项目名称**：中华神话改编系列 · 30 期全画幅独立电子文学杂志（MYTHOS RETOLD）  
> **项目版本**：`v1.0.0-PROD`（核心数据已清洗，全站已部署上线，待进阶拟真体验攻坚）  
> **目标对标**：[aifa.one](https://www.aifa.one/)（极致电子杂志拟真交互）与 Awwwards / Webby Awards / FWA 获奖级视效体验  
> **线上访问地址**：
> - 🌐 **生产主站（Cloudflare Edge）**：[`https://myth.daozhuai.cn/`](https://myth.daozhuai.cn/)
> - 📦 **GitHub Pages 镜像**：[`https://daozhu1993-oss.github.io/myth-magazine/`](https://daozhu1993-oss.github.io/myth-magazine/)
> - 🐙 **开源源码仓库**：[`https://github.com/daozhu1993-oss/myth-magazine`](https://github.com/daozhu1993-oss/myth-magazine)
> - 🏝️ **主岛生态入口**：[`https://www.daozhuai.cn/`](https://www.daozhuai.cn/)（首页「故事别传」及「独立数字杂志」双入口已打通）
> 
> **本地工程绝对路径**：
> - 杂志主代码工程：`/Users/gx/.gemini/antigravity/scratch/myth-magazine/`
> - Cloudflare Edge 代理工程：`/Users/gx/.gemini/antigravity/scratch/daozhu-myth-proxy/`
> - 主岛门户工程：`/Users/gx/.gemini/antigravity/scratch/daozhu-island/`

---

## 一、 项目背景与资产底座现状

本项目是将作者电脑桌面上《神话改编系列》的 **30 篇原创中短篇神话重构小说**（约 14.3 万字，涵盖共工、精卫、仓颉、刑天、后羿、梁祝、白蛇、聊斋等，**哪吒篇已按要求永久剔除**），打造为对标顶级数字出版物的一款独立电子文学杂志。

### 1. 已完成的基础建设与底座资产
- **30 篇纯净文学数据库**：
  - 全部原始 `.docx` / `.md` 文本已通过专用流水线清洗，过滤了标题泄漏、非正文日期标记（如 `2026.9.25`）与残缺幕次；
  - 重点篇目已完成戏剧性分幕：如《梁祝·化蝶》重构成三幕戏剧结构（青绸车、黄土坟、彩蝶说），《夸父逐日》作者阐述提炼至题记卡片；
  - 数据库统一生成至 `data/refined_articles.json` 与 `js/data.js`（挂载于 `window.MYTH_ARTICLES`）。
- **专属艺术原画资产库**：
  - 13 幅 16:9 宽屏水墨重彩定制插画（存放在 `assets/illustrations/`），并严格对齐 30 篇神话故事（封面图与正文插图精准匹配，0 张错置配图）。
- **典范中文文学排版引擎**：
  - 彻底铲除了早期导致阅读顺序错乱的“交错网格”（CSS Grid 曾导致第1段在左、第2段在右、第3段在左的致命断序）；
  - 目前采用单列居中阅读流（`max-width: 760px`，首行缩进 `text-indent: 2em`，行高 `1.98`，两端对齐，段落对话平滑流淌）；
  - 每幕底部配有显式「章末下一幕导引卡」（In-Page Progression）。
- **基础设施与全球边缘加速**：
  - 配置了 GitHub Actions 自动构建部署工作流（`.github/workflows/deploy.yml`）；
  - 配置了 Cloudflare Worker 边缘代理（`daozhu-myth-proxy`），绑定自定义域名 `myth.daozhuai.cn`，支持核心脚本防缓存与静态大图边缘缓存。

---

## 二、 痛点深度复盘：为什么用户觉得“还原的不够好”？

用户明确反馈：**“我觉得还原的不够好”**，并指明参考网站为 **[https://www.aifa.one/](https://www.aifa.one/)**，期望品质达到 **Awwwards / Webby Awards / FWA 获奖级水准**。

经过深入拆解 [aifa.one](https://www.aifa.one/) 与传统“网页版阅读器”的本质区别，当前版本存在以下**核心差距**，请 Workbuddy 重点攻坚：

```
当前实现 (偏扁平网页式滑动)                 用户期待的 Aifa.one (真实物理杂志翻页感)
┌─────────────────────────┐               ┌────────────┬────────────┐
│      [ 满幅大单屏 ]      │               │  左页(画)   │  右页(文)   │
│   (平移 slide 切换)      │   ─────►      │ 3D 卷角翻页、书脊中缝立体折痕│
│   较生硬，缺乏书本仪式感  │               │ 纸张拖拽受力变形、纸张厚度阴影│
└─────────────────────────┘               └────────────┴────────────┘
```

### 1. 翻页交互的物理真实感（The Tactile Flip Sensation）
- **现状缺陷**：目前页面切换采用的是基于 CSS `translateX` 的左右平移动画（Slide Transition），配合简单的透明度淡入淡出。本质上依然是“PPT 切页”或“轮播图”，**没有纸张弯曲、没有纸张厚度、没有折痕阴影**。
- **Aifa.one 的标杆表现**：
  - 用户用鼠标拖拽页面角落时，纸张会随鼠标位置产生**物理卷曲与撕拉变形（Peeling & Bending）**；
  - 翻动过程中，翻动页背面的半透反白、下一页露出的渐进阴影（Dynamic Drop Shadow）、翻过中线时的惯性加速坠落；
  - 纸张具有“硬挺度”与“重力感”。

### 2. 开本布局模式：单页居中 vs 桌面端“双页跨页开本”（Double-Page Spread）
- **现状缺陷**：当前所有内容无论在多大屏幕上，都是单一垂直居中的单屏单列页面。
- **Aifa.one 的标杆表现**：
  - **在桌面端（宽屏 > 1024px）**，真正的现代杂志是一本**摊开在桌面上的书**，呈 **双页跨页（Left Page + Right Page）**；
  - **左页**通常为全幅水墨大插画或艺术引题（Splash Page），**右页**为单列文学正文；或者左右两页对称排版，中间有一道清晰深邃的**立体书脊中缝阴影（Book Spine Valley Shadow）**；
  - **在移动端（< 768px）** 则自适应退化为单页翻动或纵向折页。

### 3. 出版装帧的视觉仪式感与细节雕琢（Editorial Book Design）
- **装帧细节缺失**：缺少真实印刷杂志的扉页刊例（ISSN / 卷次 / 独立编委栏）、页边裁切标记（Crop Marks）、书脊厚度立体投影、页码角落数字微标；
- **目录与画廊导轨**：缺乏底栏可视化微型缩略图滑轨（Thumbnail Scrubber Gallery），无法像看实体杂志一样“刷拉拉翻动缩略图”。
- **封面视差质感**：目前封面虽有 Ken Burns 缓慢缩放，但缺乏 WebGL 鼠标倾斜陀螺仪视差（3D Tilt Parallax）或水墨层级分离。

---

## 三、 给 Workbuddy 的进阶重构路线图 (Implementation Recipes)

请 Workbuddy 接手后按优先级逐步推进重构：

### 🎯 阶段一 (P0): 引入真正的 3D 拟真翻页物理引擎

**核心目标**：彻底丢弃 `translateX` 轮播切页，升级为具有纸张受力弯曲、3D 翻转的物理图书引擎。

#### 推荐方案 A：集成 `StPageFlip` (Page-Flip) 物理翻页库（推荐首选）
`page-flip`（[nodegarden/page-flip](https://github.com/nodegarden/page-flip)）是目前开源中最成熟、无重度框架依赖（Vanilla JS 原生支持）的物理翻页库，支持 Canvas 高帧率渲染纸张弯曲高光与中缝阴影。

- **快速集成方式**：
  ```html
  <!-- 在 index.html 引入 -->
  <script src="https://cdn.jsdelivr.net/npm/page-flip/dist/js/page-flip.browser.js"></script>
  ```
- **配置参数样例**：
  ```javascript
  const pageFlip = new St.PageFlip(document.getElementById('book-container'), {
    width: 600,            // 单页宽度
    height: 840,           // 单页高度
    size: 'stretch',       // 自适应容器
    minWidth: 320,
    maxWidth: 960,
    minHeight: 480,
    maxHeight: 1200,
    drawShadow: true,      // 核心：纸张投影
    flippingTime: 700,     // 物理翻页时长 (ms)
    usePortrait: true,     // 移动端单页，宽屏双页
    startZIndex: 10,
    autoSize: true,
    maxShadowOpacity: 0.5, // 中缝与翻动面阴影浓度
    showCover: true        // 独立封面
  });
  ```

#### 推荐方案 B：基于纯 CSS 3D Transforms 构建杂志翻折状态机
若不希望引入外部库，可使用 CSS 3D 透视重构：
```css
.magazine-viewport {
  perspective: 2400px;
  perspective-origin: 50% 50%;
}
.magazine-book {
  position: relative;
  transform-style: preserve-3d;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
}
/* 书脊中缝深谷阴影 (Spine Shadow) */
.magazine-book::after {
  content: "";
  position: absolute;
  top: 0; bottom: 0; left: 50%; width: 60px;
  transform: translateX(-50%);
  background: linear-gradient(
    to right,
    rgba(0,0,0,0) 0%,
    rgba(0,0,0,0.18) 42%,
    rgba(0,0,0,0.35) 50%,
    rgba(0,0,0,0.18) 58%,
    rgba(0,0,0,0) 100%
  );
  pointer-events: none;
  z-index: 50;
}
```

---

### 🎯 阶段二 (P0): 桌面端打造「双页跨页开本」（Double-Page Spread）

将当前“每章垂直滑一屏”改造为**“杂志跨页”结构**：
- **跨页模型 (Spread)**：
  - **Spread 0 (封面)**：全画幅大刊封面（独立单页展开或大折页）；
  - **Spread 1 (题记跨页)**：左页为《山海经》古籍原典影印拓片感设计，右页为金印题记与原典正文出处；
  - **Spread 2 (第一幕跨页)**：
    - **左页（Visual Page）**：16:9 全幅无边距神话大插画 + 竖排朱砂印章 + 画面解构导引语；
    - **右页（Text Page）**：单列严谨正文排版（第一幕情节展开）；
  - **Spread 3...N (后续幕次)**：左右页对称排版，图文穿插；
  - **Spread 终 (刊记封底)**：仿旧藏书票印记、完卷印章、下期预告与版权页。

---

### 🎯 阶段三 (P1): 底栏新增「可视化缩略图画廊导轨 (Thumbnail Scrubber)」

在 Aifa.one 中，读者可以随时展开或滑过底部导轨查看所有页面的微缩页面（Miniature Preview）：
1. 在底部悬浮栏上方增加 `.magazine-scrubber-track`；
2. 每一个 Page 对应一个比例为 `1:1.414`（国际大度 16 开杂志比例）的微型缩略卡；
3. 鼠标划过微缩卡时，微缩图轻微浮起上扬，并显示页码与篇章标题（如 `P.4 第一幕 · 天柱折`）；
4. 点击直接物理翻至该页。

---

### 🎯 阶段四 (P2): 封面 WebGL / 3D 景深视差与宣纸环境联觉

提升至 Awwwards 标准的微细节：
1. **封面 3D 视差推拉 (Layered Depth Parallax)**：
   - 将封面拆分为三层：`背景深空/山峦`、`插画核心主体（共工/精卫/战神）`、`前景标题字与悬浮浮雕印章`；
   - 随鼠标移动在 `(-15deg, 15deg)` 范围内产生微弱的 3D 透视偏转。
2. **宣纸肌理（Washi Paper Texture）与翻页音效联动**：
   - 现有的 Web Audio 合成翻页音效（`playPageTurnSound()`）已在 `js/app.js` 中就绪；
   - 翻页时可让音效音量与翻页角速度（速度快声音干脆，速度慢声音轻柔沙沙作响）实现动态绑定。

---

## 四、 代码仓库架构与关键文件索引

Workbuddy 请直接针对以下目录及文件进行开发与重构：

```
myth-magazine/
├── index.html                   # 页面主入口 (杂志外壳、顶栏、底栏双胶囊岛、边缘感应区)
├── css/
│   ├── main.css                 # 全局基础变量、宣纸肌理、磁吸鼠标、首页流式网格样式
│   └── reader.css               # 【重构核心】阅读器全套样式 (建议重构为 Spread 双页与 3D 翻页)
├── js/
│   ├── app.js                   # 【重构核心】应用交互与阅读器状态机 (renderPage, turnPage, TOC)
│   └── data.js                  # 自动生成的全量文章数据库 window.MYTH_ARTICLES (30篇)
├── data/
│   ├── articles.json            # 原始解析文章池
│   └── refined_articles.json    # 精准清洗后的 30 篇最终数据 (含分幕、专属配图、题记)
├── assets/
│   └── illustrations/           # 13 幅 16:9 高清无水印定制神话大画幅插画
├── build_database_v5.py         # 数据清洗与结构生成脚本 (如有新增文本修改可重新执行)
└── .github/workflows/deploy.yml # GitHub Actions 自动化部署流水线
```

### 核心数据模型说明 (`data/refined_articles.json`)
每个文章对象结构如下，可直接用于双页渲染：
```typescript
interface MythArticle {
  id: string;               // "issue-001"
  issueNumber: string;      // "No. 001"
  cleanTitle: string;       // "共工怒触不周山"
  subtitle: string;         // 导语
  category: string;         // "卷二 · 反叛与神罚"
  originalMyth: string;     // 古籍原典出处: "《山海经·大荒西经》·《淮南子·天文训》"
  classicQuote: string;     // 原典名句
  coverImg: string;         // 专属封面插画相对路径
  inlineImg: string;        // 专属正文大插画相对路径
  imgCaption: string;       // 插画场景解构题注
  totalPages: number;       // 总页数
  pages: Array<{
    type: 'cover' | 'inscription' | 'chapter' | 'colophon';
    pageNumber: number;
    title: string;
    chapterTitle?: string;  // 幕次标题: "第一幕 · 天柱折"
    paragraphs?: string[];  // 严格清洗后的纯段落数组 (已去除多列污染)
    inlineImg?: string;
    imgCaption?: string;
    nextChapterTitle?: string; // 下一幕标题 (用于章末导流卡)
  }>;
}
```

---

## 五、 Workbuddy 本地运行与部署命令集

### 1. 本地启动预览
主工程为原生现代 Web 架构，零繁琐打包等待，直接启动 HTTP 服务器：
```bash
cd /Users/gx/.gemini/antigravity/scratch/myth-magazine
python3 -m http.server 3456 --bind 127.0.0.1
# 浏览器打开: http://127.0.0.1:3456/
```

### 2. 提交与推送至 GitHub 生产仓库
代码修改完成后，提交并推送到 GitHub，CI/CD 会自动在数十秒内完成 Pages 边缘部署：
```bash
cd /Users/gx/.gemini/antigravity/scratch/myth-magazine
git add .
git commit -m "feat(magazine): 升级 3D 物理翻页引擎与双页跨页开本设计"
git push origin main
```
> **检查 CI 状态**：`gh run list --repo daozhu1993-oss/myth-magazine`

### 3. 同步至 Cloudflare Edge 代理 (`myth.daozhuai.cn`)
若调整了 CDN 缓存策略或路由，进入代理目录部署：
```bash
cd /Users/gx/.gemini/antigravity/scratch/daozhu-myth-proxy
npx wrangler deploy
```

### 4. 同步至主岛门户 (`daozhuai.cn`)
将打包好的最新静态文件同步至主岛仓库目录：
```bash
cd /Users/gx/.gemini/antigravity/scratch/daozhu-island
cp -r /Users/gx/.gemini/antigravity/scratch/myth-magazine/{index.html,css,js,data,assets} myth/
git add myth/ v2/index.html
git commit -m "feat(portal): 同步最新版神话杂志至主岛"
git push origin main
```

---

## 六、 终态验收清单 (Definition of Done & QA Checklist)

Workbuddy 交付下一阶段成果时，请对照以下指标进行逐一验收：

- [ ] **物理拟真翻页**：拖拽或点击角落时，呈现具有纸张弯折度、高光漫反射与边缘阴影的拟真翻转过程（非简陋平移动画）；
- [ ] **宽屏双页展开（Double-Page Spread）**：在屏幕宽度 $\ge 1024\text{px}$ 时呈现完整的摊开杂志跨页形态，中缝具备立体深谷渐变阴影；
- [ ] **移动端优雅降级**：在手机或坚屏平板上自动降级为平滑单页翻阅或全幅纵向开本；
- [ ] **图文匹配与无错漏**：全 30 篇小说每一篇正文与专属大插画严丝合缝，哪吒篇 100% 排除在外；
- [ ] **阅读流畅无障碍**：正文从上至下顺序叙事绝对连贯，排版两字符规范首行缩进，无跨列跳跃；
- [ ] **缩略图滑轨导览**：底部提供可折叠的页面迷你微缩导览条，方便快速跳转；
- [ ] **三端域名访问正常**：
  - `https://myth.daozhuai.cn/` 正常秒开且无报错；
  - `https://daozhu1993-oss.github.io/myth-magazine/` 正常秒开；
  - `https://www.daozhuai.cn/` 首页点击「《神话》· MYTHOS 独立文学杂志」能够顺畅进入。
