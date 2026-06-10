# peril_lookup.py
# ─────────────────────────────────────────────────────────────────────────────
# Peril set code → description mapping
# Source: AIRReference.dbo.tPerilSet
# Codes represent combinations of perils covered in a model run.
#
# Peril abbreviations:
#   TC = Wind (Tropical Cyclone)     ST = Severe Thunderstorm
#   EQ = Earthquake Shake            FF = Fire Following
#   CF = Coastal Flood               TR = Terrorism
#   SU = Storm Surge                 IF = Inland Flood
#   WS = Winter Storm                WF = Wildfire
#   HL = Hail                        TD = Tornado
#   SL = Straight-Line Winds         LS = Landslide
#   LQ = Liquefaction                PN = Pandemic
#   NC = NonCat                      CH = Crop Hail
#   PF = Precipitation Flood         TS = Tsunami
# ─────────────────────────────────────────────────────────────────────────────

PERIL_SET = {
    -1:  "All Perils",
    1:   "Wind",
    2:   "Severe Thunderstorm",
    3:   "Severe Thunderstorm, Wind",
    4:   "Earthquake",
    5:   "Earthquake, Wind",
    6:   "Earthquake, Severe Thunderstorm",
    7:   "Earthquake, Severe Thunderstorm, Wind",
    8:   "Fire Following",
    9:   "Fire Following, Wind",
    10:  "Fire Following, Severe Thunderstorm",
    11:  "Fire Following, Severe Thunderstorm, Wind",
    12:  "Earthquake, Fire Following",
    13:  "Earthquake, Fire Following, Wind",
    14:  "Earthquake, Fire Following, Severe Thunderstorm",
    15:  "Earthquake, Fire Following, Severe Thunderstorm, Wind",
    16:  "Coastal Flood",
    17:  "Coastal Flood, Wind",
    18:  "Coastal Flood, Severe Thunderstorm",
    19:  "Coastal Flood, Severe Thunderstorm, Wind",
    20:  "Coastal Flood, Earthquake",
    21:  "Coastal Flood, Earthquake, Wind",
    22:  "Coastal Flood, Earthquake, Severe Thunderstorm",
    23:  "Coastal Flood, Earthquake, Severe Thunderstorm, Wind",
    24:  "Coastal Flood, Fire Following",
    25:  "Coastal Flood, Fire Following, Wind",
    26:  "Coastal Flood, Fire Following, Severe Thunderstorm",
    27:  "Coastal Flood, Fire Following, Severe Thunderstorm, Wind",
    28:  "Coastal Flood, Earthquake, Fire Following",
    29:  "Coastal Flood, Earthquake, Fire Following, Wind",
    30:  "Coastal Flood, Earthquake, Fire Following, Severe Thunderstorm",
    31:  "Coastal Flood, Earthquake, Fire Following, Severe Thunderstorm, Wind",
    32:  "Terrorism",
    33:  "Terrorism, Wind",
    34:  "Severe Thunderstorm, Terrorism",
    35:  "Severe Thunderstorm, Terrorism, Wind",
    36:  "Earthquake, Terrorism",
    37:  "Earthquake, Terrorism, Wind",
    38:  "Earthquake, Severe Thunderstorm, Terrorism",
    39:  "Earthquake, Severe Thunderstorm, Terrorism, Wind",
    40:  "Fire Following, Terrorism",
    41:  "Fire Following, Terrorism, Wind",
    42:  "Fire Following, Severe Thunderstorm, Terrorism",
    43:  "Fire Following, Severe Thunderstorm, Terrorism, Wind",
    44:  "Earthquake, Fire Following, Terrorism",
    45:  "Earthquake, Fire Following, Terrorism, Wind",
    46:  "Earthquake, Fire Following, Severe Thunderstorm, Terrorism",
    47:  "Earthquake, Fire Following, Severe Thunderstorm, Terrorism, Wind",
    48:  "Coastal Flood, Terrorism",
    49:  "Coastal Flood, Terrorism, Wind",
    50:  "Coastal Flood, Severe Thunderstorm, Terrorism",
    51:  "Coastal Flood, Severe Thunderstorm, Terrorism, Wind",
    52:  "Coastal Flood, Earthquake, Terrorism",
    53:  "Coastal Flood, Earthquake, Terrorism, Wind",
    54:  "Coastal Flood, Earthquake, Severe Thunderstorm, Terrorism",
    55:  "Coastal Flood, Earthquake, Severe Thunderstorm, Terrorism, Wind",
    56:  "Coastal Flood, Fire Following, Terrorism",
    57:  "Coastal Flood, Fire Following, Terrorism, Wind",
    58:  "Coastal Flood, Fire Following, Severe Thunderstorm, Terrorism",
    59:  "Coastal Flood, Fire Following, Severe Thunderstorm, Terrorism, Wind",
    60:  "Coastal Flood, Earthquake, Fire Following, Terrorism",
    61:  "Coastal Flood, Earthquake, Fire Following, Terrorism, Wind",
    62:  "Coastal Flood, Earthquake, Fire Following, Severe Thunderstorm, Terrorism",
    63:  "Coastal Flood, Earthquake, Fire Following, Severe Thunderstorm, Terrorism, Wind",
    64:  "Winter Storm",
    65:  "Wind, Winter Storm",
    66:  "Severe Thunderstorm, Winter Storm",
    67:  "Severe Thunderstorm, Wind, Winter Storm",
    68:  "Earthquake, Winter Storm",
    69:  "Earthquake, Wind, Winter Storm",
    70:  "Earthquake, Severe Thunderstorm, Winter Storm",
    71:  "Earthquake, Severe Thunderstorm, Wind, Winter Storm",
    72:  "Fire Following, Winter Storm",
    73:  "Fire Following, Wind, Winter Storm",
    74:  "Fire Following, Severe Thunderstorm, Winter Storm",
    75:  "Fire Following, Severe Thunderstorm, Wind, Winter Storm",
    76:  "Earthquake, Fire Following, Winter Storm",
    77:  "Earthquake, Fire Following, Wind, Winter Storm",
    78:  "Earthquake, Fire Following, Severe Thunderstorm, Winter Storm",
    79:  "Earthquake, Fire Following, Severe Thunderstorm, Wind, Winter Storm",
    128: "Sprinkler Leakage",
    256: "Storm Surge",
    512: "Wildfire",
    1024:"Inland Flood",
    2048:"Precipitation Flood",
    4096:"Tsunami",
    8192:"Pandemic",
}

