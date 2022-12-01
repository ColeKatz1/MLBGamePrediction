import Baseball_Reference_Scraping_Functions as br

br.completedBattingStatsOfAllTeams("2021") #creates a dataset of completed batting stats for every team in given year
br.completedBattingStatsOfAllTeams("2022") #creates a dataset of completed batting stats for every team in given year
br.combineToOneDataFrame("2021") #combines all games from 1 year into dataframe
br.combineToOneDataFrame("2022") #combines all games from 1 year into dataframe
br.combineAllYears(["2021","2022"]) #combines all years of scraped data into one dataset
br.addFinalFeatures() #prepares data for machine learning purposes by combining data between teams for each game they play against each other
