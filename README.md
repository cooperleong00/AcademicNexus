# AcademicNexus

**AcademicNexus** aims to build an intelligent academic search engine leveraging GPT-3.5-turbo. Our initial focus is on Arxiv, a popular repository for academic papers, due to its accessible API and easy-to-parse search results format.


## Features
* Keyword extraction: GPT-3.5-turbo processes the title and abstract of the user-provided paper and extracts relevant keywords.
* Arxiv search: The extracted keywords are used to search for related papers on Arxiv.
* Paper ranking: GPT-3.5-turbo ranks the search results based on their titles and relevance to the user's query.
* Summary generation: The top-ranked papers' abstracts are processed, and GPT-3.5-turbo generates a summary highlighting the relationships between the user's query paper and the related papers.

## Getting Started


1. Create virtual environment.
```
conda create -n academic_nexus python=3.10
```

2. Clone the repository and install dependency.
```
git clone git@github.com:prismleong/AcademicNexus.git
cd AcademicNexus
pip install -r requirements.txt
```

3. Paste your openai api key in main.py
```
# fill in your openai api key
openai.api_key = "sk-..."
```

4. Run the application:
```
streamlit run main.py
```

5. paste the arxiv id and click search!