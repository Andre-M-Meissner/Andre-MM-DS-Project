import streamlit as st
import csv
import re
import datasketch as ds


def load_data(number_doc: int):
    '''Loading the data with words in lowercase'''
    dataset = []

    with open('./mtsamples.csv', encoding='utf-8') as csvdata:
        csv_reader_object = csv.reader(csvdata)
        rownumber = 0
        for row in csv_reader_object:
            if rownumber > 0 and rownumber < number_doc+1:
                dataset.append(row[4].lower())  # String converted to lowercase
            rownumber += 1
            if rownumber == number_doc+1:
                break
    return dataset


def clean_data(dataset: list):
    '''Removing punctuation + useless whitespaces'''
    for i in range(len(dataset)):
        dataset[i] = re.sub(pattern="[^\w\s\']", repl=" ", string=dataset[i])
        dataset[i] = re.sub(pattern="[\s]+", repl=" ", string=dataset[i])
        dataset[i] = dataset[i].strip()
        dataset[i] = dataset[i].split(" ")  # String into list with words
    return dataset


def remove_stopwords(dataset: list, stopword_list: list):
    '''Removing stopwords from all documents'''
    for i in range(len(dataset)):
        dataset[i] = [word for word in dataset[i] if not word in stopword_list]
    return dataset


def create_shingle_lists(dataset: list, shingle_size: int):
    '''Create shingle_lists for all documents and one universal shingle list'''
    shingle_list = set()  # universal shingle set
    shingle_docs = {}  # shingles in certain docs (ones in char. matrix)
    for i in range(len(dataset)):
        shingle_docs[i] = set()

    for i in range(len(dataset)):  # Gets all shingles from documents
        for j in range(len(dataset[i])+1-shingle_size):
            end = j + shingle_size
            potential_shingle = ' '.join(dataset[i][j:end])
            shingle_docs[i].add(potential_shingle)
            shingle_list.add(potential_shingle)
    return list(shingle_list), shingle_docs


def create_char_matrix(shingle_list: list, shingle_docs: dict):
    '''Creates the Characteristic Matrix'''
    char_matrix = {}
    for i in range(len(shingle_list)):
        char_matrix[i] = []

    for i in range(len(shingle_docs)):
        for j in range(len(shingle_list)):
            if shingle_list[j] in shingle_docs[i]:
                char_matrix[j].append(i)

    return char_matrix


def minhash(doc_one: list, doc_two: list, no_hashf=200):
    '''Performs minhash approximation for Jaccard Similarity'''
    hashvalue_one = ds.MinHash(num_perm=no_hashf)
    hashvalue_two = ds.MinHash(num_perm=no_hashf)

    for i in doc_one:
        hashvalue_one.update(i.encode("utf8"))

    for i in doc_two:
        hashvalue_two.update(i.encode("utf8"))

    return hashvalue_one.jaccard(hashvalue_two)


def jaccard_similarity(doc_one: list, doc_two: list):
    '''Computes Jaccard Similarity'''
    set_one = set(doc_one)
    set_two = set(doc_two)

    intersection_size = len(set_one.intersection(set_two))
    union_size = len(set_one.union(set_two))

    return intersection_size/union_size

# Maincode:
st.title('Data Science Project Shingling')

st.subheader('Pre-Analysis')  # PRE_ANALYSIS
num_docs = st.slider('Choose number of documents:', value=250, step=50,
                     min_value=100, max_value=4999)
st.write('Data cleaning steps:\n1. Put all documents in lowercase\
\n2. Exchange all puncuation for single blank\n3. Remove unnecessary blanks\
\n4. Remove stopwords')

dataset = load_data(num_docs)  # Loading data
dataset = clean_data(dataset)  # Cleaning data

stopwords = open('./clinical-stopwords.txt', "r", encoding="utf-8")
stopword_list = stopwords.read()  # Loading stopwords
stopword_list = stopword_list.split("\n")
stopwords.close()

dataset = remove_stopwords(dataset, stopword_list)  # Remove stopwords

#st.subheader('Analysis of Characteristic Matrix')  # ANALYSIS START
st.subheader('Analysis of two documents')
shingle_size = st.slider('Choose shingle size', value=3, step=1, min_value=1,
                         max_value=10)

shingle_list, shingle_docs = create_shingle_lists(dataset, shingle_size)
#char_matrix = create_char_matrix(shingle_list, shingle_docs)
#st.write('First 5 Elements in Char. Matrix (Here: Adjacency list)')
#st.write('Shingle 1  -> ', str(char_matrix[0]))
#st.write('Shingle 2  -> ', str(char_matrix[1]))
#st.write('Shingle 3  -> ', str(char_matrix[2]))
#st.write('Shingle 4  -> ', str(char_matrix[3]))
#st.write('Shingle 5  -> ', str(char_matrix[4]))

num_hashf = st.slider('Choose number of hashfunctions', value=500, step=1,
                      min_value=1, max_value=1000)

doc_one = st.number_input('Select first document: ', min_value=1,
                          max_value=len(dataset), value=4, step=1)

if st.button('Show shingles for 1st document', key='a'):
    st.write(shingle_docs[doc_one-1], '...')
doc_two = st.number_input('Select second document: ', min_value=1,
                          max_value=len(dataset), value=10, step=1)

if st.button('Show shingles for 2nd document', key='b'):
    st.write(shingle_docs[doc_two-1], '...')

if st.button('Run', key='c'):
    estimate_js = minhash(shingle_docs[doc_one-1], shingle_docs[doc_two-1],
                          num_hashf)
    actual_js = jaccard_similarity(shingle_docs[doc_one-1],
                                   shingle_docs[doc_two-1])

    st.subheader('Results')
    st.write('Minhash-based estimation: ', estimate_js)
    st.write('True Jaccard-Similarity: ', actual_js)
