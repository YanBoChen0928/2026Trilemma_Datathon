# 下一步執行步驟 — 駕駛視角（Yan-Bo）

> 依據：`mvp_implementation_handoff_en.md`（唯一工程依據）
> 原則：先做出可以 demo 的駕駛視角，市府視角由 Anahid 與 Juwon 平行進行。

---

## 目前進度（更新於 2026-10-11）

- **現在停在：Step 2 停車表前處理**（預計今天 10am–1pm）。
- Step 0：大部分完成，還在等組員回覆兩項（見下方）。
- Step 1：完成，已推到 `YB` 分支；PR `YB → main` 待合併。
- **開新對話時**：告訴 Claude WD 是 `/Users/yanbochen/IdeaProjects/202610_Datathon_Trilemma`，並請它先讀這三份：`next_steps_driver.md`、`mvp_implementation_handoff_en.md`、`CONTRIBUTING.md`。

## Git 流程（每一步都照這個循環）

本機 `main` 只用來同步，永遠不直接 commit，作為「上次合併完成」的乾淨參考點；開發都在 `YB` 上。

```bash
# 1. 更新本機 main
git checkout main
git pull --no-rebase origin main

# 2. 回到 YB，把最新的 main 併進來
git checkout YB
git merge main

# 3. 開發、測試後推送
git add ...
git commit -m "..."
git push

# 4. 在 GitHub 開 PR：YB → main，合併
gh pr create --base main --head YB --web
```

YB 出問題時：`git diff main` 比對差異；`git restore --source=main <檔案>` 還原單一檔案。

---

## Step 0：開工前確認（約 30 分鐘）

- [x] 整合與部署負責人：你（Anahid 可能一起）。你建立 Streamlit app 骨架，並維護 `app.py` 與 `requirements.txt`。
- [x] 共用資料格式：照 handoff §6.1、§9.1。
- [x] Demo 情境：市中心、2026-10-13（星期二，平日）晚上 6:00 抵達、停留 2 小時。
- [ ] Demo 目的地：Step 4 完成後，在市中心試幾個地點，挑「最近的停車表不能推薦、附近仍有合法選項」的地點；做 `Load demo example` 前要確定。
- [x] Python 版本與 `requirements.txt`：見 Step 1。
- [ ] **等組員回覆**：部署平台（建議 Streamlit Community Cloud）。
- [ ] **等組員回覆**：Anahid 與 Juwon 的市府視角分工。
- [ ] 加 Juwon 為 repo 協作者（需要她的 GitHub handle）。

## Step 1：建立專案結構

建議的資料夾配置：

```
app.py                  # Streamlit 入口（你建立並維護）
pages/driver.py         # 駕駛頁面（你）
pages/city.py           # 市府頁面（Anahid、Juwon）
curbcheck/rules.py      # 規則引擎（純函式）
curbcheck/meters.py     # 停車表前處理
data/raw/               # 原始資料快照（註明下載日期）
data/meters_clean.csv   # 前處理輸出
tests/test_rules.py     # 規則引擎測試
requirements.txt
README.md
```

- [x] 虛擬環境：用 pyenv 的 Python 3.11.11 建立 `.venv`（不進 repo）。
- [x] `requirements.txt`：`streamlit==1.65.0`、`folium==0.20.0`、`streamlit-folium==0.27.4`、`pandas==3.0.6`、`pytest==9.1.1`。
- [x] `app.py`、`pages/driver.py`、`pages/city.py`（空白頁）、`curbcheck/__init__.py`、`data/raw/`、`tests/`。
- [x] README：一句話介紹與本機啟動指令（資料快照日期等 Step 2 完成後補上）。
- [x] `.gitignore`：`archive/`、`.venv/`、`data/raw/`、`__pycache__/`、`.pytest_cache/`、`.DS_Store`。
- [x] 驗證：三個頁面都能載入、伺服器健康檢查正常。

本機啟動（終端機要保持開著，關掉後頁面連結會變灰色不能點）：

```bash
source .venv/bin/activate
streamlit run app.py
```

## Step 2：停車表前處理（handoff §6）

