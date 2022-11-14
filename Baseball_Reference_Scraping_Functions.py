from cmath import nan
from contextlib import nullcontext
from itertools import groupby
from pickle import TRUE
from random import seed
from turtle import home
import pandas, numpy
import requests, bs4
import re, os
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import glob
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier 
import random
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import classification_report,confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
from torch import long


#this function finds all tables on a given url
#this is useful for when we want to pull a table, we need to know the title of the table (the table id)
# on this site, table ids follow the format: team+batting, team+pitching. For example, ArizonaDiamondbackspitching is one table id
def findTables(url):
    res = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    divs = soup.findAll('div', id = "content")
    divs = divs[0].findAll("div", id=re.compile("^all"))
    ids = []
    for div in divs:
        searchme = str(div.findAll("table"))
        x = searchme[searchme.find("id=") + 3: searchme.find(">")]
        x = x.replace("\"", "")
        if len(x) > 0:
            ids.append(x)
    return(ids)

#this functions returns the data from a specific table in a given url
#the data that is returned is the team statistics for all relevant box score stats
#The url input is the url to the game's box score. For example, "https://www.baseball-reference.com/boxes/SDN/SDN202104010.shtml"
def pullTable(url, tableID):
    res = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    tables = soup.findAll('table', id = tableID)
    data_rows = tables[0].findAll('tr')
    data_header = tables[0].findAll('thead')
    data_header = data_header[0].findAll("tr")
    data_header = data_header[0].findAll("th")
    game_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])]
        for i in range(len(data_rows))
        ]
    data = pandas.DataFrame(game_data)
    header = []
    for i in range(len(data.columns)):
        header.append(data_header[i].getText())
    data = data.drop(0)
    data = data.reset_index(drop = True)
    return(data)

#this function gets the batting datatable for a given team
#The input for team should have no spaces. For example, Arizona Diamonds would be input as "ArizonaDiamondbacks"
#the url is a url to the box score of a given game for the team
def pullBattingData(url, team):
    teamBatting = pullTable(url, team + "batting")
    teamBatting = teamBatting.loc[[len(teamBatting)-1]]
    return(teamBatting)


#this function is used to find all the box scores in a season for a given team
#For example, for the Arizona Diamondsbacks: url = "https://www.baseball-reference.com/teams/ARI/2021-schedule-scores.shtml"
#Then, running this function with the given url will return a list of urls to every box score of the 2021 season for this team
def boxScoreUrls(url):
    res = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    dataLink = []
    for link in soup.findAll('a'):
        if link.has_attr('href'):
            allLinks = link.attrs['href']
            dataLink.append(allLinks)
    r = re.compile("/boxes/\w\w\w/\w\w\w\d")  
    specificLink = list(filter(r.match, dataLink))
    dfOfLinks = pandas.DataFrame(specificLink, columns=['url'])
    dfOfLinks = dfOfLinks.drop_duplicates()
    urlList = dfOfLinks.values.tolist()
    finalUrlList = ['https://www.baseball-reference.com' + str(i) for i in urlList]
    finalUrlList = [i.replace('[\'','') for i in finalUrlList]
    finalUrlList = [i.replace('\']','') for i in finalUrlList]
    return(finalUrlList)


#this function goes through a team's schedule and creates a new dummy variable for if the team is home or away
#it uses the url to a team's game by game schedule
#For example, it would be "https://www.baseball-reference.com/teams/ARI/2021-schedule-scores.shtml" for the Arizona Diamondbacks
#This is the same url as used in the boxScoreUrls function for each team
def homeOrAwayList(url):
    schedule_table = pullTable(url, 'team_schedule')

    homeOrAwayFirst = schedule_table[4]

    homeOrAway = homeOrAwayFirst.values.tolist()

    homeOrAwayBinary = []
    
    for i in range(len(homeOrAway)):
        if homeOrAway[i] == '@':
            homeOrAwayBinary.append(1)
        elif homeOrAway[i] == '':
            homeOrAwayBinary.append(0)
        else:
            homeOrAwayBinary = homeOrAwayBinary
    return(homeOrAwayBinary)

