import requests
from bs4 import BeautifulSoup
import re
import json
import base64
import csv
import time
import random

def extract_variables(url, variable_list):
    """Extracts specified variables from an HTML file, simulating a Safari browser.

    Args:
        url: The URL of the HTML file.
        variable_list: A list of variable names to search for.

    Returns:
        A dictionary containing the extracted variables and their values.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.61 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script')

    variables_found = {}

    for script in scripts:
        script_text = script.string
        if script_text:
            for variable in variable_list:
                match = re.search(rf"var {variable} = (.*?);", script_text)
                if match:
                    try:
                        value = match.group(1).strip('"')
                        decoded_value = json.loads(base64.b64decode(value).decode('utf-8'))
                        variables_found[variable] = decoded_value
                    except Exception as e:
                        print(f"Error processing variable {variable}: {e}")

    return variables_found

def export_to_csv(data, output_file):


    years = [str(year) for year in range(2004, 2024)]
    months = ["agosto de 2023", "septiembre de 2023", "octubre de 2023", "noviembre de 2023", "diciembre de 2023",
              "enero de 2024", "febrero de 2024", "marzo de 2024", "abril de 2024", "mayo de 2024", "junio de 2024", "julio de 2024"]
    columns = ["city", "variable"] + years + months

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()

        for item in data:
            city = item['city']
            for variable, data_points in item.items():
                if variable != 'city':
                    row = {'city': city, 'variable': variable}  # Initialize row dictionary
                    for data_point in data_points:
                        label = data_point['Label']
                        # Only add label if it's a valid field name (in columns)
                        if label in columns:
                            row[label] = data_point['Value']
                    writer.writerow(row)
                    
def process_links(input_csv, output_csv):
    with open(input_csv, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        all_data = []
        for row in reader:
            city, link = row
            # Introduce random delay

            variables = extract_variables(link, ['ysd', 'msd', 'yrd', 'mrd'])

            # Create a dictionary to store data for the city
            city_data = {'city': city}
            for variable, data_points in variables.items():
                city_data[variable] = data_points
            all_data.append(city_data)
            delay = random.randint(121, 145)
            print(row," Delay:",delay)
            time.sleep(delay)

        export_to_csv(all_data, output_csv)


input_csv_file = 'input_links.csv'
output_csv_file = 'output_yearly.csv'
process_links(input_csv_file, output_csv_file)