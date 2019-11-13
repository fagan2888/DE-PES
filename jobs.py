import json
import os
import pandas as pd
import csv

def load_jobs(path):
    if path == None: return []
    jobs = []
    for fn in os.listdir(path):
        index = int(fn.split('.')[0])
        with open('{}/{}'.format(path, fn)) as f:
            data = json.load(f)
            if len(data['skills']) == 0: continue
            data['index'] = index
            jobs.append(data)
    return jobs

def compute_skill_percents(skills, jobs):
    skill_percents = { s: 0 for s in skills }
    for s in skills:
        for job in jobs:
            if s in job['skills']:
                skill_percents[s] += 1
        skill_percents[s] /= len(jobs)
        skill_percents[s] = round(100 * skill_percents[s], 2)
    return skill_percents

def get_sorted_skills(skills, skill_percents):
    pairs = []
    for s in skills:
        pairs.append((skill_percents[s], s))
    pairs.sort(reverse=True)
    return [s for _, s in pairs]


#### APRIORI

####

class SkillSet:

    def __init__(self, skills, percent, support, max_index):
        self.skills = skills
        self.percent = percent
        self.support = support
        self.max_index = max_index

    def __lt__(self, other):
        return self.percent > other.percent

    def __eq__(self, other):
        return self.percent == other.percent

    def __str__(self):
        return str(self.skills)

