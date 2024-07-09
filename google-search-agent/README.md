# Google Search Agent
The most imporant file in this directory is `search_agent.py`, which contains 2 classes: `SearchAgent` and `SearchSelectAgent`

`SearchAgent` always performs a google search no matter what

`SearchSelectAgent` decides whether or not to perform a google search or not (and is more advanced, it can perform mulitple google searches, as it iteratively decides whether or not it has enough information).

Unlike most of the other directories in this project, this directory requires an initial setup since it involves calling the Google Search API. 


`search-prototyping.ipnyb` is a notebook file where you can play around with the search agent.

## Google Programmable Search Engine API
To perform google searches, we use Google Cloud's Programmable Search Engine API. Here is a link to google's guide: https://developers.google.com/custom-search/v1/overview

### 1) Create a programmable search engine
You can create one at this link: https://programmablesearchengine.google.com/controlpanel/all

You can choose any name you want. However, make sure to choose `Search the entire web`. You can leave `image search` and `safe search` off. Then, hit create.

After creating, go to the `Overview` tab and copy the `Search engine ID`

### 2) Create a .env file
Create a .env file in this directory. This file will store the environment variables. First, add an environment variable called `SEARCH_ENGINE_ID` and assign it to the search engine ID you copied from above.

### 3) Get your Google Cloud API key
If you haven't already, go to https://cloud.google.com/ and create an account. Once you have created an account, you can go to the `Console`. There, you can create a new project, and title it whatever you want.

After, go to your dashboard, then go to `APIs and Services`. Then, go to `Credentials` and create a new API key. Add this API Key to the `.env` file, and name it `GOOGLE_CLOUD_API_KEY`

Your .env file should like like this:
```
GOOGLE_CLOUD_API_KEY=<YOUR_API_KEY>
SEARCH_ENGINE_ID=<YOUR_SEARCH_ENGINE_ID>
```

### 4) Enalbe the Custom Search API in Google Cloud
Go to https://console.cloud.google.com/apis/library/customsearch.googleapis.com and enable to custom search api. After enabling, you should be good to go, and you can now run the code.
