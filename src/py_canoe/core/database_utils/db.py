try:
    import canmatrix.formats
    CANMATRIX_AVAILABLE = True
except ImportError:
    CANMATRIX_AVAILABLE = False

from typing import Dict, Any

from py_canoe.helpers.common import logger


def fetch_database_info(db_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load a database from the given path and extract structured information.

    Args:
        db_path: Path to the database file.

    Returns:
        A dictionary containing 'networks', 'ecus', 'frames', 'pdus', 'frames_signals', and 'pdus_signals' as sub-dictionaries.
        Returns an empty dict if loading fails.
    """
    if not CANMATRIX_AVAILABLE:
        raise ImportError(
            "canmatrix is required for database operations. "
            "Install it with: uv pip install py-canoe[database] or uv pip install canmatrix[arxml,kcd,ldf,xls,xlsx,yaml,eds]"
        )
    try:
        logger.info(f"Loading database from: {db_path}")
        db = canmatrix.formats.loadp(db_path)
        logger.info(f"Database loaded successfully: {db_path}")
        db_info = {
            'networks': {},
            'ecus': {},
            'frames': {},
            'frames_signals': {},
            'pdus': {},
            'pdus_signals': {},
        }
        for network_name, network_obj in db.items():
            db_info['networks'][network_name] = network_obj
            db_info['ecus'].update({ecu.name: ecu for ecu in network_obj.ecus})
            for frame_obj in network_obj.frames:
                db_info['frames'][frame_obj.name] = frame_obj
                for signal_obj in frame_obj.signals:
                    signal_key = f"{frame_obj.name}::{signal_obj.name}"
                    db_info['frames_signals'][signal_key] = signal_obj
                if hasattr(frame_obj, 'pdus'):
                    for pdu_obj in frame_obj.pdus:
                        db_info['pdus'][pdu_obj.name] = pdu_obj
                        for pdu_signal_obj in pdu_obj.signals:
                            pdu_signal_name = f"{pdu_obj.name}::{pdu_signal_obj.name}"
                            db_info['pdus_signals'][pdu_signal_name] = pdu_signal_obj
        return db_info
    except Exception as e:
        logger.error(f"❌ Error occurred while fetching database information: {e}")
        return {}
