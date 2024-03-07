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
import openai
import time
from indexer import *



stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
             "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
             "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
             "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
             "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself",
             "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
             "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of",
             "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
             "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
             "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
             "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
             "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
             "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
             "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
             "yourself", "yourselves"]

def query_processing(query):
    query_index={}
    ps = PorterStemmer()
   
    q_words = [ps.stem(word) for word in set(re.findall(r'[a-zA-Z0-9]+', query))] #tokenizes and stems the query
    
    for word in q_words: #loops through the query to get postings of every word in the query.
        char_pos = 0
        first_letter = word[0]
        flag2=False
        with open("index3.txt", 'r') as file:   #searches for the first aphabet in index3.txt
            while True:
                line = file.readline()
                if not line: 
                    break
                alpha = line[0]
                if alpha == first_letter:
                    char_pos = int(line.split(':')[1].strip())
                
        with open("index2.txt", 'r') as file:   #jumps to words statrting with the same first letter and searches for the token in index2.txt
            file.seek(char_pos)
            flag = True
            while flag:
                line = file.readline()
                w = line.split(':')[0]
                if w[0]!= first_letter:
                    flag2=True
                    break
                if w == word:
                    char_pos = int(line.split(':')[1].strip())
                    flag = False

        if flag2:   #skips the loop if there is no such word in the indexer
            continue

        with open("finalreverseindexer.txt", 'r') as file:  #jumps to the word and retrives all of its posting
            file.seek(char_pos)
            line = file.readline()
            w = line.split(':')[0]
            query_index[w]={}
            for posting in line.split(':')[1].split():
                pos_list = [term.strip() for term in posting.split(',')]
                doc_id = int(pos_list[0])
                tf_idf = float(pos_list[1])
                imp = int(pos_list[2])
                query_index[w][doc_id] = [tf_idf,imp]
    return query_index

def stopword_check(query_index):    #removes the stopwords posting from the posting dict
    poppedlist=[]
    for i in query_index.keys():
        if i in stopwords:
            poppedlist.append(i)
    for i in poppedlist:
        query_index.pop(i)

    return query_index
            

def bool_AND(query_index):      #retrieves the commom docids which contain all the query words
    common_subkeys_list = []

    for word, doc_dict in query_index.items():
        doc_keys = set(doc_dict.keys())

        if common_subkeys_list:
            common_subkeys_list = list(set(common_subkeys_list).intersection(set(doc_keys)))   #accumulates the common docids among the query terms
        else:
            common_subkeys_list = list(doc_keys)

    return common_subkeys_list


def calculate_Score(query_index,common_subkeys_list):   #scores and ranks the common docids accordingly 
    scores = {}  
    for i in common_subkeys_list:
        score = 0
        for posting in query_index:     # loops through every query word
            if i in query_index[posting]:
                score += query_index[posting][i][0]
                if query_index[posting][i][1] == 1:
                    score += 1
        scores[i]=score
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))      #sorts the urls in descending order of their score.

    return (sorted_scores)

def print_search(sorted_scores):    #used only when running Seracher.py directly. prints the top five urls and their summary using openai api
    counter = 5
    urldict={}
    with open("docIDs.json","r") as file :      #opens DocIds.json file and maps the docids to the url name
            urldict=json.load(file)
    urldict2 = {value: key for key, value in urldict.items()}
    keys = list(sorted_scores.keys())
    if len(keys)<5:
        for i in range (0,len(keys)):
            print((urldict2[keys[0]]))
    else:
        while counter >0 :
            if keys:
                print(urldict2[keys[0]])
                keys.remove(keys[0])
                openai.api_key = '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'   #below code uses openai api to generate summary of the url

                u = urldict2[keys[0]]
                prompt = f"Summarize the contents of the web page at {u}."

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": "What is the summary?"},
                    ],
                )
                summary = response.choices[0].message.content
                print(summary)
            else:
                print("Not a valid query!")
                break
            counter -=1 

if __name__ == "__main__":
    
    while True:
        query = input("Enter the query")    #input the query
        start_time = time.time()        #starts the timer

        query_index=query_processing(query)     
        query_index=stopword_check(query_index)
        common_subkeys_list = bool_AND(query_index)
        score = calculate_Score(query_index, common_subkeys_list)
        print_search(score)
        
        query_index={}
        common_subkeys_list=[]
        end_time = time.time()      #stops the timer
        elapsed_time = (end_time - start_time)*1000     #converts to milli-seconds

        print(f"The function took {elapsed_time} milli-seconds to complete.")
        ch = input("Do you want to search more? (y/n)")     #asks if want to search a query again if no then break the while loop.
        if ch=='n' :        
            break
