"""Convert the receipt image to text and filter out food items.

Food items are identified using the USDA's Food Data Central Database.
"""


try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import requests
from typing import List, Dict
import json

import base64
import io


def get_words(b64) -> List[Dict[str, str]]:
    """Main entrypoint to the program."""
    # In order to bypass the image conversions of pytesseract, just use relative or absolute image path
    text: str = image_to_text(b64)
    formatted_text: List[List[str]] = format_lines(text)
    food_list: List[str] = extract_foods(formatted_text)
    data_summary: List[Dict[str, str]] = summarize_food_data(food_list)
    # with open("summary_data.json", "w") as data_file: 
    #     json.dump(data_summary, data_file)
    return data_summary


def image_to_text(image_filepath: str) -> str:
    """Convert the receipt image to text."""
    # If you don't have tesseract executable in your PATH, include the following:
    pytesseract.pytesseract.tesseract_cmd = r'/app/.apt/usr/bin/tesseract'
    imgstring = image_filepath
    pic = io.StringIO()
    image_string = io.BytesIO(base64.b64decode(imgstring))
    image = Image.open(image_string)
    # bg = Image.new("RGB", image.size, (255,255,255))
    # bg.paste(image,image)

    # print(pytesseract.image_to_string(bg))

    result = pytesseract.image_to_string(image)
    return result


def format_lines(unprocessed_text: str) -> List[List[str]]:
    """Formats the text so that each line is a new array and each word is a new string."""
    stored_lines: List[List[str]] = []
    new_line: List = []
    new_word: str = ""
    for char in unprocessed_text:
        if char != "\n":
            if char != " " and char.isalpha():
                new_word += char
            else:
                new_line.append(new_word)
                new_word = ""
        else:
            stored_lines.append(new_line)
            new_line = []
    return stored_lines


def extract_foods(complete_text: List[List[str]]) -> List[str]:
    """Extracts food words from the text."""
    foods: List[str] = []
    non_foods: List[str] = ["Authorization Code", "Card", "Change", "Sales Tax", "Sub Total", "Total", "Total Due", "Total Savings"]
    for unprocessed_line in complete_text:
        processed_line: str = ""
        for word in unprocessed_line:
            if len(word) > 2:
                processed_line += word
                processed_line += " "
        processed_line = processed_line.strip()
        if (is_food(processed_line)) and (processed_line != "") and (processed_line not in non_foods):
            foods.append(processed_line)
    return(foods)


def is_food(query: str) -> bool:
    """Checks against Food Data Central to see if a word is food."""
    # Provide necessary setup
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('api_key', 'EeLMUKBgETbdHiStHFuPQbMpYDpxLGkr9HLvbaOt'),
    )

    # Create and send request and receive response from the FDC API
    data = str('{"query": "' + query + '", "sortBy": "fdcId", "sortOrder": "desc"}')
    response = requests.post('https://api.nal.usda.gov/fdc/v1/foods/search', headers=headers, params=params, data=data)

    # Use the built in json() method to convert the response into a dictionary
    processable_response = response.json()

    # Determine how many items in the food database match the query; if no matches are found, the item is not food.
    number_of_matches = processable_response["totalHits"]
    if number_of_matches == 0:
        return False
    else:
        return True


def summarize_food_data(unprocessed_food_list: List[str]) -> List[Dict[str, str]]:
    """Creates a list of dictionaries indicating the item name, quantity, and units.
    
    As units are not part of the data extracted from the receipt, dashes are put in as a placeholder.
    """
    summary: List[Dict[str, str]] = []
    item_count_data: Dict[str, int] = {}

    for item in unprocessed_food_list:
        if item not in item_count_data:
            item_count_data[item] = 1
        else:
            item_count_data[item] += 1
    
    for product in item_count_data:
        item_information: Dict[str, str] = {}
        item_information["name"] = product
        item_information["quantity"] = str(item_count_data[product])
        item_information["units"] = "-"
        summary.append(item_information)
    
    return summary


# if __name__ == "__main__":
#     main()