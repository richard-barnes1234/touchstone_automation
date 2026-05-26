import xml.etree.ElementTree as ET

def parse_exposure_sets(response_text):
    """Parses GetExposureSets response and returns a list of exposure sets"""
    root = ET.fromstring(response_text)
    exposure_sets = []

    for elem in root.iter():
       if elem.tag.endswith('}ExposureSet') or elem.tag == 'Exposureset':
          exp = {}
          for child in elem:
            tag = child.tag.split('}')[-1]  if '}' in child.tag else child.tag
            exp[tag] = child.text
          if exp:
           exposure_sets.append(exp)
    return exposure_sets

def print_exposure_sets(exposure_sets):
 """" Print the list of exposure sets in a readable format """""
 print(f"\n{'='*60}")
 print(f"EXPOSURE SETS RETRIEVED: {len(exposure_sets)}")
 print(f"{'='*60}")
 print(f"{'SID':<10} {'NAME':<30} {'STATUS':<10} {'CREATED'}")

print(f"{'-'*60}")