# Short peril labels for UI badges
PERIL_SHORT = {
    -1:  "All",
    1:   "Wind",
    2:   "SevThunderstorm",
    3:   "ST+Wind",
    4:   "Earthquake",
    5:   "EQ+Wind",
    6:   "EQ+ST",
    7:   "EQ+ST+Wind",
    8:   "FireFollowing",
    12:  "EQ+FF",
    15:  "EQ+FF+ST+Wind",
    16:  "CoastalFlood",
    32:  "Terrorism",
    64:  "WinterStorm",
    256: "StormSurge",
    512: "Wildfire",
    1024:"InlandFlood",
}


def get_peril_description(peril_set_code):
    """Returns full peril description for a given PerilSetCode"""
    try:
        code = int(peril_set_code)
        return PERIL_SET.get(code, f"Peril Set {code}")
    except (TypeError, ValueError):
        return str(peril_set_code) if peril_set_code else "Unknown"


def get_peril_short(peril_set_code):
    """Returns short peril label for UI badges"""
    try:
        code = int(peril_set_code)
        return PERIL_SHORT.get(code, PERIL_SET.get(code, f"PSC-{code}"))
    except (TypeError, ValueError):
        return str(peril_set_code) if peril_set_code else "Unknown"


def enrich_with_peril(df):
    """
    Adds a PerilDescription column to a DataFrame that contains PeriSetCode.
    Safe to call — does nothing if PeriSetCode column not present.
    """
    if df is None or df.empty:
        return df
    if 'PeriSetCode' not in df.columns:
        return df
    df = df.copy()
    df.insert(
        df.columns.get_loc('PeriSetCode') + 1,
        'PerilDescription',
        df['PeriSetCode'].apply(get_peril_description)
    )
    return df


def get_unique_perils(df):
    """
    Returns a list of unique peril descriptions in a DataFrame.
    Useful for building filter dropdowns.
    """
    if df is None or df.empty or 'PeriSetCode' not in df.columns:
        return []
    codes = df['PeriSetCode'].dropna().unique()
    return sorted({get_peril_description(c) for c in codes})


if __name__ == "__main__":
    print("Peril Set Lookup — sample entries:")
    for code in [1, 4, 7, 15, 16, 32, 64, 256]:
        print(f"  Code {code:>4}  →  {get_peril_description(code)}")