#This returns a list of opponents that a given team will play 
#url is the same as above (same as homeOrAwayList and boxScoreUrls)
#Each team in the list is given via their 3 letter abreviations. For example, LAD for the LA dodgers or ARI for the Arizona Diamondbakcs
def opponentList(url):
    schedule_table = pullTable(url, 'team_schedule')

    opponentColumn = schedule_table[5]

    opponentList = opponentColumn.values.tolist()

    opponentListFinal = []

    for i in range(len(opponentList)):
        if opponentList[i] != 'Opp':
            opponentListFinal.append(opponentList[i])
    
    return(opponentListFinal)


#this function goes through a team's schedule for the year and creates a new dummy variable that states if the game was won or lost
#url is the same as the above functions (opponentList, boxScoreURls, etc.)
def winOrLossList(url):
    schedule_table = pullTable(url, 'team_schedule')
    winOrLossColumn = schedule_table[6]
    winOrLossList = winOrLossColumn.values.tolist()
    winOrLossListFinal = []
    for i in range(len(winOrLossList)):
        if winOrLossList[i] == 'W' or winOrLossList[i] == 'W-wo':
            winOrLossListFinal.append(0)
        elif winOrLossList[i] == 'L' or winOrLossList[i] == 'L-wo':
            winOrLossListFinal.append(1)
        else:
            winOrLossListFinal = winOrLossListFinal
    return(winOrLossListFinal)


#this function gets the season statistics for a given team
#the url is the same url as for boxScoreUrls, it is the url to the team's schedule. For example, "https://www.baseball-reference.com/teams/ARI/2021-schedule-scores.shtml"
#the team input is the team's abbreviated name like LAD or ARI
#teamFullName is the team's full name with no spaces and proper capitalization like "ArizonaDiamondbacks"
#It works with the following steps: 
#1. get urls for all box scores
#2. get the batting data for each game using the pullBattingData function
#3. only keeps the relevant batting statistics
#4. adds other statistics like homeOrAway, opponent, and winOrLoss for each game
#5. returns the dataframe
def getSeasonStats(url, team, teamFullName):
    teamList = []
    battingDataList = []
    urlList = boxScoreUrls(url)
    for i in urlList:
        battingData = pullBattingData(i, teamFullName)
        battingDataList.append(battingData)
    if len(battingDataList) == 162:
        battingDataList = numpy.reshape(battingDataList, (162,24))
    elif len(battingDataList) == 161:
        battingDataList = numpy.reshape(battingDataList, (161,24))
    dfOfBattingData = pandas.DataFrame(battingDataList) 
    dfOfBattingData.columns = ['Batting','AB','R','H','RBI','BB','SO','PA','BA','OBP','SLG','OPS','Pit','Str','WPA','aLI','WPA+','WPA-','cWPA','acLI','RE24','PO','A','Details']
    dfOfBattingData = dfOfBattingData.drop(['Batting','WPA','aLI','WPA+','WPA-','cWPA','acLI','PO','A','Details'], axis=1)
    for i in range(len(dfOfBattingData)):
        teamListComplete = teamList.append(team)
    homeOrAway = homeOrAwayList(url)
    opponent = opponentList(url)
    winOrLoss = winOrLossList(url)
    dfOfBattingData['WinOrLoss'] = winOrLoss
    dfOfBattingData['Team'] = teamList
    dfOfBattingData['Opponent'] = opponent
    dfOfBattingData['HomeOrAway'] = homeOrAway
    dfOfBattingData['url'] = urlList
    #dfOfBattingData.to_csv(teamFullName + "_Batting_Statistics.csv")
    return(dfOfBattingData)

#this function finds the moving average of a given stat for a given number of games (for example, 5 game moving average of the runs stats)
def findMovingAverage(df, columnName, numberOfGames):
    variableList = df[columnName]
    variableSeries = pandas.Series(variableList)
    windows = variableSeries.rolling(numberOfGames)
    movingAverage = windows.mean()
    movingAverageList = movingAverage.values.tolist()
    movingAverageList.insert(0, nan)
    movingAverageList.pop()
    return(movingAverageList)