class Jobs:

    def __init__(self, path="./json"):
        self.jobs = load_jobs(path)
        self.initialize_data(self.jobs)
    
    def initialize_data(self, jobs):
        # compute global skill percentages
        self.skills = set()
        for job in self.jobs:
            for s in job['skills']:
                self.skills.add(s)
        self.skills = list(self.skills)
        self.skills.sort()
        self.skill_percents = compute_skill_percents(self.skills, self.jobs)
        # compute jobs by continent
        self.jobs_by_continent = {}
        self.continents = set()
        for job in self.jobs:
            c = job['continent']
            self.continents.add(c)
            if not c in self.jobs_by_continent:
                self.jobs_by_continent[c] = []
            self.jobs_by_continent[c].append(job)
        self.continents = list(self.continents)
        self.continents.sort()
        # compute jobs by xp level
        self.jobs_by_level = {}
        self.levels = ['Internship', 'Entry level', 'Associate', 'Mid-Senior', 'Senior', 'Director', 'Executive', 'Not specified']
        for job in self.jobs:
            l = job['eng-level']
            if not l in self.jobs_by_level:
                self.jobs_by_level[l] = []
            self.jobs_by_level[l].append(job)
        # compute skills per continent
        self.skills_per_continent = {}
        for c in self.continents:
            self.skills_per_continent[c] = compute_skill_percents(self.skills, self.jobs_by_continent[c])
        # compute skills per level
        self.skills_per_level = {}
        for l in self.levels:
            self.skills_per_level[l] = compute_skill_percents(self.skills, self.jobs_by_level[l])
        self.sorted_skills = get_sorted_skills(self.skills, self.skill_percents)

    def get_skill_percents(self, jobs):
        return compute_skill_percents(self.skills, jobs)


    def frequent_skill_sets(self, threshold, max_size, verbose=False):
        threshold /= 100.0
        # compute supports
        support = { skill: set() for skill in self.skills }
        for skill in self.skills:
            for job in self.jobs:
                if skill in job['skills']:
                    support[skill].add(job['index'])
        # compute frequent skill sets of size one
        fs = {}
        fs[1] = []
        for i, skill in enumerate(self.skills):
            freq = len(support[skill]) / len(self.jobs)
            if freq >= threshold:
                fs[1].append(SkillSet([skill], 100 * freq, support[skill], i))
        # compute frequent skill sets of larget size
        for size in range(2, max_size + 1):
            if len(fs[size - 1]) == 0: break
            if(verbose): print('computing size {}. previous set size {}'.format(size, len(fs[size - 1])))
            fs[size] = []
            for skill_set in fs[size - 1]:
                for i in range(skill_set.max_index + 1, len(self.skills)):
                    skill = self.skills[i]
                    sup = skill_set.support.intersection(support[skill])
                    freq = len(sup) / len(self.jobs)
                    if freq >= threshold:
                        fs[size].append(SkillSet(skill_set.skills + [skill], 100 * freq, sup, i))
        return fs

    def frequent_skill_sets2(self, threshold, max_size, skills, verbose=False):
        threshold /= 100.0
        # compute supports
        support = { skill: set() for skill in skills }
        for skill in skills:
            for job in self.jobs:
                if skill in job['skills']:
                    support[skill].add(job['index'])
        # compute frequent skill sets of size one
        fs = {}
        fs[1] = []
        for i, skill in enumerate(skills):
            freq = len(support[skill]) / len(self.jobs)
            if freq >= threshold:
                fs[1].append(SkillSet([skill], 100 * freq, support[skill], i))
        # compute frequent skill sets of larget size
        for size in range(2, max_size + 1):
            if len(fs[size - 1]) == 0: break
            if(verbose): print('computing size {}. previous set size {}'.format(size, len(fs[size - 1])))
            fs[size] = []
            for skill_set in fs[size - 1]:
                for i in range(skill_set.max_index + 1, len(skills)):
                    skill = skills[i]
                    sup = skill_set.support.intersection(support[skill])
                    freq = len(sup) / len(self.jobs)
                    if freq >= threshold:
                        fs[size].append(SkillSet(skill_set.skills + [skill], 100 * freq, sup, i))
        return fs

    def skill_sets_to_csv(self, skill_sets, filename, include_indexes=False):
        rows = [ ]
        for size in skill_sets:
            skill_sets[size].sort()
            for s in skill_sets[size]:
                s.skills.sort()
                indexes = list(s.support)
                indexes.sort()
                row = [size, round(s.percent, 2)] + s.skills
                if include_indexes:
                    row += indexes
                rows.append(row)
        with open('csv/{}.csv'.format(filename), mode='w') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

    def get_jobs_that_contain_one_of(self, skills):
        ret = []
        for job in self.jobs:
            ok = False
            for s in skills:
                if s in job['skills']:
                    ok = True
                    break
            if ok:
                ret.append(job)
        return ret
    
    def get_level_distribution(self, jobs):
        job_dist = {}
        for job in jobs:
            level = job['eng-level']
            if level in job_dist:
                job_dist[level] = 0
            job_dist[level] += 1
        return job_dist

    def percentage_jobs_that_contain_at_lest_one(self, skills):
        return 100 * len(self.get_jobs_that_contain_one_of(skills)) / len(self.jobs)

    def get_skill_continent_rankings(self, skill):
        ranks = {}
        for c in self.continents:
            sorted_skills_c = get_sorted_skills(self.skills, self.skills_per_continent[c])
            rank = sorted_skills_c.index(skill) + 1
            ranks[c] = rank
        ranks['Global'] = self.sorted_skills.index(skill) + 1
        return ranks

    def get_skill_continent_rankings_df(self, skill):
        ranks = self.get_skill_continent_rankings(skill)
        tmp = self.continents + ['Global']
        data = { skill: [ranks[c] for c in tmp] }
        return pd.DataFrame.from_dict(data, orient='index', columns=tmp)

    def get_skills_continent_rankings_df(self, skills):
        data = {}
        for skill in skills:
            ranks = self.get_skill_continent_rankings(skill)
            tmp = self.continents + ['Global']
            data[skill] = [ranks[c] for c in tmp]
        return pd.DataFrame.from_dict(data, orient='index', columns=tmp)
    

    def get_skill_level_rankings(self, skill):
        ranks = {}
        for l in self.levels:
            sorted_skills_l = get_sorted_skills(self.skills, self.skills_per_level[l])
            rank = sorted_skills_l.index(skill) + 1
            ranks[l] = rank
        return ranks

    def get_skill_level_rankings_df(self, skill):
        ranks = self.get_skill_level_rankings(skill)
        data = { skill: [ranks[l] for l in self.levels] }
        return pd.DataFrame.from_dict(data, orient='index', columns=self.levels)

    def get_skills_level_rankings_df(self, skills):
        data = {}
        for skill in skills:
            ranks = self.get_skill_level_rankings(skill)
            data[skill] = [ranks[l] for l in self.levels]
        return pd.DataFrame.from_dict(data, orient='index', columns=self.levels)


    def get_num_jobs_per_continent(self):
        return { c: len(self.jobs_by_continent[c]) for c in self.continents }
      
    def get_num_jobs_per_continent_df(self):
        return pd.DataFrame.from_dict(self.get_num_jobs_per_continent(), orient='index')

    def get_num_jobs_per_level(self):
        return { l: len(self.jobs_by_level[l]) for l in self.levels }

    def get_num_jobs_per_level_df(self):
        return pd.DataFrame.from_dict(self.get_num_jobs_per_level(), orient='index')

    def format_percent(self, value):
        return '{0:.2f}%'.format(value)

    def get_skill_percents_by_continent(self, skill):
        data = { c: self.skills_per_continent[c][skill] for c in self.continents }
        data['Global'] = self.skill_percents[skill]
        return data

    def get_skill_percents_by_continent_df(self, skill):
        percents = self.get_skill_percents_by_continent(skill)
        tmp = self.continents + ['Global']
        data = { skill: [percents[c] for c in tmp] }
        return pd.DataFrame.from_dict(data, orient='index', columns=tmp)

    def get_skills_percents_by_continent_df(self, skills):
        data = {}
        for skill in skills:
            percents = self.get_skill_percents_by_continent(skill)
            tmp = self.continents + ['Global']
            data[skill] = [percents[c] for c in tmp]
        return pd.DataFrame.from_dict(data, orient='index', columns=tmp)
    
    def get_skill_percents_by_level(self, skill):
        return { l: self.skills_per_level[l][skill] for l in self.levels }

    def get_skill_percents_by_level_df(self, skill):
        percents = self.get_skill_percents_by_level(skill)
        data = { skill: [percents[l] for l in self.levels] }
        return pd.DataFrame.from_dict(data, orient='index', columns=self.levels)
    
    def get_skills_percents_by_level_df(self, skills):
        data = {}
        for skill in skills:
            percents = self.get_skill_percents_by_level(skill)
            data[skill] = [percents[l] for l in self.levels]
            data[skill].append(self.skill_percents[skill])
        cols = self.levels + ['Global']
        return pd.DataFrame.from_dict(data, orient='index', columns=cols)


    def get_skills_ranked_by_continent_df(self):
        data = {}
        sorted_skills = {}
        for c in self.continents:
            sorted_skills[c] = get_sorted_skills(self.skills, self.skills_per_continent[c])
        cols = self.continents + ['Global']
        sorted_skills['Global'] = get_sorted_skills(self.skills, self.skill_percents)
        for i in range(len(self.skills)):
            data[i + 1] = []
            for l in cols:
                data[i + 1].append(sorted_skills[l][i])
        return pd.DataFrame.from_dict(data, orient='index', columns=cols)

    def get_skills_ranked_by_level_df(self):
        data = {}
        sorted_skills = {}
        for l in self.levels:
            sorted_skills[l] = get_sorted_skills(self.skills, self.skills_per_level[l])
        cols = self.levels + ['Global']
        sorted_skills['Global'] = get_sorted_skills(self.skills, self.skill_percents)
        for i in range(len(self.skills)):
            data[i + 1] = []
            for l in cols:
                data[i + 1].append(sorted_skills[l][i])
        return pd.DataFrame.from_dict(data, orient='index', columns=cols)


    def get_skill_maximum_rank(self):
        data = {}
        for skill in self.skills:
            max_rank = -1
            for l in self.levels:
                sorted_skills = get_sorted_skills(self.skills, self.skills_per_level[l])
                rank = sorted_skills.index(skill) + 1
                max_rank = max(max_rank, rank)
            data[skill] = [max_rank, self.skill_percents[skill]]
        return pd.DataFrame.from_dict(data, orient='index', columns=['Maximum rank', 'Global %'])
    
    def get_skill_minimum_rank(self):
        data = {}
        for skill in self.skills:
            min_rank = float('inf')
            for l in self.levels:
                sorted_skills = get_sorted_skills(self.skills, self.skills_per_level[l])
                rank = sorted_skills.index(skill) + 1
                min_rank = min(min_rank, rank)
            data[skill] = min_rank
        return pd.DataFrame.from_dict(data, orient='index', columns=['Minimum rank'])
    
    def aggregate_jobs_from_levels(self, levels):
        jobs = []
        for l in self.levels:
            jobs += self.jobs_by_level[l]
        return jobs


    def get_level_percentage_deltas(self):
        deltas = []
        for i, l in enumerate(self.levels):
            if i == 0: continue
            delta = [ 0 ] * len(self.skills)
            j = 0
            for s in self.skills:
                delta[j] = float(self.skills_per_level[l][s]) - float(self.skills_per_level[self.levels[i - 1]][s])
                j += 1
            deltas.append(delta)
        return deltas

    def get_level_percentage_max_deltas(self):
        max_deltas = {}
        for s in self.skills:
            tmp = []
            for l in self.levels:
                tmp.append(self.skills_per_level[l][s])
            tmp.sort()
            max_deltas[s] =tmp[-1] - tmp[0]
        return pd.DataFrame.from_dict(max_deltas, orient='index', columns=['Maximum delta %'])

    def format(self, value_list):
        for i, v in enumerate(value_list):
            if type(v) is float:
                 value_list[i] = self.format_percent(v)
        return value_list
