# MLBGamePrediction

This project attempts to predict the outcome of Major League Baseball games using machine learning. 

Process:

1. Use web scraping to obtain data from baseball-reference.com. This data is the team totals from the box scores of each game such as total number of runs, hits, strikeouts, etc. 
2. Next, create moving average variables for each team such as moving average of runs, hits, strikeouts, etc.
3. Combine datasets to form one dataset with the ratios of moving averages serving as the variables
4. Determine the most important features
5. Use SVM to predict wins and losses for each team