#this function adds the 3 game, 10 game, and 31 game moving averages of a given stat to the dataframe/dataset
def addMovingAveragesOfStat(df, stat):
    movingAverage3 = findMovingAverage(df,stat,3)
    df[stat + '_Moving_Average_3'] = movingAverage3
    movingAverage10 = findMovingAverage(df,stat,10)
    df[stat + '_Moving_Average_10'] = movingAverage10
    movingAverage31 = findMovingAverage(df,stat,31)
    df[stat + '_Moving_Average_31'] = movingAverage31

#this function adds season long average stats to the dataframe/dataset (season long average number of runs)
def addSeasonLongAverageStatistics(df, stat):
    variableContinuedStatList = []
    variableList = df[stat]
    totalSum = 0
    totalCount = 0
    variableContinuedStatList.insert(0,nan)

    for i in range(len(variableList)):
        totalSum = totalSum + float(variableList[i])
        totalCount = totalCount + 1
        average = totalSum/totalCount
        variableContinuedStatList.append(average)
    variableContinuedStatList.pop()
    df[stat + '_Season_Long_Average'] = variableContinuedStatList

#this function adds the season long totals of a specific stat to the dataframe/dataset (season total number of runs)
def addSeasonLongCount(df, stat):
    countTotalList = []
    variableList = df[stat]
    count = 0
    countTotalList.insert(0,nan)
    for i in range(len(variableList)):
        count = count + int(variableList[i])
        countTotalList.append(count)
    countTotalList.pop()
    df[stat + "_Season_Long_Count"] = countTotalList

#this function gets the basic stats from the season of a team and transforms them to moving averages, season long counts, 
#and season long averages in the hopes of adding more relevant variables
def transformedSeasonStats(url, team, teamFullName):
    df = getSeasonStats(url, team, teamFullName)
    winsList = df['WinOrLoss']
    winsTotal = 0
    gamesTotal = 0
    winningPercentageList = []
    winningPercentageList.insert(0,nan)
    for i in range(len(winsList)):
        if winsList[i] == 0:
            winsTotal = winsTotal + 1
            gamesTotal = gamesTotal + 1
            winningPercentage = winsTotal / gamesTotal
            winningPercentageList.append(winningPercentage)
        elif winsList[i] == 1:
            gamesTotal = gamesTotal + 1
            winningPercentage = winsTotal / gamesTotal
            winningPercentageList.append(winningPercentage)
    winningPercentageList.pop()
    df['Win_Percentage'] = winningPercentageList
    addSeasonLongCount(df,'R')
    addSeasonLongCount(df,'H')
    addSeasonLongCount(df,'BB')
    addSeasonLongCount(df,'SO')
    addSeasonLongCount(df,'PA')
    addMovingAveragesOfStat(df, 'R')
    addMovingAveragesOfStat(df, 'SLG')
    addMovingAveragesOfStat(df, 'BA')
    addMovingAveragesOfStat(df, 'OBP')
    addMovingAveragesOfStat(df, 'SO')
    addMovingAveragesOfStat(df, 'AB')
    addMovingAveragesOfStat(df, 'Pit')
    addMovingAveragesOfStat(df, 'H')
    addMovingAveragesOfStat(df, 'BB')
    addMovingAveragesOfStat(df, 'OPS')
    addMovingAveragesOfStat(df, 'RE24')
    addMovingAveragesOfStat(df, 'Win_Percentage')
    addSeasonLongAverageStatistics(df,'BA')
    addSeasonLongAverageStatistics(df,'SLG')
    addSeasonLongAverageStatistics(df,'OPS')
    return(df)


#this creates a csv file on your computer of the batting statistics of the given team
def createCSVOfTeamStats(url, team, teamFullName):
    transformedDf = transformedSeasonStats(url, team, teamFullName)
    transformedDf.to_csv(teamFullName + "_Completed_Batting_Statistics.csv")
    return(transformedDf)


