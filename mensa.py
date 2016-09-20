#!/usr/bin/env python3
import copy
import datetime
import itertools
import re
import time
from bs4 import BeautifulSoup
import click
import parsedatetime
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

def get_food_plan(html, food_plan_id):
    food_plan = html.find(id=food_plan_id)
    categories = food_plan.find_all(class_="food-category")
    for category in categories:
        title = category.find(class_="category-name")
        meals = category.find_all(class_="field-name-field-description")
        yield (title.get_text(), [normalize(clean(meal).get_text()) for meal in meals])

def get_available_food_plans(html):
    food_plans = []
    pdt_locale = parsedatetime.Constants("de_DE", usePyICU=False)
    pdt = parsedatetime.Calendar(pdt_locale)
    links = html.find_all("a", href=re.compile(r"#food-plan-\d"))
    for link in links:
        date_string = link.find("span", class_="tab-date").get_text()
        time_struct, err = pdt.parse(date_string)
        if err == 0:
            #should not happen
            raise ValueError((time_struct, err))
        id = link["href"][1:]
        date = datetime.date.fromtimestamp(time.mktime(time_struct))
        food_plans.append((id, date))
    return food_plans

def get_html(mensa_id):
    r = requests.get("http://www.stw-bremen.de/de/essen-trinken/{}".format(mensa_id))
    r.raise_for_status()
    html = BeautifulSoup(r.text, "html.parser")
    return html

def prettify(food_plan):
    return "\n\n".join(["{:-^80}\n{}".format(cat, "\n".join(meals)) for cat, meals in food_plan])

def _parse_date(ctx, param, value):
    c = parsedatetime.Calendar()
    date, err = c.parse(value)
    if err != 1:
        raise click.BadParameter(value)
    return datetime.date.fromtimestamp(time.mktime(date))

@click.command(help="Command line interface to read the menu of the University of Bremen's cafeteria from the terminal.")
@click.argument("date", default="today", callback=_parse_date)
def main(date):
    html = get_html("uni-mensa")
    afp = get_available_food_plans(html)
    try:
        fp_id = list(filter(lambda t: t[1] == date, afp))[0]
    except IndexError:
        msg = "No food plan for {} (available: {})"
        raise click.ClickException(msg.format(date, ", ".join([str(fp_date) for fp_id, fp_date in afp])))
    fp = get_food_plan(html, fp_id)
    click.echo(prettify(fp))

if __name__ == "__main__":
    main()
