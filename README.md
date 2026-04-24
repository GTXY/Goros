# Goros — goro's 全渠道货源聚合门户

> 实时聚合全球主流 goro's（高桥吾郎）二手及新品市场的商品信息，统一展示于一个本地门户网站，方便买家高效选品。

---

## 目录

- [项目背景](#项目背景)
- [PRD · 产品需求文档](#prd--产品需求文档)
- [技术架构](#技术架构)
- [目录结构](#目录结构)
- [数据源清单](#数据源清单)
- [快速启动](#快速启动)

---

## 项目背景

goro's（ゴローズ）是由高桥吾郎于 1971 年创立的印第安风格银饰品牌，其羽根（フェザー）系列在全球二级市场拥有极高的稀缺性与溢价。由于货源分散在多个平台（日本专门店、香港国际站、欧美授权商等），买家需要逐一访问各站才能掌握全局行情，效率极低。

本项目目标：**将 7 个权威平台的 goro's 商品数据汇聚到本地数据库，通过统一的门户页面一站式浏览、筛选、跳转购买。**

---

## PRD · 产品需求文档

### 1. 目标用户

- goro's 重度爱好者 / 收藏买家
- 主要使用场景：**PC 端浏览器**（Chrome / Safari / 夸克），兼顾手机端

---

### 2. 功能范围

#### 2.1 数据采集（后端 Scraper）

| 编号 | 数据源 | 类型 | 技术方案 | 货币 |
|------|--------|------|---------|------|
| S1 | DeltaOne JP（deltaone.jp） | goro's专门店 | Shopify JSON API | JPY |
| S2 | DeltaOne HK（deltaone.com.hk） | goro's专门店·国际版 | Shopify JSON API | HKD |
| S3 | Corner（corneronline.store） | goro's专门店 | Shopify JSON API | JPY |
| S4 | TrueMark（shop.yellow-eagle.net） | goro's专门店 | Shopify JSON API | JPY |
| S5 | FiveSix · 66666（56s.jp） | goro's专门店 | requests + BeautifulSoup | JPY |
| S6 | Native Feather（nativefeather.jp） | 官方授权经销商 | Shopify JSON API | USD |
| S7 | RINKAN（rinkan-goros.com） | 综合买取平台 | requests + BeautifulSoup（增量同步） | JPY |

> **注**：TrueMark 主站为 Wix，实际商品托管在 Shopify 子域名 `shop.yellow-eagle.net`，使用 Shopify API 抓取。RINKAN 实际域名为 `rinkan-goros.com`（MakeShop 平台），静态 HTML 即含全部商品数据，无需 JS 渲染。

**采集策略（防止封 IP 核心方案）：**

- 所有数据**每天凌晨 03:00 自动抓取一次**（APScheduler 定时任务，内嵌于 FastAPI 进程）
- 前端所有请求（含分页）均指向**本地 API**，绝不直接请求源站
- Shopify 站通过官方 JSON API 拉取（`/products.json`），请求频率温和
- 非 Shopify 站设置标准 User-Agent + 请求间隔（0.6~1.5 秒/请求）
- 支持手动触发全量抓取（前端 Header「Sync Now」按钮）；触发时有防重入保护，不会并发执行两次

**RINKAN 增量同步策略（独立于其他 Scraper）：**

由于 RINKAN 商品量大（300+ 件）且服务器响应慢（~12 秒/请求），采用集合差运算实现高效增量同步：

1. **Phase 1**：爬取所有列表页，收集当前在售 brandcodes（`live_ids`）——仅请求列表页，快速
2. **Phase 2**：查询数据库已有的 RINKAN source_id（`db_ids`）
3. **Phase 3a 售出标记**：`sold = db_ids − live_ids` → SQL 批量更新 `available=False`，**无需 HTTP 请求，瞬间完成**
4. **Phase 3b 新品入库**：`new = live_ids − db_ids` → 仅对新 brandcode 请求详情页并 INSERT

首次全量约需 60~90 分钟（凌晨运行）；后续每日增量仅处理当天新上架的几件商品，通常 5 分钟内完成。

**ASK 价格处理：**

部分商品不公开定价，原站以以下方式标注：
- Shopify 价格字段为 `0.00`
- DeltaOne HK 等港台电商使用 `888,888,888`（吉祥数占位符）
- 换算后日元超过 5 亿（明显虚假大数）

以上情形统一在后端抓取时识别，存储为 `price_raw="ASK"`、`price_jpy=NULL`，前端显示「ASK」并隐藏货币标签。

**采集字段：**

| 字段 | 说明 |
|------|------|
| `id` | 本地自增主键 |
| `source` | 来源平台标识（deltaone_jp / rinkan 等） |
| `source_id` | 原站商品 ID / brandcode |
| `title` | 商品名称（日文原文） |
| `price_raw` | 价格原始字符串（含货币符号，ASK 时为 "ASK"） |
| `price_jpy` | 统一换算为日元（用于排序/比较，ASK 时为 NULL） |
| `currency` | 货币单位（JPY / HKD / USD） |
| `condition` | 成色（新品 / ほぼ新品 / 美品 / 中古 / 不明 等） |
| `images` | 图片 URL 数组（JSON 存储） |
| `url` | 商品原始链接 |
| `available` | 是否在库（true/false） |
| `tags` | 原始标签 |
| `description` | 商品详情文本 |
| `scraped_at` | 最后抓取时间 |
| `created_at` | 首次入库时间 |

---

#### 2.2 页面功能

##### P1 · 列表页（首页 `/`）

**布局：**
- PC 端：顶部筛选栏 + 主体卡片网格（每行 3~4 张，响应式自适应）
- 平板端：每行 2~3 张
- 手机端：每行 1~2 张，或跳转手机专属页面

**商品卡片展示字段：**
- 主图（封面图，统一比例裁切）
- 商品名称（超长截断，根据当前语言自动翻译）
- 来源平台标签
- 价格（醒目展示，标注货币单位；日语环境显示 JPY，繁中环境显示 CNY 换算值；询价商品显示「ASK」）
- 成色标签（色块区分：新品绿 / 美品蓝 / 中古灰）
- 在库状态（售罄时灰化）

**筛选 / 排序功能：**
- 按来源平台筛选（多选）
- 按成色筛选（多选）
- 按在库状态筛选（默认只显示有货）
- 按价格排序（低→高 / 高→低）
- 按上架时间排序（最新优先）
- 关键词搜索（匹配商品名称）

**分页：**
- 每页默认 24 条
- 支持跳页，显示总数
- 分页数据全部来自本地 API，无源站请求

---

##### P2 · 详情页（`/product/:id`）

**展示内容：**
- 图片轮播（支持多图，点击放大）
- 商品全名（自动翻译为当前 UI 语言）
- 来源平台（可点击跳转原始链接）
- 价格（大字展示，标注货币单位；询价显示「ASK」）
- 成色 / 标签
- 商品详情描述（自动翻译为当前 UI 语言）
- 在库状态
- 最后数据更新时间
- 「前往原站购买」按钮（新标签页打开原始链接）

---

##### P3 · 手动抓取面板（集成于 Header）

Header 右侧提供「Sync Now」按钮，点击后：

1. 调用后端 `POST /api/scrape/all`
2. 按钮变为 loading 状态（旋转图标 + 文字「同步中」）
3. 实时展示各数据源抓取进度（成功绿点 / 失败红点 / 待抓取灰点）
4. 完成后自动刷新当前页面数据

**Header 另显示：**
- 上次抓取时间
- 数据总量统计

---

#### 2.3 终端适配策略

| 终端 | 策略 |
|------|------|
| PC（≥1024px） | 主版本，完整功能 |
| 平板（768px~1023px） | 响应式缩减，布局自适应 |
| 手机（<768px） | 进入页面时检测 UA，自动跳转 `/m/` 前缀的手机专属路由，展示简化版列表与详情页 |

手机版核心功能与 PC 版一致，仅在布局、字号、交互方式上进行适配（单列卡片等）。

---

#### 2.4 多语言 & 货币规范

**语言：**
- 使用 `vue-i18n`，支持 **日本語（ja）** 和 **繁體中文（zh-TW）** 两种语言
- **默认语言：日本語**；语言偏好持久化至 `localStorage`（版本键 `lang_ver=v3`）
- 切换入口：Header 右侧「日本語 | 繁中」按钮
- 切换范围：所有 UI 界面文字；商品标题与描述通过 Google Translate 免费 API 自动翻译并缓存

**货币：**
- 后端提供 `/api/products/rates` 接口，每 24 小时从 [Frankfurter API](https://www.frankfurter.app)（欧洲央行，免费无 key）获取实时汇率（JPY → CNY / HKD / USD），网络不通时 fallback 到内置汇率
- 前端应用启动时拉取一次汇率，存入 Pinia `ratesStore`
- **日语环境**：价格以 JPY 显示（`¥500,000 JPY`）
- **繁中环境**：价格换算为 CNY 后显示（`¥23,700 CNY`）
- 询价商品：两种语言均显示「ASK」

---

#### 2.5 非功能需求

| 项目 | 要求 |
|------|------|
| 浏览器兼容 | Chrome / Safari / 夸克（最新2个主要版本） |
| 首屏加载 | < 2 秒（本地服务环境） |
| 数据库大小 | 预估 < 100MB（7站全量约 3000~6000 条） |
| 图片加载 | 懒加载，避免首屏全量加载 |
| 错误处理 | 某站抓取失败不影响其他站；前端展示来源进度状态 |
| 页面一致性 | 所有页面共享统一 Header / 配色 / 字体规范 |
| 定时任务 | APScheduler 内嵌于 FastAPI 进程，每天 03:00 触发；需配合 macOS「定时唤醒」确保睡眠中也能触发 |

---

### 3. 设计规范

- **风格**：深色系（暗金 + 黑色底），契合 goro's 品牌调性
- **主色**：`#C9A84C`（暗金色）
- **背景**：`#0F0F0F` / `#1A1A1A`，全站背景叠加 goro's 标志性全金特大フェザー轮廓作为水印纹理（透明度约 3~5%）
- **文字**：`#F5F5F5`（主）/ `#999999`（辅）
- **强调色**：`#C9A84C`（金）
- **字体**：`Inter`（数字/拉丁），`Noto Sans JP`（日文），`DM Mono`（价格数字）
- **卡片**：圆角 `8px`，轻微阴影，hover 上浮效果

#### 筛选栏交互规范

筛选条件**不平铺展示**，采用以下方案：
- 顶部筛选栏仅显示「筛选」按钮 + 当前已激活的筛选条数角标（如「筛选 · 3」）
- 点击展开**下拉筛选面板**，分组：来源平台 / 商品品类 / 成色 / 在库状态
- 筛选面板外点击关闭；已选条件以 chip 形式显示

---

## 技术架构

```
┌──────────────────────────────────────────────────────┐
│                    用户浏览器                          │
│         Vue 3 + TypeScript + TailwindCSS              │
│   Vite · Vue Router · Pinia（product / filter / rates）│
└─────────────────────┬────────────────────────────────┘
                      │ HTTP (axios)
                      ▼
┌──────────────────────────────────────────────────────┐
│              后端 API · FastAPI (Python)               │
│  /api/products  /api/products/:id  /api/products/rates│
│  /api/scrape/all  /api/scrape/status  /api/stats      │
│                                                       │
│  APScheduler（内嵌）· 每天 03:00 自动触发全量同步      │
└──────────┬──────────────────────┬────────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────┐    ┌──────────────────────────────┐
│  SQLite 数据库   │    │         Scraper 模块           │
│  products 表    │    │  Shopify API（4站）             │
│  scrape_logs 表 │    │  requests+BS4（3站）            │
└─────────────────┘    │  RINKAN 增量同步（集合差运算）  │
                       └──────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              deltaone.jp   corneronline   nativefeather
              deltaone.hk   yellow-eagle   56s.jp
                                         rinkan-goros.com
```

---

## 目录结构

```
Goros/
├── README.md                        # 本文档（PRD + 架构说明）
│
├── backend/                         # Python 后端
│   ├── app/
│   │   ├── main.py                  # FastAPI 应用入口 + APScheduler 定时任务（03:00）
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── products.py      # 商品列表/详情/汇率接口
│   │   │       └── scrape.py        # 手动触发抓取 & 进度状态接口
│   │   ├── core/
│   │   │   ├── config.py            # 配置（请求延迟、汇率 fallback 等）
│   │   │   └── database.py          # SQLite 连接 & 初始化
│   │   ├── models/
│   │   │   └── product.py           # SQLAlchemy ORM 模型
│   │   ├── schemas/
│   │   │   └── product.py           # Pydantic 请求/响应 Schema
│   │   ├── services/
│   │   │   └── product_service.py   # 业务逻辑层（upsert / stats / categories）
│   │   └── scrapers/
│   │       ├── __init__.py
│   │       ├── base.py              # Scraper 基类（公共方法、run() 流程）
│   │       ├── shopify_base.py      # Shopify JSON API 通用抓取器（含 ASK 检测）
│   │       ├── deltaone_jp.py       # DeltaOne JP（Shopify）
│   │       ├── deltaone_hk.py       # DeltaOne HK（Shopify，HKD）
│   │       ├── corner.py            # Corner（Shopify）
│   │       ├── nativefeather.py     # Native Feather（Shopify，USD）
│   │       ├── truemark.py          # TrueMark（Shopify，shop.yellow-eagle.net）
│   │       ├── fivesix.py           # FiveSix（requests+BS4，Playwright 备用）
│   │       └── rinkan.py            # RINKAN（requests+BS4，增量同步，覆盖 run()）
│   └── requirements.txt
│
├── frontend/                        # Vue 3 前端
│   ├── public/
│   │   └── feather-watermark.svg    # 背景水印羽毛 SVG
│   └── src/
│       ├── components/
│       │   ├── common/
│       │   │   ├── AppHeader.vue    # Header（Sync Now、统计、语言切换 ja|繁中）
│       │   │   ├── ScrapePanel.vue  # 抓取进度浮层（紧凑间距）
│       │   │   └── ...
│       │   └── product/
│       │       ├── ProductCard.vue  # 商品卡片（自动翻译标题、locale 感知价格）
│       │       ├── FilterPanel.vue  # 下拉筛选面板（apply 后触发 fetchProducts）
│       │       └── ...
│       ├── views/
│       │   ├── ListView.vue         # PC 列表页
│       │   ├── DetailView.vue       # PC 详情页（自动翻译标题+描述、locale 价格）
│       │   └── mobile/
│       │       ├── MobileListView.vue
│       │       └── MobileDetailView.vue
│       ├── stores/
│       │   ├── productStore.ts      # 商品列表状态
│       │   ├── filterStore.ts       # 筛选条件状态
│       │   └── ratesStore.ts        # 实时汇率状态（应用启动时拉取一次）
│       ├── locales/
│       │   ├── ja.ts                # 日本語语言包（默认）
│       │   └── zh-TW.ts             # 繁體中文语言包
│       ├── utils/
│       │   ├── api.ts               # axios 实例（含 ratesApi.get()）
│       │   ├── currency.ts          # formatPriceByLocale / isAskPrice / currencyLabel
│       │   └── translate.ts         # Google Translate 免费 API + localStorage 缓存
│       ├── types/index.ts           # TypeScript 类型定义
│       ├── App.vue                  # 根组件（onMounted 拉取汇率）
│       └── main.ts                  # 应用入口（默认 ja，lang_ver=v3）
│
└── start.sh                         # 一键启动脚本
```

---

## 数据源清单

| # | 平台 | 域名 | 抓取方式 | 货币 | 备注 |
|---|------|------|---------|------|------|
| 1 | DeltaOne JP | deltaone.jp | Shopify API | JPY | 最大货源，フェザー tag 过滤 |
| 2 | DeltaOne HK | deltaone.com.hk | Shopify API | HKD | 国际版，部分商品 ASK 定价 |
| 3 | Corner | corneronline.store | Shopify API | JPY | goro's + Chrome Hearts |
| 4 | Native Feather | nativefeather.jp | Shopify API | USD | 官方授权，以新品为主 |
| 5 | TrueMark | shop.yellow-eagle.net | Shopify API | JPY | 9项鉴定，含回购保障 |
| 6 | FiveSix | 56s.jp | requests + BS4 | JPY | 线上专门店；库存不稳定，空库存属正常 |
| 7 | RINKAN | rinkan-goros.com | requests + BS4（增量） | JPY | 综合平台，MakeShop；增量同步降低请求压力 |

---

## 快速启动

### 环境要求

- Python 3.11+
- Node.js 20+
- npm 或 pnpm

### 一键启动

```bash
cd Goros
bash start.sh
```

### 手动分步启动

```bash
# 后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium          # 仅首次需要（FiveSix Playwright 备用）
uvicorn app.main:app --port 8000

# 前端（另开终端）
cd frontend
npm install
npm run dev
```

### 定时任务说明

定时任务已**内嵌于 FastAPI 进程**（APScheduler），无需单独运行：
- 每天 **03:00**（本机时区）自动全量同步所有数据源
- 若后端进程运行中，任务会按时触发；防重入保护确保不会并发执行两次
- **Mac 用户注意**：电脑睡眠时进程挂起，建议在「系统设置 → 电池 → 计划」中设置每天 **02:58 定时唤醒**，确保定时任务正常触发

### 手动触发抓取

在前端页面 Header 右侧点击「Sync Now」按钮即可，实时查看各数据源进度。

---

## 开发计划

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | 项目骨架 + Shopify 通用抓取器 + 数据库 | ✅ 完成 |
| Phase 2 | 5个 Shopify 站数据接入 + 基础列表 API | ✅ 完成 |
| Phase 3 | Vue 前端列表页 + 详情页（PC） | ✅ 完成 |
| Phase 4 | TrueMark / FiveSix / RINKAN 自定义爬虫 | ✅ 完成 |
| Phase 5 | 手机端适配 | ✅ 完成 |
| Phase 6 | 筛选 / 排序 / 搜索 / 分页完善 | ✅ 完成 |
| Phase 7 | 多语言（ja/zh-TW）+ 自动翻译 | ✅ 完成 |
| Phase 8 | 实时汇率（JPY/CNY 按语言切换）+ ASK 价格处理 | ✅ 完成 |
| Phase 9 | RINKAN 增量同步（集合差运算，降低请求量） | ✅ 完成 |
| Phase 10 | APScheduler 定时任务（凌晨 03:00 自动同步） | ✅ 完成 |
| Phase 11 | 样式精调（间距优化、语言按钮顺序、ScrapePanel 紧凑化） | ✅ 完成 |
|| Phase 12 | 品牌 Logo 升级 + TypeScript 全局变量声明修复 | ✅ 完成 |

---

## 更新日志

### v1.0（2026-04-23）

**品牌 Logo 全面升级**

- 将原有对称叶形 SVG 图标替换为 Goros 标志性「上银银绳青松石羽毛」实物照片
- 使用 AI 抠图（rembg / U²-Net 模型）去除白色背景，生成真正的 RGBA 透明通道 PNG
- 同步更新桌面端（`AppHeader.vue`）、手机列表页（`MobileListView.vue`）、手机详情页（`MobileDetailView.vue`）三处 Logo，尺寸分别为 `h-7` / `h-6` / `h-5`，与各端标题字号对齐
- 将 `favicon.svg` 替换为多尺寸 `favicon.ico`（16 / 32 / 48 / 64px），浏览器标签页同步更新

**构建修复**

- 新增 `src/env.d.ts`，声明 Vite `define` 注入的全局变量 `__APP_ENV__` 和 `__ALLOW_MANUAL_SYNC__`，修复 `vue-tsc` 构建时 TS2552 类型报错
