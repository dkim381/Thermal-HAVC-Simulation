def heat_energy_kwh(Q_hvac_W: float, dt_s: float, COP: float = 1.0) -> float:
    """
    Convert HVAC thermal heat flow (W) into electrical energy use (kWh).

    Assumptions
    - Heating only: Q_hvac_W > 0 means heating delivered to the zone.
    - Electrical input power = Q_thermal / COP
      (COP=1 -> electric resistance; COP>1 -> heat pump)
    """
    if Q_hvac_W <= 0.0:
        return 0.0

    P_elec_W = Q_hvac_W / COP
    E_Wh = P_elec_W * (dt_s / 3600.0)
    return E_Wh / 1000.0
