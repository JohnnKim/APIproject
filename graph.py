import pandas as pd
import matplotlib.pyplot as plt
import json

with open("precip_colorado.json") as f:
    data = json.load(f)

precip_dict = data["properties"]["parameter"]["PRECTOTCORR"]

df_precip_daily = (
    pd.DataFrame([
        {"date": pd.to_datetime(k), "precip_mm": v}
        for k, v in precip_dict.items()
        if int(k[:4]) >= 2010
    ])
    .sort_values("date")
)

df_fire_archive = pd.read_csv("fire_archive_SV-C2_739413.csv")
df_fire_nrt = pd.read_csv("fire_nrt_SV-C2_739413.csv")

df_fires = pd.concat([df_fire_archive, df_fire_nrt], ignore_index=True)

CO_MIN_LAT, CO_MAX_LAT = 36.9, 41.0
CO_MIN_LON, CO_MAX_LON = -109.1, -102.0

df_fires_co = df_fires[
    (df_fires["latitude"].between(CO_MIN_LAT, CO_MAX_LAT)) &
    (df_fires["longitude"].between(CO_MIN_LON, CO_MAX_LON))
].copy()

df_fires_co["acq_date"] = pd.to_datetime(df_fires_co["acq_date"])

df_fire_daily = df_fires_co.groupby("acq_date").size().reset_index(name="fire_count")

df = pd.merge(df_precip_daily, df_fire_daily, left_on="date", right_on="acq_date", how="left")
df["fire_count"] = df["fire_count"].fillna(0)

fig, ax1 = plt.subplots(figsize=(14,6))

ax1.bar(df["date"], df["precip_mm"], color="blue", alpha=0.3)
ax1.set_ylabel("Precipitation (mm)", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")

ax2 = ax1.twinx()
ax2.plot(df["date"], df["fire_count"], color="red", linewidth=2)
ax2.set_ylabel("Fire Count", color="red")
ax2.tick_params(axis="y", labelcolor="red")

plt.title("Colorado: Daily Precipitation vs Fire Detections")
plt.tight_layout()
plt.show()
