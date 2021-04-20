""" 
Handles all duties related to ingredients 
within the recipe dataset, including 
tokenization and similarity measures.

Author: Liam Daniels
Date: 19 April 2021
"""
import pandas as pd
import numpy as np

DATASET_DIR = "app/irsystem/controllers/Dataset/files/"
RECIPE_FILE = "{}sampled_recipes.csv".format(DATASET_DIR)
ING_CATEGORY_NAME = "ingredients" 
RECIPE_CO2_FILENAME = "{}recipes_co2_sorted.csv".format(DATASET_DIR)
DIETARY_FILENAME = "{}dietary_restrictions.csv".format(DATASET_DIR)

def tokenize_recipe_ingredients(df):
    """
    Given a dataframe of the sampled recipe data,
    replaces that dataframe's ingredients field
    with a list of strings (tokens) instead of a 
    single long string. Also outputs this modified
    dataframe.
    """
    # Space seems like the best delimiter because we
    # want to isolate words like "beef" in ingredients
    # like "ground beef."
    DELIM = " "
    STRIP = "[] ',"

    ing_str_as_list = lambda ing: [s.strip(STRIP) for s in ing.split(DELIM)]
    df[ING_CATEGORY_NAME] = df[ING_CATEGORY_NAME].apply(ing_str_as_list)

    return df

def calc_edit_distance(s1, s2):
    """ Calculates Levenshtein edit distance between two strings"""
    INSERT_COST = 1
    DELETE_COST = 1
    SUB_COST    = 2
    NO_COST     = 0
    sub_func = lambda q, d, i, j: NO_COST if q[i - 1] == d[j - 1] else SUB_COST

    m = len(s1) + 1
    n = len(s2) + 1

    matrix = np.zeros((m, n))
    for i in range(1, m):
            matrix[i, 0] = matrix[i - 1, 0] + DELETE_COST
    for j in range(1, n):
        matrix[0, j] = matrix[0, j - 1] + INSERT_COST
    for i in range(1, m):
        for j in range(1, n):
            matrix[i, j] = min(
                matrix[i - 1, j] + DELETE_COST,
                matrix[i, j - 1] + INSERT_COST, 
                matrix[i - 1, j - 1] + sub_func(s1, s2, i, j) 
            )

    return matrix[-1][-1]

def contains_ingredient(recipe_series, ingredient_query, max_dist=2):
    """
    Checks whether or not a given recipe has an ingredient that
    is within a certain edit distance from the inputted ingredient 
    string. 

    Precondition: ingredients have already been tokenized.

    Parameters:
    -----------------
    recipe_series : pandas.Series
        A row in the recipes dataframe, representing one recipe.

    ingredient_query : str
        The ingredient being checked for within the recipe's ingredients.

    max_dist : int
        The largest edit distance such that two strings are still 
        considered equal.

    Returns:
    ------------------
    bool
        Whether recipe's ingredients contains a token within max_dist of
        the inputted ingredient.
    """
    ingredients = recipe_series[ING_CATEGORY_NAME]
    return list_contains_ingredient(ingredients, ingredient_query, max_dist)
    

def list_contains_ingredient(ingredients, ingredient_query, max_dist=2):
    for ing in ingredients:
        if calc_edit_distance(ing, ingredient_query) <= max_dist:
            return True
    return False

def make_meat_alias_dict(ALIAS_CSV="meat_aliases.csv"):
    """
    Creates dictionary that maps obscure meat parts to their
    common names. Based on specific file structure of a CSV
    that must be in the directory with a specific name.
    """
    with open(ALIAS_CSV) as f:
        lines = f.readlines()
    lines = [l.split(",") for l in lines[1:]]

    aliases = {}
    for l in lines:
        # Element 0 is original name, all others are aliases
        for i in range(1, len(l)):
            alias = l[i].strip()
            original = l[0].strip()
            aliases[alias] = original
    return aliases

def first_n_filtered(ranked_ids, banned_foods, dietary_restrictions, n,
                    max_dist=2):
    """
    Given a list of recipe ids, outputs a list of the first n
    recipes that do not contain ingredients from the list of
    banned foods. The dietary restrictions is a list of strings
    that adds pre-made lists to banned foods.
    """
    df = tokenize_recipe_ingredients(pd.read_csv(RECIPE_FILE))

    diet_r_df = pd.read_csv(DIETARY_FILENAME)
    VEGET = "vegetarian"
    VEGAN = "vegan"
    PESCA = "pescatarian"
    for restriction in [VEGET, VEGAN, PESCA]:
        upper_rest = restriction.upper()
        if restriction in dietary_restrictions:
            banned_foods += diet_r_df[upper_rest].dropna().to_list()

    def contains_banned_ing(rec_ser):
        if banned_foods is not None:
            for food in banned_foods:
                if contains_ingredient(rec_ser, food, max_dist):
                    return True
        return False

    count = 0
    ls = []
    for i in range(0, len(ranked_ids)):
        recipe_df = df.loc[df["id"] == ranked_ids[i]]
        if len(recipe_df) > 0 and not contains_banned_ing(recipe_df.iloc[0]):
            ls.append(ranked_ids[i])
            count += 1
        if count >= n:
            break
    return ls

def get_recipe_co2_df():
    df = tokenize_recipe_ingredients(pd.read_csv(RECIPE_CO2_FILENAME))
    return df
