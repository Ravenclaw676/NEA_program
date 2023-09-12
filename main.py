from tables import initalise_database
from add_data import add_weapon_keyword_to_table,\
                    add_weapon_statline_to_table, add_weapon_to_table, \
                    add_unit_keyword, add_faction_to_table, add_unit_to_table, \
                    add_leader_to_table
from manifest_generator import download_pdfs
from search_table import get_unit_name, get_unit_id
import json

import PyPDF2
import re

import sqlite3

import time
import threading

import config

config.lock = threading.Lock()

leader_units = []

def read_manifest_json(URL: str) -> list:
    """loads a json file that URL the specifies"""
    with open(URL, "r") as manifest_file:
        return json.loads(manifest_file.read())


def compile_regex() -> dict:
    weapon_pattern = (r"([A-Z][a-z\-– ]+)( |\n)(\[[A-Z1-6 \-\+,]+\])*"
                      r"( |)([0-9]+\"|Melee) ([0-9+*\-Dd N\/A]+)")
    weapons_compiled = re.compile(weapon_pattern)
    unit_keywords_pattern = "KEYWORDS: +([A-z, \n’]+)?(?=(RANGED|FACTION KEYWORD))"
    keywords_compiled = re.compile(unit_keywords_pattern)
    faction_name_pattern = "FACTION KEYWORDS: *\n *(([A-z][A-z,’ ]+)){1,2}?(?=ABILITIES)"
    faction_name_compiled = re.compile(faction_name_pattern)
    unit_name_pattern = "^([A-Z ÛÔ!Â‘’É-]+)?(?=\n)"
    unit_name_compiled = re.compile(unit_name_pattern)

    dictionary = {"weapons": weapons_compiled, "keywords": keywords_compiled, "faction_name": faction_name_compiled, "unit_name": unit_name_compiled}
    return dictionary


def read_pdf(URL: str, cursor: sqlite3.Cursor, threads: list, regex: dict) -> list:
    """reads each page of a given pdf adnd adds the data to the Database.
    """
    file = PyPDF2.PdfReader(URL)
    for count, page in enumerate(file.pages):
        text = page.extract_text()
        temp_threads = []
        # removes pages that are not relevent to the program
        if re.findall(".+\nARMY RULES\n.+", text) or \
            re.findall(".+\nDETACHMENT RULE\n.+",text) or \
            re.findall(".+\nSTRATAGEMS\n.+", text) or \
            re.findall(".+Enhancements.+", text) or text == "":
            continue
        elif re.findall("RANGED WEAPONS[A-z0-9 \n-–’]+WARGEAR OPTIONS", text):
            # some units have all their information on 1 page
            unit_factions = add_faction(regex["faction_name"], text, cursor)
            unit_id = add_unit(regex["unit_name"], text, cursor, unit_factions)
            
            if re.findall("LEADER", text):
                temp_threads.append(threading.Thread(target=add_leader, args=(" ■([A-Z][A-z ]+[^:* ])\n", text, cursor, unit_id)))
            # each function that inputs the data into the database is executed on a seperate thread
            temp_threads.append(threading.Thread(target=add_weapon, args=(regex["weapons"], text, cursor)))
            temp_threads.append(threading.Thread(target=add_unit_keywords, args=(regex["keywords"], text, unit_id, cursor)))
        elif re.findall("WARGEAR OPTIONS", text):
            # unit_name = re.findall("(?<!\n)(?<=[.a-z)])((?! *UNIT)[A-Z ÛÔÂ‘’É!-]{3,})\n", text)
            #  unit_name = [name for name in unit_name if not name.isspace()]
            # if unit_name[0] in (" ATV", " WHERE "):
            #     unit_name = unit_name[1]
            # else:
            #     unit_name = unit_name[0]
            # unit_name = unit_name.replace("  ", " ")
            # if unit_name[0] == " ":
            #     unit_name = unit_name[1:]
            # 
            # unit_name = unit_name.title()
            
            # unit_id = get_unit_id(unit_name, cursor)
            # if unit_id == None:
            #     print(text)
            # if re.findall("LEADER", text):
            #    temp_threads.append(threading.Thread(target=add_leader, args=(" ■([A-Z][A-z ]+[^:* ])\n", text, cursor, unit_id)))   
            pass
        else:
            unit_factions = add_faction(regex["faction_name"], text, cursor)
            unit_id = add_unit(regex["unit_name"], text, cursor, unit_factions)

            # each function that inputs the data into the database is executed on a seperate thread
            temp_threads.append(threading.Thread(target=add_weapon, args=(regex["weapons"], text, cursor)))
            temp_threads.append(threading.Thread(target=add_unit_keywords, args=(regex["keywords"], text, unit_id, cursor)))

        #this starts each thread
        for thread in temp_threads:
            thread.start()
            threads.append(thread)

    return threads


