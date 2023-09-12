from sqlite3 import Cursor


def create_unit_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Unit(
            ID INTEGER NOT NULL PRIMARY KEY,
            PrimaryFactionID INTEGER NOT NULL REFERENCES Faction(ID),
            Name STRING NOT NULL UNIQUE,
            SecondaryFactionID INTEGER REFERENCES Faction(ID)
        );""")

    print("Created the Unit table")
    return cursor


def create_faction_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Faction(
            ID INTEGER PRIMARY KEY,
            Name STRING NOT NULL UNIQUE
        );""")

    print("Created the faction table")
    return cursor


def create_faction_ability_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FactionAbility (
            ID INTEGER NOT NULL PRIMARY KEY,
            FactionID INTEGER NOT NULL REFERENCES Faction(ID),
            Name STRING NOT NULL,
            Description STRING NO NULL,
            UNIQUE(Name, Description)
        );""")

    print("Created the facition ability table")

    return cursor


def create_unit_composition_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UnitComposition (
            FactionID INTEGER NOT NULL REFERENCES Faction(ID),
            ModelID INTEGER NOT NULL REFERENCES Model(ID),
            Amount INTEGER NOT NULL,
            PRIMARY KEY (FactionID, ModelID)
        );""")

    print("Created unit composition table")
    return cursor


def create_model_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Model (
            ID INTEGER NOT NULL PRIMARY KEY,
            UnitID INTEGER NOT NULL REFERENCES Unit(ID),
            Name STRING NOT NULL UNIQUE,
            StatlineID INTEGER NOT NULL REFERENCES ModelStatline(ID)
        );""")

    print("Created model table")
    return cursor


def create_model_statline_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ModelStatline (
            ID INTEGER NOT NULL PRIMARY KEY,
            Move INTEGER NOT NULL,
            Toughness INTEGER NOT NULL,
            Save INTEGER NOT NULL,
            Wounds INTEGER NOT NULL,
            Leadership INTEGER NOT NULL,
            ObjectiveControl INTEGER NOT NULL,
            InvulernableSave INTEGER,
            FeelNoPain INTEGER
        );""")

    print("Created model statline table")
    return cursor


def create_wargear_options_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WargearOptions (
            ID INTEGER NOT NULL PRIMARY KEY,
            ModelID INTEGER NOT NULL REFERENCES Model(ID),
            WargearID INTEGER REFERENCES Weargear(ID),
            WeaponID INTEGER REFERENCES Weapon(ID)
        );""")

    print("Created Wargear options table")
    return cursor


def create_wargear_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Wargear (
            ID INTEGER NOT NULL PRIMARY KEY,
            Name STRING NOT NULL,
            Description STRING NOT NULL,
            UNIQUE(Name, Description)
        );""")

    print("Created wargear options table")
    return cursor


def create_weapon_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Weapons(
            ID INTEGER NOT NULL PRIMARY KEY,
            StatlineID INTEGER NOT NULL REFERENCES WeaponStatline(ID),
            Name STRING NOT NULL UNIQUE
        );""")

    print("Created the weapons tables")
    return cursor


def create_weapon_statline_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WeaponStatline(
            ID INTEGER NOT NULL PRIMARY KEY,
            Range INTEGER NOT NULL,
            Attacks STRING NOT NULL,
            Skill INTEGER NOT NULL,
            Strength STRING NOT NULL,
            AP INTEGER NOT NULL,
            Damage STRING NOT NULL
        );""")

    print("created the weapon statline table")
    return cursor


def create_weapon_keywords_used_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WeaponKeyWordsUsed(
            WeaponID INTEGER NOT NULL REFERENCES Weapons(ID),
            WeaponKeywordID INTEGER NOT NULL REFERENCES WeaponKeywords(ID),
            PRIMARY KEY (WeaponID, WeaponKeyWordID)
        );""")

    print("created the weapon keywords used table")
    return cursor


def create_weapon_keywords_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WeaponKeywords(
            ID INTEGER NOT NULL PRIMARY KEY,
            Name STRING NOT NULL UNIQUE
        );""")

    print("created the weapon keywords table")
    return cursor


def create_unit_keywords_used_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UnitKeywordsUsed(
            UnitID INTEGER NOT NULL REFERENCES Unit(ID),
            KeywordID INTEGER NOT NULL REFERENCES UnitKeywords(ID),
            PRIMARY KEY(UnitID, KeywordID)
        );""")

    print("Created the unit keywords used table")
    return cursor


def create_unit_keywords_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UnitKeywords(
            ID INTEGER NOT NULL PRIMARY KEY,
            Name STRING NOT NULL UNIQUE
        );""")

    print("Created the unit keywords table")
    return cursor


def create_abilities_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Abilites(
            UnitID INTEGER NOT NULL REFERENCES Unit(ID),
            AbilityID INTEGER NOT NULL,
            Type INTEGER NOT NULL,
            PRIMARY KEY (UnitID, AbilityID, Type)
        );""")

    print("created the abilites table")
    return cursor


def create_core_ability_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CoreAbilites(
            ID INTEGER NOT NULL PRIMARY KEY,
            Name STRING NOT NULL UNIQUE
        );""")

    print("created the core abilites table")
    return cursor


def create_unit_abilities_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UnitAbilites(
            ID INTEGER NOT NULL PRIMARY KEY,
            Name STRING NOT NULL,
            Description STRING NULL,
            UNIQUE(Name, Description)
        );""")

    print("created the unit ability table")
    return cursor


def create_leader_ability_table(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LeaderAbility(
            ID INTEGER NOT NULL PRIMARY KEY,
            Name STRING NOT NULL,
            Description STING NOT NULL,
            UNIQUE(Name, Description)
        );""")

    print("created the leader ability table")
    return cursor


def create_leadable_units(cursor: Cursor) -> Cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LeadableUnits(
            LeaderID INTEGER NOT NULL REFERENCES Unit(ID),
            UnitID INTEGER NOT NULL REFERENCES Unit(ID),
            PRIMARY KEY (LeaderID, UnitID)
        );""")

    print("created the leadable units table")
    return cursor


def initalise_database(cursor: Cursor) -> Cursor:
    """creates the tables in the database, checking if they do not exist"""

    cursor = create_unit_table(cursor)
    cursor = create_faction_table(cursor)
    cursor = create_faction_ability_table(cursor)
    cursor = create_unit_composition_table(cursor)
    cursor = create_model_table(cursor)
    cursor = create_model_statline_table(cursor)
    cursor = create_wargear_options_table(cursor)
    cursor = create_wargear_table(cursor)
    cursor = create_weapon_table(cursor)
    cursor = create_weapon_statline_table(cursor)
    cursor = create_weapon_keywords_used_table(cursor)
    cursor = create_weapon_keywords_table(cursor)
    cursor = create_unit_keywords_used_table(cursor)
    cursor = create_unit_keywords_table(cursor)
    cursor = create_abilities_table(cursor)
    cursor = create_core_ability_table(cursor)
    cursor = create_unit_abilities_table(cursor)
    cursor = create_leader_ability_table(cursor)
    cursor = create_leadable_units(cursor)
