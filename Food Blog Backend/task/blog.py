import argparse
import os
import sqlite3
import sys


def create_table(query_):
    global dbname
    connection_ = sqlite3.connect(dbname)
    cursor_ = connection_.cursor()
    cursor_.execute(query_)
    connection_.commit()
    cursor_.close()


def create_recipe(option_):
    if option_ == "":
        return False
    print("Recipe description:")
    id_ = add_recipe(option_, input())
    print("1) breakfast  2) brunch  3) lunch  4) supper")
    print("When the dish can be served:")
    meals_ = input().split(" ")
    print(id_)
    add_serve(id_, meals_)
    add_quantity(id_)
    return True


def add_quantity(id_):
    connection_ = sqlite3.connect(dbname)
    cursor_ = connection_.cursor()
    while True:
        print("Input quantity of ingredient <press enter to stop>:")
        choice_ = input().split(" ")
        if len(choice_) == 1:
            break
        if len(choice_) < 3:
            measure_ = ""
            quantity_ = int(choice_[0])
            ingredient_ = check_ingredient(choice_[1])
            if len(ingredient_) > 1:
                print("The ingredient is not conclusive!")
                continue
            measure_id_ = cursor_.execute("SELECT measure_id FROM measures WHERE measure_name=''").fetchone()[0]
            connection_.commit()
            ingredient_id_ = cursor_.execute(("SELECT ingredient_id FROM ingredients WHERE ingredient_name='{}'"
                                              .format(ingredient_[0]))).fetchone()[0]
            connection_.commit()
            query_ = """INSERT OR IGNORE INTO quantity (quantity, measure_id, ingredient_id, recipe_id)
                        VALUES ({}, {}, {}, {})""".format(quantity_, int(measure_id_), int(ingredient_id_), id_)
            cursor_.execute(query_)
            connection_.commit()
        else:
            measure_ = check_measure(choice_[1])
            if len(measure_) > 1:
                print("The measure is not conclusive!")
                continue
            quantity_ = int(choice_[0])
            ingredient_ = check_ingredient(choice_[2])
            if len(ingredient_) > 1:
                print("The ingredient is not conclusive!")
                continue
            measure_id_ = cursor_.execute("SELECT measure_id FROM measures WHERE measure_name='{}'"
                                          .format(measure_[0])).fetchone()[0]
            connection_.commit()
            ingredient_id_ = cursor_.execute(("SELECT ingredient_id FROM ingredients WHERE ingredient_name='{}'"
                                              .format(ingredient_[0]))).fetchone()[0]
            connection_.commit()
            query_ = """INSERT OR IGNORE INTO quantity (quantity, measure_id, ingredient_id, recipe_id)
                        VALUES ({}, {}, {}, {})""".format(quantity_, int(measure_id_), int(ingredient_id_), id_)
            cursor_.execute(query_)
            connection_.commit()

    cursor_.close()


def check_ingredient(ingredient_):
    global data
    return [x for x in data["ingredients"] if x.__contains__(ingredient_)]


def check_measure(measure_):
    global data
    return [x for x in data["measures"] if x.startswith(measure_)]


def add_serve(id_, meals_):
    global dbname
    connection_ = sqlite3.connect(dbname)
    cursor_ = connection_.cursor()
    for meal_ in meals_:
        query_ = "INSERT OR IGNORE INTO serve (recipe_id, meal_id) VALUES ({}, {})".format(id_, int(meal_))
        print(query_)
        cursor_.execute(query_)
        connection_.commit()
    cursor_.close()


def add_recipe(name_, desc_):
    global dbname
    connection_ = sqlite3.connect(dbname)
    cursor_ = connection_.cursor()
    query_ = "INSERT OR IGNORE INTO recipes (recipe_name, recipe_description) VALUES ('{}', '{}')" \
        .format(name_, desc_)
    id_ = cursor_.execute(query_).lastrowid
    connection_.commit()
    cursor_.close()
    return id_


