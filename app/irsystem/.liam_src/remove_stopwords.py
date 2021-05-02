"""
Removes stopwords from the descriptions in the
recipes data csv. 

Author: Liam Daniels
Date: May 2, 2021
"""
import pandas as pd

DATASET_DIR = "../controllers/Dataset/files/"
RECIPES_IN  = "{}sampled_recipes.csv".format(DATASET_DIR)
RECIPES_OUT = "{}sampled_recipes_short.csv".format(DATASET_DIR)

STOPWORDS_FILE = "stop_words_english.txt"

DESCRIPTION_ATTR = "description"

def read_stopwords(FILE=STOPWORDS_FILE):
    """ Precondition: stopwords file has one word on each line. """
    with open(FILE, "r") as f:
        lines = f.readlines()
    words = [w.strip() for w in lines]
    return words

def remove_stopwords_sentence(stopwords, sentence):
    tokens = sentence.split(" ")
    new_tokens = [t for t in tokens if t.strip() not in stopwords]
    return " ".join(new_tokens)

def remove_stopwords_df(stopwords, recipes_df):
    """ Note: Mutates the recipes_df. """
    rm_stop = lambda s: remove_stopwords_sentence(stopwords, s)
    recipes_df[DESCRIPTION_ATTR] = recipes_df[DESCRIPTION_ATTR].apply(rm_stop)
    return recipes_df

def make_new_recipes(FILENAME=RECIPES_OUT):
    recipes_df = pd.read_csv(RECIPES_IN)
    stopwords = read_stopwords()
    short_df = remove_stopwords_df(stopwords, recipes_df)
    short_df.to_csv(FILENAME, index = False)

if __name__ == "__main__":
    make_new_recipes()
    print("Done!")
