from descSimilarity import get_cosine_similarities
import time

diffs = []
for i in range(20):
  t = time.time()
  a= get_cosine_similarities('sweet sour tasty')
  diff = time.time() - t
  diffs.append(diff)

print(sum(diffs)/len(diffs))
b = list(a.items())
b.sort(key = lambda x : x[1], reverse=True)
print(b[:10])