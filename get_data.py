from dict_hash import Hashable
from cache_decorator import Cache
import json
import requests


class LoomRecord(Hashable):
    """
    A class for a single Loom record based on a research article
    """

    def __init__(self):
        # the unique name of the folder for the record/article
        self.folder_name = ""
        # files which belong to the record/article
        self.resources = []
        # ro-crate metadata json
        self._ro_crate = None

    def _get_ro_crate(self):
        """
        A getter method for the ro-crate metadata

        :return: the ro-crate metadata as a Python object
        """
        if self._ro_crate is None:
            self._ro_crate = self._find_ro_crate()
        return self._ro_crate
    ro_crate = property(_get_ro_crate)

    def _find_ro_crate(self):
        """
        Extract the ro-crate metadata from resources

        :return: the ro-crate metadata as a Python object
        """
        ro_resource = next(
            (dct for dct in self.resources if dct["name"] == "ro-crate-metadata.json"),
            None)
        ro_url = ro_resource["url"]
        ro_json = requests.get(ro_url).text
        ro_crate = json.loads(ro_json)["@graph"]
        return ro_crate

    def get_field_names(self):
        """
        Obtain the names of research domains to which the record belongs

        :return: the set of domain names
        """
        field_names = set()
        root = list(
            filter(lambda element: element['@id'] == './', self.ro_crate))[0]
        self.root = root
        if "about" in root:
            field_names |= set(root["about"])
            self.field_names = field_names
        return field_names

    def get_record_name(self):
        """
        Obtain the record name

        :return: the record name as a string
        """
        return self.root["name"]

    def get_publication_url(self):
        """
        Obtain the url(s) of the research article

        :return: the list of urls, most frequently with a single element
        """
        url_list = []
        for element in self.root["isBasedOn"]:
            url_list.append(element["@id"])
        return url_list

    def get_code_url(self):
        """
        Obtain the names and urls of code files

        :return: the dictionary with code files names as keys and urls as values
        """
        code_url = {}
        for resource in self.resources:
            if ".py" in resource["name"] or ".R" in resource["name"]:
                code_url[resource["name"]] = resource["url"]
        return code_url

    def get_data_url(self):
        """
        Obtain the names and urls of data files

        :return: a dictionary with data files names as keys and urls as values
        """
        data_url = {}
        for resource in self.resources:
            if ".csv" in resource["name"]:
                data_url[resource["name"]] = resource["url"]
        return data_url

    def count_statements(self):
        """
        Count the number of statements in the record

        :return: the number of statements as integer
        """
        statements_info = list(
            filter(lambda element: element['@type'] == ['Statement'], self.ro_crate))
        count = len(statements_info)
        return count

    def get_authors(self):
        """
        Obtain the names of the research article authors

        :return: the list of authors names
        """
        author_list = []
        author_info = list(
            filter(lambda element: element['@type'] == 'Person', self.ro_crate))
        for element in author_info:
            author_name = element.get('name', None)
            author_list.append(author_name)
        return author_list

    def count_languages(self):
        """
        Count the number of files in Python and R languages

        :return: a dictionary with Python and R as keys and numbers of files as values
        """
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
        """
        Count the number of .csv files in the record

        :return: the number of .csv files as integer
        """
        count = 0
        files_info = list(filter(lambda element: element['@type'] ==
                                 ['File'], self.ro_crate))
        for file in files_info:
            if ".csv" in file['@id']:
                count += 1
        return count

    @Cache(validity_duration="1d")
    def count_methods(self):
        """
        Count and cache the number of schemata used in the record

        :return: a dictionary with abbreviated names of schemata as keys and their counts as values
        """
        schemata_names = ["dp", "ds", "ae", "ma", "ca", "gc", "ra", "cp", "cd", "fa"]
        # schemata ids from https://knowledgeloom.tib.eu/pages/help
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
        """
        Hash function for the record
        Since records have unique folder names, we just use that

        :return: hash string
        """
        return self.folder_name


