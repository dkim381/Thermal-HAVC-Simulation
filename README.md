# HVAC RC Thermal & Carbon Model

A simplified **one-zone RC (resistance–capacitance) building thermal model** with  
**thermostat-controlled HVAC**, **energy consumption**, and **CO₂ emissions comparison**.

This project simulates indoor temperature dynamics using real weather data and
compares **electric resistance heating (COP = 1)** with a **heat pump (COP = 3)**
in terms of energy use and carbon emissions.

---

## Features

- **1-zone RC thermal model** (physics-based)
- **Deadband thermostat controller** (HEAT / OFF / COOL)
- **HVAC heating energy calculation** (kWh)
- **CO₂ emissions analysis** for multiple COP scenarios
- **Clear time-series and summary visualizations**

---

## Model Overview

- **Thermal model**  
  Indoor temperature evolves based on envelope heat transfer, internal gains,
  and HVAC heat input using a first-order RC model
  (integrated with forward Euler time stepping).

  C * dT_in/dt = UA * (T_out - T_in) + Q_int + Q_hvac

- **Thermostat control**  
  A deadband thermostat determines HVAC operation to maintain indoor temperature
  around a setpoint.

- **HVAC & energy model**  
  HVAC delivers fixed thermal power when active.  
  Electrical energy consumption is computed as:
  
E_elec = Q_thermal / COP
- **Carbon model**  
  CO₂ emissions are calculated from electricity use using a constant emissions factor
  and compared across COP values (e.g. resistance vs heat pump).

---

## Example Results

- **Stable indoor temperature tracking** within the thermostat deadband despite
  large outdoor temperature variations
- **Heating duty cycle** increases during colder outdoor conditions, as expected
- **~65–70% reduction in electricity use and CO₂ emissions** when using
  a heat pump (COP = 3) compared to electric resistance heating (COP = 1)
- Results visualized using:
  - Indoor vs outdoor temperature
  - Heating duty cycle
  - Hourly & cumulative heating energy
  - Cumulative CO₂ emissions and total CO₂ comparison

---

## Why This Matters

This project demonstrates how **simple physics-based models** can be used to:
- Analyze HVAC control behavior
- Quantify building energy consumption
- Evaluate carbon reduction benefits of high-efficiency heat pumps

The framework is intentionally lightweight but extensible to more advanced
building energy and control studies.
