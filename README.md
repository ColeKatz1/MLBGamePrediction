# MLBGamePrediction

This project attempts to predict the outcome of Major League Baseball games using machine learning. 

Process:

1. Use web scraping to obtain data from baseball-reference.com. This data is the team totals from the box scores of each game such as total number of runs, hits, strikeouts, etc. I collected the data for every game and every team from the 2021 season for this project.
2. Next, create moving average variables for each team such as moving average of runs, hits, strikeouts, etc in the hopes that these variables will serve as good predictors.
3. Then, for each game, we combine the stats of the two teams playing by subtracting the away team's stats from the home team's stats to create new variables that account for opponents. For example, for the variable "seasonLongRunCount", subtraction for example could be (100 runs - 94 runs) = 6 runs. The new statistic we use for machine learning is that the home team has a total of 6 more runs than the away team for the season.
4. Determine the most important features
5. Use SVM to predict wins and losses for each team
