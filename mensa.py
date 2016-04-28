#!/usr/bin/env python3
import argparse
import os
import urllib.request
from bs4 import BeautifulSoup
import re

_MENSA_URL = "http://www.uni-bremen.de/service/taeglicher-bedarf/essen-auf-dem-campus/cafeteria/390"


def _get_mensa_info():
    result = urllib.request.urlopen(_MENSA_URL)
    html = result.read()

    soup = BeautifulSoup(html, "html.parser")

    main_div = soup.html.find("div", class_="tx-hbucafeteria-pi1")
    main_heading = main_div.find("h2")
    meal_trs = main_div.find("table")
    hours_div = main_div.find_all("div", class_="tx-hbucafeteria-pi1-info")[1]

    return (main_heading.string, meal_trs, hours_div)


def _get_hours():
    heading, meal_trs, hours_div = _get_mensa_info()
    strings = [str(tag) for tag in hours_div.contents[2:]]
    return "".join(strings).replace("<br>", "\n").replace("</br>", "")



if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Mensa menu from your terminal.")
    argparser.add_argument("-o" "--open",
                           action="store_true",
                           help="Show opening hours.")
    args = argparser.parse_args()

    hours = _get_hours()
    print(hours)
    quit()
