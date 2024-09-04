from typing import Optional

from fastapi import FastAPI

app = FastAPI()

import openai
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Response
from pydantic import BaseModel
import json
from fastapi.middleware.cors import CORSMiddleware

origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


load_dotenv()


openai.api_key = os.getenv("openai_api_key")

client = OpenAI(
    api_key = os.getenv("openai_api_key"),
)

class RequestData(BaseModel):
    user_query: str


# user_query = r'{"round1":382,  "round2":300,  "round3":250,  "round4":200,  "round5":150,  "round6":450,  "round7":550, } generate me insightful chart for given data'
@app.post("/query_response")
def query_response(request_data:RequestData):
    user_query = request_data.user_query

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": r"""You are a coding bot. you will answer all the coding questions with appropriate responses.\
            # Critical Instructions:\
            - choose the appropriate graph very carefully. Analyse data multiple times and choose only the graph that gets highest score in evaluation\
            - Do not generate line graph if data is too fluctuating and not giving meaningful line. If points are too far away or random then generate Scatter chart\
            - for data like this format [{x:x1,y:y1,z:z1},{x:x2,y:y2,z:z2},{x:x3,y:y3,z:z3},{x:x4,y:y4,z:z4}] change lables like "x","y","z" if all 3 are numerical\
            - for data like this format [{x:x1,y:y1,z:z1},{x:x2,y:y2,z:z2},{x:x3,y:y3,z:z3},{x:x4,y:y4,z:z4}] change lables like "x","y","z". if there are 2 numerical among given x,y,z data and one categorical data then keep numeric data labels as x and y. for categorical value make/change label as z {x:numerical,y:numerical,z:categorical}. Create Scatter chart for this case with category\
            - for this kind of data [{x:x1,y:y1,z:z1},{x:x2,y:y2,z:z2},{x:x3,y:y3,z:z3},{x:x4,y:y4,z:z4}] generate Bubble chart if all x,y and z are numerical. \
            - If user give any sign data like '$,%' etc then it should show in the chart accordingly with labels\
            - If percentage data is passed in y-values, then format the y-axis as percentage using this yaxis.labels.formatter function
                yaxis: {labels: {formatter: function(value) {return value + '%'}}}\
            - Generate the apexcharts series in xy format as below
                series=[{data: [{x: {x-value},y: {y-value}}]}]\
            - if a pie, donut or radialbar chart is required, then use the below format
                series=[array of y-values]
                labels=[array of string labels]\
            -  Give only pure code when any code/program/programmimg language question is asked. \
            - When any chart specific question is asked make sure you generate code using APEXCHARTS.js library\
            - send full html source code. include APEX chart is must if visualization question\
            - Do not sent any programming language name in the begininning of the output\
            - Do not include ``` in the begininning and the end\
            - generate response in following format in Json {"code":"code generated" , "explanation":"this must contain the explanation"}\
            - generate more technical, detailed, precised explanation\
            - explain user for the choosing the graph and logic behind it\
            - at least generate 150 words explanation in following format : - Logic behind choice of graph (expain why it is most suitable graph for given data/problem) - explanation and facts about that graph - explain given data as well (summarize data for user in statistical way)  """},
            {"role": "user", "content": user_query}]
    )
    response = json.loads(response.choices[0].message.content)
    soup = BeautifulSoup(response["code"], 'html.parser')
    response["code"] = str(soup)
    # print(html_string)

    return response
    


