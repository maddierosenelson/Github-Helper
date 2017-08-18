import json
import os
import requests
import argparse
import datetime
from urllib import urlopen
#Instal terminaltables with `pip install terminaltables`
from terminaltables import SingleTable
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = "https://jaxf-github.fanatics.corp/api/v3"
ORG_NAME  = "apparel"

URLTableData=[]
URLHeader=['Repository Name','Pull Request Name','URL']

contributorsTableData=[]
contributorsHeader=['Repository Name','Pull Request Name', 'Contributors']

lastUpdatedTableData=[]
lastUpdatedHeader=['Repository Name','Pull Request Name','User','Last Updated','URL']

userInputTableData=[]
userInputHeader=['Repository Name','Pull Request Name','Last Updated','URL']

contributorsInputTableData=[]
contributorsInputHeader=['Repository Name','Pull Request Name','Last Updated','URL']

repoInputTableData=[]
repoInputHeader=['Repository Name','Pull Request Name','URL']

xDaysOldTableData=[]
xDaysOldHeader=['Repository Name','Pull Request Name','User','Last Updated']

searchInputTableData=[]
searchInputTableHeader=['Repository Name','Pull Request Name','User','Last Updated','URL']

firstContributor=True
allContributors=[]


uniqueKeyAndDateSort={}
prData={}

def run(usernameInput, contributorInput, repoInput, daysInput, searchInput):
    if daysInput:
        int(daysInput)
    
    resp = requests.get("{}/orgs/{}/repos".format(BASE_URL, ORG_NAME), verify=False)
    if resp.status_code != 200:
        raise Exception("Unable to pull repos...")

    #append headers to the top of table
    repos = json.loads(resp.content)
    URLTableData.append(URLHeader)
    contributorsTableData.append(contributorsHeader)
    lastUpdatedTableData.append(lastUpdatedHeader)
    userInputTableData.append(userInputHeader)
    contributorsInputTableData.append(contributorsInputHeader)
    repoInputTableData.append(repoInputHeader)
    xDaysOldTableData.append(xDaysOldHeader)
    searchInputTableData.append(searchInputTableHeader)

    print "Summary of Open Pull Requests:"
    for repo in repos:
        r = requests.get("{}/repos/{}/{}/pulls".format(BASE_URL, ORG_NAME, repo["name"]), verify=False)
        
        if r.status_code != 200:
            raise Exception("Unable to pull PRs...")
        
        prs = json.loads(r.content)
        
        if prs:
            print '({}) PRs found for {}'.format(len(prs), repo['name'])
            for pr in prs:
                fillDictionaries(repo, pr, usernameInput, contributorInput, repoInput)

    loadSortedDataFromDictionaries(usernameInput, contributorInput, repoInput, daysInput, searchInput)
    printTables(usernameInput, contributorInput, repoInput, daysInput, searchInput)

def fillDictionaries(repo, pr, usernameInput, contributorInput, repoInput):
    contributorsResp=requests.get(repo["contributors_url"])
    allContributorsData=json.loads(contributorsResp.content) #produces a dictionary out of the given string
    contributors=[]
    firstContributor=True
    
    for currContributor in range(1, len(allContributorsData)):
        currContributorData=allContributorsData[currContributor]
        currContributorName=currContributorData["login"]
        contributors.append(currContributorName)
        allContributors.append(currContributorName)
        #When printing the contributorsTable, it is easier to read if the first contributor is listed next to the repo name and pr title and then the following contributors are listed next to empty spaces.
        if firstContributor:
            contributorsTableData.append([repo['name'],pr["title"], str(currContributorName)])
            firstContributor=False
        else:
            contributorsTableData.append(["","", str(currContributorName)])
    
    date=pr["updated_at"][0:10]
    #Must use both the repo name and pr name as the unique key as some prs have the same name.
    uniqueKey="{}".format(pr["title"].encode('utf-8'))+"{}".format(repo['name'])
    prData[uniqueKey]=[repo['name'], pr["title"], pr["user"]["login"], date, pr["url"], contributors]
    uniqueKeyAndDateSort[uniqueKey]=[date]

def loadSortedDataFromDictionaries(usernameInput, contributorInput, repoInput, daysInput, searchInput):
    #Sort the dictionary using sorted() so the prs will print from oldest to newest for whichever input given or table being printed.
    for key, value in sorted(uniqueKeyAndDateSort.iteritems(), key=lambda (k,v): (v,k)):
        curPRInfo=prData[key]
        repo=curPRInfo[0]
        pr=curPRInfo[1]
        user=curPRInfo[2]
        date=curPRInfo[3]
        url=curPRInfo[4]
        prContributors=curPRInfo[5]
        lastUpdatedTableData.append([repo, pr, user, date, url])

        if usernameInput==user:
            userInputTableData.append([repo, pr, date, url])

        if contributorInput in prContributors:
            contributorsInputTableData.append([repo, pr, date, url])
        
        if (repoInput==repo):
            repoInputTableData.append([repo, pr, url])  

        if searchInput:
            prUpper=pr.upper()
            if(searchInput.upper() in prUpper):
                searchInputTableData.append([repo, pr, user, date, url])

        loadXDaysTable(repo, pr, user, date, url, daysInput)
        #The URLTable is a basic table that prints all of the prs. However, the actual printing statement is commented out below.
        URLTableData.append([repo, pr, url])

