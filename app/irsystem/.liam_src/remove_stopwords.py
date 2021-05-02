"""
Removes stopwords from the descriptions in the
recipes data csv. 

Author: liam daniels
Date: May 2, 2021
"""
import pandas as pd

dataset_dir = "../controllers/dataset/files/"
recipes_in  = "{}sampled_recipes.csv".format(dataset_dir)
recipes_out = "{}sampled_recipes_short.csv".format(dataset_dir)

stopwords_file = "stop_words_english.txt"

description_attr = "description"

def read_stopwords(file=stopwords_file):
    """ precondition: stopwords file has one word on each line. """
    with open(file, "r") as f:
        lines = f.readlines()
    words = [w.strip() for w in lines]
    return words

def remove_stopwords_sentence(stopwords, sentence):
    tokens = sentence.split(" ")
    new_tokens = [t for t in tokens if t.strip() not in stopwords]
    return " ".join(new_tokens)

def remove_stopwords_df(stopwords, recipes_df):
    """ note: mutates the recipes_df. """
    rm_stop = lambda s: remove_stopwords_sentence(stopwords, s)
    recipes_df[description_attr] = recipes_df[description_attr].apply(rm_stop)
    return recipes_df

def make_new_recipes(filename=recipes_out):
    recipes_df = pd.read_csv(recipes_in)
    stopwords = read_stopwords()
    short_df = remove_stopwords_df(stopwords, recipes_df)
    short_df.to_csv(filename, index = false)

if __name__ == "__main__":
    make_new_recipes()
    print("done!")
