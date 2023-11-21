"""
This module is used to build a Question Generator using Streamlit.
It generates questions based on selected parameters and allows the user to download the data in CSV or JSON format.
Author: Saahil Mehta (saahil.mehta8520@gmail.com)
"""

import pandas as pd
import streamlit as st
from lookup_dicts import domain_descriptions,stakeholder_descriptions, metrics_descriptions, question_type_descriptions

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    """Function to handle click event of the 'Generate Questions' button."""
    st.session_state.clicked = True

@st.cache_data
def convert_df(df):
    """
    Converts a DataFrame to CSV and encodes it in utf-8 format.
    
    Args:
        df (pd.DataFrame): The DataFrame to convert.
        
    Returns:
        The encoded CSV data.
    """
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

@st.cache_data
def convert_df_to_json(df):
    """
    Converts a DataFrame to JSON and encodes it in utf-8 format.
    
    Args:
        df (pd.DataFrame): The DataFrame to convert.
        
    Returns:
        The encoded JSON data.
    """
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_json().encode('utf-8')

@st.cache_data
def load_data():
    """
    Load data from a CSV file and strips white spaces from all columns.
    
    Returns:
        pd.DataFrame: The loaded data.
    """
    db = pd.read_csv("mainDB.csv")
    # Strip whitespaces from all columns
    db = db.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return db

@st.cache_data
def generate_questions(data, timeline, stakeholders, metrics, domains, questiontype):
    """
    Generates questions by filtering data based on selected parameters.
    
    Args:
        data (pd.DataFrame): The DataFrame containing all questions.
        timeline (int): The selected timeline.
        stakeholders (list): The selected stakeholders.
        metrics (list): The selected metrics.
        domains (list): The selected domains.
        questiontype (list): The selected question types.
        
    Returns:
        pd.DataFrame: The DataFrame containing generated questions.
    """
    questions_df = data

    # Filter the questions based on the selected parameters
    filtered_questions_df = questions_df[(questions_df['Domain'].isin(domains)) &
                                         (questions_df['Stakeholder'].isin(stakeholders))&
                                         (questions_df['Metric Area'].isin(metrics)) &
                                         (questions_df['Question Type'].isin(questiontype))
                                         ]

    # Get the list of filtered questions
    # questions = filtered_questions_df['Question'].tolist()

    data_df = pd.DataFrame({
        "row_number" : range(0, len(filtered_questions_df)),
        "questions": filtered_questions_df['Question'],
        "relevant?": [False] * len(filtered_questions_df),
        "domain": filtered_questions_df['Domain'],
        "timeline (in months)": [timeline] * len(filtered_questions_df),
        "stakeholders": filtered_questions_df['Stakeholder'],
        "metrics": filtered_questions_df['Metric Area'],
        "options" : filtered_questions_df["Answer Options"]
    })
    

    return data_df

def generate_personal_questions():

    file_path = 'personalDB.csv'
    personal_questions_df = pd.read_csv(file_path)

    return personal_questions_df


def get_domain(db):
    """
    Get the unique domain values from the database and create a multiselect widget for domain selection.
    
    Args:
        db (pd.DataFrame): The DataFrame containing all data.
        
    Returns:
        list: The list of selected domains.
    """
    domainValues = db["Domain"].str.strip()
    domains = domainValues.unique()
    domain = st.multiselect("Domains", domains, placeholder="Click for options, select max 3.",max_selections=3)
    for dom in domain:
        st.caption("_"+dom+": "+domain_descriptions[dom]+"_")  # Display the description for the selected domain
    return domain

def get_timeline(db):
    """
    Create a slider widget for timeline selection.
    
    Args:
        db (pd.DataFrame): The DataFrame containing all data.
        
    Returns:
        int: The selected timeline.
    """
    selected_timeline = st.slider("Months", 3, 60, 3, step=1)
    return selected_timeline

def get_stakeholders(db, domains):
    """
    Get the unique stakeholder values based on selected domains and create a multiselect widget for stakeholder selection.
    
    Args:
        db (pd.DataFrame): The DataFrame containing all data.
        domains (list): The list of selected domains.
        
    Returns:
        list: The list of selected stakeholders.
    """
    #if domains:
    #    stakeValues = db.loc[db['Domain'].isin(domains), 'Stakeholder'].str.strip()
    #else:
    #    stakeValues = db['Stakeholder'].str.strip()
    stakeValues = db['Stakeholder'].str.strip()
        
    stakeholders = stakeValues.unique()
    selected_stakeholders = st.multiselect("Stakeholder selection", stakeholders, placeholder="Click for options. Please note this is based on 'Domain' selection.")
    for stakeholder in selected_stakeholders:
        st.caption("_"+stakeholder+": "+stakeholder_descriptions[stakeholder]+"_")  # Display the description for the selected stakeholders
    return selected_stakeholders
    
def get_metrics(db,stakeholders):
    """
    Get the unique metric values based on selected stakeholders and create a multiselect widget for metric selection.
    
    Args:
        db (pd.DataFrame): The DataFrame containing all data.
        stakeholders (list): The list of selected stakeholders.
        
    Returns:
        list: The list of selected metrics.
    """
    if stakeholders:
        metricValues = db.loc[db['Stakeholder'].isin(stakeholders), 'Metric Area'].str.strip()
    else:
        metricValues = db['Metric Area'].str.strip()

    metrics = metricValues.unique()
    selected_metrics = st.multiselect("Likely Metrics to Measure", metrics, placeholder="Click for options.Please note this is based on 'Stakeholder' selection.")
    for metric in selected_metrics:
        st.caption("_"+metric+": "+metrics_descriptions[metric]+"_")
    return selected_metrics

