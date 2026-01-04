from contextlib import contextmanager
import os
import sys
from cache_decorator import Cache
import time
import requests
import json
# start
API_Base_URL = "https://service.tib.eu/ldmservice/api/3/action/"
API_URL = API_Base_URL + "package_search"
print("API URL is: ", API_URL)
print("Method: GET")
params = {"fq": "tags:reborn", "rows": 999}
try:
    response = requests.get(API_URL, params=params)
except requests.exceptions.RequestException as e:
    print("ERROR ACCESSING API: ", API_URL, e.__str__())
search_result = response.json().get('result')
folders_1 = search_result["results"]
folders_2 = [d for d in folders_1 if d.get("notes") != '']
folders_3 = [d for d in folders_2 if d.get("notes").split()[1][:-1].startswith("https")]


def find_papers(folders):
    papers = {}
    for folder in folders:
        folder_name = folder["title"][:-2]
        if folder_name in papers:
            papers[folder_name] += folder["resources"]
        else:
            papers[folder_name] = folder["resources"]
    return papers


papers2 = find_papers(folders_3)
ro_resource = next(
    (dct for dct in papers2["ceballos-2023-1"] if dct["name"] == "ro-crate-metadata.json"),
    None)
if ro_resource is None:
    print("wow")


def find_methods(papers):
    methods_dct = {}
    for paper, resources in papers.items():
        methods_count = {"ds": 0, "gc": 0}
        for resource in resources:
            if ".json" in resource["name"] and "ro-crate-metadata" not in resource["name"]:
                this_json = requests.get(resource["url"]).text
                if "doi:5b66cb584b974b186f37" in this_json:
                    methods_count["ds"] += 1
                if "doi:b9335ce2c99ed87735a6" in this_json:
                    methods_count["gc"] += 1
        methods_dct[paper] = methods_count
    return methods_dct


wtf = find_methods(papers)


def count_field_papers(ro_data):
    papers_dict = {}
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            for name in root["about"]:
                if name in papers_dict:
                    papers_dict[name] += 1
                else:
                    papers_dict[name] = 1
    papers_dict['Overall'] = len(ro_data)
    return papers_dict


def count_all_statements(ro_data):
    count = 0
    for ro in ro_data:
        statements_info = list(
            filter(lambda element: element['@type'] == ['Statement'], ro))
        count = count + len(statements_info)
    return count


def find_ro_crates(papers):
    ro_crates = []
    for paper, resources in papers.items():
        ro_resource = next(
            (dct for dct in resources if dct["name"] == "ro-crate-metadata.json"),
            None)
        ro_url = ro_resource["url"]
        ro_json = requests.get(ro_url).text
        ro_py = json.loads(ro_json)["@graph"]
        ro_crates.append(ro_py)
    return ro_crates


def count_name_statements(ro_data, field_name):
    count = 0
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            if field_name in root["about"]:
                statements_info = list(
                    filter(lambda element: element['@type'] == ['Statement'], ro))
            else:
                statements_info = []
            count = count + len(statements_info)
    return count


def count_field_statements(ro_data):
    field_names = get_all_field_names(papers)
    statements_dict = {}
    for name in field_names:
        count = count_name_statements(ro_data, name)
        statements_dict[name] = count
    statements_dict['Overall'] = sum(statements_dict.values())
    return statements_dict


def count_all_authors(ro_data):
    aut_list = []
    for ro in ro_data:
        aut_info = list(
            filter(lambda element: element['@type'] == 'Person', ro))
        for element in aut_info:
            author_name = element.get('name', None)
            if author_name not in aut_list and author_name is not None:
                aut_list.append(author_name)
    return len(aut_list)


def count_name_authors(ro_data, field_name):
    aut_list = []
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            if field_name in root["about"]:
                aut_info = list(
                    filter(lambda element: element['@type'] == 'Person', ro))
                for element in aut_info:
                    author_name = element.get('name', None)
                    if author_name not in aut_list and author_name is not None:
                        aut_list.append(author_name)
    return len(aut_list)


def count_all_csv(ro_data):
    count = 0
    for ro in ro_data:
        files_info = list(filter(lambda element: element['@type'] ==
                                 ['File'], ro))
        for file in files_info:
            if ".csv" in file['@id']:
                count += 1
    return count


def count_name_csv(ro_data, field_name):
    count = 0
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            if field_name in root["about"]:
                files_info = list(filter(lambda element: element['@type'] ==
                                         ['File'], ro))
                for file in files_info:
                    if ".csv" in file['@id']:
                        count += 1
            else:
                files_info = []
    return count


def count_all_lang(ro_data):
    count = {"Python": 0, "R": 0}
    for ro in ro_data:
        files_info = list(filter(lambda element: element['@type'] ==
                                 ['File', 'SoftwareSourceCode'], ro))
        for file in files_info:
            if ".py" in file['@id']:
                count["Python"] += 1
            elif ".R" in file['@id']:
                count["R"] += 1
    return count


