# Thermal model utilities
# - 1-zone RC (resistance–capacitance) building model
# - Simple on/off HVAC heat input


# Update indoor temperature using a first-order RC thermal model
def step_temperature(
    T_in_C: float,
    T_out_C: float,
    UA_W_per_K: float,
    C_J_per_K: float,
    Q_int_W: float,
    Q_hvac_W: float,
    dt_s: float
) -> float:
    """
    One-step indoor temperature update (Euler forward).

    Physical meaning:
    - UA*(T_out - T_in): heat exchange through envelope
    - Q_int: internal gains
    - Q_hvac: HVAC heat input (heating +, cooling -)
    """

    # Heat transfer through building envelope
    Q_env_W = UA_W_per_K * (T_out_C - T_in_C)

    # Net heat flow into the zone
    Q_net_W = Q_env_W + Q_int_W + Q_hvac_W

    # Temperature update
    T_next_C = T_in_C + (dt_s / C_J_per_K) * Q_net_W

    return T_next_C


# Map thermostat mode to HVAC heat flow (ideal on/off model)
def hvac_heat_flow(
    mode: str,
    Q_max_heat_W: float,
    Q_max_cool_W: float
) -> float:
    """
    Convert thermostat mode into HVAC heat flow.

    Assumptions:
    - ON/OFF control
    - When ON, HVAC delivers maximum capacity
    """

    if mode == "HEAT":
        return Q_max_heat_W          # heating adds heat
    elif mode == "COOL":
        return -Q_max_cool_W         # cooling removes heat
    else:
        return 0.0                  # HVAC OFF
