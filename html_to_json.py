import requests as reqs 
from bs4 import BeautifulSoup
import os
import time
import sys
import re
import json

r = 'abcdefghijklmnopqrstuvwxyz+-#0123456789'

continent_map = {
  "WWW": "North America",
  "AD": "Europe",
  "AE": "Asia",
  "AF": "Asia",
  "AG": "North America",
  "AI": "North America",
  "AL": "Europe",
  "AM": "Asia",
  "AN": "North America",
  "AO": "Africa",
  "AQ": "Antarctica",
  "AR": "South America",
  "AS": "Australia",
  "AT": "Europe",
  "AU": "Australia",
  "AW": "North America",
  "AZ": "Asia",
  "BA": "Europe",
  "BB": "North America",
  "BD": "Asia",
  "BE": "Europe",
  "BF": "Africa",
  "BG": "Europe",
  "BH": "Asia",
  "BI": "Africa",
  "BJ": "Africa",
  "BM": "North America",
  "BN": "Asia",
  "BO": "South America",
  "BR": "South America",
  "BS": "North America",
  "BT": "Asia",
  "BW": "Africa",
  "BY": "Europe",
  "BZ": "North America",
  "CA": "North America",
  "CC": "Asia",
  "CD": "Africa",
  "CF": "Africa",
  "CG": "Africa",
  "CH": "Europe",
  "CI": "Africa",
  "CK": "Australia",
  "CL": "South America",
  "CM": "Africa",
  "CN": "Asia",
  "CO": "South America",
  "CR": "North America",
  "CU": "North America",
  "CV": "Africa",
  "CX": "Asia",
  "CY": "Asia",
  "CZ": "Europe",
  "DE": "Europe",
  "DJ": "Africa",
  "DK": "Europe",
  "DM": "North America",
  "DO": "North America",
  "DZ": "Africa",
  "EC": "South America",
  "EE": "Europe",
  "EG": "Africa",
  "EH": "Africa",
  "ER": "Africa",
  "ES": "Europe",
  "ET": "Africa",
  "FI": "Europe",
  "FJ": "Australia",
  "FK": "South America",
  "FM": "Australia",
  "FO": "Europe",
  "FR": "Europe",
  "GA": "Africa",
  "GB": "Europe",
  "GD": "North America",
  "GE": "Asia",
  "GF": "South America",
  "GG": "Europe",
  "GH": "Africa",
  "GI": "Europe",
  "GL": "North America",
  "GM": "Africa",
  "GN": "Africa",
  "GP": "North America",
  "GQ": "Africa",
  "GR": "Europe",
  "GS": "Antarctica",
  "GT": "North America",
  "GU": "Australia",
  "GW": "Africa",
  "GY": "South America",
  "HK": "Asia",
  "HN": "North America",
  "HR": "Europe",
  "HT": "North America",
  "HU": "Europe",
  "ID": "Asia",
  "IE": "Europe",
  "IL": "Asia",
  "IM": "Europe",
  "IN": "Asia",
  "IO": "Asia",
  "IQ": "Asia",
  "IR": "Asia",
  "IS": "Europe",
  "IT": "Europe",
  "JE": "Europe",
  "JM": "North America",
  "JO": "Asia",
  "JP": "Asia",
  "KE": "Africa",
  "KG": "Asia",
  "KH": "Asia",
  "KI": "Australia",
  "KM": "Africa",
  "KN": "North America",
  "KP": "Asia",
  "KR": "Asia",
  "KW": "Asia",
  "KY": "North America",
  "KZ": "Asia",
  "LA": "Asia",
  "LB": "Asia",
  "LC": "North America",
  "LI": "Europe",
  "LK": "Asia",
  "LR": "Africa",
  "LS": "Africa",
  "LT": "Europe",
  "LU": "Europe",
  "LV": "Europe",
  "LY": "Africa",
  "MA": "Africa",
  "MC": "Europe",
  "MD": "Europe",
  "ME": "Europe",
  "MG": "Africa",
  "MH": "Australia",
  "MK": "Europe",
  "ML": "Africa",
  "MM": "Asia",
  "MN": "Asia",
  "MO": "Asia",
  "MP": "Australia",
  "MQ": "North America",
  "MR": "Africa",
  "MS": "North America",
  "MT": "Europe",
  "MU": "Africa",
  "MV": "Asia",
  "MW": "Africa",
  "MX": "North America",
  "MY": "Asia",
  "MZ": "Africa",
  "NA": "Africa",
  "NC": "Australia",
  "NE": "Africa",
  "NF": "Australia",
  "NG": "Africa",
  "NI": "North America",
  "NL": "Europe",
  "NO": "Europe",
  "NP": "Asia",
  "NR": "Australia",
  "NU": "Australia",
  "NZ": "Australia",
  "OM": "Asia",
  "PA": "North America",
  "PE": "South America",
  "PF": "Australia",
  "PG": "Australia",
  "PH": "Asia",
  "PK": "Asia",
  "PL": "Europe",
  "PM": "North America",
  "PN": "Australia",
  "PR": "North America",
  "PS": "Asia",
  "PT": "Europe",
  "PW": "Australia",
  "PY": "South America",
  "QA": "Asia",
  "RE": "Africa",
  "RO": "Europe",
  "RS": "Europe",
  "RU": "Europe",
  "RW": "Africa",
  "SA": "Asia",
  "SB": "Australia",
  "SC": "Africa",
  "SD": "Africa",
  "SE": "Europe",
  "SG": "Asia",
  "SH": "Africa",
  "SI": "Europe",
  "SJ": "Europe",
  "SK": "Europe",
  "SL": "Africa",
  "SM": "Europe",
  "SN": "Africa",
  "SO": "Africa",
  "SR": "South America",
  "ST": "Africa",
  "SV": "North America",
  "SY": "Asia",
  "SZ": "Africa",
  "TC": "North America",
  "TD": "Africa",
  "TF": "Antarctica",
  "TG": "Africa",
  "TH": "Asia",
  "TJ": "Asia",
  "TK": "Australia",
  "TM": "Asia",
  "TN": "Africa",
  "TO": "Australia",
  "TR": "Asia",
  "TT": "North America",
  "TV": "Australia",
  "TW": "Asia",
  "TZ": "Africa",
  "UK": "Europe",
  "UA": "Europe",
  "UG": "Africa",
  "US": "North America",
  "UY": "South America",
  "UZ": "Asia",
  "VC": "North America",
  "VE": "South America",
  "VG": "North America",
  "VI": "North America",
  "VN": "Asia",
  "VU": "Australia",
  "WF": "Australia",
  "WS": "Australia",
  "YE": "Asia",
  "YT": "Africa",
  "ZA": "Africa",
  "ZM": "Africa",
  "ZW": "Africa"
}


