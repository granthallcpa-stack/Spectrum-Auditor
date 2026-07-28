"""
RF Service Definitions
"""

from dataclasses import dataclass
from knowledge.models import KnowledgeSignal


@dataclass(frozen=True, slots=True)
class RFService:

    symbol: str
    tolerance_hz: int


SERVICES = {

    "AF": RFService(
        symbol="AF",
        tolerance_hz=3000
    ),

    "AS": RFService(
        symbol="AS",
        tolerance_hz=48000
    ),

    "CD": RFService(
        symbol="CD",
        tolerance_hz=2500
    ),

    "FM": RFService(
        symbol="FM",
        tolerance_hz=85500
    ),

    "GB": RFService(
        symbol="GB",
        tolerance_hz=900
    ),

    "GE": RFService(
        symbol="GE",
        tolerance_hz=2200
    ),

    "GM": RFService(
        symbol="GM",
        tolerance_hz=2200
    ),

    "GO": RFService(
        symbol="GO",
        tolerance_hz=2200
    ),

    "GS": RFService(
        symbol="GS",
        tolerance_hz=1400
    ),

    "HAM": RFService(
        symbol="HAM",
        tolerance_hz=24000
    ),

    "IG": RFService(
        symbol="IG",
        tolerance_hz=23000
    ),

    "IK": RFService(
        symbol="IK",
        tolerance_hz=23000
    ),

    "LN": RFService(
        symbol="LN",
        tolerance_hz=1400
    ),

    "MC": RFService(
        symbol="MC",
        tolerance_hz=1700
    ),

    "MG": RFService(
        symbol="MG",
        tolerance_hz=5000
    ),

    "MW": RFService(
        symbol="MW",
        tolerance_hz=5000
    ),

    "PW": RFService(
        symbol="PW",
        tolerance_hz=2100
    ),

    "RP": RFService(
        symbol="RP",
        tolerance_hz=2300
    ),

    "SY": RFService(
        symbol="SY",
        tolerance_hz=2000
    ),

    "YB": RFService(
        symbol="YB",
        tolerance_hz=2200
    ),

    "YE": RFService(
        symbol="YE",
        tolerance_hz=2200
    ),

    "YG": RFService(
        symbol="YG",
        tolerance_hz=2300
    ),

    "YW": RFService(
        symbol="YW",
        tolerance_hz=23000
    ),

    "YX": RFService(
        symbol="YX",
        tolerance_hz=2200
    )

}


def get_service(symbol: str) -> RFService | None:

    return SERVICES.get(symbol)


def get_tolerance(symbol: str) -> int:

    service = get_service(symbol)

    if service is None:

        raise KeyError(
            f"Unknown RF service: {symbol}"
        )

    return service.tolerance_hz