
import xml.dom.minidom

def parse_xml(response_text):
    """
    Parses the XML response and prints it in a readable format """

    try:

        clean = response_text.encode('utf-8')
        dom = xml.dom.minidom.parseString(clean)
        pretty_xml = dom.toprettyxml(indent="  ")
        print(pretty_xml)
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        print('\n'.join(lines))
    except Exception as e:
        print(f"Error parsing XML: {e}")
        print("Raw response :")
        print(response_text)