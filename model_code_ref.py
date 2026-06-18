# model_code_ref.py
# ─────────────────────────────────────────────────────────────────────────────
# ModelCode reference table matching the broker report's "ModelCodeRef" sheet.
# Used to populate the ModelCodeRef sheet in the new SOR-style Excel export
# and to label each analysis (e.g. "AIR Severe Storm", "AIR Earthquake").
#
# Source: Copy_of_SampleReportCalculation_SOR_20260618.xlsx -> ModelCodeRef sheet
# Columns: ModelCode, Model, (blank), BriefName, Analysis Name for Report
# ─────────────────────────────────────────────────────────────────────────────

MODEL_CODE_REF = [
    (1,   "The AIR Terrorism Model",                                  "M01 US TR",     "AIR Terrorism"),
    (2,   "AIR U.S. Workers Compensation Model",                       "M02 US WC",     None),
    (3,   "AIR Japan Personal Accident",                               "M03 Jpn PA",    None),
    (4,   "AIR Longevity",                                             "M04 AIR Longevity", None),
    (5,   "AIR Wildfire Model for  the U.S.",                          "M05 US WF",     "AIR Wildfire"),
    (6,   "AIR Bushfire Model for Australia ",                         "M06 Aus BF",    None),
    (7,   "AIR Multiple-Peril Crop Insurance Model for the U.S.",      "M07 US AG",     None),
    (8,   "AIR Inland Flood Model for the U.S.",                       "M08 US IF",     "AIR Inland Flood"),
    (11,  "AIR Earthquake Model for the U.S. and Canada",              "M11 US EQ",     "AIR Earthquake"),
    (12,  "AIR Earthquake Model for Canada",                           "M12 Can EQ",    None),
    (13,  "AIR Earthquake Model for Hawaii",                           "M13 Haw EQ",    None),
    (14,  "AIR Earthquake Model for Alaska",                           "M14 Ala EQ",    None),
    (15,  "AIR Earthquake Model for the Caribbean",                    "M15 Car EQ",    None),
    (18,  "AIR Japan Inland Flood Model",                              "M18 Jpn IF",    None),
    (20,  "AIR Severe Thunderstorm Model for the U.S. and Canada",     "M20 NorAm ST",  None),
    (21,  "AIR Hurricane Model for the United States",                 "M27 NorAtl TC", None),
    (22,  "AIR Severe Thunderstorm Model for the U.S.",                "M22 US ST",     "AIR Severe Storm"),
    (23,  "AIR Hurricane Model for Hawaii",                            "M23 Haw TC",    None),
    (24,  "AIR Hurricane Model for Offshore Assets",                   "M27 NorAtl TC", None),
    (25,  "AIR Tropical Cyclone Model for the Caribbean",              "M27 NorAtl TC", None),
    (26,  "AIR Severe Thunderstorm Model for Canada",                  "M26 Can ST",    None),
    (27,  "AIR North Atlantic Basinwide Hurricane Model",              "M27 NorAtl TC", "AIR Windstorm"),
    (28,  "AIR Winter Storm Model for the U.S.",                       "M28 US WS",     "AIR Severe Storm"),
    (29,  "AIR Tropical Cyclone Model for Mexico",                     "M27 NorAtl TC", None),
    (30,  "AIR Tropical Cyclone Model for Canada",                     "M30 Can TC",    None),
    (31,  "AIR Earthquake Model for the Pan-European Region",          "M31 Eur EQ",    None),
    (33,  "AIR Earthquake Model for Southeast Europe",                 "M33 SEU EQ",    None),
    (41,  "AIR Extra Tropical Cyclone Model for Europe",               "M41 Eur ETC",   None),
    (42,  "AIR Winter Storm Model for Canada",                         "M42 Can WS",    None),
    (43,  "AIR Severe Thunderstorm Model for Europe",                  "M43 EUR ST",    None),
    (44,  "AIR Severe Thunderstorm Model for Australia",               "M44 Aus ST",    None),
    (51,  "AIR Earthquake Model for Australia",                        "M51 Aus EQ",    None),
    (52,  "AIR Earthquake Model for Japan",                            "M52 Jpn EQ",    None),
    (53,  "AIR Earthquake Model for New Zealand",                      "M53 NZ EQ",     None),
    (54,  "AIR Earthquake Model for Southeast Asia",                   "M54 SEA EQ",    None),
    (55,  "AIR Earthquake Model for China",                            "M55 Chi EQ",    None),
    (58,  "AIR Earthquake Model for India",                            "M58 Ind EQ",    None),
    (60,  "AIR Northwest Pacific Basinwide Typhoon Model",             "M60 NorPac TC", None),
    (61,  "AIR Tropical Cyclone Model for Australia",                  "M61 Aus TC ",   None),
    (62,  "AIR Typhoon Model for Japan",                               "M60 NorPac TC", None),
    (63,  "AIR Hurricane Model for New Zealand",                       "M63 NZL TC",    None),
    (64,  "AIR Typhoon Model for Southeast Asia",                      "M60 NorPac TC", None),
    (65,  "AIR Typhoon Model for China",                               "M60 NorPac TC", None),
    (66,  "AIR Typhoon Model for South Korea",                         "M60 NorPac TC", None),
    (67,  "AIR Tropical Cyclone Model for Central America",            "M27 NorAtl TC", None),
    (68,  "AIR Tropical Cyclone Model for India",                      "M68 Ind TC",    None),
    (70,  "AIR Earthquake Model for South America",                    "M70 SouAm EQ",  None),
    (71,  "AIR Earthquake Model for Colombia",                         "M70 SouAm EQ",  None),
    (72,  "AIR Earthquake Model for Mexico",                           "M72 Mex EQ",    None),
    (73,  "AIR Earthquake Model for Chile",                            "M70 SouAm EQ",  None),
    (74,  "AIR Earthquake Model for Venezuela",                        "M70 SouAm EQ",  None),
    (75,  "AIR Earthquake Model for Peru",                             "M70 SouAm EQ",  None),
    (76,  "AIR Earthquake Model for Central America",                  "M76 CenAm EQ",  None),
    (81,  "AIR Pandemic Flu Model",                                    "M81 AIR PN",    None),
    (84,  "AIR Cyber (ARC) Model",                                     "M84 AIR SB",    None),
    (85,  "AIR Multiple-Peril Crop Insurance Model for China",         "M85 Chi AG",    None),
    (86,  "AIR Crop Hail Model for the U.S. and Canada",               "M86 US CH",     None),
    (87,  "AIR Multiple-Peril Crop Insurance Model for India",         "M87 Ind AG",    None),
    (89,  "AIR Multiple-Peril Crop Insurance Model for Canada",        "M89 Canada MPCI", None),
    (90,  "AIR Inland Flood Model for Central Europe",                 "M90 CenEur IF", None),
    (91,  "AIR Coastal Flood Model for Great Britain",                 "M91 UK CFL",    None),
    (92,  "AIR Inland Flood Model for Great Britain",                  "M92 UK IF",     None),
    (93,  "AIR Inland Flood Model for Germany",                        "M93 Ger IF",    None),
    (94,  "AIR Inland Flood Model for Southeast Europe",               "M94 SEU IF",    None),
    (95,  "AIR Inland Flood Model for Austria, Czech and Switzerland", "M95 Cze IF",    None),
    (521, "AIR Hurricane Model for the United States",                 "M521 US TC",    None),
]

# Quick lookup: ModelCode -> Analysis Name for Report (used for the U1 label, Python-side fallback)
REPORT_LABEL = {code: label for code, _, _, label in MODEL_CODE_REF if label}


def get_report_label(model_code):
    """Returns the broker-facing analysis label for a ModelCode, e.g. 'AIR Severe Storm'."""
    try:
        return REPORT_LABEL.get(int(model_code), f"Model {model_code}")
    except (TypeError, ValueError):
        return str(model_code)