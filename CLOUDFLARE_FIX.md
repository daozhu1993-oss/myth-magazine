# 网站加载慢 —— 剩余瓶颈在 Cloudflare，需要人工改一行配置

> 交接对象：Antigravity / 岛主
> 生成时间：2026-10-12
> 相关提交：`9301991`（数据拆分）、`0835ef8`（配图压缩）、`90dfd05`（容错降级）

---

## 一、结论先说

网站 `https://myth.daozhuai.cn/` 加载慢的**根本原因不是代码，是 Cloudflare 代理**。

GitHub Pages 源站很快，但请求经过 Cloudflare 之后慢了 **20～60 倍**，而且会随机断连。

### 实测对比（同一张 31KB 缩略图 `assets/illustrations/th/illust_01.jpg`）

| 访问方式 | 耗时 | 结果 |
|---|---|---|
| **直连 GitHub Pages**<br>`https://daozhu1993-oss.github.io/myth-magazine/...` | **0.33 秒** | ✅ 秒开 |
| **经 Cloudflare**<br>`https://myth.daozhuai.cn/...` | **6 ～ 20 秒** | ⚠️ 还经常 `ERR_CONNECTION_CLOSED` |

反复 5 次请求同一张 31KB 图的实测结果：

```
尝试1: HTTP 200   31863B   15.42s
尝试2: HTTP 000       0B   20.00s   ← 超时
尝试3: HTTP 200   27331B   20.00s   ← 只传了一部分
尝试4: HTTP 200   31863B    6.81s
尝试5: HTTP 200   31863B    6.04s
```

**为什么会这样**：GitHub Pages 对每个响应都发 `Cache-Control: no-cache, no-store, must-revalidate`，
Cloudflare 严格遵守，于是**每一次请求都回源一次**，缓存形同虚设。

---

## 二、方案 A（推荐）：给 Cloudflare 加一条缓存规则

优点：保留 Cloudflare 的 HTTPS / 防护 / 压缩，同时把静态资源缓存到边缘节点，第二次访问直接秒开。

### 操作步骤

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com) → 选中 `daozhuai.cn`（或 `myth.daozhuai.cn` 所在域）
2. 左侧菜单 **Caching** → **Cache Rules** → **Create rule**
3. 按下表填写：

| 配置项 | 值 |
|---|---|
| Rule name | `Cache static assets` |
| **If incoming requests match…** | **Custom filter expression** |
| Field | `URI Path` |
| Operator | `starts with` |
| Value | `/assets/` |
| （可选，加一条 OR） | URI Path `starts with` `/data/` |
| **Then…** | 勾选 **Cache eligibility: Eligible for cache** |
| **Edge TTL** | 选 **Ignore cache-control header** → 填 `1 month`（或 `604800` 秒 = 7 天） |
| **Browser TTL** | 选 **Ignore cache-control header** → 填 `1 day` |

4. **Deploy** 保存
5. 如需立即生效：**Caching** → **Configuration** → **Purge Everything**

### 验证是否生效

```bash
# 连着请求两次同一个静态资源
curl -sI "https://myth.daozhuai.cn/assets/illustrations/th/illust_01.jpg" | grep -i 'cf-cache-status'
```

- 第一次应显示 `cf-cache-status: MISS`
- 第二次应显示 **`cf-cache-status: HIT`** ← 看到 HIT 就成功了

再打开网站，图片应该是秒出。

---

## 三、方案 B（更快更省事）：关掉 Cloudflare 代理（灰云）

如果你不需要 Cloudflare 的 CDN/WAF 功能，直接让域名解析到 GitHub Pages：

1. Cloudflare Dashboard → **DNS** → **Records**
2. 找到 `myth` 这条 CNAME（指向 `daozhu1993-oss.github.io`）
3. 点右侧橙色的 **Proxy status** 云朵图标，切成 **DNS only（灰色）**
4. 等几分钟 DNS 生效

实测直连 GitHub Pages 是 **0.33 秒**，比现在快 20 倍以上。

