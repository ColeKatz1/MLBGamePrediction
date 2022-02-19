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

def pullBattingData(url):
    OaklandAthleticsBatting = pullTable(url, "OaklandAthleticsbatting")
    OaklandAthleticsBatting = OaklandAthleticsBatting.loc[[len(OaklandAthleticsBatting)-1]]
    return(OaklandAthleticsBatting)

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

def getSeasonStats(url, team):
    teamList = []
    battingDataList = []
    urlList = boxScoreUrls(url)
    for i in urlList:
        battingData = pullBattingData(i)
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
    return(dfOfBattingData)

df = pandas.read_csv('improvedData.csv')

def transformSeasonStats(df):
    #df = getSeasonStats(url, team)
    runsList = df['R']
    runsTotal = 0
    runsTotalList = []
    for i in range(len(runsList)):
        runsTotal = runsTotal + runsList[i]
        runsTotalList.append(runsTotal)
    df['R_Count'] = runsTotalList

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

    return(df)

transformedDf = transformSeasonStats(df)

print(transformedDf)
#tryOne = getSeasonStats("https://www.baseball-reference.com/teams/OAK/2021-schedule-scores.shtml",'OAK')

#print(tryOne)

#tryOne.to_csv('improvedData.csv')




