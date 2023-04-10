import arxiv
import requests
import bs4
import os.path as osp

import streamlit as st
import openai
# fill in your openai api key
openai.api_key = ""


keyword_extraction_prompt = \
"""Given the title and abstract of an academic paper below, please identify and extract the most crucial and innovative keywords that represent the core focus of the research. Keep in mind that the purpose of extracting these keywords is to further search for related literature, so avoid providing the most widely used keywords in the research field. Instead, focus on the unique aspects and innovations presented in this paper:

Title: "{title}"
Abstract: "{abstract}"

Provide a python list of the most important keywords as following format: ["keyword1", "keyword2", "keyword3"], the number of keywords should not exceed 3."""

title_ranking_prompt = \
"""Rank the relevance of a set of candidate article titles to a given academic paper. Consider the title and abstract of the paper, as well as the titles of the candidate articles, and arrange the candidate titles in order from most to least relevant. Your model should be able to identify key concepts and themes in the paper and candidate titles, and use them to determine the degree of relevance.

Here is the given paper:
Given Title: "{title}"
Given Abstract: "{abstract}"

Here are the candidate titles:
{titles}

Provide a python list of the candidate titles in order from most to least relevant, as following format: ["title1", "title2", "title3", "title4", "title5"], the number of titles should be 5, you should filter out those unrelevant ones and should not contain the given title.
"""


insight_prompt = \
"""Given several articles with title and abstract:

{related_content}

You should provide a comprehensive analysis of these articles in four parts and in the following markdown format:
"
### Overview
Summarize the main ideas and findings presented in the main article and related articles in a concise and short manner. 

### Commonalities
Identify the common themes or research methods shared among these articles.

### Innovations
Discuss the innovative aspects of each articles in comparison to each other.

### Research trends
Based on the information provided, speculate on the future research trends, challenges or opportunities in this field.
"
Make sure to use specific information from the article titles and abstracts to support your analysis, and reference the articles in the analysis using corresponding [number] appropriately.

"""


def get_chatgpt_response(prompt, **kwargs):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.25, top_p=0.95, **kwargs)
    return completion.choices[0]['message']['content']

def get_chatgpt_response_stream(prompt, **kwargs):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0.25, top_p=0.95, stream=True, **kwargs)
    for chunk in response:
        yield chunk['choices'][0]['delta'].get('content', "")


def main():
    st.title("Academic Nexus")
    input_id = st.text_input("input arxiv id", "2203.02155")
    if st.button("Search"):
        search = arxiv.Search(id_list=[input_id])
        paper = next(search.results())
        # paper ->  title, summary
        title = paper.title
        abstract = paper.summary.replace("\n", " ")

        st.write(f"## Query Title: {title}")
        st.write(f"*Query Abstract:* {abstract}")

        prompt = keyword_extraction_prompt.format(title=title, abstract=abstract)
        print("keyword extraction prompt "+""*80)
        print(prompt)
        print("-"*100)
        print("")

        with st.spinner("Extracting keywords..."):
            keywords = get_chatgpt_response(prompt)


        print("keywords "+""*80)
        print(keywords)
        print("-"*100)
        print("")
        keywords = eval(keywords)

        st.write(f"*Keywords:* {', '.join(keywords)}")
        st.write("-"*100)

        #keywords = ["InstructGPT", "fine-tuning", "human feedback"]

        query = r"%20".join([k.replace(" ", "+") for k in keywords])
        result_ids = []
        with st.spinner("Searching related papers..."):
            for start in [0, 10]:
                resp = requests.get(f"https://search.arxiv.org/?in=&query={query}&startat={start}", verify=False)
                soup = bs4.BeautifulSoup(resp.text, "html.parser")
                ids = [osp.basename(a.text) for a in soup.find_all('a', class_='url')]
                ids = [id for id in ids if id != input_id]
                result_ids.extend(ids)

            result_search = arxiv.Search(id_list=result_ids)
        result_infos = [(paper.title, paper.summary.replace("\n", " ")) for paper in result_search.results()]
        result_titles = [i[0] for i in result_infos]
        result_abstracts = [i[1] for i in result_infos]
        prompt = title_ranking_prompt.format(title=title, abstract=abstract, titles=result_titles)
        print("title ranking prompt "+"-"*80)
        print(prompt)
        print("-"*100)
        print("")
        ranked_titles = get_chatgpt_response(prompt)
        print(ranked_titles)
        ranked_titles = eval(ranked_titles)
        ranked_ids = [result_ids[result_titles.index(t)] for t in ranked_titles]
        ranked_abstracts = [result_abstracts[result_titles.index(t)] for t in ranked_titles]

        ranked_titles = [title] + ranked_titles
        ranked_ids = [input_id] + ranked_ids
        ranked_abstracts = [abstract] + ranked_abstracts
        related_content = ""
        for i, (t, u, a) in enumerate(zip(ranked_titles, ranked_ids, ranked_abstracts)):
            related_content += f"[{i+1}] Title: {t}\n[{i+1}] Abstract: {a}\n\n"
        prompt = insight_prompt.format(related_content=related_content)

        print("insight prompt "+"-"*80)
        print(prompt)
        print("-"*100)
        print("")

        print("insight summary "+"-"*80)
        st.write("## Insight Summary")
        insight_area = st.empty()
        insight = ""
        for delta in get_chatgpt_response_stream(prompt):
            insight += delta
            print(delta, sep="", end="")
            insight_area.markdown(insight, unsafe_allow_html=True)

        st.write("### Reference")
        st.write(related_content)

        print("\n"+"-"*80)


if __name__ == "__main__":
    main()