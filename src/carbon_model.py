import pandas as pd


def add_heatpump_carbon(
    df: pd.DataFrame,
    dt_s: float,
    elec_kgco2_per_kwh: float = 0.30,
    cops=(1.0, 3.0)
) -> pd.DataFrame:
    """
    Adds heating electricity (kWh) and CO2 (kg) columns for COP scenarios.

    Required column:
    - Q_hvac_W : HVAC heat added to zone [W] (heating +, cooling -)
    """
    if "Q_hvac_W" not in df.columns:
        raise ValueError("df must contain 'Q_hvac_W'")

    out = df.copy()

    # Heating thermal energy delivered per step [kWh_th] (cooling/negative -> 0)
    Q_heat_W = out["Q_hvac_W"].clip(lower=0.0)
    E_heat_th_kWh = (Q_heat_W * (dt_s / 3600.0)) / 1000.0
    out["E_heat_th_kWh"] = E_heat_th_kWh

    # For each COP: electricity [kWh] and CO2 [kg]
    for cop in cops:
        tag = str(cop).replace(".", "p")  # 3.0 -> "3p0"
        e_col = f"E_heat_elec_kWh_COP{tag}"
        c_col = f"CO2_kg_COP{tag}"

        out[e_col] = out["E_heat_th_kWh"] / cop
        out[c_col] = out[e_col] * elec_kgco2_per_kwh

        out[f"{e_col}_cum"] = out[e_col].cumsum()
        out[f"{c_col}_cum"] = out[c_col].cumsum()

    return out
