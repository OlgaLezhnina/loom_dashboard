from dict_hash import Hashable
from cache_decorator import Cache
import json
import requests
# from .timing import Timer, timing
# TODO throw away papers without ABOUT (field) or call then unspecified?
# TODO typos in fields?


class Paper(Hashable):
    def __init__(self):
        self.folder_name = ""
        # the unique name of the folder for the paper
        self.resources = []
        # files belonging to the paper
        self._ro_crate = None
        # json with important information
        # RO for research objects

    def _get_ro_crate(self):
        if self._ro_crate is None:
            self._ro_crate = self._find_ro_crate()
        return self._ro_crate
    ro_crate = property(_get_ro_crate)

    def _find_ro_crate(self):
        ro_resource = next(
            (dct for dct in self.resources if dct["name"] == "ro-crate-metadata.json"),
            None)
        ro_url = ro_resource["url"]
        ro_json = requests.get(ro_url).text
        ro_crate = json.loads(ro_json)["@graph"]
        return ro_crate

    def get_field_names(self):
        field_names = set()
        root = list(
            filter(lambda element: element['@id'] == './', self.ro_crate))[0]
        self.root = root
        if "about" in root:
            field_names |= set(root["about"])
            self.field_names = field_names
        return field_names

    def get_record_name(self):
        return self.root["name"]

    def get_publication_url(self):
        url_list = []
        for element in self.root["isBasedOn"]:
            url_list.append(element["@id"])
        return url_list

    def get_code_url(self):
        code_url = {}
        for resource in self.resources:
            if ".py" in resource["name"] or ".R" in resource["name"]:
                code_url[resource["name"]] = resource["url"]
        return code_url

    def get_data_url(self):
        data_url = {}
        for resource in self.resources:
            if ".csv" in resource["name"]:
                data_url[resource["name"]] = resource["url"]
        return data_url

    def count_statements(self):
        statements_info = list(
            filter(lambda element: element['@type'] == ['Statement'], self.ro_crate))
        count = len(statements_info)
        # count_dict = dict.fromkeys(self.field_names, count)
        return count

    def get_authors(self):
        author_list = []
        author_info = list(
            filter(lambda element: element['@type'] == 'Person', self.ro_crate))
        for element in author_info:
            author_name = element.get('name', None)
            author_list.append(author_name)
        return author_list

    def count_languages(self):
        count = {"Python": 0, "R": 0}
        files_info = list(filter(lambda element: element['@type'] ==
                                 ['File', 'SoftwareSourceCode'], self.ro_crate))
        for file in files_info:
            if ".py" in file['@id']:
                count["Python"] += 1
            elif ".R" in file['@id']:
                count["R"] += 1
        return count

    def count_csv(self):
        count = 0
        files_info = list(filter(lambda element: element['@type'] ==
                                 ['File'], self.ro_crate))
        for file in files_info:
            if ".csv" in file['@id']:
                count += 1
        return count

    @Cache(validity_duration="1d")
    def count_methods(self):
        schemata_names = ["dp", "ds", "ae", "ma", "ca", "gc", "ra", "cp", "cd", "fa"]
        schemata_ids = ["37182ecfb4474942e255", "5b66cb584b974b186f37",
                        "5e782e67e70d0b2a022a", "c6b413ba96ba477b5dca",
                        "3f64a93eef69d721518f", "b9335ce2c99ed87735a6",
                        "286991b26f02d58ee490", "6e3e29ce3ba5a0b9abfe",
                        "c6e19df3b52ab8d855a9", "437807f8d1a81b5138a3"]
        schemata_dict = dict(zip(schemata_names, schemata_ids))
        methods_count = dict.fromkeys(schemata_names, 0)
        for resource in self.resources:
            if ".json" in resource["name"] and "ro-crate-metadata" not in resource["name"]:
                this_json = requests.get(resource["url"]).text
                for key, value in schemata_dict.items():
                    if "doi:" + value in this_json:
                        methods_count[key] += 1

        return methods_count

    def consistent_hash(self):
        return self.folder_name


def find_papers():
    API_Base_URL = "https://service.tib.eu/ldmservice/api/3/action/"
    API_URL = API_Base_URL + "package_search"
    params = {"fq": "tags:reborn", "rows": 999}
    try:
        response = requests.get(API_URL, params=params)
    except requests.exceptions.RequestException as e:
        print("ERROR ACCESSING API: ", API_URL, e.__str__())
    search_result = response.json().get('result')
    folders_1 = search_result["results"]
    folders_2 = [d for d in folders_1 if d.get("notes") != '']
    folders_3 = [d for d in folders_2 if d.get("notes").split()[1][:-1].startswith("https")]
    papers = {}
    for folder in folders_3:
        folder_name = folder["title"][:-2]
        if folder_name in papers:
            papers[folder_name].resources += folder["resources"]
        else:
            paper = Paper()
            paper.resources = folder["resources"]
            paper.folder_name = folder_name
            papers[folder_name] = paper
    return papers


