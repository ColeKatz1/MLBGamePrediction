# MLBGamePrediction

This project attempts to predict the outcome of Major League Baseball games using machine learning. 

Process:

1. Use web scraping to obtain data from baseball-reference.com. This data is the team totals from the box scores of each game such as total number of runs, hits, strikeouts, etc. 
2. Next, create moving average variables for each team such as moving average of runs, hits, strikeouts, etc.
3. Combine datasets to form one dataset with the ratios of moving averages serving as the variables
4. Determine the most important features
5. Use SVM to predict wins and losses for each team

Files:

The Baseball_Reference_Scraping.py file collects data from baseball-reference.com

Prediction Accuracy:

To start, we used svc linear machine learning to test out the prediction on a very basic model. The model only uses batting data from one team. It also gives the winning percentage of one team and tells if that team is home or away. It does not consider pitching data nor the opponent. Still, the svc linear model obtains results consistenly between 53% to 60%. Hopefully, this can be greatly improved as opponent data and pitching data are added to the dataset.