def loadXDaysTable(repo, pr, user, lastUpdatedDate, url, daysInput):
    currentDate=datetime.datetime.now().today()
    lastDate=datetime.datetime.strptime(lastUpdatedDate, '%Y-%m-%d')
    difference=abs((currentDate-lastDate).days)
    if daysInput and daysInput>0:
        if int(difference)>=int(daysInput):
            xDaysOldTableData.append([repo, pr, user, lastUpdatedDate])

def printTables(usernameInput, contributorInput, repoInput, daysInput, searchInput):
    if usernameInput:
        #Table with the prs created by the inputted username.
        if len(userInputTableData) >=2:
            userInputTable = SingleTable(userInputTableData)
            userInputTable.inner_row_border = True
            print ("Printing PRs created by: " + usernameInput)
            print userInputTable.table
        #If the username is in allContributors, then likely it just hasn't opened a PR right now and that the name is not invalid.
        elif usernameInput in allContributors:
            print ("This user has no open PRs.")
        else:
            print ("This username is invalid. Please try again.")
    
    if contributorInput:
        #Table with the prs contributed to by the inputted username. 
        if len(contributorsInputTableData)>=2:
            contributorsInputTable = SingleTable(contributorsInputTableData)
            contributorsInputTable.inner_row_border = True
            print ("Printing PRs contributed to by: " + contributorInput)
            print contributorsInputTable.table
        elif contributorInput=="all":
            print ("Printing all open PRs and their contributors.")
            #Table with all of the contributors for each pull request listed
            contributorTable = SingleTable(contributorsTableData)
            contributorTable.inner_row_border = True
            print contributorTable.table
        else:
            print ("This user has not contributed to any open PRs or the username was inputted incorrectly.")
   
    if repoInput:
        #Table with the prs in the repo inputted. 
        if len(repoInputTableData)>=2:
            repoInputTable = SingleTable(repoInputTableData)
            repoInputTable.inner_row_border = True
            print ("Printing open PRs in: " + repoInput)
            print repoInputTable.table
        elif repoInput=="all":
            print ("Printing open PRs in all repos.")
            #Table with the last updated dates arranged from oldest to newest.
            lastUpdatedTable = SingleTable(lastUpdatedTableData)
            lastUpdatedTable.inner_row_border = True
            print lastUpdatedTable.table
        else:
            print ("This repository has no open PRs or the repository name was inputted incorrectly.")
    
    if daysInput:
        #Table with the prs last updated more than X days ago.
        if daysInput<0:
            print ("The inputted value: "+str(daysInput)+" is invalid.")
        elif len(xDaysOldTableData)>=2:
            xDaysInputTable=SingleTable(xDaysOldTableData)
            xDaysInputTable.inner_row_border=True
            print ("Printing PRs that were last updated more than "+str(daysInput)+" days ago.")
            print xDaysInputTable.table
        else:
            print ("There are no PRs that were last updated more than "+str(daysInput)+" days ago.")

    if searchInput:
        if len(searchInputTableData)>=2:
            #Table with the prs containing the search term in the pr name.
            searchInputTable=SingleTable(searchInputTableData)
            searchInputTable.inner_row_border=True
            print ("Printing PRs with "+searchInput+" in the title.")
            print searchInputTable.table
        else:
            print ("There are no open PRs with "+searchInput+" in the title. Please try a different search term.")

    #table with the urls for each of the pull requests.
    # URLtable = SingleTable(URLTableData)
    # URLtable.inner_row_border = True
    # print URLtable.table


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    #If the user inputs -u, get_prs.py will return a table with just the prs that the user has created.
    PARSER.add_argument("-u", "--username", help="Username")
    #If the user inputs -c, get_prs.py will return a table with the prs that user has contributed to. If the user inputs -c "all", all the contributors for each pr will be printed.
    PARSER.add_argument("-c", "--contributor", help="Contributor")
    #If the user inputs -r, get_prs.py will return a table with the prs in that repo. If the user inputs -r "all", all the open prs will be printed.
    PARSER.add_argument("-r", "--repo", help="Repo")
    #If the user inputs -x, get_prs.py will return a table with the prs that have been open longer than x days.
    PARSER.add_argument("-x", "--days", help="XDaysOld")
    #If the user inputs -s, get_prs.py will return all prs with the inputted string in its name.
    PARSER.add_argument("-s", "--search", help="Search")

    ARGS = PARSER.parse_args()

    run(ARGS.username, ARGS.contributor, ARGS.repo, ARGS.days, ARGS.search)
   
   
