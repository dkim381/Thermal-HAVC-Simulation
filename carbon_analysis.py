# results/carbon_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from src.carbon_model import add_heatpump_carbon


def format_time_axis(ax):
    locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)


def main():
    INPUT_CSV = "results/sim_rc_thermostat.csv"
    OUT_CSV = "results/sim_with_carbon.csv"

    # IMPORTANT: must match your simulation timestep
    DT_S = 900  # 15 min

    # Assumption: electricity emissions factor (kg CO2 / kWh)
    elec_kgco2_per_kwh = 0.30

    # Compare COP scenarios (resistance vs heat pump)
    cops = (1.0, 3.0)

    # =========================
    # Load
    # =========================
    df = pd.read_csv(INPUT_CSV)

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
    elif "DateTime" in df.columns:
        df["datetime"] = pd.to_datetime(df["DateTime"])
    else:
        raise ValueError("No datetime column found (expected 'datetime' or 'DateTime').")

    df = df.sort_values("datetime").reset_index(drop=True)

    # =========================
    # Add carbon columns
    # =========================
    out = add_heatpump_carbon(
        df,
        dt_s=DT_S,
        elec_kgco2_per_kwh=elec_kgco2_per_kwh,
        cops=cops
    )

    # Save CSV
    out.to_csv(OUT_CSV, index=False)
    print(f"Saved: {OUT_CSV}")

    # =========================
    # Summary print
    # =========================
    print("\n==== Carbon Summary (total over window) ====")
    for cop in cops:
        tag = str(cop).replace(".", "p")
        e_total = out[f"E_heat_elec_kWh_COP{tag}"].sum()
        c_total = out[f"CO2_kg_COP{tag}"].sum()
        print(f"COP={cop}: Elec={e_total:.2f} kWh, CO2={c_total:.2f} kg")

    # Savings COP3 vs COP1
    if 1.0 in cops and 3.0 in cops:
        c1 = out["CO2_kg_COP1p0"].sum()
        c3 = out["CO2_kg_COP3p0"].sum()
        if c1 > 0:
            print(f"\nCOP=3 vs COP=1 CO2 reduction: {(c1-c3):.2f} kg ({100*(c1-c3)/c1:.1f}%)")

    # =========================
    # Plots (2-day zoom)
    # =========================
    zoom_days = 2
    t0 = out["datetime"].min()
    t1 = t0 + pd.Timedelta(days=zoom_days)
    z = out[(out["datetime"] >= t0) & (out["datetime"] <= t1)].copy()

    # Plot 1: cumulative CO2 (zoom window)
    fig, ax = plt.subplots()
    for cop in cops:
        tag = str(cop).replace(".", "p")
        ax.plot(z["datetime"], z[f"CO2_kg_COP{tag}_cum"], label=f"CO2 cum (COP={cop})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative CO2 (kg)")
    ax.legend(loc="upper left")
    format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(f"results/zoom_co2_cum_{zoom_days}days.png", dpi=220)
    plt.close(fig)

    # Plot 2: total CO2 bar (full window)
    labels = []
    totals = []
    for cop in cops:
        tag = str(cop).replace(".", "p")
        labels.append(f"COP {cop}")
        totals.append(out[f"CO2_kg_COP{tag}"].sum())

    fig, ax = plt.subplots()
    ax.bar(labels, totals)
    ax.set_ylabel("Total CO2 (kg) over window")
    ax.set_title("Heating CO2 Comparison (Electric)")
    fig.tight_layout()
    fig.savefig("results/co2_compare_bar.png", dpi=220)
    plt.close(fig)

    print("\nSaved plots:")
    print(f"- results/zoom_co2_cum_{zoom_days}days.png")
    print("- results/co2_compare_bar.png")


if __name__ == "__main__":
    main()