> ⚠️ 注意：GitHub Pages 自带 HTTPS，关掉代理后证书会自动签发（可能需要等 15 分钟～1 小时）。
> 如果域名在阿里云/腾讯云买的、DNS 也在那边，同样操作（删掉 Cloudflare 的 NS，改回原 DNS，
> 然后加一条 CNAME 指向 `daozhu1993-oss.github.io`）。

---

## 四、方案 C：换托管（如果想彻底解决）

GitHub Pages 不支持自定义 `Cache-Control`，天然不适合做图片站。可考虑：

| 平台 | 优点 |
|---|---|
| **Vercel** | 自带全球 CDN + 图片优化，缓存策略可配；仓库根目录已有 `vercel.json` |
| **Netlify** | 类似 Vercel，配置简单 |
| **Cloudflare Pages** | 直接部署在 CF 上，静态资源默认缓存，不走回源 |

---

## 五、我这边已经做完的优化（代码层面已到极限）

### 1. 配图压缩（`0835ef8`）
- 原图：2500×1400 PNG，单张 3～6MB，**共 154MB**
- 压缩后：`th/`（480px，~30KB/张）+ `lg/`（1280px，~170KB/张），**共 11MB**
- **压缩率 92.6%**
- 工具：`optimize_images.py`（以后加新图直接跑它）

### 2. 数据拆分（`9301991`）
- 原 `js/data.js` 1.07MB 一次性下载（含 30 篇全部正文）
- 现在：`data/meta.js` **12.6KB**（首页/网格元数据）+ `data/content/<id>.json` **~31KB/篇**（阅读器按需 fetch）
- **首屏下载量降 99%**
- 工具：`split_data.py`

### 3. 网格分批
- 原来一次渲染 30 张卡（30 张图同时拉）
- 现在初始只渲染 **12 张** + 「载入更多」按钮

### 4. 容错降级（`90dfd05`）
- 图片失败 → 0.8s 后换尺寸档重试 → 1.8s 后加时间戳重试 → 渲染朱砂「神」印占位卡
- 保证**永远不出现破图**，版面不塌（占位高度与原图一致 186px）

### 实测效果

| 指标 | 修复前 | 修复后 |
|---|---|---|
| DOMContentLoaded | **104 秒**（一度 140 秒） | **8.4 秒** |
| 网格首次渲染 | 104 秒 | 8.5 秒 |
| 首屏下载量 | ~54 MB | ~1.2 MB |
| JS 数据 | 1.07 MB | 12.6 KB |
| 破图 | 31 张全 pending | 0（有重试+占位兜底） |

---

## 六、给 Antigravity 的清单

如果要继续推进，请按这个顺序：

- [ ] **必做**：按「方案 A」在 Cloudflare 加缓存规则（或按「方案 B」关代理）
- [ ] 验证 `cf-cache-status: HIT`
- [ ] 刷新 https://myth.daozhuai.cn/ 确认图片秒出
- [ ] 可选：清理仓库历史里 154MB 的原图（`.git` 现在 157MB，拖慢每次 Pages 构建）
      ```bash
      git filter-repo --path assets/illustrations/illust_ --path assets/illustrations/art_ --invert-paths
      # 或更简单：把原图移到 Git 外，只保留 th/ 和 lg/
      ```

---

## 七、关键文件速查

| 文件 | 作用 |
|---|---|
| `optimize_images.py` | 批量压缩配图 → `th/` + `lg/` |
| `split_data.py` | 拆分 `refined_articles.json` → `meta.js` + `content/*.json` |
| `data/meta.js` | 首页元数据（12.6KB），`window.MYTH_META` |
| `data/content/<id>.json` | 单篇正文，阅读器按需 fetch |
| `js/app.js` | `mythImg()` 路径转换、`fetchFullArticle()` 按需加载、`installImgFallback()` 容错 |
| `js/spread-reader.js` | 跨页阅读器，接收完整 article 对象 |
| `css/magazine.css` | `.load-more-btn`、`.img-fallback` 占位样式 |
