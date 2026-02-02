"""
Unit conversion utilities (SI <-> US customary)

Conventions:
- Temperature: Fahrenheit (F), Celsius (C)
- Power/heat rate: Watt (W), Btu/hr (Btuh)
"""

# --- Temperature ---

# Convert Fahrenheit to Celsius
def F_to_C(T_F: float) -> float:
    return (T_F - 32.0) * 5.0 / 9.0


# Convert Celsius to Fahrenheit
def C_to_F(T_C: float) -> float:
    return T_C * 9.0 / 5.0 + 32.0


# --- Power / Heat rate ---

# Convert Btu/hr to Watt
def Btuh_to_W(Btuh: float) -> float:
    return Btuh * 0.293071


# Convert Watt to Btu/hr
def W_to_Btuh(W: float) -> float:
    return W * 3.412142
