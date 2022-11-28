from functions.dbpedia import (
    next_person_ontology_question,
    next_character_ontology_question,
    next_predicate_question,
    save_answer,
    make_guess
)
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
    base_kind_map = {
        "Fictional character": "dbo:FictionalCharacter",
        "Real-world person": "dbo:Person",
    }
    base_kind = base_kind_map.get(first_question)

    answer_mapping = {
        "-": None,
        "Yes": True,
        "No": False,
        "I don't know": None,
    }
    default_answer_options = answer_mapping.keys()
    question, assertions, df, row = ' ', [], None, None

    start_predicate_questions = False
    if first_question == 'Fictional character':
        st.write('So, you are thinking of a Fictional character...')

        next_question = True
        while next_question:
            next_question = False
            question, assertions, df, row = next_character_ontology_question(
                assertions, df, row)
            if len(question) > 1:
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
                    start_predicate_questions = True
                    break

    elif first_question == 'Real-world person':
        st.write("So, you are thinking of a Real-world person...")

        next_question = True
        while next_question:
            next_question = False
            question, assertions, df, row = next_person_ontology_question(
                assertions, df, row)
            if len(question) > 1:

                answer = st.radio(
                    label=question,
                    options=default_answer_options,
                )
                answer_bool = answer_mapping.get(answer)
                assertions = save_answer(answer_bool, assertions)
                if answer != '-':
                    next_question = True
            if question == '':
                start_predicate_questions = True
                break

    if start_predicate_questions:
        more_predicate_questions = True
        assertions = [assertion for assertion in assertions if isinstance(assertion, tuple)]
        question, df, row = ' ', None, None
        while more_predicate_questions:
            more_predicate_questions = False
            question, assertions, df, row = next_predicate_question(
                assertions, base_kind, df, row
            )
            if len(question) > 1:
                try:
                    answer = st.radio(
                        label=question,
                        options=default_answer_options,
                    )
                    answer_bool = answer_mapping.get(answer)
                    assertions = save_answer(answer_bool, assertions)

                    if answer != '-':
                        more_predicate_questions = True
                except DuplicateWidgetID:
                    break

    if len(assertions) > 0:

        st.sidebar.write(str(assertions))
        st.text("")
        if st.checkbox("Guess now!", False):
            base_kind = {
                "Fictional character": "dbo:FictionalCharacter",
                "Real-world person": "dbo:Person",
            }
            question, guesses = make_guess(
                assertions, base_kind=base_kind.get(first_question))
            guess = st.radio(question, ("-", "Yes", "No"))
            if guess == "Yes":
                st.success("Yaaaaay! :tada:")

            elif guess == "No":
                st.text("That was the best we could do, these were our top guesses:")
                st.write(guesses)


if __name__ == "__main__":
    # command to run the app: streamlit run app.py
    app()
