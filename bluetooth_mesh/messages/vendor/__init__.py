from construct import Select

from .thermostat import ThermostatMessage

VendorMessage = Select(
    ThermostatMessage,
)
