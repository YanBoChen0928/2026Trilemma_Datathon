# CurbCheck — Datathon Proposal（中文 / English）

> Status: Draft v0.1 · 2026-10-07 · Team size: 3 · Build: Thu 10/8 – Mon 10/12 · Demo Day: Tue 10/13
> Based on the team brief "Datathon brief: CurbCheck & Smoke Day Planner", with data fields verified against the City of Vancouver open data API on 2026-10-07.
> Event: Trilemma × Northeastern Datathon, Vancouver（規則待確認 / rules TBC）

---

## 中文版

### 1. 一句話價值

出發前花 10 秒，看懂一個溫哥華市中心街區的停車規則和取締模式，避免無心收到罰單。CurbCheck 是**規劃工具**，不是即時找車位的工具。

### 2. 要解決的問題

- 市中心的停車規則逐街區不同：時間限制、尖峰時段拖吊區、收費時段。駕駛常常是收到罰單才知道。
- 很多罰單來自「不知道」，例如 PayByPhone 時間過期、沒注意到尖峰時段禁停。
- 市府公開了每一張罰單，但沒有人把這些歷史整理成駕駛可以在 10 秒內查到的資訊。

### 3. 目標使用者

聚焦在**出發前會查、或重複去同一區域**的人：

- **規律開車進城的通勤者**：每週固定去某個地方，值得事先了解附近街區。
- **送貨與維修司機**（最強的使用者）：每天停很多次、常跑重複路線，罰單直接吃掉利潤。
- **事先規劃的訪客**：例如前一晚查好要停哪裡。
- **小店家與活動主辦者**：需要告訴顧客或來賓附近停哪裡比較安全。

**不適用**：想知道「現在哪裡有空位」的人。目前沒有公開的即時停車佔用資料，產品會清楚說明這點。

### 4. 產品定位

- 定位為「**看懂規則、避免無心違規**」，不是「哪裡不會被抓」。
- 每張街區卡片都標示資料期間與來源。
- 是否已有類似工具仍待確認（PayByPhone 等 app 提供費率與付款，但未見提供街區的取締歷史）。

### 5. 資料來源（2026-10-07 實際查詢驗證）

| 資料 | 在 Trilemma 目錄？ | 內容 | 最新資料 / 更新 | 角色 |
| --- | --- | --- | --- | --- |
| 停車罰單 2020–2025 | ✅ `vancouver-parking-tickets` | 約 247 萬筆；100 號街區、街名、**日期（無時間）**、法規條文、違規說明、狀態 | 2020–2025 歷史資料；另有 `parking-tickets`（2026 年 1 至 6 月，Trilemma 連結的版本） | 核心 |
| 停車表 | ❌ 市府開放資料 `parking-meters` | 3,642 個停車表；座標、平日 / 週末費率與時限、尖峰時段、禁停規定 | 2026-10-05 更新 | 核心 |
| 地址 | ✅ `vancouver-property-addresses` | 每個地址的座標，用來把「`1900 YEW ST`」轉成地圖位置 | 每週更新 | 核心（地理對應） |
| 311 市民服務請求 | ✅ `vancouver-311-service-requests` | 「Parking Enforcement Request」約 3.7 萬筆，**有時間戳記與經緯度** | 最新到 10/5 晚間；每日批次 | 補充（時段） |
| 道路封閉 | ✅ `vancouver-road-closures` | 目前的施工項目與路段 | **2026-09-17 後未更新** | 加分（需標示日期） |
| 天氣 | ✅ `open-meteo-weather-forecast`、`noaa-ncei-daily-summaries` | 每日天氣 | 持續更新 | 加分（雨天分析） |
| 停車場位置 | ✅ `osm-overpass` | OSM 停車場與立體停車場 | 持續更新 | 加分（替代選擇） |

所有資料都**不是即時的**。罰單資料目前到 2026 年 6 月底（落後約 3 到 4 個月），停車表是規則資料。

### 6. 方法

- **地理對應**：用地址資料將「100 號街區 + 街名」轉成座標，計算一次後快取。
- **彙總**：依「街區 × 星期幾」計算罰單數與前三大違規類型。
- **取締強度**：有停車表的街區用「每個停車表的罰單數」；沒有停車表的街區只顯示罰單數並標示。
- **時段資訊**：「哪幾個小時有限制」來自停車表規則；311 檢舉時間作為補充，並註明是檢舉、不是實際開罰。
- **白話結論**：依規則模板產生，例如「平日取締很嚴，多數罰單是 PayByPhone 時間過期。」

