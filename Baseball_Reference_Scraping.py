from cmath import nan
from contextlib import nullcontext
from turtle import home
import pandas, numpy
import requests, bs4
import re, os

def findTables(url):
    res = requests.get(url)
    ## The next two lines get around the issue with comments breaking the parsing.
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

## Pulls a single table from a url provided by the user.
## The desired table should be specified by tableID.
## This function is used in all functions that do more complicated pulls.
def pullTable(url, tableID):
    res = requests.get(url)
    ## Work around comments
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
    #data.columns = header
    #data = data.loc[data[header[0]] != header[0]]
    data = data.drop(0)
    data = data.reset_index(drop = True)
    return(data)

def pullHeader(url, tableID):
    res = requests.get(url)
    ## Work around comments
    comm = re.compile("<!--|-->")
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    tables = soup.findAll('table', id = tableID)
    data_rows = tables[0].findAll('tr')
    data_header = tables[0].findAll('thead')
    data_header = data_header[0].findAll("tr")
    data_header = data_header[0].findAll("th")
    game_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])]
        for i in range(1)
        ]
    data = pandas.DataFrame(game_data)
    return(data)

def pullBattingData(url, team):
    teamBatting = pullTable(url, team + "batting")
    teamBatting = teamBatting.loc[[len(teamBatting)-1]]
    return(teamBatting)

def boxScoreUrls(url):
    res = requests.get(url)
    ## Work around comments
    comm = re.compile("<!--|-->")
    soup = bs4.BeautifulSoup(comm.sub("", res.text), 'lxml')
    dataLink = []
    #tables = soup.findAll('table', id = "team_schedule")
    #data_rows = tables[0].findAll('tr')
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

def opponentList(url):
    schedule_table = pullTable(url, 'team_schedule')

    opponentColumn = schedule_table[5]

    opponentList = opponentColumn.values.tolist()

    opponentListFinal = []

    for i in range(len(opponentList)):
        if opponentList[i] != 'Opp':
            opponentListFinal.append(opponentList[i])
    
    return(opponentListFinal)

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

def getSeasonStats(url, team, teamFullName):
    teamList = []
    battingDataList = []
    urlList = boxScoreUrls(url)
    for i in urlList:
        battingData = pullBattingData(i, teamFullName)
        battingDataList.append(battingData)
    battingDataList = numpy.reshape(battingDataList, (162,24))
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
    dfOfBattingData.to_csv(teamFullName + "_Batting_Statistics.csv")
    return(dfOfBattingData)

def findMovingAverage(df, columnName, numberOfGames):
    variableList = df[columnName]
    variableSeries = pandas.Series(variableList)
    windows = variableSeries.rolling(numberOfGames)
    movingAverage = windows.mean()
    movingAverageList = movingAverage.values.tolist()
    movingAverageList.insert(0, nan)
    movingAverageList.pop()
    return(movingAverageList)

def addMovingAveragesOfStat(df, stat):
    movingAverage3 = findMovingAverage(df,stat,3)
    df[stat + '_Moving_Average_3'] = movingAverage3
    movingAverage10 = findMovingAverage(df,stat,10)
    df[stat + '_Moving_Average_10'] = movingAverage10
    movingAverage31 = findMovingAverage(df,stat,31)
    df[stat + '_Moving_Average_31'] = movingAverage31

def addSeasonLongAverageStatistics(df, stat):
    variableContinuedStatList = []
    variableList = df[stat]
    totalSum = 0
    totalCount = 0

    for i in range(len(variableList)):
        totalSum = totalSum + variableList[i]
        totalCount = totalCount + 1
        average = totalSum/totalCount
        variableContinuedStatList.append(average)
    df[stat + '_Season_Long_Average'] = variableContinuedStatList

def addSeasonLongCount(df, stat):
    countTotalList = []
    variableList = df[stat]
    count = 0
    for i in range(len(variableList)):
        count = count + int(variableList[i])
        countTotalList.append(count)
    df[stat + "_Season_Long_Count"] = countTotalList


def transformedSeasonStats(df):
    #df = getSeasonStats(url, team, teamFullName)
    winsList = df['WinOrLoss']
    winsTotal = 0
    gamesTotal = 0
    winningPercentageList = []
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

def completedBattingStatsOfTeamdf(url, team, teamFullName):
    getSeasonStats(url, team, teamFullName)
    df = pandas.read_csv(teamFullName + "_Batting_Statistics.csv")
    transformedDf = transformedSeasonStats(df)
    return(transformedDf)


def completedBattingStatsOfAllTeams():
    allScheduleUrlList = ["https://www.baseball-reference.com/teams/ARI/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/ATL/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/BAL/2021-schedule-scores.shtml", "https://www.baseball-reference.com/teams/BOS/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CHW/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CHC/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CIN/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/CLE/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/COL/2021.shtml","https://www.baseball-reference.com/teams/DET/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/HOU/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/KCR/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/LAA/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/LAD/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/MIA/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/MIL/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/MIN/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/NYY/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/NYM/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/OAK/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/PHI/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/PIT/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/SDP/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/SFG/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/SEA/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/STL/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/TBR/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/TEX/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/TOR/2021-schedule-scores.shtml","https://www.baseball-reference.com/teams/WSN/2021-schedule-scores.shtml"]
    allTeamList = ['ARI','ATL','BAL','BOS','CHW','CHC','CIN','CLE','COL','DET','HOU','KCR','LAA','LAD','MIA','MIL','MIN','NYY','NYM','OAK','PHI','PIT','SDP','SFG','SEA','STL','TBR','TEX','TOR','WAS']
    allTeamFullNameList = ["ArizonaDiamondbacks","AtlantaBraves","BaltimoreOrioles","BostonRedSox","ChicagoWhiteSox","ChicagoCubs","CincinnatiReds","ClevelandIndians","ColoradoRockies","DetroitTigers","HoustonAstros","KansasCityRoyals","LosAngelesAngels","LosAngelesDodgers","MiamiMarlins","MilwaukeeBrewers","MinnesotaTwins","NewYorkYankees","NewYorkMets","OaklandAthletics","PhiladelphiaPhillies","PittsburghPirates","SanDiegoPadres","SanFranciscoGiants","SeattleMariners","StLouisCardinals","TampaBayRays","TexasRangers","TorontoBlueJays","WashingtonNationals"]
    # only need 1 for loop to go through each team
    for i in range(len(allTeamList)):
        completedBattingStatsOfTeamdf(allScheduleUrlList[i],allTeamList[i],allTeamFullNameList[i])
        

print(getSeasonStats("https://www.baseball-reference.com/teams/STL/2021-schedule-scores.shtml",'STL',"StLouisCardinals"))