- [ ] 從市府開放資料下載 `parking-meters`，存成有日期的快照。
- [ ] 保留原始欄位，另外產生解析後的欄位（費率、分鐘制時限、尖峰起訖、兩組禁停）。
- [ ] 依 §6.2 標記 `supported` 與 `unsupported_reason`：
  - 非 In Service、非 `Any Vehicle`、有固定費率
  - `time_limit_override` 或 `prohibition_override` 為 Yes
  - 必要的費率或時限（平日與週末）為空值、無法解析
  - 尖峰或禁停欄位只填了一部分，或有值但無法解析（整組空白＝沒有該項限制，需先核對原始資料）
  - 座標缺失或無效
- [ ] 時限欄位：`No Time Limit` 寫成 `-1`，空值代表資料缺失。
- [ ] 輸出 `data/meters_clean.csv` 與前處理報告 `data/meters_preprocessing_report.json`（兩者都 commit）。

**檢查點**：可評估筆數應接近全市 2,761、市中心 637（§6.3）。差很多就先查原因。

## Step 3：規則引擎與測試（handoff §7、§12）

- [ ] 寫純函式 `evaluate_meter(meter, arrival_datetime, duration_minutes)`，不依賴 Streamlit。
- [ ] 依 §7.2 的順序實作：晚上 10 點後不支援 → 早於 9 點不支援 → 停用資料 → 平日 / 週末時限 → 尖峰重疊（含 9:00–9:30）→ 兩組禁停 → 6 點切分 → 三種結果判斷（§7.4）→ 按分鐘比例估算費用。
- [ ] 先通過 §12 的 8 個測試，其中跨 6 點用一個 parameterized test 涵蓋三個案例。

**檢查點**：不開 Streamlit，單獨跑 `pytest` 全部通過。

## Step 4：排序（handoff §7.3）

- [ ] 用直線距離找出 250 公尺內的停車表。
- [ ] 只推薦 `supported == True` 且 `legal == True` 的停車表（`legal` 為 `False` 或 `None` 都不推薦），依估算費用、再依距離排序，取前三。
- [ ] 另外評估「最近的停車表」，以便說明它為什麼不能停（包含 unsupported 或 `legal == None` 的情況）。

## Step 5：駕駛頁面（handoff §8）

- [ ] 真實地圖（folium + OpenStreetMap），點選設定目的地，顯示 OSM 來源標註。
- [ ] 輸入：日期、抵達時間、停留時數；旁邊顯示目前支援的範圍。
- [ ] 推薦卡片：停車表 ID、估算費用、約略距離、費率、警告。
- [ ] 無結果、不支援、資料錯誤時的說明。
- [ ] 固定顯示：`Posted signs take precedence.`
- [ ] 加上 `Load demo example` 按鈕。

**檢查點**：本機用 demo 情境完整操作一次。

## Step 6：整合與部署（依 `CONTRIBUTING.md` §7）

- [ ] 第 1 天完成 Step 2 後，**先推一版 `meters_clean.csv`**，讓 City View 的費率圖層不必等待。
- [ ] 本機把駕駛頁面接進共用的 Streamlit app，與 City View 整合。
- [ ] **第 2 天直接部署完整 MVP**，不先部署空骨架。
- [ ] 部署後檢查：兩個頁面能開、資料能載入、地圖能顯示、錯誤有合理提示。
- [ ] 只使用平台內建的執行紀錄，不另外做監控。

## Step 7：收尾

- [ ] 第 3 天中午功能凍結。
- [ ] 錄一段 demo 操作影片，作為現場網路不穩時的備案。
- [ ] 有時間再做加分項：街區提醒（需要市府團隊的 `tickets_block_agg.csv`）。

---

## 時間安排參考

| 時段 | 目標 |
| --- | --- |
| 第 1 天 | Step 0 到 Step 3：前處理完成、規則引擎測試通過 |
| 第 2 天 | Step 4 到 Step 6：排序、頁面、**部署上線** |
| 第 3 天上午 | Step 7：測試、修 bug、錄影 |
| 第 3 天中午後 | 功能凍結、排練 |
