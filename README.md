# Search-engine

Modules you will need to execute this search engine:-
1. nltk
2. bs4
3. re
4. os
5. json
6. tqdm (timer)
7. openai (for openai api)
8. timer

You can install all these with pip3  in your terminal.

Files you should see once you unzip the submission file:-
1. indexer.py
2. Searcher.py
3. gui.py
4. README.txt
5. templates folder with-
                index.html

To build the Indexer:-
1. Make sure you have the DEV folder in the same directory as indexer.py
2. Run indexer.py on python3.2. It should show a progress bar with runtime.
3. It should take 15-16 mins for the program to end and to build all indexer files.
4.. It should make 4 files in the same directory - 
                    finalreverseindexer.txt
                    index2.txt
                    index3.txt
                    DocIDS.json


To build the Search engine web GUI:-
1. Run gui.py on python3.
2. It will print flask information about the web GUI on the console.
3. Open the link given by the console in a web browser. Eg - If the console prints 'Running on http://127.0.0.1:5000', open http://127.0.0.1:5000. 
4. The http link will open our Search engine webpage where you can enter the query and see its search result and the time it took to generate the result.


Extra credits:-
1. Implemented a Web GUI for the Search Engine.
2. Detected and eliminated duplicate pages.
3. Implemented the summarization of the resulting pages using the OpenAI API and show the short summaries in the web GUI. (Takes 5-6 secs to generate the summary after you click the summary button.)
