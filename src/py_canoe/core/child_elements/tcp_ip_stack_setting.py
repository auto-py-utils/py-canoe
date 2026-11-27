from py_canoe.core.com_session import dispatch_com_object


class TcpIpAdapter:
    """Wrapper for a single TCP/IP adapter in CANoe."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    def __getattr__(self, item):
        return getattr(self.com_object, item)


class TcpIpAdapters:
    """Collection of TcpIpAdapter objects."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    @property
    def count(self) -> int:
        return self.com_object.Count

    def item(self, index: int) -> TcpIpAdapter:
        return TcpIpAdapter(self.com_object.Item(index))


class SecurityConfiguration:
    """Wrapper for the SecurityConfiguration COM object."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    def __getattr__(self, item):
        return getattr(self.com_object, item)


class TcpIpStackSetting:
    """The TcpIpStackSetting object represents CANoe TCP/IP stack settings."""

    def __init__(self, com_object):
        self.com_object = dispatch_com_object(com_object)

    def __getattr__(self, item):
        return getattr(self.com_object, item)

    @property
    def delayed_ack_enabled(self) -> bool:
        return self.com_object.DelayedAckEnabled

    @delayed_ack_enabled.setter
    def delayed_ack_enabled(self, value: bool):
        self.com_object.DelayedAckEnabled = value

    @property
    def ipv4_default_gateway(self) -> str:
        return self.com_object.IPv4DefaultGateway

    @ipv4_default_gateway.setter
    def ipv4_default_gateway(self, value: str):
        self.com_object.IPv4DefaultGateway = value

    @property
    def ipv6_default_gateway(self) -> str:
        return self.com_object.IPv6DefaultGateway

    @ipv6_default_gateway.setter
    def ipv6_default_gateway(self, value: str):
        self.com_object.IPv6DefaultGateway = value

    @property
    def routing_enabled(self) -> bool:
        return self.com_object.RoutingEnabled

    @routing_enabled.setter
    def routing_enabled(self, value: bool):
        self.com_object.RoutingEnabled = value

    @property
    def security_configuration(self) -> SecurityConfiguration:
        return SecurityConfiguration(self.com_object.SecurityConfiguration)

    @property
    def stack_selection(self) -> int:
        return self.com_object.StackSelection

    @stack_selection.setter
    def stack_selection(self, value: int):
        self.com_object.StackSelection = value

    @property
    def tcp_ip_adapters(self) -> TcpIpAdapters:
        return TcpIpAdapters(self.com_object.TcpIpAdapters)
