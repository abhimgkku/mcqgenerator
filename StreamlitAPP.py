import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

#loading json file
with open('C:\Study\mcqgenerator\Response.json','r') as f:
    RESPONSE_JSON = json.load(f)
    
# Tile of the app
st.title("MCQ GENERATOR APPLICATION")

#Creating a form
with st.form("user_inputs"):
    # File Upload
    uploaded_file = st.file_uploader("Upload your PDF file")
    
    #Inputs Fields
    mcq_count = st.number_input("Enter number of MCQs you want to generate", min_value=3,max_value=50)
    
    #subject 
    subject = st.text_input("Insert Subject", max_chars=20)
    
    #Quiz Difficulty
    
    tone = st.text_input("Enter the difficulty level of the MCQs to be generated",max_chars=20,placeholder="Easy")
    
    #Add button
    button = st.form_submit_button("Create MCQs")
    
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Generating MCQs, kindly wait..."):
            try:
                text = read_file(uploaded_file)
                # Count tokens and cost of API calls
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain(
                        {
                            "text":text,
                            "number":mcq_count,
                            "subject":subject,
                            "tone":tone,
                            "response_json":json.dumps(RESPONSE_JSON),
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e),e, e.__traceback__)
                st.error("Error")
            else:
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"Completion Tokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                
                #Extract the quiz data from the response
                if isinstance(response,dict):
                    quiz = response.get("quiz",None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1 
                            st.table(df)
                            # Display the review in the text box
                            st.text_area(label="Review",value=response['Review'])
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response)
                    
                    
    