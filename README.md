# MLB Daily Schedule ETL Pipeline

這是一個自動化的資料工程專題，透過 Python 每天定時抓取 MLB 官方 API 的比賽賽程與比分資料，並寫入 MariaDB 資料庫，建立每日更新的棒球資料庫。

此專案展示完整的 ETL 流程設計、資料庫操作與排程自動化，適合作為資料工程師轉職作品。

---

## 📊 專案架構

lb-data-pipeline/
│
├─ scripts/
│ └─ fetch_mlb_schedule.py # 主程式：抓 MLB API → 清洗 → 寫入 DB
│
├─ data/ # 預留資料存放資料夾
├─ logs/ # cron 排程執行紀錄
└─ README.md


---

## ⚙️ 技術棧（Tech Stack）

- Python 3
- requests
- pymysql
- MariaDB
- Linux (Ubuntu on GCP VM)
- Cron 自動排程
- Git / GitHub

---

## 🔄 ETL 流程說明

1. **Extract（擷取）**  
   - 從 MLB 官方 Stats API 取得每日賽程與比分資料  

2. **Transform（轉換）**  
   - 解析 JSON  
   - 擷取比賽日期、主隊、客隊、比分、狀態、gamePk  

3. **Load（載入）**  
   - 將資料 Upsert 寫入 MariaDB 資料表 `mlb_games`  
   - 避免重複資料  

---

## ⏰ 自動化排程

本專案使用 Linux cron 排程，每天台灣時間 23:00 自動執行：

```bash
0 23 * * * /home/jacketman0112/.venv/bin/python /home/jacketman0112/mlb-data-pipeline/scripts/fetch_mlb_schedule.py >> /home/jacketman0112/mlb-data-pipeline/logs/cron.log 2>&1

🗄️ 資料表設計（mlb_games）

欄位包含：

game_pk (主鍵)

game_date

home_team

away_team

home_score

away_score

status

使用方式

建立虛擬環境並安裝套件：

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


執行程式
python scripts/fetch_mlb_schedule.py

專案特色

串接真實官方 API（MLB Stats API）

完整 ETL 流程實作

資料庫 Upsert 防重複設計

Cron 排程自動化每日更新

部署於 Google Cloud VM

未來可擴充方向

增加球員數據、投打成績

建立球隊勝率統計表

串接 Airflow / Cloud Composer

建立 Dashboard（Tableau / Looker Studio）

作者

Mike（資料工程轉職學習專題）