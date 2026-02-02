import pandas as pd

from src.units import F_to_C
from src.controller import thermostat_mode
from src.thermal_model import step_temperature, hvac_heat_flow
from src.hvac_model import heat_energy_kwh


def main():
    # =========================
    # File paths
    # =========================
    WEATHER_CSV = "data/Seattle_Weather_Chart.csv"
    OUTPUT_CSV = "results/sim_rc_thermostat.csv"

    # =========================
    # Time settings (global constant)
    # =========================
    DT_S = 900  # 15 minutes
    dt_s = DT_S  # local name for readability

    # =========================
    # Thermostat settings (US units for user)
    # =========================
    T_set_F = 70.0
    deadband_F = 2.0      # +/- 1 F
    T_init_F = 70.0

    # =========================
    # Building parameters (SI units)
    # =========================
    UA_W_per_K = 250.0
    C_J_per_K = 3.0e7

    # =========================
    # HVAC capacity (thermal power)
    # =========================
    Q_max_heat_W = 12000.0
    Q_max_cool_W = 12000.0  # keep if you allow COOL mode

    # =========================
    # HVAC efficiency
    # =========================
    COP_HEAT = 3.0  # heat pump COP

    # =========================
    # Internal gains
    # =========================
    Q_int_W = 2000.0

    # =========================
    # Load weather data
    # =========================
    df = pd.read_csv(WEATHER_CSV)
    df["datetime"] = pd.to_datetime(df["DateTime"])
    df["T_out_C"] = df["Temperature"].apply(F_to_C)

    # =========================
    # Convert thermostat settings to SI
    # =========================
    T_set_C = F_to_C(T_set_F)
    deadband_C = deadband_F * 5.0 / 9.0
    T_in_C = F_to_C(T_init_F)

    # =========================
    # Storage
    # =========================
    T_in_list = []
    mode_list = []
    Q_hvac_list = []
    E_heat_kWh_list = []

    # =========================
    # Time marching simulation
    # =========================
    for _, row in df.iterrows():
        T_out_C = float(row["T_out_C"])

        mode = thermostat_mode(T_in_C, T_set_C, deadband_C)

        Q_hvac_W = hvac_heat_flow(mode, Q_max_heat_W, Q_max_cool_W)

        # Heating electricity (kWh per timestep)
        E_heat_kWh = heat_energy_kwh(Q_hvac_W, dt_s, COP=COP_HEAT)

        T_next_C = step_temperature(
            T_in_C, T_out_C,
            UA_W_per_K, C_J_per_K,
            Q_int_W, Q_hvac_W,
            dt_s
        )

        T_in_list.append(T_in_C)
        mode_list.append(mode)
        Q_hvac_list.append(Q_hvac_W)
        E_heat_kWh_list.append(E_heat_kWh)

        T_in_C = T_next_C

    # =========================
    # Save results
    # =========================
    out = df.copy()
    out["T_in_C"] = T_in_list
    out["mode"] = mode_list
    out["Q_hvac_W"] = Q_hvac_list
    out["E_heat_kWh"] = E_heat_kWh_list
    out["E_heat_kWh_cum"] = out["E_heat_kWh"].cumsum()

    out.to_csv(OUTPUT_CSV, index=False)

    total_kwh = out["E_heat_kWh"].sum()
    print(f"Simulation finished. Results saved to: {OUTPUT_CSV}")
    print(f"Total heating electricity over window: {total_kwh:.2f} kWh (COP={COP_HEAT})")
    print(out.head())


if __name__ == "__main__":
    main()