### 7. MVP 功能

- **Block Map**：市中心街區依取締強度上色。
- **Block Card**：點選街區、選星期幾，顯示罰單量、前三大違規、費率與時限、資料期間。
- **白話結論**：一句話說明這個街區要注意什麼。

### 8. 加分功能

- 「步行 5 分鐘內較安心的街區」。
- 雨天是否影響取締（天氣資料）。
- 311 檢舉時段熱點。
- 附近停車場替代選擇（OSM）。

### 9. 不做的事（Non-goals）

- 不提供即時空位或佔用資訊。
- 不宣稱「被開單的機率」。
- 不涵蓋市中心以外地區（MVP 階段）。
- 不提供規避取締的建議。

### 10. 分工（3 人）

| 角色 | 負責內容 |
| --- | --- |
| A：Data | 抓取與清理罰單、停車表、地址資料；地理對應；街區 × 星期彙總；取締強度指標 |
| B：Map & UI | 地圖、街區卡片、手機版介面、部署 |
| C：Product | 使用者訪談與測試、白話結論文字、限制說明、demo 腳本與簡報 |

### 11. 五天工作進度（Demo Day：週二 10/13）

| 日期 | 全隊 | A：Data | B：Map & UI | C：Product | 完成標準 |
| --- | --- | --- | --- | --- | --- |
| **週四 10/8** | 開場會議（約 1 小時）：鎖定市中心範圍、確認資料格式（欄位與檔名）、確認 datathon 是否允許目錄外資料 | 下載罰單（建議先取 2025 年 1 月至 2026 年 6 月）、停車表、地址資料；檢查缺值 | 建 repo 與地圖骨架；選定地圖套件 | 寫訪談問題；聯絡 5 位會開車進城的測試者 | 有原始資料與可顯示的空白地圖 |
| **週五 10/9** | 晚上同步會議（約 30 分鐘）；向 mentor 確認取締強度指標 | 完成地理對應與「街區 × 星期」彙總；計算取締強度 | 地圖依取締強度上色；街區卡片雛形 | 撰寫白話結論模板；整理常見違規的白話說明 | 地圖上能看到上色的街區 |
| **週六 10/10** | 晚上同步會議；決定加分項 | 加入 311 檢舉時段（補充）；資料品質檢查 | 串接卡片資料；完成結論顯示；手機版 | **找 5 位測試者試用**並記錄回饋 | 可用版本交給測試者 |
| **週日 10/11** | 晚上功能凍結 | 依回饋修正資料問題；撰寫資料來源與限制說明 | 依回饋修 UI；部署（Streamlit 或靜態網頁地圖） | 整理測試回饋；撰寫 demo 腳本 | 功能凍結（feature freeze） |
| **週一 10/12** | 一起排練 demo（至少兩次） | README 與資料說明定稿 | 最後修 bug；確認線上版穩定 | 完成簡報；準備評審可能問的問題 | 可以現場 demo |
| **週二 10/13** | **Demo Day** | | | | 現場展示 |

協作原則：

- 週日晚上之後不再加新功能，只修 bug 與文件。
- 週四開場會議先鎖定資料格式，三人才能平行工作。
- 每晚同步會議只回答三件事：今天完成什麼、明天要做什麼、有沒有卡住。
- 任何人卡住超過 2 小時，就在群組提出。

### 12. Demo 腳本（2 分鐘）

1. 用一個真實的市中心街區開場：「去年這個街區被開了 X 張罰單，大多在平日。」
2. 現場讓評審挑一個街區和星期幾，卡片用一句話回答。
3. 展示測試回饋：「5 位駕駛試用後，他們改變了哪些想法。」
4. 結尾說明下一步：送貨司機的路線模式。

### 13. 風險