def find_recipe(ingredients_, meals_):
    global dbname
    connection_ = sqlite3.connect(dbname)
    cursor_ = connection_.cursor()
    max_id = cursor_.execute("SELECT MAX(recipe_id) FROM recipes").fetchone()[0]
    connection_.commit()

    meals_id = []
    for meal_ in meals_.split(","):
        meal_id_ = cursor_.execute("SELECT meal_id FROM meals WHERE meal_name='{}'".format(meal_)).fetchone()[0]
        connection_.commit()
        meals_id.append(str(meal_id_))
    meal_recipe_ = cursor_.execute("SELECT recipe_id FROM serve WHERE meal_id IN ({})".format(", ".join(meals_id))).fetchall()
    connection_.commit()
    recipes_meals = []
    for recipe_ in meal_recipe_:
        if recipe_[0] not in recipes_meals:
            recipes_meals.append(recipe_[0])


    ingredients_id = []
    for ingredient_ in ingredients_.split(","):
        ingredient_ = ingredient_.strip()
        ingredient_id_ = cursor_.execute("SELECT ingredient_id FROM ingredients WHERE ingredient_name='{}'".format(ingredient_)).fetchone()
        if ingredient_id_ is None:
            print("There are no such recipes in the database.")
            return
        connection_.commit()
        ingredients_id.append(str(ingredient_id_[0]))

    recipes_ing = []
    for recipe_ in ingredients_id:
        if recipe_[0] not in recipes_ing:
            recipes_ing.append(int(recipe_[0]))

    recipes_final = []
    for id_ in recipes_meals:
        ingredient_recipe_ = cursor_.execute("SELECT ingredient_id FROM quantity WHERE recipe_id IN ({})".format(id_)).fetchall()
        connection_.commit()
        temp = []
        for x_ in ingredient_recipe_:
            temp.append(x_[0])
        if set(recipes_ing).issubset(set(temp)):
            recipes_final.append(id_)
    connection_.commit()
    recipes_ = []
    for id_ in recipes_final:
        final_ = cursor_.execute("SELECT recipe_name FROM recipes WHERE recipe_id={}".format(id_)).fetchone()[0]
        recipes_.append(final_)
        connection_.commit()
    if len(recipes_) < 1:
        print("There are no such recipes in the database.")
    else:
        print("Recipes selected for you: {}".format(", ".join(recipes_)))
    cursor_.close()

parser = argparse.ArgumentParser(description="This program prints recipes \
consisting of the ingredients you provide.")
parser.add_argument("dbname")
parser.add_argument("--ingredients")
parser.add_argument("--meals")
args = parser.parse_args()
dbname = args.dbname

if args.ingredients is not None and args.meals is not None:
    find_recipe(args.ingredients, args.meals)
else:
    create_measure_query = """CREATE TABLE IF NOT EXISTS measures (
                                measure_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                measure_name TEXT UNIQUE);"""
    create_ingredient_query = """CREATE TABLE IF NOT EXISTS ingredients (
                                ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                ingredient_name TEXT NOT NULL UNIQUE);"""
    create_meal_query = """CREATE TABLE IF NOT EXISTS meals (
                                meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                meal_name TEXT NOT NULL UNIQUE);"""
    create_recipe_query = """CREATE TABLE IF NOT EXISTS recipes (
                                recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                recipe_name TEXT NOT NULL, recipe_description TEXT);"""
    create_serve_query = """CREATE TABLE IF NOT EXISTS serve(serve_id INTEGER PRIMARY KEY, recipe_id INTEGER NOT NULL,
                                meal_id INTEGER NOT NULL,
                                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id), 
                                FOREIGN KEY(meal_id) REFERENCES meals(meal_id));"""
    create_quantity_query = """CREATE TABLE IF NOT EXISTS quantity(quantity_id INTEGER PRIMARY KEY,
                                quantity INTEGER NOT NULL,
                                measure_id INTEGER NOT NULL,
                                ingredient_id INTEGER NOT NULL,
                                recipe_id INTEGER NOT NULL,
                                FOREIGN KEY(measure_id) REFERENCES measures(measure_id),
                                FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id),
                                FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id));"""

    create_table(create_measure_query)
    create_table(create_ingredient_query)
    create_table(create_meal_query)
    create_table(create_recipe_query)
    create_table(create_serve_query)
    create_table(create_quantity_query)

    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    for table in data:
        for item in data[table]:
            sql_statement = "INSERT OR IGNORE INTO {} ({}) VALUES ('{}')" \
                .format(table, table.rstrip("s") + "_name", item)
            cursor.execute(sql_statement)
            connection.commit()

    result = True
    print("Pass the empty recipe name to exit.")
    while result:
        print("Recipe name:")
        result = create_recipe(input())

    cursor.close()
    connection.close()
