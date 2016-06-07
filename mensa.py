#!/usr/bin/env python3
import copy
import itertools
from bs4 import BeautifulSoup
import requests

def normalize(string):
    generator = map(str.strip, string.splitlines())
    line_parts = list()
    while True:
        l = list(itertools.takewhile(lambda x: x != "", generator))
        if len(l) == 0:
            break
        line_parts.append(" ".join(l))
    return ", ".join(line_parts)

def clean(html):
    html = copy.copy(html)
    for tag in html.find_all("sup"):
        tag.decompose()
    return html

def get_food_plan():
    r = requests.get("http://www.stw-bremen.de/de/essen-trinken/uni-mensa")
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    food_plan = soup.find(id="food-plan-0")
    categories = food_plan.find_all(class_="food-category")
    for category in categories:
        title = category.find(class_="category-name")
        meals = category.find_all(class_="field-name-field-description")
        yield (title.get_text(), [normalize(clean(meal).get_text()) for meal in meals])

if __name__ == "__main__":
    print("\n\n".join(["{:-^80}\n{}".format(cat, "\n".join(meals)) for cat, meals in get_food_plan()]))
