from sqlite3 import Cursor, IntegrityError
from functools import lru_cache
import config



@lru_cache
def add_faction_to_table(name: str, cursor: Cursor) -> int:
    faction_id = -1
    if name.startswith("select one of its profiles "):
        return 
    try:
        config.lock.acquire(True)
        cursor.execute("""INSERT OR IGNORE INTO Faction(Name) VALUES (?) RETURNING ID;""", (name,))
        faction_id = cursor.fetchone()[0]
        if faction_id == -1:
            cursor.execute(f"""SELECT ID FROM Faction WHERE Name='{name}'""")
            faction_id = cursor.fetchone()[0]
    except IntegrityError:
        cursor.execute(f"""SELECT ID FROM Faction WHERE Name='{name}'""")
        faction_id = cursor.fetchone()[0]
    finally:
        config.lock.release()
        return faction_id


def add_leader_to_table(cursor: Cursor, leader_id: int, unit_name: str):
    try:
        config.lock.acquire(True)
        cursor.execute(f"""SELECT ID FROM Unit WHERE Name='{unit_name}'""")
        unit_id = cursor.fetchone()[0]
        cursor.execute("""INSERT OR IGNORE INTO LeadableUnits(LeaderID, UnitID) VALUES(?,?)""", (leader_id, unit_id))
    finally:
        config.lock.release()


def add_unit_to_table(name: int, factions: tuple, cursor: Cursor) -> int:
    id = None
    try:
        config.lock.acquire(True)
        if len(factions) >= 2:
            cursor.execute("""INSERT INTO Unit(PrimaryFactionID, Name, SecondaryFactionID) VALUES(?,?,?) RETURNING ID;""", (factions[0], name, factions[1]))
            id = cursor.fetchone()[0]
        elif len(factions) == 1:
            cursor.execute("""INSERT INTO Unit(PrimaryFactionID, Name) VALUES(?,?) RETURNING ID;""", (factions[0], name))
            id = cursor.fetchone()[0]
        
        if id == None:
            cursor.execute(f"""SELECT ID FROM Unit WHERE Name='{name}'""")
            id = cursor.fetchone()[0]
            if id == None:
                print("here 4")
    except IntegrityError:
        pass
    finally:
        config.lock.release()
        return id


@lru_cache
def add_weapon_keyword_to_table(weapon_id: int, keywords: str, cursor: Cursor):
    keyword_id = None
    keywords = keywords.strip("[")
    keywords = keywords.strip("]")
    keywords = keywords.split(",")
    for keyword in keywords:
        if keyword[0] == " ":
            keyword = keyword[1:]
        elif keyword[0:1] == "  ":
            keyword = keyword[2:]
        try:
            config.lock.acquire(True)
            cursor.execute("""INSERT OR IGNORE INTO WeaponKeywords(Name) VALUES (?) RETURNING ID;""", (keyword,))
            keyword_id = cursor.fetchone()
            if keyword_id is None:
                cursor.execute(f"""SELECT ID FROM WeaponKeywords WHERE Name='{keyword}'""")
                keyword_id = cursor.fetchone()

            cursor.execute("""INSERT OR IGNORE INTO WeaponKeyWordsUsed(WeaponID, WeaponKeywordID) VALUES(?,?);""", (weapon_id, keyword_id[0]))
        except IntegrityError:
            config.lock.release()
        finally:
            config.lock.release()


def add_unit_keyword(keyword: str, cursor: Cursor, unit_id: int):
    try:
        config.lock.acquire(True)
        cursor.execute("""INSERT OR IGNORE INTO UnitKeywords(Name) VALUES(?) RETURNING ID;""", (keyword, ))
        keywordID = cursor.fetchone()
        if type(keywordID) is tuple:
            keywordID = keywordID[0]
        cursor.execute("""INSERT INTO UnitKeywordsUsed(UnitID, KeywordID) VALUES(?,?)""", (unit_id, keywordID))
    except IntegrityError:
        cursor.execute(f"""SELECT ID FROM UnitKeywords Where Name='{keyword}'""")
        keywordID = cursor.fetchone()
        if type(keywordID) is tuple:
            keywordID = keywordID[0]
        cursor.execute("""INSERT OR IGNORE INTO UnitKeywordsUsed(UnitID, KeywordID) VALUES(?,?)""", (unit_id, keywordID))
    finally:
        config.lock.release()


def add_weapon_to_table(name: str, statlineID: int, cursor: Cursor) -> int:
    try:
        config.lock.acquire(True)
        cursor.execute("""INSERT OR IGNORE INTO Weapons(StatlineID, Name)
                        VALUES(?,?)
                        RETURNING ID;""", (statlineID, name))    
        id = cursor.fetchone()
        if id is None:
            cursor.execute(f"""SELECT ID FROM Weapons WHERE Name='{name}';""")
            id = cursor.fetchone()
    except IntegrityError as Error:
        print(Error)
        config.lock.release()
    finally:
        config.lock.release()

    return id[0]


def add_weapon_statline_to_table(statline: list, range: str, cursor: Cursor) -> int:
    attacks = statline[0]
    skill = statline[1][0]
    if skill == "N":
        skill = -1
    skill = int(skill)
    strength = statline[2]
    ap = int(statline[3].strip("-"))
    damage = statline[4]
    
    try:
        config.lock.acquire(True)
        cursor.execute(f"""
            SELECT ID
            FROM WeaponStatline
            WHERE Range='{range}' AND Attacks='{attacks}' AND Skill={skill} AND
                Strength='{strength}' AND AP={ap} and Damage='{damage}';""")
        
        statlines_found = cursor.fetchall()
        if statlines_found != []:
            return statlines_found[0][0]
        else:
            cursor.execute("""INSERT INTO WeaponStatline(Range, Attacks, Skill, Strength, AP, Damage)
                        VALUES(?,?,?,?,?,?)
                        RETURNING ID;""", (range, attacks, skill, strength, ap, damage))
        
            id = cursor.fetchone()
            return id[0]
    finally:
        config.lock.release()
