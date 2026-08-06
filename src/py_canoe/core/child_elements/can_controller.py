import win32com.client
from py_canoe.helpers.common import logger

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




class CanChannelConfiguration:
    """CAN channel bit-timing configuration with linked parameter derivation and validation.

    Parameter relationships (time quantum, TQ)::

        CAN baudrate (kbit/s) = CAN clock (kHz) / (1 + tseg1 + tseg2)
        sample (%)            = (1 + tseg1) / (1 + tseg1 + tseg2) * 100

    Convention: **a default value of 0 means "not provided, derived by the library"**.

    Three ways to construct (choose one):

    1. **By requirement (recommended)**: provide baudrate + sample point, the
       library derives TSEG etc.::

        cfg = CanChannelConfiguration(baudrate=500, sample_point=75.0)
        # => tseg1=11, tseg2=4, sjw=3, sam=1 (derived by the library)

    2. **By register parameters**: provide baudrate + TSEG, validated for
       consistency::

        cfg = CanChannelConfiguration(baudrate=500, tseg1=12, tseg2=3)
        # => sample=81.25% (derived back from TSEG), baudrate validated

    3. **By TSEG only**: derive baudrate and sample point from TSEG::

        cfg = CanChannelConfiguration(tseg1=12, tseg2=3)
        # => baudrate=500, sample=81.25%

    Any conflicting or invalid parameter raises ``ValueError`` at construction
    time, preventing an invalid configuration from reaching CANoe.
    """

    #: Default clock frequency for classic CAN mode (kHz).
    DEFAULT_CAN_CLOCK_FREQUENCY_KHZ = 8000

    #: Default clock frequency for CAN FD mode (kHz).
    DEFAULT_CAN_FD_CLOCK_FREQUENCY_KHZ = 80000

    #: Default CAN controller clock frequency (kHz). Used when clock_frequency=0.
    DEFAULT_CLOCK_FREQUENCY_KHZ = DEFAULT_CAN_CLOCK_FREQUENCY_KHZ

    #: Allowed tolerance when deriving the sample point (percent).
    #: Values beyond this are considered not exactly reachable and raise an error.
    SAMPLE_POINT_TOLERANCE_PCT = 1.0

    def __init__(
        self,
        baudrate: int = 0,           # kbit/s; 0 = derived from tseg
        sample_point: float = 0.0,   # %; 0 = derived from tseg
        tseg1: int = 0,              # time quantum; 0 = derived from baudrate+sample_point
        tseg2: int = 0,              # time quantum; 0 = derived
        sjw: int = 0,                # 0 = derived (min(tseg2, 3))
        sam: int = 0,                # sampling count; 0 = default 1 (only 1 or 3 allowed)
        flags: int = 0,              # bit0=silent mode, bit1=ISO(0)/non-ISO(1) CAN FD
        clock_frequency: int = 0,    # kHz; 0 = use DEFAULT_CLOCK_FREQUENCY_KHZ
    ):
        self._clock_frequency = clock_frequency or self.DEFAULT_CLOCK_FREQUENCY_KHZ
        self._baudrate = baudrate
        self._sample_point = sample_point
        self._tseg1 = tseg1
        self._tseg2 = tseg2
        self._sjw = sjw
        self._sam = sam
        self._flags = flags
        self._resolve()  # derive + validate; raises ValueError if invalid

    # ------------------------------------------------------------------
    # Scenario constructors (automatically select the correct clock frequency)
    # ------------------------------------------------------------------

    @classmethod
    def for_can(cls, baudrate: int = 0, sample_point: float = 0.0,
                tseg1: int = 0, tseg2: int = 0, sjw: int = 0, sam: int = 0,
                flags: int = 0, clock_frequency: int = 0) -> "CanChannelConfiguration":
        """Create a classic CAN configuration, using the 8000 kHz clock by default.

        When ``clock_frequency`` is not passed explicitly, the 8 MHz clock
        source of classic CAN is used automatically.
        """
        return cls(baudrate=baudrate, sample_point=sample_point, tseg1=tseg1,
                   tseg2=tseg2, sjw=sjw, sam=sam, flags=flags,
                   clock_frequency=clock_frequency or cls.DEFAULT_CAN_CLOCK_FREQUENCY_KHZ)

    @classmethod
    def for_can_fd(cls, baudrate: int = 0, sample_point: float = 0.0,
                   tseg1: int = 0, tseg2: int = 0, sjw: int = 0, sam: int = 0,
                   flags: int = 0, clock_frequency: int = 0) -> "CanChannelConfiguration":
        """Create a CAN FD configuration, using the 80000 kHz clock by default.

        When ``clock_frequency`` is not passed explicitly, the 80 MHz clock
        source of CAN FD is used automatically, supporting 2-5 Mbit/s data-phase
        baudrates and fine-grained sample points.
        """
        return cls(baudrate=baudrate, sample_point=sample_point, tseg1=tseg1,
                   tseg2=tseg2, sjw=sjw, sam=sam, flags=flags,
                   clock_frequency=clock_frequency or cls.DEFAULT_CAN_FD_CLOCK_FREQUENCY_KHZ)

    # ------------------------------------------------------------------
    # Derivation and validation
    # ------------------------------------------------------------------

    def _resolve(self) -> None:
        have_baud = self._baudrate > 0
        have_sample = self._sample_point > 0.0
        have_tseg = self._tseg1 > 0 and self._tseg2 > 0

        if have_baud and have_sample:
            self._derive_tseg_from_baud_and_sample()   # mode 1: baudrate+sample_point -> TSEG
        elif have_baud and have_tseg:
            self._validate_tseg_against_baud()          # mode 2: validate baudrate vs TSEG
        elif have_tseg:
            self._derive_baud_and_sample_from_tseg()    # mode 3: TSEG -> baudrate+sample_point
        else:
            raise ValueError(
                "Must provide one of (baudrate+sample_point), (baudrate+tseg1+tseg2) "
                f"or (tseg1+tseg2); got baudrate={self._baudrate}, "
                f"sample_point={self._sample_point}, tseg1={self._tseg1}, tseg2={self._tseg2}"
            )

        # ---- common range validation ----
        if self._tseg1 < 1:
            raise ValueError(f"tseg1 must be >= 1, got {self._tseg1}")
        if self._tseg2 < 1:
            raise ValueError(f"tseg2 must be >= 1, got {self._tseg2}")
        if self._baudrate <= 0:
            raise ValueError(f"baudrate must be > 0, got {self._baudrate}")

        # ---- derive missing sjw / sam (0 -> reasonable default) ----
        if self._sjw <= 0:
            self._sjw = min(self._tseg2, 3)
        if self._sjw > self._tseg2:
            raise ValueError(f"sjw ({self._sjw}) cannot be larger than tseg2 ({self._tseg2})")

        if self._sam <= 0:
            self._sam = 1
        if self._sam not in (1, 3):
            raise ValueError(f"sam must be 1 or 3, got {self._sam}")

        if self._flags & ~0b11:
            raise ValueError(f"only bit0/bit1 of flags are valid, got {self._flags:#x}")

    def _derive_tseg_from_baud_and_sample(self) -> None:
        """Mode 1: derive tseg1/tseg2 from baudrate + sample_point, validate reachability."""
        if not 0 < self._sample_point < 100:
            raise ValueError(f"sample_point must be in (0, 100), got {self._sample_point}")

        total_tq_f = self._clock_frequency / self._baudrate
        total_tq = round(total_tq_f)
        if abs(total_tq_f - total_tq) > 1e-6:
            raise ValueError(
                f"baudrate={self._baudrate} kbit/s cannot be divided into an integer "
                f"number of time quanta by clock {self._clock_frequency} kHz "
                f"({total_tq_f:.3f}), adjust baudrate or clock_frequency"
            )

        seg1 = round(self._sample_point / 100.0 * total_tq)
        if seg1 < 1:
            raise ValueError(
                f"sample_point={self._sample_point}% cannot be satisfied with {total_tq} TQ"
            )
        self._tseg1 = seg1 - 1
        self._tseg2 = total_tq - seg1
        if self._tseg2 < 1:
            raise ValueError(
                f"sample_point={self._sample_point}% with {total_tq} TQ leads to "
                f"tseg2<1, increase baudrate or lower the sample point"
            )

        # validate the derived sample point is within tolerance of the target
        # (TQ quantization prevents exact precision)
        actual_sample = self._sample_from_tseg()
        if abs(actual_sample - self._sample_point) > self.SAMPLE_POINT_TOLERANCE_PCT:
            raise ValueError(
                f"cannot reach sample_point={self._sample_point}% exactly at "
                f"clock={self._clock_frequency} kHz / baudrate={self._baudrate} kbit/s "
                f"(only {actual_sample:.2f}% achievable, beyond tolerance "
                f"{self.SAMPLE_POINT_TOLERANCE_PCT}%). Adjust the sample point or baudrate"
            )

    def _validate_tseg_against_baud(self) -> None:
        """Mode 2: validate that the baudrate derived from tseg1/tseg2 matches the given one."""
        actual = self._baudrate_from_tseg()
        if actual != self._baudrate:
            raise ValueError(
                f"baudrate={self._baudrate} is inconsistent with tseg1={self._tseg1}, "
                f"tseg2={self._tseg2}: the actual baudrate by formula is {actual} kbit/s. "
                f"Adjust one of them (clock {self._clock_frequency} kHz)"
            )
        # derive the sample point (if the user also gave sample_point it is
        # validated uniformly below)
        if self._sample_point > 0.0:
            actual_sample = self._sample_from_tseg()
            if abs(actual_sample - self._sample_point) > self.SAMPLE_POINT_TOLERANCE_PCT:
                raise ValueError(
                    f"sample_point={self._sample_point}% is inconsistent with "
                    f"tseg1={self._tseg1}, tseg2={self._tseg2}: actual sample point "
                    f"is {actual_sample:.2f}%"
                )
        else:
            self._sample_point = self._sample_from_tseg()

    def _derive_baud_and_sample_from_tseg(self) -> None:
        """Mode 3: derive baudrate and sample point from tseg1/tseg2."""
        self._baudrate = self._baudrate_from_tseg()
        self._sample_point = self._sample_from_tseg()

    # ------------------------------------------------------------------
    # Formulas
    # ------------------------------------------------------------------

    def _baudrate_from_tseg(self) -> int:
        """Derive baudrate from TSEG (requires exact division, raises otherwise)."""
        total_tq = 1 + self._tseg1 + self._tseg2
        if self._clock_frequency % total_tq != 0:
            raise ValueError(
                f"CAN clock {self._clock_frequency} kHz cannot be divided evenly by "
                f"(1+tseg1+tseg2)={total_tq}, cannot get an integer baudrate"
            )
        return self._clock_frequency // total_tq

    def _sample_from_tseg(self) -> float:
        """Derive sample point (%) from TSEG."""
        total_tq = 1 + self._tseg1 + self._tseg2
        return (1 + self._tseg1) / total_tq * 100.0

    # ------------------------------------------------------------------
    # Read-only properties (final effective values after derivation/validation)
    # ------------------------------------------------------------------

    @property
    def baudrate(self) -> int:
        """Final effective baudrate (kbit/s)."""
        return self._baudrate

    @property
    def sample_point(self) -> float:
        """Final effective sample point (%)."""
        return self._sample_point

    @property
    def tseg1(self) -> int:
        return self._tseg1

    @property
    def tseg2(self) -> int:
        return self._tseg2

    @property
    def sjw(self) -> int:
        return self._sjw

    @property
    def sam(self) -> int:
        return self._sam

    @property
    def flags(self) -> int:
        return self._flags

    @property
    def clock_frequency(self) -> int:
        """CAN controller clock (kHz)."""
        return self._clock_frequency

    @property
    def total_tq(self) -> int:
        """Total number of time quanta = 1 + tseg1 + tseg2."""
        return 1 + self._tseg1 + self._tseg2

    def __repr__(self) -> str:
        return (
            f"CanChannelConfiguration(baudrate={self.baudrate} kbit/s, "
            f"sample_point={self.sample_point:.2f}%, "
            f"tseg1={self.tseg1}, tseg2={self.tseg2}, sjw={self.sjw}, "
            f"sam={self.sam}, flags={self.flags:#x}, "
            f"clock_frequency={self.clock_frequency} kHz)"
        )

    def apply_to_can_set_config(self, can_controller: CanController):
        """Apply the configuration to a given CANController object (classic CAN)."""
        logger.info(f"Applying classic CAN config {self}")
        can_controller.can_set_config(
            baudrate=self.baudrate * 1000,  # Convert kbit/s to bit/s
            tseg1=self.tseg1,
            tseg2=self.tseg2,
            sjw=self.sjw,
            sam=self.sam,
            flags=self.flags
        )

    def apply_to_can_set_fd_arb_phase_config(self, can_controller: CanController):
        """Apply the configuration to a given CANController object for CAN FD arbitration phase."""
        logger.info(f"Applying CAN FD arbitration-phase config {self}")
        can_controller.can_set_fd_arb_phase_config(
            baudrate=self.baudrate * 1000,  # Convert kbit/s to bit/s
            tseg1=self.tseg1,
            tseg2=self.tseg2,
            sjw=self.sjw,
            flags=self.flags
        )

    def apply_to_can_set_fd_data_phase_config(self, can_controller: CanController):
        """Apply the configuration to a given CANController object for CAN FD data phase."""
        logger.info(f"Applying CAN FD data-phase config {self}")
        can_controller.can_set_fd_data_phase_config(
            baudrate=self.baudrate * 1000,  # Convert kbit/s to bit/s
            tseg1=self.tseg1,
            tseg2=self.tseg2,
            sjw=self.sjw,
            flags=self.flags
        )