- **罰單沒有時間，只有日期**：時段改用停車表規則；311 檢舉時間只作補充，因為檢舉不等於實際開罰。
- **罰單資料落後約 3 到 4 個月**（目前到 2026 年 6 月底）：每張卡片標示資料期間。
- **舊罰單與現行規則可能不一致**：停車表規則 10/5 才更新，若某街區費率或時限改過，舊罰單模式就不一定適用。
- **不是即時資料**：使用者可能以為能找空位，介面上要先說明。
- **取締強度有盲點**：沒有停車表的街區沒有分母，只能顯示罰單數。
- **街區對應座標較繁瑣**：用地址資料計算一次並快取，範圍只限市中心。
- **不含警察開立的罰單**：列入限制說明。
- **道路封閉資料過期**（9/17 後未更新）：只列為加分項，並標示更新日期。
- **定位風險**：避免被理解為教人規避取締。
- **停車表不在 Trilemma 目錄內**：需確認 datathon 規則。

### 14. 待確認問題

1. Datathon 是否允許使用目錄外資料（停車表）？
2. 取締強度指標是否合理？（向 mentor 確認）
3. 要用幾年的罰單資料？只用最近一兩年，可以減少與現行規則不一致的問題。

---

## English Version

### 1. One-Sentence Value

Check a downtown Vancouver block in 10 seconds before you go: understand its parking rules and enforcement patterns, and avoid tickets you didn't see coming. CurbCheck is a **planning tool**, not a live spot finder.

### 2. Problem

- Downtown parking rules change block by block: time limits, rush-hour tow zones, meter hours. Drivers often find out with a ticket.
- Many tickets come from not knowing — an expired PayByPhone session, a rush-hour restriction nobody noticed.
- The City publishes every ticket it issues, but nobody turns that history into something a driver can check in ten seconds.

### 3. Who It's For

People who **check before they go, or return to the same area**:

- **Regular commuters** who drive to the same place each week.
- **Delivery and service drivers** (the strongest users): many stops a day on repeat routes, where tickets eat directly into margins.
- **Visitors planning ahead**, e.g., checking the night before where to park.
- **Small businesses and event organizers** who need to tell customers or guests where to park.

**Not for**: finding an open spot right now. No public real-time occupancy data exists, and the product says so clearly.

### 4. Positioning

