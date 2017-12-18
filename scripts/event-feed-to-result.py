import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import datetime
import cgi
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree

tree = ET.parse('event-feed.xml')
root = tree.getroot()

prob_count = len(root.findall('problem'))
data = {}

for team in root.findall('team'):
    data[int(team.findall('id')[0].text)] = {
        'name': cgi.escape(team.findall('university')[0].text),
        'solve': 0, 'penalty': 0
    }

for run in root.findall('run'):
    if run.findall('judged')[0].text == 'False':
        continue

    team = int(run.findall('team')[0].text)
    time = float(run.findall('time')[0].text)
    prob = int(run.findall('problem')[0].text)
    result = run.findall('result')[0].text
    solved = run.findall('solved')[0].text
    penalty = run.findall('penalty')[0].text

    if prob not in data[team].keys():
        data[team][prob] = {'attempt': 0, 'solve': -1, 'penalty': 0}

    data[team][prob]['attempt'] += 1

    if data[team][prob]['solve'] >= 0:
        continue

    if solved == 'True':
        t = int(time / 60)
        data[team][prob]['solve'] = t
        data[team][prob]['penalty'] += t
        data[team]['solve'] += 1
        data[team]['penalty'] += data[team][prob]['penalty']
    if penalty == 'True':
        data[team][prob]['penalty'] += 20

rank = list(data.keys())
rank.sort(key=lambda x: data[x]['solve'] * -100000 + data[x]['penalty'])

prob_name = {}
for prob in root.findall('problem'):
    prob_name[int(prob.findall('id')[0].text)] = prob.findall('label')[0].text + '. ' + prob.findall('name')[0].text

print(
'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<contestStandings>'''
)

# Start of standing header
# <standingsHeader currentDate="Sun Dec 11 14:35:15 CST 2016" generatorId="$Id$" groupCount="1" medianProblemsSolved="3" problemCount="12" problemsAttempted="12" siteCount="1" systemName="CSUS Programming Contest System" systemURL="http://pc2.ecs.csus.edu/" systemVersion="9.3.3 20160914 build 3454" title="The 2016 ACM-ICPC Asia China-Final (Shanghai) Contest" totalAttempts="4753" totalSolved="1224">

tot_attempt = 0
tot_solve = 0
prob_attempt = 0
for prob in range(1, prob_count + 1):
    flag = False
    for team in data.keys():
        if prob not in data[team].keys():
            continue
        flag = True
        tot_attempt += data[team][prob]['attempt']
        if data[team][prob]['solve'] >= 0:
            tot_solve += 1
    if flag:
        prob_attempt += 1

title = root.findall('info')[0].findall('title')[0].text

each_solve = []
for team in data.keys():
    each_solve.append(data[team]['solve'])
each_solve.sort()
mid_solve = each_solve[len(each_solve) // 2]

fmt = '%a %b %d %H:%M:%S %Y'
current_date = datetime.datetime.now().strftime(fmt)

print('  <standingsHeader currentDate="%s" generatorId="$Id$" groupCount="1" medianProblemsSolved="%d" problemCount="%d" problemsAttempted="%d" siteCount="1" systemName="CSUS Programming Contest System" systemURL="http://pc2.ecs.csus.edu/" systemVersion="9.3.3 20160914 build 3454" title="%s" totalAttempts="%d" totalSolved="%d">' % (current_date, mid_solve, prob_count, prob_attempt, title, tot_attempt, tot_solve))

# Problem id
print(
'''    <groupList/>
    <colorList>
      <colors id="1" siteNum="1">'''
)

for prob in root.findall('problem'):
    print('        <problem id="%s" />' % prob.findall('id')[0].text)

print(
'''      </colors>
    </colorList>'''
)

# Problem info
for prob in range(1, prob_count + 1):
    print('    <problem ', end='')

    attempt = 0
    first_solve = 99999
    last_solve = -1
    num_solve = 0

    for team in data.keys():
        if prob not in data[team].keys():
            continue

        attempt += data[team][prob]['attempt']
        if data[team][prob]['solve'] >= 0:
            first_solve = min(first_solve, data[team][prob]['solve'])
            last_solve = max(last_solve, data[team][prob]['solve'])
            num_solve += 1

    print('attempts="%d" bestSolutionTime="%d" id="%d" lastSolutionTime="%d" numberSolved="%d" title="%s" />' % (attempt, first_solve, prob, last_solve, num_solve, prob_name[prob]))

# End of standing header
print('  </standingsHeader>')

# Team standings
idx = 0
for team in rank:
    # <teamStanding firstSolved="2" index="0" lastSolved="257" points="1069" problemsAttempted="12" rank="1" solved="11" teamAlias="清华大学 深黑幻想/177/B31 (not aliasesd)" teamExternalId="1177" teamId="177" teamKey="1TEAM177" teamName="清华大学 深黑幻想/177/B31" teamSiteId="1" totalAttempts="21">
    penalty = data[team]['penalty']
    name = data[team]['name']

    first_solve = 99999
    last_solve = -1
    prob_attempt = 0
    prob_solve = 0
    tot_attempt = 0
    for prob in range(1, prob_count + 1):
        if prob not in data[team].keys():
            continue

        prob_attempt += 1
        tot_attempt += data[team][prob]['attempt']
        if data[team][prob]['solve'] >= 0:
            prob_solve += 1
            first_solve = min(first_solve, data[team][prob]['solve'])
            last_solve = max(last_solve, data[team][prob]['solve'])

    if first_solve == 99999:
        first_solve = -1
    if last_solve == -1:
        last_solve = 0

    print('  <teamStanding firstSolved="%d" index="%d" lastSolved="%d" points="%d" problemsAttempted="%d" rank="%d" solved="%d" teamAlias="%s (not aliasesd)" teamExternalId="1%d" teamId="%d" teamKey="1TEAM%d" teamName="%s" teamSiteId="1" totalAttempts="%d">' % (first_solve, idx, last_solve, penalty, prob_attempt, idx + 1, prob_solve, name, team, team, team, name, tot_attempt))

    # <problemSummaryInfo attempts="1" index="1" isPending="false" isSolved="true" points="3" problemId="A. Number Theory Problem-8102580133801794793" solutionTime="3"/>
    for prob in range(1, prob_count + 1):
        if prob in data[team].keys():
            attempt = data[team][prob]['attempt']
            solve = 'true' if data[team][prob]['solve'] >= 0 else 'false'
            point = data[team][prob]['penalty'] if solve == 'true' else 0
            sol_time = data[team][prob]['solve']
        else:
            attempt = 0
            solve = 'false'
            point = 0
            sol_time = 0
        print('    <problemSummaryInfo attempts="%d" index="%d" isPending="false" isSolved="%s" points="%d" problemId="%s" solutionTime="%d"/>' % (attempt, prob, solve, point, prob_name[prob], sol_time))

    print('  </teamStanding>')

    idx += 1

print('</contestStandings>')