class Summary():
    def __init__(self, papers):
        self.papers = papers
        # folders/papers and their resources
        self._all_field_names = None
        self._get_all_field_names()
        # unique names of fields
        self.pp_count = self.count_field_papers()
        # number of papers per field
        self.st_count = self.count_field_statements()
        # number of statements per field
        self.au_count = self.count_field_authors()
        # number of authors per field
        self.lang_count = self.count_field_languages()
        # number of languages (Python and R) per field
        self.csv_count = self.count_field_csv()
        # number of csv files per field
        self._method_count = None
        self._get_method_count()
        # number of methods per field
        self.final_info = self.collect_url_info()
        # loom record names, paper dois, methods used, data and code urls to download

    def _get_all_field_names(self):
        if self._all_field_names is None:
            all_field_set = set()
            for paper in self.papers.values():
                all_field_set |= paper.get_field_names()
            all_field_names = sorted(all_field_set)
            all_field_names.append("Overall")
            self._all_field_names = all_field_names
        return self._all_field_names
    all_field_names = property(_get_all_field_names)

    def count_field_papers(self):
        papers_dict = dict.fromkeys(self.all_field_names, 0)
        for paper in self.papers.values():
            field_names = paper.get_field_names()
            for name in field_names:
                papers_dict[name] += 1
        papers_dict['Overall'] = len(papers)
        return papers_dict

    def count_field_statements(self):
        statements_dict = dict.fromkeys(self.all_field_names, 0)
        overall_count = 0
        for paper in self.papers.values():
            statements_each = paper.count_statements()
            overall_count += statements_each
            field_names = paper.get_field_names()
            for name in field_names:
                statements_dict[name] += statements_each
        statements_dict['Overall'] = overall_count
        return statements_dict

    def count_field_authors(self):
        authors_dict = {x: set() for x in self.all_field_names}
        for paper in self.papers.values():
            field_names = paper.get_field_names()
            for name in field_names:
                authors_dict[name] |= set(paper.get_authors())
        overall_set = set()
        for key, value in authors_dict.items():
            overall_set |= value
            authors_dict[key] = len(value)
        authors_dict['Overall'] = len(overall_set)
        return authors_dict

    def count_field_languages(self):
        languages_dict = {x: {"Python": 0, "R": 0} for x in self.all_field_names}
        overall_count = {"Python": 0, "R": 0}
        for paper in self.papers.values():
            languages_each = paper.count_languages()
            overall_count = {lang: overall_count[lang] +
                             languages_each[lang] for lang in languages_each}
            field_names = paper.get_field_names()
            for name in field_names:
                languages_dict[name] = {lang: languages_dict[name][lang] +
                                        languages_each[lang] for lang in languages_each}
        languages_dict['Overall'] = overall_count
        return languages_dict

    def count_field_csv(self):
        csv_dict = dict.fromkeys(self.all_field_names, 0)
        for paper in self.papers.values():
            field_names = paper.get_field_names()
            csv_each = paper.count_csv()
            for name in field_names:
                csv_dict[name] += csv_each
        csv_dict['Overall'] = sum(csv_dict.values())
        return csv_dict

    def _get_method_count(self):
        if self._method_count is None:
            self._method_count = self._count_field_methods()
        return self._method_count
    method_count = property(_get_method_count)

    def _count_field_methods(self):
        schemata_names = ["dp", "ds", "ae", "ma", "ca", "gc", "ra", "cp", "cd", "fa"]  # line 81
        methods_dict = {x: dict.fromkeys(schemata_names, 0) for x in self.all_field_names}
        overall_count = dict.fromkeys(schemata_names, 0)
        for paper in self.papers.values():
            methods_each = paper.count_methods()
            overall_count = {meth: overall_count[meth] +
                             methods_each[meth] for meth in methods_each}
            field_names = paper.get_field_names()
            for name in field_names:
                methods_dict[name] = {meth: methods_dict[name][meth] +
                                      methods_each[meth] for meth in methods_each}
        methods_dict['Overall'] = overall_count
        return methods_dict

    def collect_url_info(self):
        final_dict = {x: [] for x in self.all_field_names}
        for paper in self.papers.values():
            methods_count = paper.count_methods()
            methods_list = [key for key, value in methods_count.items() if value >= 1]
            paper_info = [paper.get_record_name(),
                          methods_list,
                          paper.get_publication_url(),
                          paper.get_code_url(),
                          paper.get_data_url()]
            field_names = paper.get_field_names()
            for name in field_names:
                final_dict[name] += [paper_info]
        # overall is show all undiff
        return final_dict


# with timing("get_data"):
papers = find_papers()
summary = Summary(papers)
