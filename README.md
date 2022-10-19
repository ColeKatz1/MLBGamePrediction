# MLBGamePrediction

This project attempts to predict the outcome of Major League Baseball games using machine learning. 

Process:

1. Use web scraping to obtain data from baseball-reference.com. This data is the team totals from the box scores of each game such as total number of runs, hits, strikeouts, etc. I collected the data for every game and every team from the 2021 season for this project.
2. Next, create moving average variables for each team such as moving average of runs, hits, strikeouts, etc in the hopes that these variables will serve as good predictors.
3. Then, for each game, we combine the stats of the two teams playing by subtracting the away team's stats from the home team's stats to create new variables that account for opponents. For example, for the variable "seasonLongRunCount", subtraction for example could be (100 runs - 94 runs) = 6 runs. The new statistic we use for machine learning is that the home team has a total of 6 more runs than the away team for the season.
4. Determine the most important features
5. Use SVM to predict wins and losses for each team

Files:

The Baseball_Reference_Scraping.py file collects data from baseball-reference.com

Prediction Accuracy:

To start, we used svc linear machine learning to test out the prediction on a very basic model. The model only uses batting data from one team. It also gives the winning percentage of one team and tells if that team is home or away. It does not consider pitching data nor the opponent. Still, the svc linear model obtains results consistenly between 53% to 60%. Hopefully, this can be greatly improved as opponent data and pitching data are added to the dataset.

![MLBSimplePredictionOutput](https://user-images.githubusercontent.com/84477747/154859990-86e9c36e-1c9b-43eb-9a0b-0062b163019c.jpg)

Above it the output of running the SVC linear prediction a number of times to demonstrate the average accuracy. 
