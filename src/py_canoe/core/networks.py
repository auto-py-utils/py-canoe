import time
from typing import Union

from py_canoe.helpers.common import logger
from py_canoe.helpers.common import wait
from py_canoe.core.child_elements.diagnostic import Diagnostic
from py_canoe.core.child_elements.network import Network


class Networks:
    """
    The Networks object represents the networks of CANoe.
    """
    def __init__(self, app):
        self.com_object = app.com_object.Networks
        self.diagnostic_devices: dict[str, Diagnostic] = dict()

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> Network:
        return Network(self.com_object.Item(index))

    def get_all_network_names(self) -> list[str]:
        try:
            count = self.count
            names = []
            for i in range(1, count + 1):
                network = self.item(i)
                name = network.name
                if name is not None:
                    names.append(name)
            logger.info(f'networks: {names}')
            return names
        except Exception as e:
            logger.error(f"Error retrieving network names: {e}")
            return []

    def fetch_diagnostic_devices(self):
        try:
            for i in range(1, self.count + 1):
                network = self.item(i)
                for j in range(1, network.devices.count + 1):
                    device = network.devices.item(j)
                    try:
                        diagnostic = getattr(device.com_object, 'Diagnostic', None)
                        if diagnostic:
                            self.diagnostic_devices[device.name] = Diagnostic(diagnostic)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"❌ Error fetching Diagnostic Devices: {e}")
            return None

    def send_diag_request(self, diag_ecu_qualifier_name: str, request: str, request_in_bytes=True, return_sender_name=False, response_in_bytearray=False, timeout: float = 10.0, poll_s: float = 0.01) -> Union[str, dict]:
        try:
            diag_devices = self.diagnostic_devices
            if not diag_devices or diag_ecu_qualifier_name not in diag_devices:
                self.fetch_diagnostic_devices()
                diag_devices = self.diagnostic_devices
            diag_device = diag_devices.get(diag_ecu_qualifier_name)
            if diag_device:
                if request_in_bytes:
                    diag_req_in_bytes = bytearray()
                    byte_stream = ''.join(request.split(' '))
                    for i in range(0, len(byte_stream), 2):
                        diag_req_in_bytes.append(int(byte_stream[i:i + 2], 16))
                    diag_request = diag_device.create_request_from_stream(diag_req_in_bytes)
                else:
                    diag_request = diag_device.create_request(request)
                diag_request.send()
                logger.info(f'💉 {diag_ecu_qualifier_name}: Diagnostic Request = {request}')
                start_time = time.time()
                while (diag_request.responses.count == 0 and (time.time() - start_time) < timeout):
                    if (time.time() - start_time) >= timeout:
                        logger.warning(f"Diagnostic request timed out after {timeout}s: {request}")
                        return f"ERROR: timeout after {timeout}s"
                    wait(poll_s)
                if diag_request.responses.count > 0:
                    wait(poll_s)
                diag_responses_dict = {}
                diag_response_including_sender_name = {}
                for i in range(1, diag_request.responses.count + 1):
                    diag_response = diag_request.responses.item(i)
                    diag_response_positive = diag_response.positive
                    response_code = diag_response.response_code
                    response_sender = diag_response.sender
                    response_stream = diag_response.stream
                    response_stream_in_str = " ".join(f"{d:02X}" for d in response_stream).upper()
                    diag_responses_dict[response_sender] = {
                        "positive": diag_response_positive,
                        "response_code": response_code,
                        "stream": response_stream,
                        "stream_in_str": response_stream_in_str
                    }
                    if response_in_bytearray:
                        diag_response_including_sender_name[response_sender] = response_stream
                    else:
                        diag_response_including_sender_name[response_sender] = response_stream_in_str
                    if diag_response_positive:
                        logger.info(f'🟢 {response_sender}: Diagnostic Response = {response_stream_in_str}')
                    else:
                        logger.info(f'🔴 {response_sender}: Diagnostic Response = {response_stream_in_str}')
                if return_sender_name:
                    return diag_response_including_sender_name
                if diag_ecu_qualifier_name in diag_response_including_sender_name:
                    return diag_response_including_sender_name[diag_ecu_qualifier_name]
                return next(iter(diag_response_including_sender_name.values()), "")
            else:
                logger.warning(f'⚠️ No responses received for request: {request}')
                return {"error": "No responses received"}
        except Exception as e:
            logger.error(f"❌ Error sending diagnostic request: {e}")
            return {"error": str(e)}

    def control_tester_present(self, diag_ecu_qualifier_name: str, value: bool) -> bool:
        try:
            diag_device: Diagnostic = self.diagnostic_devices.get(diag_ecu_qualifier_name)
            if diag_device:
                if value:
                    diag_device.diag_start_tester_present()
                    logger.info(f'✔️ {diag_ecu_qualifier_name}: Tester Present started 🏃')
                else:
                    diag_device.diag_stop_tester_present()
                    logger.info(f'⏹️ {diag_ecu_qualifier_name}: Tester Present stopped 🧍')
                return True
            else:
                logger.warning(f'⚠️ No diagnostic device found for: {diag_ecu_qualifier_name}')
                return False
        except Exception as e:
            logger.error(f"❌ Error controlling tester present: {e}")
            return False