def read_html(fn):
    f = open('./html/{}'.format(fn))
    html = f.read()
    f.close()
    return html

def read_soup(fn):
    return BeautifulSoup(read_html(fn), 'html.parser')

def get_location(soup):
    h3 = soup.findAll("h3", {"class": "topcard__flavor-row"})
    span = h3[0].findAll("span")
    location = span[-1].text.strip()
    return location

def get_job_title(soup):
    h1 = soup.find("h1", {"class": "topcard__title"})
    return h1.get_text().strip()

def get_level(soup):
    item = soup.findAll("li", {"class": "job-criteria__item"})[0]
    span = item.findAll("span")[0]
    return span.getText().strip()

def clean(s):
    s = s.strip()
    s = s.lower()
    sc = []
    for x in s:
        if x in r:
            sc.append(x)
        else:
            sc.append(' ')
    s = ''.join(sc)
    s = re.sub('\s+', ' ', s).strip()
    return s

def get_words(soup):
    description = soup.find("section", {"class": "description"})
    li = description.find_all("li")
    text = []
    for item in li:
        tmp = item.get_text()
        tmp = clean(tmp)
        text.append(tmp)
    p = description.find_all("p")
    for item in p:
        tmp = item.get_text()
        tmp = clean(tmp)
        text.append(tmp)
    return ' '.join(text).split()

def find_skills(soup, skills):
    words = get_words(soup)
    skill_set = set()
    n = len(words)
    for s in skills:
        L = skills[s]
        match = True
        for skill in L:
            skill = skill.split()
            m = len(skill)
            for i in range(n - m + 1):
                # check match
                match = True
                for j in range(m):
                    if skill[j] != words[i + j]:
                        match = False
                        break
                if match:
                    skill_set.add(s)
                    break
    return skill_set

def load_skills():
    with open('skills.json', 'r') as f:
        return json.load(f)

def make_json(index, soup, skills, urls):
    title = get_job_title(soup)
    location = get_location(soup)
    level = get_level(soup)
    kw = find_skills(soup, skills)
    url = urls[index]
    country = url[8:].split('.')[0].upper()
    if country == 'WWW':
        country = 'US'
    continent = continent_map[country]        
    return {
        'index': int(index),
        'title': title,
        'location': location,
        'level': level,
        'skills': list(kw),
        'country': country,
        'continent': continent,
        'url': url
    }

def make_all():
    f = open('de_job_urls.txt')
    urls = [line.strip() for line in f.readlines()]
    f.close()
    skills = load_skills()
    for skill in skills:
        assert skill in skills[skill]
    all_data = []
    done = set()
    for fn in os.listdir('./json/'):
        index = int(fn.split('.')[0])
        done.add(index)
    count = 0
    for fn in os.listdir('./html/'):
        index = int(fn.split('.')[0])
        if index in done: continue
        percent = round(100 * (count + len(done)) / len(urls))
        print('{} / {}%'.format(fn, percent))
        soup = read_soup(fn)
        data = make_json(index, soup, skills, urls)
        with open('./json/{}.json'.format(index), mode='w', encoding='utf8') as f:
            f.write(json.dumps(data, indent=4))
        all_data.append(data)
        count += 1
    with open('de.json', mode='w', encoding='utf8') as f:
        f.write(json.dumps(all_data, indent=4))


def load_jobs():
    jobs = []
    for fn in os.listdir('./json/'):
        index = int(fn.split('.')[0])
        with open('./json/{}'.format(fn)) as f:
            data = json.load(f)
            if len(data['skills']) == 0: continue
            data['index'] = index
            jobs.append(data)
    return jobs

def analyze_skills(skills):
    jobs = load_jobs()
    for job in jobs:
        index = job['index']
        print(index)
        soup = read_soup('{}.html'.format(index))
        s = find_skills(soup, skills)
        for skill in job['skills']:
            s.add(skill)
        if len(s) != len(job['skills']):
            print('change')
            job['skills'] = list(s)
            with open('./json/{}.json'.format(index), mode='w', encoding='utf8') as f:
                f.write(json.dumps(job, indent=4))
        

if __name__ == '__main__':
    #make_all()
    #analyze_skills({
    #    'mahout': ['mahout'],
        'hawq': ['hawq'],
        'llap': ['llap'],
        'phoenix': ['phoenix']
    })