def count_name_lang(ro_data, field_name):
    count = {"Python": 0, "R": 0}
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            if field_name in root["about"]:
                files_info = list(filter(lambda element: element['@type'] ==
                                         ['File', 'SoftwareSourceCode'], ro))
                for file in files_info:
                    if ".py" in file['@id']:
                        count["Python"] += 1
                    elif ".R" in file['@id']:
                        count["R"] += 1
            else:
                files_info = []
    return count


a = {"b": 0, "c": 1}

d = {"b": 2, "c": 3}

dct = {"w1": a, "w2": 0}
dct = {x: d[x] + a[x] for x in d}
dct
dct["w1"] += d.values()
for keys in dct:


def find_all_ro_crates(papers):
    ro_crates = []
    for paper in papers.values():
        ro_py = paper.find_ro_crate()
        ro_crates.append(ro_py)
    return ro_crates


class Calculator():
    def add(self, a, b):
        summ = a+b
        return summ


def wtf(a):
    print(a)


wtf(3, 4)

wtf = Calculator()
wtf2 = wtf.add(1, 2)
wtf2

ro_crates = find_ro_crates(papers)


text_requests = 0
dict_update = 0
time_all = 0


def hc_fun():
    return 42


class C:
    def __init__(self):
        self._x = None
        self._y = None

    def getx(self):
        if self._x is None:
            self._x = hc_fun()
        print("Hello from getter!")
        return self._x

    def gety(self):
        if self._y is None:
            self._y = self.x
        print("Hello from getter!")
        return self._y

    x = property(getx)
    y = property(gety)


wtf = C()

wtf.y
wtf.x = 1
wtf.x
wtf._x

schemata_names = ["dp", "ds", "ae", "ma", "ca", "gc", "ra", "cp", "cd", "fa"]
schemata_ids = ["37182ecfb4474942e255", "5b66cb584b974b186f37",
                "5e782e67e70d0b2a022a", "c6b413ba96ba477b5dca",
                "3f64a93eef69d721518f", "b9335ce2c99ed87735a6",
                "286991b26f02d58ee490", "6e3e29ce3ba5a0b9abfe",
                "c6e19df3b52ab8d855a9", "437807f8d1a81b5138a3"]
schemata_dict = dict(zip(schemata_names, schemata_ids))
methods_count = dict.fromkeys(schemata_names, 0)

this_json = "wtf, doi:37182ecfb4474942e255"


for key, value in schemata_dict.items():
    if "doi:" + value in this_json:
        methods_count[key] += 1


@Cache(validity_duration="1d")
def cached_requests_get_text(url):
    return requests.get(url).text


def find_jsons(papers):
    global text_requests, dict_update, time_all
    t0 = time.perf_counter()
    jsons = []
    for paper, resources in papers.items():
        jsons_paper = {}
        for resource in resources:
            if ".json" in resource["name"]:
                if resource["name"] not in jsons_paper:
                    t1 = time.perf_counter()
                    this_json = cached_requests_get_text(resource["url"])
                    t2 = time.perf_counter()
                    jsons_paper.update({resource["name"]: this_json})
                    t3 = time.perf_counter()
                    text_requests += t2-t1
                    dict_update += t3-t2
        jsons.append({paper: jsons_paper})
    time_all = time.perf_counter() - t0
    return jsons


jsons = find_jsons(papers)  # 257 about 100 in thiessen

text_requests
dict_update
time_all


# 5b66cb584b974b186f37 descriptive statistics
# b9335ce2c99ed87735a6 group comparison
print(jsons[1]["mcrae-2023-1"]["8hl6avb5.json"])
wtf = jsons[1]["mcrae-2023-1"]["8hl6avb5.json"]
if "doi:feeb33ad3e4440682a4d" in wtf:
    print("wow")

# text_requests
# Out[41]: 70.83302150007148
# dict_update
# Out[42]: 0.0013614000090456102
# time_all
# Out[43]: 70.83589840000059

# text_requests
# Out[48]: 10.075651899973309
# dict_update
# Out[49]: 0.0009630000240576919
# time_all
# Out[50]: 10.077987399999984


sys.version


print(jsons[10]["gkatzelis-2021"]["8mmu5d8q.json"])  # example
example = jsons[10]["gkatzelis-2021"]["8mmu5d8q.json"]
wtf = json.loads(example)  # this is json turned back into py
example_ro = jsons[10]["gkatzelis-2021"]["ro-crate-metadata.json"]
wtf_ro = json.loads(example_ro)


def find_fields(ro_data):
    field_list = []
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            field_info = root["about"]
        else:
            field_info = ""
        field_list.append(field_info)
    return field_list


