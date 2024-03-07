# Function that takes a 3 tuple and passes the content through the stemmer and returns a dictionary
# whose key is token and value is dictionary whose key is url name and value is [frequency]
# d={token : {url : [freq]}}

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
import re
import json
import os
from collections import defaultdict
from tqdm import tqdm
import math
import time
from urllib.parse import urldefrag

indexer_dict = {}  # indexer of structure : {token : {docID : [tf-idf, imp]}}
files_count = 0  # total json files parsed
offloadcounter = 0  # counter of partial indexers offloaded
urltoid = {}  # dictionary of structure : {url : docID} for search
uniqueurlcounter = 0  # unique url parsed
offloadlist = []  # list of partial indexes offloaded to disk


def all_files(mainfolder):  # extracting Files from the DEV folder
    global files_count
    list_files = []  # list of all the files in DEV folder
    files_count = 0

    folder_path = os.path.join(os.getcwd(), mainfolder)  # Getting the CWD
    if os.path.exists(folder_path):
        for root, _dirs, files in os.walk(folder_path):
            for i in files:
                if i.endswith('json'):  # iterating through the json files
                    filepath = os.path.join(root, i)
                    list_files.append(filepath)
    else:
        print("Directory does not exist")
    return list_files

# reads all json files and returns a tuple of url, content, encoding


def json_content(jsonfilename):
    with open(jsonfilename, 'r') as jsonfileread:
        # tuple of url, content and encoding
        jsonfiletup = list(json.load(jsonfileread).values())
    wanted, _unwanted = urldefrag(jsonfiletup[0])  # defragging url
    jsonfiletup[0] = wanted
    return jsonfiletup


def word_parser(tp1):  # takes the tuples and parses the content using tokeniser and stemmer
    global indexer_dict, uniqueurlcounter

    url, content, encoding = tp1
    if url not in urltoid:
        uniqueurlcounter += 1
        urltoid[url] = uniqueurlcounter

    ps = PorterStemmer()  # Creating a Stemmer Object
    soup = BeautifulSoup(content, "html.parser")
    content = soup.get_text()
    imptext = soup.find_all(['h1', 'h2', 'h3', 'b', 'strong'])

    implist = list()  # List of all important words
    for i in imptext:
        for j in i.text.split():
            implist.append(ps.stem(j))

    wordlst = re.findall(r'[a-zA-Z0-9]+', content)  # Takes the tokenised words

    for i in wordlst:
        i = ps.stem(i)  # Stemming each token
        # Creating the indexer of structure : {token : {docID : [tf-idf, imp]}}
        if i in indexer_dict:
            if urltoid[url] in indexer_dict[i]:
                indexer_dict[i][urltoid[url]][0] += 1
            else:
                indexer_dict[i][urltoid[url]] = [1, 0]
        else:
            indexer_dict[i] = {urltoid[url]: [1, 0]}

        tf = indexer_dict[i][urltoid[url]][0]
        indexer_dict[i][urltoid[url]][0] = tf
        if i in implist:
            indexer_dict[i][urltoid[url]][1] = 1


def offload():
    global offloadcounter, indexer_dict, offloadlist
    offloadcounter += 1
    filename = f"Pi{offloadcounter}.txt"
    offloadlist.append(f"Pi{offloadcounter}.txt")
    # writing partial indexes to drive
    with open(filename, 'w') as file:
        for word, sub_dict in indexer_dict.items():
            file.write(f"{word}:")

            for docid, sub_val_list in sub_dict.items():
                file.write(
                    f"{docid},{sub_val_list[0]},{sub_val_list[1]} ")
            file.write('\n')
    indexer_dict = {}


'''function to take list of partial indexes, starting ascii value, and ending ascii value and creates a txt file from start to end values'''


