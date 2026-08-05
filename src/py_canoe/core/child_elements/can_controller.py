import win32com.client


class CanController:
    """The CANController object represents a CAN controller for a specific channel.

    Wraps the COM ``CANController`` object (see official CANoe COM docs), which
    can be reached via:

        Application » Configuration » GeneralSetup » CANController
        Application » Bus » Channels » Channel » CANController

    Provides baudrate / sample-point configuration through the properties and
    the ``can_set_*`` methods.
    """

    def __init__(self, com_object):
        self.com_object = win32com.client.Dispatch(com_object)

    @property
    def acknowledge(self):
        """Sets or returns the acknowledge type of the CAN controller."""
        return self.com_object.Acknowledge

    @acknowledge.setter
    def acknowledge(self, value: bool):
        self.com_object.Acknowledge = value

    @property
    def baudrate(self):
        """Sets or returns the current baudrate of the CAN controller (bit/s)."""
        return self.com_object.Baudrate

    @baudrate.setter
    def baudrate(self, value: int):
        self.com_object.Baudrate = value

    @property
    def btr0(self):
        """Returns the BTR0 register of the CAN controller (read-only)."""
        return self.com_object.BTR0

    @property
    def btr1(self):
        """Returns the BTR1 register of the CAN controller (read-only)."""
        return self.com_object.BTR1

    @property
    def output_control(self):
        """Sets or returns the Output Control Register of the CAN controller."""
        return self.com_object.OutputControl

    @output_control.setter
    def output_control(self, value: int):
        self.com_object.OutputControl = value

    @property
    def samples(self):
        """Sets or returns the number of times the CAN controller samples (1 or 3)."""
        return self.com_object.Samples

    @samples.setter
    def samples(self, value: int):
        self.com_object.Samples = value

    @property
    def self_ack_enabled(self):
        """Sets or returns the Tx-SelfACK option of the CAN controller."""
        return self.com_object.SelfAckEnabled

    @self_ack_enabled.setter
    def self_ack_enabled(self, value: bool):
        self.com_object.SelfAckEnabled = value

    @property
    def synchronisation(self):
        """Sets or returns the synchronization type of the CAN controller."""
        return self.com_object.Synchronisation

    @synchronisation.setter
    def synchronisation(self, value: int):
        self.com_object.Synchronisation = value

    def can_set_config(self, baudrate: int, tseg1: int, tseg2: int, sjw: int, sam: int, flags: int):
        """Sets the configuration of a CAN channel (switches to CAN mode if it was CAN FD).

        Args:
            baudrate: Baudrate in bit/s (e.g. 500000 for 500 kBit/s).
            tseg1: Length of time segment 1 in time quanta.
            tseg2: Length of time segment 2 in time quanta.
            sjw: Sync jump width in time quanta; cannot be larger than tseg2.
            sam: Number of sampling points (1 or 3).
            flags: 0 = normal mode, 1 = silent mode.
        """
        self.com_object.CANSetConfig(baudrate, tseg1, tseg2, sjw, sam, flags)

    def can_set_fd_arb_phase_config(self, baudrate: int, tseg1: int, tseg2: int, sjw: int, flags: int):
        """Sets the arbitration phase configuration of a CAN FD channel
        (switches to CAN FD mode if it was CAN).

        Args:
            baudrate: Baudrate in bit/s (e.g. 500000 for 500 kBit/s).
            tseg1: Length of time segment 1 in time quanta.
            tseg2: Length of time segment 2 in time quanta.
            sjw: Sync jump width in time quanta; cannot be larger than tseg2.
            flags: Bit 0 = normal(0)/silent(1) mode; Bit 1 = ISO(0)/non-ISO(1) CAN FD.
        """
        self.com_object.CANSetFDArbPhaseConfig(baudrate, tseg1, tseg2, sjw, flags)

    def can_set_fd_data_phase_config(self, baudrate: int, tseg1: int, tseg2: int, sjw: int, flags: int):
        """Sets the data phase configuration of a CAN FD channel
        (switches to CAN FD mode if it was CAN).

        Args:
            baudrate: Baudrate in bit/s (e.g. 2000000 for 2 MBit/s).
            tseg1: Length of time segment 1 in time quanta.
            tseg2: Length of time segment 2 in time quanta.
            sjw: Sync jump width in time quanta; cannot be larger than tseg2.
            flags: Bit 0 = normal(0)/silent(1) mode; Bit 1 = ISO(0)/non-ISO(1) CAN FD.
        """
        self.com_object.CANSetFDDataPhaseConfig(baudrate, tseg1, tseg2, sjw, flags)

    def set_btr(self, btr0: int, btr1: int):
        """Sets the BTR registers of the CAN controller.

        Args:
            btr0: The value of the BTR0 register.
            btr1: The value of the BTR1 register.
        """
        self.com_object.SetBTR(btr0, btr1)
