import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from src.units import C_to_F


def format_time_axis(ax):
    locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def compute_duty_cycle(df, rule="1H"):
    df2 = df.copy().set_index("datetime")
    df2["is_heat"] = (df2["mode"].astype(str) == "HEAT").astype(int)
    duty = df2["is_heat"].resample(rule).mean().to_frame("heat_duty")
    return duty.fillna(0.0).reset_index()


def compute_hourly_energy(df, rule="1H"):
    if "E_heat_kWh" not in df.columns:
        raise ValueError("E_heat_kWh not found. Run run.py with HVAC energy enabled.")

    df2 = df.copy().set_index("datetime")
    hourly = df2["E_heat_kWh"].resample(rule).sum().to_frame("E_heat_kWh_hourly")
    hourly["E_heat_kWh_hourly"] = hourly["E_heat_kWh_hourly"].fillna(0.0)
    hourly["E_heat_kWh_cum_hourly"] = hourly["E_heat_kWh_hourly"].cumsum()
    return hourly.reset_index()


def main():
    INPUT_CSV = "results/sim_rc_thermostat.csv"
    OUT_DIR = "results"
    os.makedirs(OUT_DIR, exist_ok=True)

    # Must match run.py (for setpoint lines)
    T_set_F = 70.0
    deadband_F = 2.0

    zoom_days = 2

    # =========================
    # Load results
    # =========================
    df = pd.read_csv(INPUT_CSV)

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
    elif "DateTime" in df.columns:
        df["datetime"] = pd.to_datetime(df["DateTime"])
    else:
        raise ValueError("No datetime column found (expected 'datetime' or 'DateTime').")

    if "Temperature" in df.columns:
        df["T_out_F"] = df["Temperature"]
    else:
        raise ValueError("No outdoor temperature column found (expected 'Temperature').")

    if "T_in_C" not in df.columns:
        raise ValueError("No indoor temperature column found (expected 'T_in_C').")
    df["T_in_F"] = C_to_F(df["T_in_C"])

    df = df.sort_values("datetime").reset_index(drop=True)

    duty = compute_duty_cycle(df, rule="1H")
    energy = compute_hourly_energy(df, rule="1H")

    # =========================
    # Print summary
    # =========================
    heat_runtime_frac = (df["mode"].astype(str) == "HEAT").mean()
    total_kwh = df["E_heat_kWh"].sum()

    print("==== Summary (full window) ====")
    print(f"Indoor Temp (F): mean={df['T_in_F'].mean():.2f}, min={df['T_in_F'].min():.2f}, max={df['T_in_F'].max():.2f}")
    print(f"Outdoor Temp (F): mean={df['T_out_F'].mean():.2f}, min={df['T_out_F'].min():.2f}, max={df['T_out_F'].max():.2f}")
    print(f"Heating runtime fraction (timestep-level): {100*heat_runtime_frac:.1f}%")
    print(f"Hourly duty cycle: mean={100*duty['heat_duty'].mean():.1f}%")
    print(f"Total heating electricity over window: {total_kwh:.2f} kWh")

    # =========================
    # Zoom window slice
    # =========================
    low = T_set_F - deadband_F / 2.0
    high = T_set_F + deadband_F / 2.0

    t0 = df["datetime"].min()
    t1 = t0 + pd.Timedelta(days=zoom_days)

    dfz = df[(df["datetime"] >= t0) & (df["datetime"] <= t1)].copy()
    dutyz = duty[(duty["datetime"] >= t0) & (duty["datetime"] <= t1)].copy()
    energyz = energy[(energy["datetime"] >= t0) & (energy["datetime"] <= t1)].copy()

    # Plot 1: Zoomed temperature
    fig, ax = plt.subplots()
    ax.plot(dfz["datetime"], dfz["T_in_F"], label="Indoor Temp (F)")
    ax.plot(dfz["datetime"], dfz["T_out_F"], label="Outdoor Temp (F)")
    ax.axhline(T_set_F, linestyle="--", linewidth=1.0, alpha=0.7, label="Setpoint (F)")
    ax.fill_between(dfz["datetime"], low, high, alpha=0.15, label="Deadband")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (F)")
    ax.legend(loc="lower right")
    format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/zoom_temp_{zoom_days}days.png", dpi=220)
    plt.close(fig)

    # Plot 2: Zoomed duty cycle
    fig, ax = plt.subplots()
    ax.plot(dutyz["datetime"], 100.0 * dutyz["heat_duty"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Heating Duty Cycle (%)")
    ax.set_ylim(-5, 105)
    format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/zoom_duty_{zoom_days}days.png", dpi=220)
    plt.close(fig)

    # Plot 3: Zoomed hourly heating energy
    fig, ax = plt.subplots()
    ax.plot(energyz["datetime"], energyz["E_heat_kWh_hourly"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Heating Electricity (kWh/hour)")
    format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/zoom_energy_hourly_{zoom_days}days.png", dpi=220)
    plt.close(fig)

    # Plot 4: Zoomed cumulative heating energy
    fig, ax = plt.subplots()
    ax.plot(energyz["datetime"], energyz["E_heat_kWh_cum_hourly"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative Heating Electricity (kWh)")
    format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/zoom_energy_cum_{zoom_days}days.png", dpi=220)
    plt.close(fig)

    print("\nSaved plots:")
    print(f"- {OUT_DIR}/zoom_temp_{zoom_days}days.png")
    print(f"- {OUT_DIR}/zoom_duty_{zoom_days}days.png")
    print(f"- {OUT_DIR}/zoom_energy_hourly_{zoom_days}days.png")
    print(f"- {OUT_DIR}/zoom_energy_cum_{zoom_days}days.png")


if __name__ == "__main__":
    main()
