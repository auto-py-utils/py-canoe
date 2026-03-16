import time
from datetime import datetime, timezone
from typing import Optional, Union

from py_canoe.core.child_elements.channels import Channels
from py_canoe.core.child_elements.database_setup import Databases
from py_canoe.core.child_elements.nodes import Nodes
from py_canoe.core.child_elements.ports import Ports
from py_canoe.core.child_elements.replay_collection import ReplayCollection
from py_canoe.core.child_elements.security_configuration import SecurityConfiguration
from py_canoe.core.child_elements.signals import Signal
from py_canoe.core.database_utils.db import fetch_database_info
from py_canoe.helpers.common import logger, wait


class Bus:
    """
    The Bus object represents a bus of the CANoe application.
    """
    def __init__(self, app):
        self.app = app
        self.com_object = self.set_bus('CAN')
        self.VALUE_TABLE_SIGNAL_IS_ONLINE = {
            True: "measurement is running and the signal has been received.",
            False: "The signal is not online."
        }
        self.VALUE_TABLE_SIGNAL_STATE = {
            0: "The default value of the signal is returned.",
            1: "The measurement is not running. The value set by the application is returned.",
            2: "The measurement is not running. The value of the last measurement is returned.",
            3: "The signal has been received in the current measurement. The current value is returned."
        }

    def set_bus(self, bus_type: str = 'CAN'):
        try:
            self.com_object = self.app.com_object.GetBus(bus_type)
            return self.com_object
        except Exception as e:
            logger.error(f"❌ Error retrieving {bus_type} bus: {e}")
            return self.com_object

    @property
    def active(self) -> bool:
        return self.com_object.Active

    @property
    def baudrate(self) -> int:
        return self.com_object.Baudrate()

    @baudrate.setter
    def baudrate(self, value: int):
        self.com_object.SetBaudrate(value)

    @property
    def channels(self) -> 'Channels':
        return Channels(self.com_object.Channels)

    @property
    def databases(self) -> 'Databases':
        return Databases(self.com_object.Databases)

    @property
    def name(self) -> str:
        return self.com_object.Name

    @name.setter
    def name(self, name: str):
        self.com_object.Name = name

    @property
    def nodes(self) -> 'Nodes':
        return Nodes(self.com_object.Nodes)

    @property
    def ports(self) -> 'Ports':
        return Ports(self.com_object.Port)

    @property
    def ports_of_channel(self) -> 'Ports':
        return Ports(self.com_object.PortsOfChannel)

    @property
    def replay_collection(self) -> 'ReplayCollection':
        return ReplayCollection(self.com_object.ReplayCollection)

    @property
    def security_configuration(self) -> 'SecurityConfiguration':
        return SecurityConfiguration(self.com_object.SecurityConfiguration)

    def get_signal(self, channel: int, message: str, signal: str) -> Signal:
        return Signal(self.com_object.GetSignal(channel, message, signal))

    def get_j1939_signal(self, channel: int, message: str, signal: str, source_address: int, destination_address: int) -> Signal:
        return Signal(self.com_object.GetJ1939Signal(channel, message, signal, source_address, destination_address))

    def get_bus_databases_info(self, bus: str = 'CAN', log_info: bool = False) -> dict:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return {}
            databases_info = {}
            self.set_bus(bus_type)
            for db_obj in self.com_object.Databases:
                db_file = getattr(db_obj, 'FullName', '')
                fetched_db_info = fetch_database_info(db_file)
                ecus = list(fetched_db_info.get('ecus', {}).keys())
                frames = list(fetched_db_info.get('frames', {}).keys())
                frames_signals = list(fetched_db_info.get('frames_signals', {}).keys())
                pdus = list(fetched_db_info.get('pdus', {}).keys())
                pdus_signals = list(fetched_db_info.get('pdus_signals', {}).keys())
                info = {
                    'full_name': getattr(db_obj, 'FullName', ''),
                    'path': getattr(db_obj, 'Path', ''),
                    'name': getattr(db_obj, 'Name', ''),
                    'channel': getattr(db_obj, 'Channel', ''),
                    'com_obj': db_obj,
                    'ecus': ecus,
                    'frames': frames,
                    'frames_signals': frames_signals,
                    'pdus': pdus,
                    'pdus_signals': pdus_signals,
                }
                databases_info[info['name']] = info
            if log_info:
                logger.info(f'📜 {bus_type} bus databases information:')
                for db_name, db_info in databases_info.items():
                    logger.info(f"    {db_name}:")
                    for key, value in db_info.items():
                        logger.info(f"        {key}: {value}")
            return databases_info
        except Exception as e:
            logger.error(f"❌ Error retrieving {bus} bus databases information: {e}")
            return {}

    def get_bus_nodes_info(self, bus: str = 'CAN', log_info: bool = False) -> dict:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return {}
            nodes_info = {}
            self.set_bus(bus_type)
            for node_obj in self.com_object.Nodes:
                info = {
                    'full_name': getattr(node_obj, 'FullName', ''),
                    'path': getattr(node_obj, 'Path', ''),
                    'name': getattr(node_obj, 'Name', ''),
                    'active': getattr(node_obj, 'Active', ''),
                    'com_obj': node_obj,
                }
                nodes_info[info['name']] = info
            if log_info:
                logger.info(f'📜 {bus_type} bus nodes information:')
                for node_name, node_info in nodes_info.items():
                    logger.info(f"    {node_name}:")
                    for key, value in node_info.items():
                        logger.info(f"        {key}: {value}")
            return nodes_info
        except Exception as e:
            logger.error(f"❌ Error retrieving {bus} bus nodes information: {e}")
            return {}

    def get_signal_value(self, bus: str, channel: int, message: str, signal: str, raw_value: bool = False) -> Union[int, float, None]:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return None
            self.set_bus(bus_type)
            signal_obj = self.get_signal(channel, message, signal)
            value = signal_obj.raw_value if raw_value else signal_obj.value
            logger.info(f"🚦Signal({signal_obj.full_name}) value = {value}")
            return value
        except Exception as e:
            logger.error(f"❌ Error retrieving {bus} bus signal value: {e}")
            return None

    def set_signal_value(self, bus: str, channel: int, message: str, signal: str, value: Union[int, float], raw_value: bool = False) -> bool:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return False
            self.set_bus(bus_type)
            signal_obj = self.get_signal(channel, message, signal)
            if raw_value:
                signal_obj.raw_value = int(value)
            else:
                signal_obj.value = value
            logger.info(f"🚦Signal({signal_obj.full_name}) value set to {value}")
            return True
        except Exception as e:
            logger.error(f"❌ Error setting {bus} bus signal value: {e}")
            return False

    def get_signal_full_name(self, bus: str, channel: int, message: str, signal: str) -> Union[str, None]:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return None
            self.set_bus(bus_type)
            signal_obj = self.get_signal(channel, message, signal)
            full_name = signal_obj.full_name
            logger.info(f'🚦Signal full name = {full_name}')
            return full_name
        except Exception as e:
            logger.error(f"❌ Error retrieving {bus} bus signal full name: {e}")
            return None

    def check_signal_online(self, bus: str, channel: int, message: str, signal: str) -> bool:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return False
            self.set_bus(bus_type)
            signal_obj = self.get_signal(channel, message, signal)
            is_online = signal_obj.is_online
            logger.info(f'🚦Signal({signal_obj.full_name}) is online ?: {is_online} ({self.VALUE_TABLE_SIGNAL_IS_ONLINE[is_online]})')
            return is_online
        except Exception as e:
            logger.error(f"❌ Error checking {bus} bus signal online status: {e}")
            return False

    def check_signal_state(self, bus: str, channel: int, message: str, signal: str) -> int:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return -1
            self.set_bus(bus_type)
            signal_obj = self.get_signal(channel, message, signal)
            state = signal_obj.state
            logger.info(f'🚦Signal({signal_obj.full_name}) state: {state} ({self.VALUE_TABLE_SIGNAL_STATE[state]})')
            return state
        except Exception as e:
            logger.error(f"❌ Error checking {bus} bus signal state: {e}")
            return -1

    def profile_signal_value(
        self,
        bus: str,
        channel: int,
        message: str,
        signal: str,
        duration: float = 1.0,
        interval: float = 0.0,
        raw_value: bool = False,
        max_samples: Optional[int] = None,
        include_samples: bool = False,
        include_timestamps: bool = False,
    ) -> dict:
        if duration <= 0:
            return {
                "count": 0,
                "duration": 0.0,
                "min": None,
                "max": None,
                "mean": None,
                "std": None,
                **({"samples": []} if include_samples else {}),
                **({"timestamps": []} if include_timestamps else {}),
            }

        bus_type = bus.upper()
        if bus_type not in self.app.bus_types:
            logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
            return {}

        self.set_bus(bus_type)
        try:
            signal_obj = self.get_signal(channel, message, signal)
        except Exception as e:
            logger.error(f"❌ Error retrieving signal object for profiling: {e}")
            return {}

        value_getter = (lambda: signal_obj.raw_value) if raw_value else (lambda: signal_obj.value)

        start = time.perf_counter()
        end_time = start + duration
        count = 0
        mean = 0.0
        m2 = 0.0
        min_value = float("inf")
        max_value = float("-inf")
        samples = [] if include_samples else None
        timestamps = [] if include_timestamps else None
        logger.info(f"📊 Starting signal profiling for {message}::{signal} on {bus} bus for duration {duration}s with interval {interval}s...")
        while True:
            now = time.perf_counter()
            if now >= end_time:
                break
            if max_samples is not None and count >= max_samples:
                break

            value = value_getter()
            # Avoid breaking on missing signals; just skip them
            if value is None:
                if interval > 0:
                    wait(interval)
                continue

            try:
                numeric = float(value)
            except Exception:
                # If value is not numeric, keep the raw value
                numeric = value

            if include_samples:
                samples.append(numeric)
            if include_timestamps:
                timestamps.append(time.time())

            if isinstance(numeric, (int, float)) and not isinstance(numeric, bool):
                count += 1
                if numeric < min_value:
                    min_value = numeric
                if numeric > max_value:
                    max_value = numeric

                # Welford's online algorithm for mean and variance
                delta = numeric - mean
                mean += delta / count
                delta2 = numeric - mean
                m2 += delta * delta2
            else:
                # For non-numeric samples we still count them, but cannot compute stats
                count += 1

            if interval > 0:
                wait(interval)

        duration_actual = time.perf_counter() - start
        variance = m2 / (count - 1) if count > 1 else None
        std = variance**0.5 if variance is not None else None

        profiled_signal = {
            "count": count,
            "duration": duration_actual,
            "min": None if count == 0 else (None if min_value == float("inf") else min_value),
            "max": None if count == 0 else (None if max_value == float("-inf") else max_value),
            "mean": None if count == 0 else mean,
            "std": std,
            **({"samples": samples} if include_samples else {}),
            **({"timestamps": timestamps} if include_timestamps else {}),
        }
        logger.info(
            f"📊 Completed signal profiling for {message}::{signal} on {bus} bus: count={count}, duration={duration_actual:.2f}s, "
            f"min={profiled_signal['min']}, max={profiled_signal['max']}, mean={profiled_signal['mean']}, std={profiled_signal['std']}"
        )
        return profiled_signal

    def get_j1939_signal_value(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, raw_value=False) -> Union[float, int, None]:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return None
            self.set_bus(bus_type)
            signal_obj = self.get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            signal_value = signal_obj.raw_value if raw_value else signal_obj.value
            logger.info(f'🚦J1939 Signal({signal_obj.full_name}) value = {signal_value}')
            return signal_value
        except Exception as e:
            logger.error(f"❌ Error retrieving J1939 bus signal value: {e}")
            return None

    def set_j1939_signal_value(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int, value: Union[float, int], raw_value: bool = False) -> bool:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return False
            self.set_bus(bus_type)
            signal_obj = self.get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            if raw_value:
                signal_obj.raw_value = int(value)
            else:
                signal_obj.value = value
            logger.info(f'🚦J1939 Signal({signal_obj.full_name}) value set to {value}')
            return True
        except Exception as e:
            logger.error(f"❌ Error setting J1939 bus signal value: {e}")
            return False

    def get_j1939_signal_full_name(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> Union[str, None]:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return None
            self.set_bus(bus_type)
            signal_obj = self.get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            full_name = signal_obj.full_name
            logger.info(f'🚦J1939 Signal full name = {full_name}')
            return full_name
        except Exception as e:
            logger.error(f"❌ Error retrieving J1939 bus signal full name: {e}")
            return None

    def check_j1939_signal_online(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> bool:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return False
            self.set_bus(bus_type)
            signal_obj = self.get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            is_online = signal_obj.is_online
            logger.info(f'🚦J1939 Signal({signal_obj.full_name}) is online ?: {is_online} ({self.VALUE_TABLE_SIGNAL_IS_ONLINE[is_online]})')
            return is_online
        except Exception as e:
            logger.error(f"❌ Error checking J1939 bus signal online status: {e}")
            return False

    def check_j1939_signal_state(self, bus: str, channel: int, message: str, signal: str, source_addr: int, dest_addr: int) -> int:
        try:
            bus_type = bus.upper()
            if bus_type not in self.app.bus_types:
                logger.error(f"❌ Invalid bus type '{bus_type}'. Supported types: {', '.join(self.app.bus_types)}")
                return -1
            self.set_bus(bus_type)
            signal_obj = self.get_j1939_signal(channel, message, signal, source_addr, dest_addr)
            state = signal_obj.state
            logger.info(f'🚦J1939 Signal({signal_obj.full_name}) state: {state} ({self.VALUE_TABLE_SIGNAL_STATE[state]})')
            return state
        except Exception as e:
            logger.error(f"❌ Error checking J1939 bus signal state: {e}")
            return -1
