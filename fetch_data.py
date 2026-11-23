import requests, pandas as pd

LAT, LON = 31.5497, 74.3436   # Lahore
START, END = "2022-08-01", "2026-11-20"
TZ = "Asia/Karachi"

def get(url, hourly):
    p = dict(latitude=LAT, longitude=LON, start_date=START, end_date=END,
             hourly=hourly, timezone=TZ)
    r = requests.get(url, params=p, timeout=120)
    r.raise_for_status()
    return pd.DataFrame(r.json()["hourly"])

aq = get("https://air-quality-api.open-meteo.com/v1/air-quality", "pm2_5,pm10")
wx = get("https://archive-api.open-meteo.com/v1/archive",
         "temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure")

df = aq.merge(wx, on="time")
df["time"] = pd.to_datetime(df["time"])
daily = df.set_index("time").resample("D").mean().dropna()
daily.to_csv("lahore_daily.csv")
print(daily.shape)
print(daily.describe().T)