- Framed as **understanding the rules and avoiding accidental violations**, not "where won't I get caught."
- Every block card shows its data period and sources.
- Whether similar tools exist is still to be confirmed (apps like PayByPhone show rates and handle payment, but we haven't seen block-level enforcement history).

### 5. Data Sources (Verified Against Live APIs on 2026-10-07)

| Data | In Trilemma catalog? | Content | Latest data / update | Role |
| --- | --- | --- | --- | --- |
| Parking tickets 2020–2025 | ✅ `vancouver-parking-tickets` | ~2.47M records; 100-block, street, **date (no time)**, bylaw section, infraction text, status | 2020–2025 history; plus `parking-tickets` (Jan–Jun 2026, the version the Trilemma catalog links to) | Core |
| Parking meters | ❌ City open data `parking-meters` | 3,642 meters; coordinates, weekday/weekend rates and limits, rush hours, prohibitions | Updated 2026-10-05 | Core |
| Property addresses | ✅ `vancouver-property-addresses` | Coordinates per address, to turn "`1900 YEW ST`" into a map location | Weekly | Core (geocoding) |
| 3-1-1 service requests | ✅ `vancouver-311-service-requests` | ~37k "Parking Enforcement Request" cases **with timestamps and coordinates** | Latest Oct 5 evening; daily batches | Supplementary (hours) |
| Road closures | ✅ `vancouver-road-closures` | Current construction projects and segments | **Not updated since 2026-09-17** | Stretch (show date) |
| Weather | ✅ `open-meteo-weather-forecast`, `noaa-ncei-daily-summaries` | Daily weather | Ongoing | Stretch (rain analysis) |
| Parking lots | ✅ `osm-overpass` | OSM parking lots and parkades | Ongoing | Stretch (alternatives) |

None of these are **real-time**. Ticket data currently runs to the end of June 2026 (about 3–4 months behind); meters are rules data.

### 6. Method

- **Geocoding**: map "100-block + street" to coordinates with the address dataset; compute once and cache.
- **Aggregation**: ticket counts and top 3 infraction types by block × weekday.
- **Enforcement intensity**: tickets per meter on metered blocks; on unmetered blocks, show raw counts with a label.
- **Hours**: "which hours have restrictions" comes from meter rules; 311 request times are supplementary and labeled as complaints, not tickets issued.
- **Plain-language verdict**: generated from templates, e.g., "Heavily enforced on weekdays. Most tickets here are for an expired PayByPhone session."

### 7. MVP Features

- **Block Map**: downtown blocks colored by enforcement intensity.
- **Block Card**: tap a block and pick a weekday to see ticket volume, top 3 infractions, rate and time limit, and the data period.
- **Verdict**: one sentence on what to watch out for on this block.

### 8. Stretch Features

- "A calmer block within a 5-minute walk."
- Whether rain changes enforcement (weather data).
- Hour-of-day hotspots from 311 requests.
- Nearby parking lots as alternatives (OSM).

### 9. Non-Goals

- No real-time availability or occupancy.
- No "probability of getting a ticket."
- No coverage beyond downtown (in the MVP).
- No advice on evading enforcement.

### 10. Team Roles (3 People)

| Role | Responsibilities |
| --- | --- |
| A: Data | Ingest and clean tickets, meters, and addresses; geocoding; block × weekday aggregation; intensity score |
| B: Map & UI | Map, block card, mobile layout, deployment |
| C: Product | User interviews and testing, verdict wording, limitations notes, demo script and slides |

### 11. Five-Day Schedule (Demo Day: Tue 10/13)

| Date | Whole team | A: Data | B: Map & UI | C: Product | Done when |
| --- | --- | --- | --- | --- | --- |
| **Thu 10/8** | Kickoff (~1 hr): lock the downtown area, agree on data format (columns and file names), confirm whether non-catalog data is allowed | Download tickets (start with January 2025 – June 2026), meters, and addresses; check missing values | Set up the repo and map scaffold; choose the map library | Write interview questions; line up 5 testers who drive downtown | Raw data and an empty map that renders |
| **Fri 10/9** | Evening sync (~30 min); check the intensity metric with mentors | Finish geocoding and block × weekday aggregation; compute intensity | Color the map by intensity; block card prototype | Draft verdict templates; write plain-language explanations of common infractions | Colored blocks appear on the map |
| **Sat 10/10** | Evening sync; decide on stretch items | Add 311 request hours (supplementary); data quality checks | Connect card data; show verdicts; mobile layout | **Have 5 testers try it** and record feedback | A usable build is in testers' hands |
| **Sun 10/11** | Feature freeze in the evening | Fix data issues from feedback; write data-source and limitations notes | Fix UI from feedback; deploy (Streamlit or static web map) | Summarize tester feedback; write the demo script | Feature freeze |
| **Mon 10/12** | Rehearse the demo together (at least twice) | Finalize README and data notes | Final bug fixes; confirm the live site is stable | Finish slides; prepare answers to likely judge questions | Ready for a live demo |
| **Tue 10/13** | **Demo Day** | | | | Live demo |

Ground rules:

- No new features after Sunday evening — only bug fixes and docs.
- Lock the data format at Thursday's kickoff so all three can work in parallel.
- Each evening sync answers only three things: what I finished today, what I'll do tomorrow, and whether I'm blocked.
- If anyone is stuck for more than 2 hours, raise it in the group chat right away.

### 12. Demo Script (2 Minutes)

1. Open with one real downtown block: "Last year, this one block got X tickets, mostly on weekdays."
2. Live: a judge picks a block and a day, and the card answers in plain language.
3. Show tester feedback: "5 drivers tried it, and here's what they changed their minds about."
4. Close with what's next: route mode for delivery drivers.

### 13. Risks

- **No time of day on tickets, only dates**: hours come from meter rules; 311 request times are supplementary only, since complaints are not tickets issued.
- **Ticket data lags ~3–4 months** (currently ends 2026-06-30): every card shows its date range.
- **Old tickets vs. current rules**: meter rules were updated on Oct 5; if a block's rate or limit changed, past ticket patterns may not apply.
- **Not real-time**: users may expect spot-finding; the UI says so up front.
- **Intensity blind spots**: blocks without meters have no denominator; show raw counts only.
- **Block-to-map matching is fiddly**: geocode once with the address data, cache it, and keep to downtown.
- **Excludes VPD-issued tickets**: listed as a limitation.
- **Stale road-closure data** (not updated since Sep 17): stretch only, with the update date shown.
- **Framing**: avoid being read as a guide to evading enforcement.
- **Meter data is outside the Trilemma catalog**: confirm datathon rules.

### 14. Open Questions

1. Does the datathon allow non-catalog data (parking meters)?
2. Is the intensity metric sound? (Check with mentors.)
3. How many years of tickets should we use? Using only the last one or two years reduces mismatch with current rules.
