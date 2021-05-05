from descSimilarity import *
import time
import pandas as pd

# t = time.time()

# inverted_index = make_inverted_index(pd.read_csv('Dataset/files/sampled_recipes.csv', index_col='id'))
# diff = time.time() - t

# t = time.time()

# diffs = []
# for i in range(10):
#   t = time.time()
#   a= get_cosine_similarities('so far this is my favorite recipe that i use.  it is from joanna lund.  i make this at least once a month.  it has a great taste and the portion size is plentiful. per serving is 260 calories.  the diabetic exchanges per serving are:  2 1/2 protein, 2 vegetable, 1 starch.  you won\'t be sorry for trying it.  my 3 year old son eats it too.  you won\'t miss the fat/calories.', inverted_index=inverted_index)
#   diff = time.time() - t
#   diffs.append(diff)

# print(sum(diffs)/len(diffs))
# b = list(a.items())
# b.sort(key = lambda x : x[1], reverse=True)
# print(b[:10])

s = 'qwer  weq.,ew .qwr ,.req ,'
a = tokenize_string(s)
print(a)