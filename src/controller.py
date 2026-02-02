def thermostat_mode(T_in, T_set, deadband):
    """
    Simple thermostat with deadband.
    - If T_in < T_set - deadband/2  -> HEAT
    - If T_in > T_set + deadband/2  -> COOL
    - Else -> OFF
    """
    low = T_set - deadband / 2.0
    high = T_set + deadband / 2.0

    if T_in < low:
        return "HEAT"
    elif T_in > high:
        return "COOL"
    else:
        return "OFF"
