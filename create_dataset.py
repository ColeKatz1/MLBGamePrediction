import Baseball_Reference_Scraping_Functions as br

br.completedBattingStatsOfAllTeams() #creates a dataset of completed batting stats for every team
br.combineToOneDataFrame() #combines all these datasets into one
br.addFinalFeatures() #prepares data for machine learning purposes by combining data between teams for each game they play against each other

