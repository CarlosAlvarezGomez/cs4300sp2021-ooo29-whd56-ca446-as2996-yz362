from descSimilarity import get_cosine_similarities, make_inverted_index
import time
import pandas as pd

t = time.time()

inverted_index = make_inverted_index(pd.read_csv('app/irsystem/controllers/Dataset/files/sampled_recipes.csv'))
diff = time.time() - t

t = time.time()

diffs = []
for i in range(1):
  a= get_cosine_similarities('sweet sour tasty', inverted_index=inverted_index)
  diff = time.time() - t
  diffs.append(diff)

b = list(a.items())
b.sort(key = lambda x : x[1], reverse=True)