def count_field_papers(ro_data):
    papers_dict = {}
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            for name in root["about"]:
                if name in papers_dict:
                    papers_dict[name] += 1
                else:
                    papers_dict[name] = 1
    papers_dict['all'] = len(ro_data)
    return papers_dict


number_papers = count_field_papers(ro_crates)
number_papers


def get_field_names(ro_data):
    unique_names = []
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            for name in root["about"]:
                if name not in unique_names:
                    unique_names.append(name)
    return unique_names


def count_all_csv(ro_data):
    count = 0
    for ro in ro_data:
        files_info = list(filter(lambda element: element['@type'] ==
                                 ['File'], ro))
        for file in files_info:
            if ".csv" in file['@id']:
                count += 1
    return count


count_all_csv(ro_crates)  # counts files in Py/R not which paper in which


def count_name_csv(ro_data, field_name):
    count = 0
    for ro in ro_data:
        root = list(
            filter(lambda element: element['@id'] == './', ro))[0]
        if "about" in root:
            if field_name in root["about"]:
                files_info = list(filter(lambda element: element['@type'] ==
                                         ['File'], ro))
                for file in files_info:
                    if ".csv" in file['@id']:
                        count += 1
            else:
                files_info = []
    return count


count_name_csv(ro_crates, 'Oceanography')


def count_field_csv(ro_data):
    field_names = get_field_names(ro_data)
    csv_dict = {}
    for name in field_names:
        count = count_name_csv(ro_data, name)
        csv_dict[name] = count
    csv_dict['Overall'] = count_all_csv(ro_data)
    return csv_dict


count_field_csv(ro_crates)


def find_all_methods(ro_data):
    count = {"descriptive": 0, "group": 0}
    for ro in ro_data:
        files_info = list(filter(lambda element: element['@type'] ==
                                 ['File'], ro))
        for file in files_info:
            if ".json" in file['@id']:
                requests.get(resource["url"]).text
    return count


a = ("abc", "cdf")
a[1]
x, y = a
x
ro_crates[8]['@graph']
wtf = list(filter(lambda element: element['@id'] == './', ro_crates[8]))
wtf[0]["about"][0]
list(filter(lambda element: element['@type'] == ['ResearchField'], ro_crates[8]))
list(filter(lambda element: element['@type'] == ['Journal'], ro_crates[15]))
list(filter(lambda element: element['@type'] == ['ScholarlyArticle'], ro_crates[8]))
# lots of info not only the paper name! also year and abstract and what not
# how we get jsonld(s)? from ro_crates but no url:
list(filter(lambda element: element['@type'] == ['File'], ro_crates[8]))
# also from papers, in papers there are urls


class Timer:
    def __init__(self, name="timer"):
        self.name = name
        self.time = 0.0
        self._start_time = None

    def start(self):
        self._start_time = time.perf_counter()

    def stop(self):
        if self._start_time is None:
            return
        self.time += time.perf_counter() - self._start_time
        self._start_time = None

    def report(self):
        print(f"{self.name} took {self.time} seconds")

    def reset(self):
        self.time = 0.0
        self._start_time = None


@contextmanager
def timing(timer=None):
    instant_report = False
    if timer is None:
        timer = Timer()
        instant_report = True
    if isinstance(timer, str):
        timer = Timer(timer)
        instant_report = True
    try:
        timer.start()
        yield timer
    finally:
        timer.stop()
        if instant_report:
            timer.report()


with timing():
    print('gegege')


timer = Timer("code")

for x in range(5):
    with timing(timer):
        print('hahaha')

with timing(timer):
    for x in range(5):
        print('hehehe')

timer.start()
print('hohoho')
timer.stop()

timer.report()


st = set(["n", "a", "b"])
type(st)
st1 = sorted(st)
st1
type(st1)
st1.insert(len(st1), "d")
st1
# self.record_name = self.papers.get_recored_name()
# a Loom record name
# self.publication_url = self.papers.get_publication_url()
# url of a publication on which the record is based
# self.code_url = self.papers.get_code_url()
# urls of code files to download
# self.data_url = self.papers.get_data_url()
# urls of csv files to download
dct = {"a": [], "b": []}
l1 = [1, 2, 3]
l2 = [4, 5, 6]
dct["a"] += [l1]
dct["a"]
dct["a"] += [l2]
x = 123456
x % (x//10)
x % 100

wtf = {'@id': 'https://doi.org/10.1098/rspb.2023.2501'}
wtf["@id"]

li = ['ds', 'ma', 'gc', 'fa']
dct = {"dp": "Data Preprocessing",
       "ds": "Descriptive Statistics",
       "ae": "Algorithm Evaluation",
       "ma": "Multilevel Analysis",
       "ca": "Correlation Analysis",
       "gc": "Group Cmparison",
       "ra": "Regression Analysis",
       "cp": "Class Prediction",
       "cd": "Class Discovery",
       "fa": "Factor Analysis"}
new_names = [dct.get(name, name) for name in li]
