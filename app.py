from functions.dbpedia import (
    next_person_ontology_question,
    next_character_ontology_question,
    get_predicate_object,
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

    answer_mapping = {
        "-": None,
        "Yes": True,
        "No": False,
        "I don't know": None,
    }
    default_answer_options = answer_mapping.keys()
    question, assertions, df, row = ' ', [], None, None

    start_algorithm = False
    if first_question == 'Fictional character':
        st.write('So, you are thinking of a Fictional character...')

        next_question = True
        while next_question:
            next_question = False
            question, assertions, df, row = next_character_ontology_question(
                assertions, df, row)
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
                    start_algorithm = True
                    break

    elif first_question == 'Real-world person':
        st.write("So, you are thinking of a Real-world person...")

        next_question = True
        while next_question:
            next_question = False
            question, assertions, df, row = next_person_ontology_question(
                assertions, df, row)
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
                    start_algorithm = True
                    break

    algorithm_next_question = True
    index = 0
    if start_algorithm:
        while algorithm_next_question:
            algorithm_next_question = False
            base_kind = "dbo:Person"
            if first_question == "Fictional Character":
                base_kind = "dbo:FictionalCharacter"

            question, assertions = get_predicate_object(base_kind,
                                                        assertions, index=index)
            if len(question) > 0:
                try:
                    answer = st.radio(
                        label=question,
                        options=default_answer_options,
                    )
                    answer_bool = answer_mapping.get(answer)
                    assertions = save_answer(answer_bool, assertions)

                    if answer_bool:
                        index = 0
                    elif not answer_bool:
                        index = 0
                    elif not isinstance(answer_bool, bool):
                        index += 1

                    if answer != '-':
                        algorithm_next_question = True
                except DuplicateWidgetID:
                    break

    if len(assertions) > 0:

        st.sidebar.write(str(assertions))
        st.text("")
        if st.button("Guess now!"):
            base_kind = {
                "Fictional character": "dbo:FictionalCharacter",
                "Real-world person": "dbo:Person",
            }
            question, guesses = make_guess(
                assertions, base_kind=base_kind.get(first_question))
            guess = st.radio(question, ("-", "Yes", "No"))
            if guess == "Yes":
                st.success("Yaaaaay! :tada:")
                if st.button("Let's play again!"):
                    st.experimental_rerun()
            elif guess == "No":
                st.text("That was the best we could do, these were our top guesses:")
                st.write(guesses)
                if st.button("Another round?"):
                    st.experimental_rerun()


if __name__ == "__main__":
    # command to run the app: streamlit run app.py
    app()
