import pandas as pd
import re
import string
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.feature_extraction.text import CountVectorizer

#reviews = pd.read_csv('app/irsystem/controllers/Dataset/files/sampled_reviews.csv')