def get_types(db,metrics):
    """
    Get the unique question type values based on selected metrics and create a multiselect widget for question type selection.
    
    Args:
        db (pd.DataFrame): The DataFrame containing all data.
        metrics (list): The list of selected metrics.
        
    Returns:
        list: The list of selected question types.
    """
    if metrics:
        qt = db.loc[db['Metric Area'].isin(metrics), 'Question Type'].str.strip()
    else:
        qt = db['Question Type'].str.strip()

    qtValues = qt.unique()
    selected_types = st.multiselect("Types of Questions Needed (NOTE: by default, ALL types are selected)", qtValues, placeholder="Click for options.", default = qtValues)
    for ques in selected_types:
        st.caption("_"+ques+": "+question_type_descriptions[ques]+"_")
    return selected_types

def main():
    """
    The main function to run the application.
    """
    st.image("Fathom-logo_With-text-1200x500px.png", use_column_width=True)
    "---"
    st.markdown("<h1 style='text-align: center;'>Question Generator</h1>", unsafe_allow_html=True)

    db = load_data()
    "---"
    st.header("Domain Selector")
    st.caption("Select the domain (or the closest possible option(s)) you want to generate questions for.")
    domain = get_domain(db)
    
    # if st.button('Confirm Domain Selection'):
    #     st.session_state.domain = domain
    #     print(st.session_state.domain) 
    # if 'domain' in st.session_state:
    #     st.header("Timeline:")
    #     st.caption("Select the number of months for the timeline to generate questions based on the specified time frame.")
    #     timeline = get_timeline(db)
        
    #     st.header("Stakeholders")
    #     st.caption("Select the stakeholders you want to generate questions for, from the options below.")
    #     stakeholders = get_stakeholders(db, st.session_state.domain)

    
    st.header("Timeline:")
    st.caption("Select the number of months for the timeline to generate questions based on the specified time frame.")
    timeline = get_timeline(db)
    
    st.header("Stakeholders")
    st.caption("Select the stakeholders you want to generate questions for, from the options below.")
    stakeholders = get_stakeholders(db, domains=domain)

    st.header("Metrics")
    st.caption("Select the metric you want to measure and generate questions for.")
    metrics = get_metrics(db, stakeholders=stakeholders)

    st.header("Question Types")
    st.caption("Select the desired types of questions you want to generate.")
    questions = get_types(db, metrics=metrics)


    st.button("Generate Questions",on_click=click_button)
    if st.session_state.clicked:
        # questions = generate_questions(data=db)
        data_df = generate_questions(data=db,timeline=timeline,domains=domain,stakeholders=stakeholders,metrics=metrics, questiontype=questions)

        final = st.data_editor(
            data_df,
            column_config={
            "relevant": st.column_config.CheckboxColumn(
            "Relevant?",
            default=False,
                )
            },
            # disabled=["widgets"],
            # hide_index=True,
        )

        include_personal_questions = st.checkbox('Would you like to download personal questions?')
        if include_personal_questions:
            # Assume that personal_questions_df is the DataFrame containing the personal questions.
            personal_questions_df = generate_personal_questions()  # Define this function to load personal questions
            st.write("Here are the included personal questions:")
            st.dataframe(personal_questions_df)
            
            personal_csv = convert_df(personal_questions_df)
            
            st.download_button(
                label="Download personal questions as CSV",
                data=personal_csv,
                file_name='personalQuestions.csv',
                mime='text/csv',
            )

        temp_data_df = data_df.copy()

            # Ask if the user wants to modify the data
        if st.checkbox('Would you like to modify the data before downloading?'):
            # Default row to modify is the first one (0)
            default_row_number = 0

            # Ask for the row number to modify, with default value
            row_number = st.number_input('Enter the row number you want to modify:', min_value=0, max_value=len(data_df) - 1, value=default_row_number, step=1)

            # Show the selected row
            st.write("You selected row:", row_number)
            st.table(temp_data_df.iloc[[row_number]])

            # Create a text area for the question column in the selected row
            user_input = st.text_area(f"Question:", temp_data_df.iloc[row_number]['questions'])
            
            # Update the temporary DataFrame with the user input
            temp_data_df.iloc[row_number, temp_data_df.columns.get_loc('questions')] = user_input


        csv = convert_df(final)
        json = convert_df_to_json(final)
        modified_csv = convert_df(temp_data_df)
        
        col1, col2, col3 = st.columns(3, gap="large")
    
        with col1:
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='finalQuestions.csv',
                mime='text/csv',
                )
        with col2:
            st.download_button(
                label="Download modified data as CSV (only if modified)",
                data=modified_csv,
                file_name='finalQuestionsModified.csv',
                mime='text/csv',
                )
        with col3:
            st.download_button(
                label="Download data as JSON",
                data=json,
                file_name='finalQuestions.json',
                mime='application/json',
                )

if __name__ == "__main__":
    
    main()

"---"
"==="
st.text("Built by Saahil using Streamlit version: "+st.__version__)
