"""Extra MQTT sensors and calculations from one successful scrape."""
from datetime import datetime
import math

def sensor(name, register, unit=None, device_class=None, state_class=None, **extra):
    result = dict(name=name, register=register, sensor_type="sensor", **extra)
    if unit: result["unit"] = unit
    if device_class: result["dev_class"] = device_class
    if state_class: result["state_class"] = state_class
    return result

DIRECT = [
    sensor("Total Generation", "total_power_yields", "kWh", "energy", "total_increasing"),
    sensor("Monthly Generation", "monthly_power_yields", "kWh", "energy", "total_increasing"),
    sensor("Yearly PV Generation", "yearly_pv_energy_yields", "kWh", "energy", "total_increasing"),
    sensor("Total Running Time", "total_running_time", "h", "duration", "total_increasing"),
    sensor("Daily Running Time", "daily_running_time", "min", "duration", "total_increasing"),
    sensor("Nominal Power", "nominal_active_power", "kW", "power", "measurement"),
    sensor("Grid Frequency", "grid_frequency", "Hz", "frequency", "measurement"),
    sensor("Power Factor", "power_factor", state_class="measurement"),
    sensor("Apparent Power", "total_apparent_power", "VA", "apparent_power", "measurement"),
    sensor("Reactive Power", "total_reactive_power", "var", "reactive_power", "measurement"),
    sensor("Status", "work_state_1"),
    sensor("System Status", "system_state"),
    sensor("Alarm Code", "alarm_code_1"),
    sensor("Inverter Alarm", "inverter_alarm"),
    sensor("ARM Firmware", "arm_software_version"),
    sensor("DSP Firmware", "dsp_software_version"),
    sensor("Serial Number", "serial_number"),
    sensor("Daily Export Energy", "daily_export_energy", "kWh", "energy", "total_increasing"),
    sensor("Total Export Energy", "total_export_energy", "kWh", "energy", "total_increasing"),
    sensor("Daily Import Energy", "daily_import_energy", "kWh", "energy", "total_increasing"),
    sensor("Total Import Energy", "total_import_energy", "kWh", "energy", "total_increasing"),
]
for i in range(1, 13):
    DIRECT += [sensor(f"MPPT {i} Voltage", f"mppt_{i}_voltage", "V", "voltage", "measurement"),
               sensor(f"MPPT {i} Current", f"mppt_{i}_current", "A", "current", "measurement")]

DERIVED = [
    sensor("Equivalent Sun Hours", "equivalent_sun_hours", "h", "duration", "measurement", requires=["daily_power_yields", "nominal_active_power"]),
    sensor("Inverter Utilization", "inverter_utilization", "%", state_class="measurement", requires=["total_active_power", "nominal_active_power"]),
    sensor("Conversion Efficiency Estimated", "conversion_efficiency_estimated", "%", state_class="measurement", requires=["total_active_power", "total_dc_power"]),
    sensor("Grid Current Estimated", "grid_current_estimated", "A", "current", "measurement", requires=["total_active_power", "phase_a_voltage", "output_type"]),
    sensor("Last Communication", "last_communication", device_class="timestamp", always=True),
]
for i in range(1, 13):
    DERIVED.append(sensor(f"MPPT {i} Power", f"mppt_{i}_power", "W", "power", "measurement", requires=[f"mppt_{i}_voltage", f"mppt_{i}_current"]))

def additional_sensors():
    return DIRECT + DERIVED

def calculate(values):
    result = {"last_communication": datetime.now().astimezone().isoformat(timespec="seconds")}
    def number(key):
        value = values.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            return value
        return None
    for i in range(1, 13):
        v, a = number(f"mppt_{i}_voltage"), number(f"mppt_{i}_current")
        if v is not None and a is not None and v >= 0 and a >= 0:
            result[f"mppt_{i}_power"] = round(v * a, 2)
    p, nominal, energy, dc = map(number, ["total_active_power", "nominal_active_power", "daily_power_yields", "total_dc_power"])
    if nominal is not None and nominal > 0:
        if energy is not None and energy >= 0:
            result["equivalent_sun_hours"] = round(energy / nominal, 3)
        if p is not None and p >= 0:
            result["inverter_utilization"] = round(100 * p / (nominal * 1000), 2)
    if p is not None and dc is not None and dc > 0 and 0 <= p <= dc:
        result["conversion_efficiency_estimated"] = round(100 * p / dc, 2)
    # Active-current equivalent at PF=1. Only calculate for a known wiring type.
    wiring = values.get("output_type")
    voltages = [number("phase_a_voltage")]
    if wiring == "3P4L": voltages += [number("phase_b_voltage"), number("phase_c_voltage")]
    if wiring in ("2P", "3P4L") and p is not None and p >= 0 and all(v is not None and v > 0 for v in voltages):
        result["grid_current_estimated"] = round(p / sum(voltages), 3)
    return result
