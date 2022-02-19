import pandas, numpy
import requests, bs4
import re, os

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

def getSeasonStats(url):
    battingDataList = []
    urlList = boxScoreUrls(url)
    for i in urlList:
        battingData = pullBattingData(i)
        battingDataList.append(battingData)
    battingDataList = numpy.reshape(battingDataList, (162,24))
    dfOfBattingData = pandas.DataFrame(battingDataList) 
    dfOfBattingData.columns = ['Batting','AB','R','H','RBI','BB','SO','PA','BA','OBP','SLG','OPS','Pit','Str','WPA','aLI','WPA+','WPA-','cWPA','acLI','RE24','PO','A','Details']
    dfOfBattingData = dfOfBattingData.drop(['Batting','WPA','aLI','WPA+','WPA-','cWPA','acLI','PO','A','Details'], axis=1)
    return(dfOfBattingData)


#print(pullTable("https://www.baseball-reference.com/boxes/ARI/ARI202104130.shtml", "OaklandAthleticsbatting"))

tryOne = getSeasonStats("https://www.baseball-reference.com/teams/OAK/2021-schedule-scores.shtml")

print(tryOne)
tryOne.to_csv('OaklandA2021.csv')
#print(findTables(urlBaseball))

#seasonUrl = boxScoreUrls("https://www.baseball-reference.com/teams/OAK/2021-schedule-scores.shtml")

#print(seasonUrl)
#seasonUrl.to_csv('seasonUrl.csv')
#print(pullTable(urlBaseball, "OaklandAthleticsbatting"))

#OaklandTotal = [OaklandBatting1, OaklandBatting2]

#OaklandTotal1 = pandas.concat(OaklandTotal)

#print(OaklandTotal)

#print(pullHeader(urlBaseball, "OaklandAthleticsbatting"))

#A_Stat_Trial = pullBattingData(urlBaseball)

#OaklandTotal1.to_csv('OaklandTotal.csv')


#homeOrAway = []