def find_loom_records():
    """
    Extract Loom records which are based on research articles from LDM

    :return: a dictionary with folder names as keys and lists of resources(files) as values
    """
    API_Base_URL = "https://service.tib.eu/ldmservice/api/3/action/"
    API_URL = API_Base_URL + "package_search"
    params = {"fq": "tags:reborn", "rows": 999}
    try:
        response = requests.get(API_URL, params=params)
    except requests.exceptions.RequestException as e:
        print("ERROR ACCESSING API: ", API_URL, e.__str__())
    search_result = response.json().get('result')
    folders_1 = search_result["results"]
    # select folders related to research articles (with a url in "notes/IsSupplementTo")
    folders_2 = [d for d in folders_1 if d.get("notes") != '']
    folders_3 = [d for d in folders_2 if d.get("notes").split()[1][:-1].startswith("https")]
    records = {}
    for folder in folders_3:
        folder_name = folder["title"][:-2]
        # if two folders are related to one article, merge them:
        if folder_name in records:
            records[folder_name].resources += folder["resources"]
        else:
            record = LoomRecord()
            record.resources = folder["resources"]
            ro_resource = next(
                (dct for dct in record.resources if dct["name"] == "ro-crate-metadata.json"),
                None)
            if ro_resource is not None:  # exclude the ones without ro-crate metadata
                record.folder_name = folder_name
                records[folder_name] = record
    return records