def add_leader(pattern: str, page: str, cursor: sqlite3.Cursor, leader_id: int):
    leadable_units = re.findall(pattern, page)
    for count, unit in enumerate(leadable_units):
        leader_name = get_unit_name(leader_id, cursor)
        unit = unit.replace("  ", " ")
        unit = unit.replace("\n", "")
        if unit.find("None") != -1:
            leadable_units[count] = ""
            continue
        elif unit.endswith(leader_name.upper()):
            unit = unit.removesuffix(leader_name.upper())
            leadable_units[count] = unit.title()
        else:
            unit = unit.title()
            leadable_units[count] = unit

    
    for unit in leadable_units:
        if unit == "":
            pass
        else:
            leader_units.append((leader_id, unit))


def add_unit(pattern: re.Pattern, page: str, cursor: sqlite3.Cursor, factions: list) -> int:
    name = re.findall(pattern, page)
    if factions == []  or name == []:
        return
    name = name[0].title()
    # the first datasheets in a warhammer legends PDF starts with warhammer legends
    if name.startswith("Warhammer  Legends"):
        name = name.removeprefix("Warhammer  Legends")
    if name.endswith(" "):
        name = name[0: len(name) - 1]
    name = name.replace("  ", " ")
    id = add_unit_to_table(name, factions, cursor)
    if id == None:
        # print("here 4")
        pass
    return id


def add_faction(pattern: re.Pattern, page: str, cursor: sqlite3.Cursor) -> list:
    keywords = re.findall(pattern, page)
    if keywords != []:
        keywords = keywords[0][0].split(", ")
    
    faction_ids = []
    for keyword in keywords:
        #removes common suffixs that the REGEX does not catch
        if keyword.endswith("ABILITIES"):
            keyword = keyword.removesuffix("ABILITIES")
        elif keyword.endswith("KEYWORDS"):
            keyword = keyword.removesuffix("KEYWORDS")
        elif keyword.endswith("M T SV W LD OC"):
            keyword = keyword.removesuffix("M T SV W LD OC")
        elif keyword.find("Before") != -1:
            keyword = keyword[0:keyword.find("Before") - 1]
        if keyword == "Deathwatch":
            print("here")
        faction_ids.append(add_faction_to_table(keyword.lower(), cursor))
    return faction_ids


def add_weapon(pattern, page: str, cursor: sqlite3.Cursor):
    weapons = re.findall(pattern, page)
    for weapon in weapons:
        weapon = [x for x in weapon if x not in ["", " ", "\n"]]
        name = weapon[0]
        range = "0"
        keywords = ""
        # standardises the formating of the table
        if weapon[1][0] == "[":
            keywords = weapon[1]
            range = weapon[2]
        else:
            range = weapon[1]
        statline = ""
        if range == weapon[2]:
            statline = weapon[3].split(" ")
        else:
            statline = weapon[2].split(" ")
        statline_id = add_weapon_statline_to_table(statline, range, cursor)
        weapon_id = add_weapon_to_table(name, statline_id, cursor)
        if weapon[1][0] == "[":
            add_weapon_keyword_to_table(weapon_id, keywords, cursor)


def add_unit_keywords(keywords_pattern: re.Pattern, page: str, unit_id: int, cursor: sqlite3.Cursor):
    keywords = re.findall(keywords_pattern, page)
    if keywords != []:
        keywords = keywords[0][0].split(", ")
        for keyword in keywords:
            if keyword[0] == "\n" or keyword[0] == " ":
                keyword = keyword[1:]
                if keyword[0] == "\n":
                    keyword = keyword[1:]
            add_unit_keyword(keyword, cursor, unit_id)


def main():
    cursor = None
    database = sqlite3.connect("datasheets.db", check_same_thread=False)
    cursor = database.cursor()
    initalise_database(cursor)
    manifest = download_pdfs()
    start_time = time.time()
    regex = compile_regex()
    for pdf in manifest:
        threads = []
        # each thread read_pdf creates is added to a list.
        threads = read_pdf(f"./faction_pdfs/{pdf}", cursor, threads, regex)
        
        # waits for all threads to finish before moving onto the next PDF
        for thread in threads:
            thread.join()
        
        for leader in leader_units:
            if leader[1] == 'Imperium Battleline Infantry':
                continue
            elif leader[0] == None:
                print("here 3")
            # add_leader_to_table(cursor, *leader)

    end_time = time.time()
    print(end_time - start_time)
    
    print(leader_units)
    database.commit()


if __name__ == "__main__":
    main()
