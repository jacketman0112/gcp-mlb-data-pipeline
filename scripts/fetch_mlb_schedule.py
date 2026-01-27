import requests
import pymysql
from datetime import datetime, timedelta, timezone

DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "mlb"),
    charset="utf8mb4",
)

def fetch_schedule(start_date: str, end_date: str):
    url = "https://statsapi.mlb.com/api/v1/schedule"
    params = {
        "sportId": 1,
        "startDate": start_date,
        "endDate": end_date,
        "hydrate": "team,linescore"
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def parse_games(data):
    out = []
    for d in data.get("dates", []):
        game_date = d.get("date")
        for g in d.get("games", []):
            teams = g.get("teams", {})
            home = (teams.get("home") or {}).get("team", {}).get("name")
            away = (teams.get("away") or {}).get("team", {}).get("name")
            home_score = (teams.get("home") or {}).get("score")
            away_score = (teams.get("away") or {}).get("score")
            status = (g.get("status") or {}).get("detailedState")
            game_pk = g.get("gamePk")

            out.append({
                "game_pk": int(game_pk),
                "game_date": game_date,
                "home_team": home,
                "away_team": away,
                "home_score": home_score if home_score is not None else None,
                "away_score": away_score if away_score is not None else None,
                "status": status,
            })
    return out

def upsert_games(conn, games):
    sql = """
    INSERT INTO mlb_games
        (game_pk, game_date, home_team, away_team, home_score, away_score, status)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        game_date = VALUES(game_date),
        home_team = VALUES(home_team),
        away_team = VALUES(away_team),
        home_score = VALUES(home_score),
        away_score = VALUES(away_score),
        status = VALUES(status);
    """
    with conn.cursor() as cur:
        cur.executemany(sql, [
            (
                g["game_pk"], g["game_date"], g["home_team"], g["away_team"],
                g["home_score"], g["away_score"], g["status"]
            )
            for g in games
        ])
    conn.commit()

def main():
    tz_tw = timezone(timedelta(hours=8))
    today = datetime.now(tz=tz_tw).date()

    start_date = today.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    print(f"Fetching MLB schedule: {start_date}")

    data = fetch_schedule(start_date, end_date)
    games = parse_games(data)
    print(f"Parsed games: {len(games)}")

    if not games:
        print("No games found.")
        return

    conn = pymysql.connect(**DB_CONFIG, autocommit=False)
    try:
        upsert_games(conn, games)
        print(f"✅ Upserted {len(games)} games into mlb.mlb_games")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
