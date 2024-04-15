import sys
import json
import xml.etree.ElementTree as ET
import csv
import argparse
from operator import itemgetter

def parse_address(ent):
    """
    Parse and standardize address entries from a dictionary into a structured format.
    
    Args:
        ent (dict): A dictionary containing various parts of an address.
    
    Returns:
        dict: A dictionary with standardized address fields.
    """
    address = {}
    if 'NAME' in ent and ent['NAME'].strip():
        name_parts = ent['NAME'].split()
        address['name'] = " ".join(name_parts[:-1]) + " " + name_parts[-1]
    elif 'COMPANY' in ent:
        address['organization'] = ent['COMPANY'].strip()
    
    address['street'] = ent['STREET'].strip()
    address['city'] = ent['CITY'].strip()
    address['state'] = ent['STATE'].strip()
    address['zip'] = ent['POSTAL_CODE'].strip().replace(" -", "")
    return address

def read_xml(filename):
    """
    Read and parse an XML file into a list of address dictionaries.
    
    Args:
        filename (str): Path to the XML file.
    
    Returns:
        list: A list of dictionaries, each representing an address.
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    addresses = []
    for ent in root.findall('.//ENT'):
        entry = {child.tag: child.text for child in ent if child.text}
        address = parse_address(entry)
        addresses.append(address)
    return addresses

def read_tsv(filename):
    """
    Read and parse a TSV file into a list of address dictionaries.
    
    Args:
        filename (str): Path to the TSV file.
    
    Returns:
        list: A list of dictionaries, each representing an address.
    """
    addresses = []
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            address = {
                'organization': row['organization'].strip(),
                'street': row['address'].strip(),
                'city': row['city'].strip(),
                'state': row['state'].strip(),
                'zip': row['zip'].strip()
            }
            if row['first'].strip() or row['last'].strip():
                address['name'] = f"{row['first'].strip()} {row['last'].strip()}"
            addresses.append(address)
    return addresses

def read_txt(filename):
    """
    Read and parse a plain text file into a list of address dictionaries.
    
    Args:
        filename (str): Path to the text file.
    
    Returns:
        list: A list of dictionaries, each representing an address.
    """
    addresses = []
    with open(filename, 'r') as file:
        data = file.read().split('\n\n')
        for entry in data:
            lines = entry.split('\n')
            name = lines[0].strip()
            street = lines[1].strip()
            city_state_zip = lines[3].split(',')
            city = city_state_zip[0].strip()
            state_zip = city_state_zip[1].split()
            state = state_zip[0].strip()
            zip_code = state_zip[1].strip()
            addresses.append({
                'name': name,
                'street': street,
                'city': city,
                'state': state,
                'zip': zip_code
            })
    return addresses

def main():
    """
    Main function to handle command-line arguments and process files.
    """
    parser = argparse.ArgumentParser(description='Parse address files and output JSON sorted by ZIP code.')
    parser.add_argument('files', nargs='+', help='File paths to process.')
    args = parser.parse_args()

    all_addresses = []
    for file in args.files:
        if file.endswith('.xml'):
            all_addresses.extend(read_xml(file))
        elif file.endswith('.tsv'):
            all_addresses.extend(read_tsv(file))
        elif file.endswith('.txt'):
            all_addresses.extend(read_txt(file))
        else:
            print(f"Error: Unsupported file format {file}", file=sys.stderr)
            sys.exit(1)

    # Sort addresses by ZIP code
    all_addresses.sort(key=itemgetter('zip'))

    # Print JSON output
    print(json.dumps(all_addresses, indent=4))

if __name__ == "__main__":
    main()
