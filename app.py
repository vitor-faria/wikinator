from functions.dbpedia import next_person_ontology_question, next_character_ontology_question, save_answer
import streamlit as st
from streamlit.errors import DuplicateWidgetID


def app():
    st.sidebar.title("Wikinator")
    
    # Streamlit cheat sheet: https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py
    st.sidebar.subheader("Let me guess who you are thinking of!")
    first_question = st.sidebar.selectbox(
        label="Is it a fictional character or a real-world person?",
        options=('Select', 'Fictional character', 'Real-world person'),
    )

    answer_mapping = {
        "-": None,
        "Yes": True,
        "No": False,
        "I don't know": None,
    }
    default_answer_options = answer_mapping.keys()
    question, assertions, df, row = ' ', [], None, None

    if first_question == 'Fictional character':
        st.write('So, you are thinking of a Fictional character...')

        next_question = True
        while next_question:
            next_question = False
            question, assertions, df, row = next_character_ontology_question(assertions, df, row)
            if len(question) > 0:
                try:
                    answer = st.radio(
                        label=question,
                        options=default_answer_options,
                    )
                    answer_bool = answer_mapping.get(answer)
                    assertions = save_answer(answer_bool, assertions)
                    if answer != '-':
                        next_question = True
                except DuplicateWidgetID:
                    break

    elif first_question == 'Real-world person':
        st.write("So, you are thinking of a Real-world person...")

        next_question = True
        while next_question:
            next_question = False
            question, assertions, df, row = next_person_ontology_question(assertions, df, row)
            if len(question) > 0:
                try:
                    answer = st.radio(
                        label=question,
                        options=default_answer_options,
                    )
                    answer_bool = answer_mapping.get(answer)
                    assertions = save_answer(answer_bool, assertions)
                    if answer != '-':
                        next_question = True
                except DuplicateWidgetID:
                    break

    if len(assertions) > 0:
        st.sidebar.write(str(assertions))


if __name__ == "__main__":
    # command to run the app: streamlit run app.py
    app()