#this function creates a csv file for each team in the MLB of their batting statistics
def completedBattingStatsOfAllTeams():
    allScheduleUrlList = ["https://www.baseball-reference.com/teams/ARI/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/ATL/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/BAL/2021-schedule-scores.shtml", "https://www.baseball-reference.com/teams/BOS/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CHW/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CHC/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CIN/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CLE/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/COL/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/DET/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/HOU/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/KCR/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/LAA/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/LAD/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/MIA/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/MIL/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/MIN/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/NYY/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/NYM/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/OAK/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/PHI/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/PIT/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/SDP/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/SFG/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/SEA/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/STL/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/TBR/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/TEX/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/TOR/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/WSN/2021-schedule-scores.shtml"]
    allTeamList = ['ARI','ATL','BAL','BOS','CHW','CHC','CIN','CLE','COL','DET','HOU','KCR','LAA','LAD','MIA','MIL','MIN','NYY','NYM','OAK','PHI','PIT','SDP','SFG','SEA','STL','TBR','TEX','TOR','WSN']
    allTeamFullNameList = ["ArizonaDiamondbacks","AtlantaBraves","BaltimoreOrioles","BostonRedSox","ChicagoWhiteSox","ChicagoCubs","CincinnatiReds","ClevelandIndians","ColoradoRockies","DetroitTigers","HoustonAstros","KansasCityRoyals","LosAngelesAngels","LosAngelesDodgers","MiamiMarlins","MilwaukeeBrewers","MinnesotaTwins","NewYorkYankees","NewYorkMets","OaklandAthletics","PhiladelphiaPhillies","PittsburghPirates","SanDiegoPadres","SanFranciscoGiants","SeattleMariners","StLouisCardinals","TampaBayRays","TexasRangers","TorontoBlueJays","WashingtonNationals"]
    for i in range(len(allScheduleUrlList)):
        print(allTeamFullNameList[i])
        createCSVOfTeamStats(allScheduleUrlList[i],allTeamList[i],allTeamFullNameList[i])

#this combines all the batting stats into one dataframe
def combineToOneDataFrame():
    ARIdf = pandas.read_csv('ArizonaDiamondbacks_Completed_Batting_Statistics.csv')
    ATLdf = pandas.read_csv('AtlantaBraves_Completed_Batting_Statistics.csv')
    BALdf = pandas.read_csv('BaltimoreOrioles_Completed_Batting_Statistics.csv')
    BOSdf = pandas.read_csv('BostonRedSox_Completed_Batting_Statistics.csv')
    CHWdf = pandas.read_csv('ChicagoWhiteSox_Completed_Batting_Statistics.csv')
    CHCdf = pandas.read_csv('ChicagoCubs_Completed_Batting_Statistics.csv')
    CINdf = pandas.read_csv('CincinnatiReds_Completed_Batting_Statistics.csv')
    CLEdf = pandas.read_csv('ClevelandIndians_Completed_Batting_Statistics.csv')
    COLdf = pandas.read_csv('ColoradoRockies_Completed_Batting_Statistics.csv')
    DETdf = pandas.read_csv('DetroitTigers_Completed_Batting_Statistics.csv')
    HOUdf = pandas.read_csv('HoustonAstros_Completed_Batting_Statistics.csv')
    KCRdf = pandas.read_csv('KansasCityRoyals_Completed_Batting_Statistics.csv')
    LAAdf = pandas.read_csv('LosAngelesAngels_Completed_Batting_Statistics.csv')
    LADdf = pandas.read_csv('LosAngelesDodgers_Completed_Batting_Statistics.csv')
    MIAdf = pandas.read_csv('MiamiMarlins_Completed_Batting_Statistics.csv')
    MILdf = pandas.read_csv('MilwaukeeBrewers_Completed_Batting_Statistics.csv')
    MINdf = pandas.read_csv('MinnesotaTwins_Completed_Batting_Statistics.csv')
    NYYdf = pandas.read_csv('NewYorkYankees_Completed_Batting_Statistics.csv')
    NYMdf = pandas.read_csv('NewYorkMets_Completed_Batting_Statistics.csv')
    OAKdf = pandas.read_csv('OaklandAthletics_Completed_Batting_Statistics.csv')
    PHIdf = pandas.read_csv('PhiladelphiaPhillies_Completed_Batting_Statistics.csv')
    PITdf = pandas.read_csv('PittsburghPirates_Completed_Batting_Statistics.csv')
    SDPdf = pandas.read_csv('SanDiegoPadres_Completed_Batting_Statistics.csv')
    SFGdf = pandas.read_csv('SanfranciscoGiants_Completed_Batting_Statistics.csv')
    SEAdf = pandas.read_csv('SeattleMariners_Completed_Batting_Statistics.csv')
    STLdf = pandas.read_csv('StLouisCardinals_Completed_Batting_Statistics.csv')
    TBRdf = pandas.read_csv('TampaBayRays_Completed_Batting_Statistics.csv')
    TEXdf = pandas.read_csv('TexasRangers_Completed_Batting_Statistics.csv')
    TORdf = pandas.read_csv('TorontoBlueJays_Completed_Batting_Statistics.csv')
    WASdf = pandas.read_csv('WashingtonNationals_Completed_Batting_Statistics.csv')
    dfComplete = pandas.concat([ARIdf,ATLdf,BALdf,BOSdf,CHWdf,CHCdf,CINdf,CLEdf,COLdf,DETdf,HOUdf,KCRdf,LAAdf,LADdf,MIAdf,MILdf,MINdf,NYYdf,NYMdf,OAKdf,PHIdf,PITdf,SDPdf,SFGdf,SEAdf,STLdf,TBRdf,TEXdf,TORdf,WASdf])
    dfComplete.to_csv('dfComplete.csv')
    return(dfComplete)

