#!/usr/bin/env python3
import argparse
import os
import urllib.request
from bs4 import BeautifulSoup
import re

_MENSA_URL = "http://www.uni-bremen.de/service/taeglicher-bedarf/essen-auf-dem-campus/cafeteria/390"


def _clean(html):
    clean = html.replace("<br>", "\n").replace("</br>", "")
    clean = clean.replace("&amp;", "&")
    clean = clean.replace("\n&\n", " & ").replace("\n&", " &")

    clean = clean.replace("<strong>", "{} ".format("+" * 4)).replace("</strong>", " {}".format("+" * 4))
    return clean

def _get_mensa_info():
    result = urllib.request.urlopen(_MENSA_URL)
    html = result.read()

    soup = BeautifulSoup(html, "html.parser")

    main_div = soup.html.find("div", class_="tx-hbucafeteria-pi1")
    main_heading = main_div.find("h2")
    day_trs = main_div.find("table").find_all("tr")[1:]
    hours_div = main_div.find_all("div", class_="tx-hbucafeteria-pi1-info")[1]

    return (main_heading.string, day_trs, hours_div)


def _get_hours():
    heading, meal_trs, hours_div = _get_mensa_info()
    strings = [str(tag) for tag in hours_div.contents[2:]]
    return _clean("".join(strings))


def _get_menu():
    heading, day_trs, hours_div = _get_mensa_info()

    days_and_meals = []
    for day_tr in day_trs:
        tds = day_tr.find_all("td")

        day = tds[0]
        meal_tds = tds[1].contents[1:]
        meal_tds_strings = [str(tag) for tag in meal_tds]

        meals = _clean("".join(meal_tds_strings))

        days_and_meals.append((day.string, meals))

    return (heading, days_and_meals)




if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Mensa menu from your terminal.")
    argparser.add_argument("--open", "-o",
                           action="store_true",
                           help="Show opening hours.")
    args = argparser.parse_args()

    if args.open:
        hours = _get_hours()
        print(hours)
        quit()

    else:
        heading, menu = _get_menu()
        print(heading)
        for day, meals in menu:
            print("-" * (10 + len(day)))
            print("-{}{}{}-".format(" " * 4, day, " " * 4))
            print("-" * (10 + len(day)))

            print(meals)

        quit()
