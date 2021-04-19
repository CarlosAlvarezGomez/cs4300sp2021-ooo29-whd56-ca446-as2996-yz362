"""
This program finds the similarity between a query and the descriptions of the
recipes in the dataset.
"""

import pandas as pd
import numpy as np
import math
from collections import Counter
import time

# Paths
PATH_TO_RECIPES = '../../../Dataset/files/sampled_recipes.csv'
PATH_TO_INVERTED_INDEX = '../../../Dataset/files/inverted_index.csv'
PATH_TO_DOC_NORMS = '../../../Dataset/files/doc_norms.csv'

# Number of docs
N_DOCS = 61955

# Imports the recipe data
doc_dataframe = pd.read_csv(PATH_TO_RECIPES)

# Converts a string into a list of tokens
def tokenize_string(string):
  return string.lower().replace('.', '').replace(',', '').split(' ')

# Filters an inverted index using the so that it only keeps terms that are
# in the desired range
def filter_inverted_index(inverted_index_input, min_df=0.1, max_df=.9, n_docs=N_DOCS):
  new_inverted_index = {}
  minimum = min_df * n_docs
  maximum = max_df * n_docs

  for term, tfs in inverted_index_input.items():
    df = len(tfs)
    if df > minimum and df < maximum:
      new_inverted_index[term] = tfs
  
  return new_inverted_index

# Uses the recipes dataframe to make an inverted index
def make_inverted_index(recipes_df):
  recipe_ids = []
  recipe_desc = []
  inverted_index = {}
  
  for _, row in recipes_df.iterrows():
    recipe_ids.append(row['id'])
    recipe_desc.append(row['description'])

  # The following for-loop is mostly taken from the build-inverted-index
  # function in assignment 4
  for id, desc in zip(recipe_ids, recipe_desc):
    tokens_list = tokenize_string(desc)
    tokens_counter = Counter(tokens_list)

    for token, freq in tokens_counter.most_common():
      if token in inverted_index.keys():
        inverted_index[token] += [(id, freq)]
      else:
        inverted_index[token] = [(id, freq)]

  return filter_inverted_index(inverted_index)

# Saves the inverted index given into a csv file at the given path
def save_inverted_index(inverted_index_input, path_to_inverted_index=PATH_TO_INVERTED_INDEX):
  rows = []
  for term, tfs in inverted_index_input.items():
    string = '['
    for doc_id, freq in tfs:
      string += '(' + str(doc_id) + ':' + str(freq) + ') '

    rows.append((term, string[:-1] + ']'))
  
  inverted_index_df = pd.DataFrame(rows, columns = ['term', 'term-frequencies'])
  inverted_index_df.to_csv(path_to_inverted_index)

# Gets an inverted index from the given path
def get_inverted_index(path_to_inverted_index=PATH_TO_INVERTED_INDEX):
  inverted_index_df = pd.read_csv(path_to_inverted_index)
  inverted_indx = {}

  terms = inverted_index_df['term']
  term_frequencies = inverted_index_df['term-frequencies']

  string_to_tuple = lambda string: (int(string.split(':')[0]), float(string.split(':')[1]))

  for term, term_freqs in zip(terms, term_frequencies):
    term_freqs = list(map(lambda x : x.split(')')[0], term_freqs[1:-1].split('(')))
    term_freqs = list(map(string_to_tuple, term_freqs))

    inverted_index[term] = term_freqs

  return inverted_index
  
# Creates the inverted index used in the next functions
# inverted_index = make_inverted_index(doc_dataframe)

# Uses an inverted index to make a dictionary containing the doc norms
def make_doc_norms(inverted_index_input, n_docs=N_DOCS):
  doc_norms = {}

  for term, tfs in inverted_index_input.items():

    # The following idf formula is from assignment 4
    idf = math.log(n_docs / (1 + len(tfs))) 
    for doc_id, freq in tfs:
      if doc_id in doc_norms.keys():
        doc_norms[doc_id] = doc_norms[doc_id] + (freq*idf)**2
      else:
        doc_norms[doc_id] = (freq*idf)**2

  for doc_id, norm in doc_norms.items():
    doc_norms[doc_id] = norm**(1/2)

  return doc_norms

# Save the doc norms as a csv file at the given path
def save_doc_norms(doc_norms, path_to_doc_norms=PATH_TO_DOC_NORMS):
  df = pd.DataFrame(list(doc_norms.items()), columns=['id', 'norm'])
  df.to_csv(path_to_doc_norms)

# Gets the doc norms from a csv file at the given path
def get_doc_norms(path_to_doc_norms=PATH_TO_DOC_NORMS):
  doc_norms_df = pd.read_csv(path_to_doc_norms)

  ids = doc_norms_df['id']
  norms = doc_norms_df['norm']

  doc_norms = {}

  for id, norm in zip(ids, norms):
    doc_norms[int(id)] = float(norm)

  return doc_norms

# Calculates the cosine similiarities between the query and all the docs in
# recipe descriptions given
def get_cosine_similarities(query, inverted_index, n_docs=N_DOCS):
  
  doc_norms = get_doc_norms(PATH_TO_DOC_NORMS)

  scores = {}
  q_norm = 0
  relevant_terms = inverted_index.keys()
  query_toks_counter = Counter(tokenize_string(query))

  for term, q_freq in query_toks_counter.most_common():
    if term in relevant_terms:
      idf = math.log(n_docs / (1 + len(inverted_index[term])))
      q_norm += (q_freq*idf)**2
      for doc_id, tf in inverted_index[term]:
        if doc_id in scores.keys():
          scores[doc_id] = scores[doc_id] + (q_freq * tf * (idf**2))
        else:
          scores[doc_id] = (q_freq * tf * (idf**2))
      
  q_norm = q_norm**(1/2)
  scores_keys = list(scores.keys())
  for doc_id, doc_norm in doc_norms.items():
    if doc_id in scores_keys:
      scores[doc_id] = scores[doc_id] / (q_norm * doc_norm)
    else:
      scores[doc_id] = 0

  scores = {key:val for key, val in sorted(scores.items(), key=lambda x : x[1], reverse=True)}
  
  return scores