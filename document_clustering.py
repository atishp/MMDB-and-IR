
from __future__ import print_function
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics

from sklearn.cluster import KMeans, MiniBatchKMeans

import logging
from optparse import OptionParser
import sys
from time import time

import numpy as np


# parse commandline arguments using option parser
op = OptionParser()
op.add_option("--lsa",
              dest="n_components", type="int",
              help="Preprocess documents with latent semantic analysis.")
op.add_option("--no-minibatch",
              action="store_false", dest="minibatch", default=True,
              help="Use ordinary k-means algorithm (in batch mode).")
op.add_option("--no-idf",
              action="store_false", dest="use_idf", default=True,
              help="Disable Inverse Document Frequency feature weighting.")
op.add_option("--use-hashing",
              action="store_true", default=False,
              help="Use a hashing feature vectorizer")
op.add_option("--n-features", type=int, default=10000,
              help="Maximum number of features (dimensions)"
                   " to extract from text.")
op.add_option("--verbose",
              action="store_true", dest="verbose", default=False,
              help="Print progress reports inside k-means algorithm.")

(opts, args) = op.parse_args()
if len(args) > 0:
    op.error("this script takes no arguments.")
    sys.exit(1)

# Load some categories from the training set
categories = [
    'alt.atheism',
    'talk.religion.misc',
    'comp.graphics',
    'sci.space',
    'sci.med',
    'talk.politics.guns'
]

print("Loading 20 newsgroups dataset for categories:")
print(categories)

dataset = fetch_20newsgroups(subset='all', categories=categories,
                             shuffle=True, random_state=42)
#f = open('datasetOutput.txt','w')
##print >> f, '%s',dataset
#f.write("%s" %dataset)
#f.close()
print("%d documents" % len(dataset.data))
print("%d categories" % len(dataset.target_names))
#print ([x.encode('utf-8') for x in dataset.data])
print()

labels = dataset.target
true_k = np.unique(labels).shape[0]

print("Extracting features from the training dataset using a sparse vectorizer")
t0 = time()
#max_df - When building the vocabulary ignore terms that have a document frequency strictly higher than the given threshold
#min_df - When building the vocabulary ignore terms that have a document frequency strictly lower than the given threshold
vectorizer = TfidfVectorizer(max_df=0.5, max_features=opts.n_features,
                                 min_df=2, stop_words='english',
                                 use_idf=opts.use_idf) 
X = vectorizer.fit_transform(dataset.data)

print("done in %fs" % (time() - t0))
print()

# Do the actual clustering
#n_clusters : int, optional - The number of clusters to form as well as the number of centroids to generate.
#batch_size : int - Size of the mini batches.
#init : selects initial cluster centers for k-mean clustering in a smart way to speed up convergence. 
#n_init : Number of random initializations that are tried.
# init_size : Number of samples to randomly sample for speeding up the initialization
if opts.minibatch:
    km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                         init_size=1000, batch_size=1000, verbose=opts.verbose)
else:
    km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1,
                verbose=opts.verbose)

print("Clustering sparse data with %s" % km)
t0 = time()
km.fit(X)
print("done in %0.3fs" % (time() - t0))
print()

if not opts.use_hashing:
    print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1] #returns an index array of same shape for original array

    terms = vectorizer.get_feature_names()
    f = open('cluster_output.txt','w')

    for i in range(true_k):
        print("Cluster %d:" % i, end='')
        f.write("Cluster%d" %i)
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
            f.write(" %s" %terms[ind])
        f.write("\n")
        print()
f.close()