#this function allows you to subtract the values of two rows
def subtract(two_rows):
    x, y = two_rows.values
    return pandas.Series(x-y, two_rows.columns)

#this function uses the subtract function to create new variables which are the ratios between teams of stats
def createRatioVariables():
    dfOld = pandas.read_csv('dfComplete.csv')
    df = pandas.DataFrame({
    'url': dfOld['url'],
    'Win_Percentage': dfOld['Win_Percentage'],
    'R_Season_Long_Count': dfOld['R_Season_Long_Count'],
    'H_Season_Long_Count': dfOld['H_Season_Long_Count'],
    'BB_Season_Long_Count': dfOld['BB_Season_Long_Count'],
    'SO_Season_Long_Count': dfOld['SO_Season_Long_Count'],
    'PA_Season_Long_Count': dfOld['PA_Season_Long_Count'],
    'R_Moving_Average_3': dfOld['R_Moving_Average_3'],
    'R_Moving_Average_10': dfOld['R_Moving_Average_10'],
    'R_Moving_Average_31': dfOld['R_Moving_Average_31'],
    'SLG_Moving_Average_3': dfOld['SLG_Moving_Average_3'],
    'SLG_Moving_Average_10': dfOld['SLG_Moving_Average_10'],
    'SLG_Moving_Average_31': dfOld['SLG_Moving_Average_31'],
    'BA_Moving_Average_3': dfOld['BA_Moving_Average_3'],
    'BA_Moving_Average_10': dfOld['BA_Moving_Average_10'],
    'BA_Moving_Average_31': dfOld['BA_Moving_Average_31'],
    'OBP_Moving_Average_3': dfOld['OBP_Moving_Average_3'],
    'OBP_Moving_Average_10': dfOld['OBP_Moving_Average_10'],
    'OBP_Moving_Average_31': dfOld['OBP_Moving_Average_31'],
    'SO_Moving_Average_3': dfOld['SO_Moving_Average_3'],
    'SO_Moving_Average_10': dfOld['SO_Moving_Average_10'],
    'SO_Moving_Average_31': dfOld['SO_Moving_Average_31'],
    'AB_Moving_Average_3': dfOld['AB_Moving_Average_3'],
    'AB_Moving_Average_10': dfOld['AB_Moving_Average_10'],
    'AB_Moving_Average_31': dfOld['AB_Moving_Average_31'],
    'Pit_Moving_Average_3': dfOld['Pit_Moving_Average_3'],
    'Pit_Moving_Average_10': dfOld['Pit_Moving_Average_10'],
    'Pit_Moving_Average_31': dfOld['Pit_Moving_Average_31'],
    'H_Moving_Average_3': dfOld['H_Moving_Average_3'],
    'H_Moving_Average_10': dfOld['H_Moving_Average_10'],
    'H_Moving_Average_31': dfOld['H_Moving_Average_31'],
    'BB_Moving_Average_3': dfOld['BB_Moving_Average_3'],
    'BB_Moving_Average_10': dfOld['BB_Moving_Average_10'],
    'BB_Moving_Average_31': dfOld['BB_Moving_Average_31'],
    'OPS_Moving_Average_3': dfOld['OPS_Moving_Average_3'],
    'OPS_Moving_Average_10': dfOld['OPS_Moving_Average_10'],
    'OPS_Moving_Average_31': dfOld['OPS_Moving_Average_31'],
    'RE24_Moving_Average_3': dfOld['RE24_Moving_Average_3'],
    'RE24_Moving_Average_10': dfOld['RE24_Moving_Average_10'],
    'RE24_Moving_Average_31': dfOld['RE24_Moving_Average_31'],
    'Win_Percentage_Moving_Average_3': dfOld['Win_Percentage_Moving_Average_3'],
    'Win_Percentage_Moving_Average_10': dfOld['Win_Percentage_Moving_Average_10'],
    'Win_Percentage_Moving_Average_31': dfOld['Win_Percentage_Moving_Average_31'],
    'BA_Season_Long_Average': dfOld['BA_Season_Long_Average'],
    'SLG_Season_Long_Average': dfOld['SLG_Season_Long_Average'],
    'OPS_Season_Long_Average': dfOld['OPS_Season_Long_Average'],

})
    columns_for_ratio = ['Win_Percentage','R_Season_Long_Count','H_Season_Long_Count','BB_Season_Long_Count','SO_Season_Long_Count','PA_Season_Long_Count','R_Moving_Average_3','R_Moving_Average_10','R_Moving_Average_31','SLG_Moving_Average_3','SLG_Moving_Average_10','SLG_Moving_Average_31','BA_Moving_Average_3','BA_Moving_Average_10','BA_Moving_Average_31'
    ,'OBP_Moving_Average_3','OBP_Moving_Average_10','OBP_Moving_Average_31','SO_Moving_Average_3','SO_Moving_Average_10','SO_Moving_Average_31','AB_Moving_Average_3','AB_Moving_Average_10','AB_Moving_Average_31'
    ,'Pit_Moving_Average_3','Pit_Moving_Average_10','Pit_Moving_Average_31','H_Moving_Average_3','H_Moving_Average_10','H_Moving_Average_31'
    ,'BB_Moving_Average_3','BB_Moving_Average_10','BB_Moving_Average_31','OPS_Moving_Average_3','OPS_Moving_Average_10','OPS_Moving_Average_31'
    ,'RE24_Moving_Average_3','RE24_Moving_Average_10','RE24_Moving_Average_31','Win_Percentage_Moving_Average_3','Win_Percentage_Moving_Average_10','Win_Percentage_Moving_Average_31',
    'BA_Season_Long_Average','SLG_Season_Long_Average','OPS_Season_Long_Average']
    df = df.groupby('url')[columns_for_ratio].apply(subtract)
    return(df)


#this combines all variables into one dataframe
def addFinalFeatures():
    df = pandas.read_csv('dfComplete.csv')
    winOrLossDf = df[['WinOrLoss','url','HomeOrAway','R']]
    winOrLossDfDropped = winOrLossDf.iloc[:-2429]
    dfRatio = createRatioVariables()
    #standardizedWin_Percentage = (dfRatio['Win_Percentage']-dfRatio['Win_Percentage'].mean() / dfRatio['Win_Percentage'].std())
    #dfRatio = dfRatio.insert(2,'Standardized_Win',standardizedWin_Percentage)
    #dfRatio = (dfRatio-dfRatio.mean())/dfRatio.std()
    dfFinal = pandas.merge(dfRatio,winOrLossDfDropped, on='url')
    dfFinal = dfFinal.dropna(axis=0)
    return(dfFinal)