class Summary():
    """
    A class for summarised information on all available Loom records based on research articles
    """

    def __init__(self, records):
        # dictionary of loom records
        self.records = records
        # unique names of research domains to which the records belong
        self._all_field_names = None
        self._get_all_field_names()
        # number of articles per domain
        self.pp_count = self.count_field_articles()
        # number of statements per domain
        self.st_count = self.count_field_statements()
        # number of authors per domain
        self.au_count = self.count_field_authors()
        # number of Python and R files per domain
        self.lang_count = self.count_field_languages()
        # number of csv files per domain
        self.csv_count = self.count_field_csv()
        # number of specific schemata per domain
        self._method_count = None
        self._get_method_count()
        # record names, articles dois, data urls, code urls, and schemata used; per domain
        self.final_info = self.collect_final_info()

    def _get_all_field_names(self):
        """
        A getter method for obtaining unique domain names

        :return: a set of domain names
        """
        if self._all_field_names is None:
            all_field_set = set()
            for record in self.records.values():
                all_field_set |= record.get_field_names()
            all_field_names = sorted(all_field_set)
            all_field_names.append("Overall")
            self._all_field_names = all_field_names
        return self._all_field_names
    all_field_names = property(_get_all_field_names)

    def count_field_articles(self):
        """
        Count the number of research articles per domain

        :return: a dictionary with domain names as keys
        and research articles counts as values
        """
        articles_dict = dict.fromkeys(self.all_field_names, 0)
        for record in self.records.values():
            field_names = record.get_field_names()
            for name in field_names:
                articles_dict[name] += 1
        articles_dict['Overall'] = len(self.records)
        return articles_dict

    def count_field_statements(self):
        """
        Count the number of statements per domain

        :return: a dictionary with domain names as keys
        and statements counts as values
        """
        statements_dict = dict.fromkeys(self.all_field_names, 0)
        overall_count = 0
        for record in self.records.values():
            statements_each = record.count_statements()
            overall_count += statements_each
            field_names = record.get_field_names()
            for name in field_names:
                statements_dict[name] += statements_each
        statements_dict['Overall'] = overall_count
        return statements_dict

    def count_field_authors(self):
        """
        Count the number of authors per domain

        :return: a dictionary with domain names as keys
        and authors counts as values
        """
        authors_dict = {x: set() for x in self.all_field_names}
        for record in self.records.values():
            field_names = record.get_field_names()
            for name in field_names:
                authors_dict[name] |= set(record.get_authors())
        overall_set = set()
        for key, value in authors_dict.items():
            overall_set |= value
            authors_dict[key] = len(value)
        authors_dict['Overall'] = len(overall_set)
        return authors_dict

    def count_field_languages(self):
        """
        Count the number of files in Python and R languages per domain

        :return: a dictionary with domain names as keys
        and dictionaries with Python and R files counts as values
        """
        languages_dict = {x: {"Python": 0, "R": 0} for x in self.all_field_names}
        overall_count = {"Python": 0, "R": 0}
        for record in self.records.values():
            languages_each = record.count_languages()
            overall_count = {lang: overall_count[lang] +
                             languages_each[lang] for lang in languages_each}
            field_names = record.get_field_names()
            for name in field_names:
                languages_dict[name] = {lang: languages_dict[name][lang] +
                                        languages_each[lang] for lang in languages_each}
        languages_dict['Overall'] = overall_count
        return languages_dict

    def count_field_csv(self):
        """
        Count the number of .csv files per domain

        :return: a dictionary with domain names as keys
        and .csv files counts as values
        """
        csv_dict = dict.fromkeys(self.all_field_names, 0)
        overall_count = 0
        for record in self.records.values():
            field_names = record.get_field_names()
            csv_each = record.count_csv()
            overall_count += csv_each
            for name in field_names:
                csv_dict[name] += csv_each
        csv_dict['Overall'] = overall_count
        return csv_dict

    def _get_method_count(self):
        """
        A getter method for the schmata count per domain

        :return: a dictionary with domain names as keys
        and dictionaries with schemata counts as values
        """
        if self._method_count is None:
            self._method_count = self._count_field_methods()
        return self._method_count
    method_count = property(_get_method_count)

    def _count_field_methods(self):
        """
        Count the number of different schemata per domain

        :return: a dictionary with domain names as keys
        and dictionaries with schemata counts as values
        """
        schemata_names = ["dp", "ds", "ae", "ma", "ca", "gc", "ra", "cp", "cd", "fa"]
        methods_dict = {x: dict.fromkeys(schemata_names, 0) for x in self.all_field_names}
        overall_count = dict.fromkeys(schemata_names, 0)
        for record in self.records.values():
            methods_each = record.count_methods()
            overall_count = {meth: overall_count[meth] +
                             methods_each[meth] for meth in methods_each}
            field_names = record.get_field_names()
            for name in field_names:
                methods_dict[name] = {meth: methods_dict[name][meth] +
                                      methods_each[meth] for meth in methods_each}
        methods_dict['Overall'] = overall_count
        return methods_dict

    def collect_final_info(self):
        """
        Collect detailed information on records

        :return: a dictionary with domain names as keys and lists with record information as values,
        where a record information list includes the record name, respective article doi,
        names and urls of related code and data files, and names of schemata used in the record
        """
        final_dict = {x: [] for x in self.all_field_names}
        schemata_dct = {
            "dp": "Data Preprocessing",
            "ds": "Descriptive Statistics",
            "ae": "Algorithm Evaluation",
            "ma": "Multilevel Analysis",
            "ca": "Correlation Analysis",
            "gc": "Group Comparison",
            "ra": "Regression Analysis",
            "cp": "Class Prediction",
            "cd": "Class Discovery",
            "fa": "Factor Analysis"
        }
        for record in self.records.values():
            methods_count = record.count_methods()
            methods_list_abbreviated = [key for key, value in methods_count.items() if value >= 1]
            methods_list = [schemata_dct.get(name, name) for name in methods_list_abbreviated]
            record_info = [
                record.get_record_name(),
                record.get_publication_url(),
                record.get_data_url(),
                record.get_code_url(),
                methods_list,
            ]

            field_names = record.get_field_names()
            for name in field_names:
                final_dict[name] += [record_info]
        return final_dict


records = find_loom_records()
summary = Summary(records)
