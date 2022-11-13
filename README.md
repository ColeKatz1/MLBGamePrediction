## MLBGamePrediction

This project attempts to predict the outcome of Major League Baseball games using machine learning. The project currently uses batting statistics and categorical variables such as Home or Away from both teams in the game to predict the game's outcome. 

# Process:

1. Use web scraping to obtain data from baseball-reference.com. This data is the team totals from the box scores of each game such as total number of runs, hits, strikeouts, etc. I collected the data for every game and every team from the 2021 season for this project.
2. Next, create moving average variables for each team such as moving average of runs, hits, strikeouts, etc in the hopes that these variables will serve as good predictors.
3. Then, for each game, we combine the stats of the two teams playing by subtracting the away team's stats from the home team's stats to create new variables that account for opponents. For example, for the variable "seasonLongRunCount", subtraction for example could be (100 runs - 94 runs) = 6 runs. The new statistic we use for machine learning is that the home team has a total of 6 more runs than the away team for the season.
4. Determine the most important features
5. Use SVM to predict wins and losses for each team


# Files: 

baseball_reference_scraping_functions.py provides all the necessary functions for scraping data from baseball reference in addition to providing functions for transforming these variables into more complicated statistics like moving averages and subtraction between each team's stats. 

dfComplete.csv provides an example of statistics collected before subtraction takes place. Subtraction refers to subtracting the away team's data from the home team's data in order to create one set of statistics to use for machine learning. The .csv file gives a sense of the extensive data in our dataset.

create_dataset.py uses the baseball_reference_scraping_functions.py functions to create a final dataset we will use for machine learning.

machine_learning.py, this file runs an svc machine learning algorithm to predict if a game will be a win or loss. It then prints the accuracy of the predictions

# Future:

In order to improve the model's accuracy, more data will be added to the dataset. To start, pitching data, which is very important, will be added. This will include statistics such as ERA and pitch counts. 

Next, more categorical variables will be added to the dataset. This will include variables such as the weather in the game and the time at which the game occurs.

Finally, more seasons of data will be added to the dataset. For example, the 2022 season will be added.
