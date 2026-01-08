# Loom Dahboard
**100% AI-free: we did not use any AI technologies in developing this
dashboard.**

The dashboard is an interactive presentation of information provided by the 
[TIB Knowledge Loom](https://knowledgeloom.tib.eu/pages/about), 
which is taking the related data from [Leibnitz Data Manager](https://service.tib.eu/ldmservice/about). 
The dashboard runs on [Flask](https://flask.palletsprojects.com/en/stable/) and uses 
the [unpoly](https://unpoly.com/) framework for enhancing HTML. 

The project can be easily reproduced:
* Download the repository
* Install [Python UV](https://docs.astral.sh/uv/)
* Run the code locally:
```sh
uv run flask --app loom run -p 8000
```
When starting the dashboard for the first time, please consider that refreshing the cache takes longer 
than in subsequent runs.  