def Partial_load(l1, start, end):
    # indexer of structure : {token : {docID : [tf-idf, imp]}}
    dictionary1 = defaultdict(dict)
    for filename in l1:  # list of partial indexes
        with open(filename, 'r') as file:
            for line in file:
                line.rstrip('\n')
                word, postings = line.split(':')  # splitting [token, postings]
                p2 = postings.split(' ')  # splitting each posting seperately
                for i in p2:
                    # splitting each posting into [docid,tf,imp]
                    p3 = i.split(',')
                    # edge case for end of file with '\n' or empty string
                    if p3 == [""] or p3 == ['\n']:
                        continue
                    for j in p3:
                        docid = int(p3[0])
                        tf = p3[1]
                        imp = p3[2]
                        if type(start) == int:  # seperate case for numerical files
                            if word[0] >= chr(start) and word[0] <= chr(end):
                                dictionary1[word][docid] = [tf, imp]
                        else:  # case for a-g, h-s, t-z
                            if word[0] >= start and word[0] <= end:
                                dictionary1[word][docid] = [tf, imp]

    dictionary1 = {word: {docid: dictionary1[word][docid] for docid in sorted(
        dictionary1[word])} for word in sorted(dictionary1)}  # sorting dictionary by word (a to z) and then by docid value (increasing order)
    for word in dictionary1:  # calculating tf-idf score
        df = len(dictionary1[word])
        idf = math.log((55393/df), 10)
        for d in dictionary1[word]:
            tf = float(dictionary1[word][d][0])
            w = (1+math.log(tf, 10))*idf
            dictionary1[word][d][0] = w
    filename2 = f'indexer{start}-{end}.txt'
    with open(filename2, 'w') as file:  # writing three files to disk from start letter to end letter
        for word in sorted(dictionary1.keys()):
            sub_dict = dictionary1[word]
            file.write(f'{word}:')
            for dociD, sub_docID in sub_dict.items():
                if '\n' in sub_docID[1]:
                    sub_docID[1] = sub_docID[1].replace('\n', '')
                file.write(f'{dociD},{sub_docID[0]},{sub_docID[1]} ')
            file.write('\n')


'''Function that takes a list of input files and merges them into one output file'''


def merge_partial(input_files, outputfile):
    with open(outputfile, 'w') as outfile:
        for file_name in input_files:
            with open(file_name, 'r') as infile:
                for line in infile:
                    outfile.write(line)

            os.remove(file_name)


'''function to create an indexer of indexer of the structure: {word : int(character position of that word)}'''


def character_indexer(outputfile):

    ind2 = {}
    line = ''
    flag = True
    with open(outputfile, 'r') as file:
        while flag:
            char_pos = file.tell()
            line = file.readline()
            if not line:
                flag = False
            else:
                word = line.split(":")[0]
                ind2[word] = char_pos

    with open('index2.txt', 'w') as file:
        for word, char_pos in ind2.items():
            file.write(f"{word}:{char_pos}\n")


'''function to create alphabet-wise indexer: {alphabet from a - z : starting character position of that alphabet}'''


def alphabet_indexer(ind2):
    ind3 = {}
    temp_char = ''
    flag = True
    with open(ind2, "r") as file:
        while flag:
            char_pos = file.tell()
            line = file.readline()
            if not line:

                flag = False
            else:
                alpha = line[0]
                if temp_char != alpha:
                    ind3[alpha] = char_pos
                    temp_char = alpha
                else:
                    pass

    with open("index3.txt", "w") as file:
        for word, char_pos in ind3.items():
            file.write(f"{word}:{char_pos}\n")


if __name__ == "__main__":
    partialcounter = 0
    folder_name = 'DEV'
    json_files = all_files(folder_name)
    # progress bar to visualize partial indexing process and time
    with tqdm(total=(len(json_files))) as pbar:
        for file in json_files:
            if (partialcounter == 10000):
                partialcounter = 0
                offload()
            file_extract = json_content(file)
            if file_extract != None:
                partialcounter += 1
                word_parser(file_extract)
                files_count += 1
            else:
                print("Invalid json file")
            pbar.update(1)
        partialcounter += 1
    offload()  # extra offload() function for last 5000 files
    with open("DocIDs.json", 'w') as file:
        json.dump(urltoid, file)
    with tqdm(total=4) as p1bar:  # progress bar for start to end indexes
        Partial_load(offloadlist, 'a', 'g')
        p1bar.update(1)
        Partial_load(offloadlist, 'h', 's')
        p1bar.update(1)
        Partial_load(offloadlist, 't', 'z')
        p1bar.update(1)
        Partial_load(offloadlist, 48, 57)
        p1bar.update(1)

    for i in offloadlist:
        os.remove(i)
    with tqdm(total=3) as p2bar:
        merge_partial(['indexera-g.txt', 'indexerh-s.txt',
                       'indexert-z.txt', 'indexer48-57.txt'], 'finalreverseindexer.txt')  # merging all start to end indexes into one text file
        p2bar.update(1)
        character_indexer('finalreverseindexer.txt')
        p2bar.update(1)
        alphabet_indexer("index2.txt")
        p2bar.update(1)
    char_pos = 0
    start_time = time.time()
