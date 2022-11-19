from functions.dbpedia import next_person_ontology_question, save_answer, get_predicate_object
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

    if first_question == 'Fictional character':
        st.write('So, you are thinking of a Fictional character...')
        is_human = st.radio(
            label="Is this fictional character an human being?",
            options=default_answer_options,
        )

        if is_human == 'Yes':
            is_woman = st.radio(
                label=f"Is this fictional character a woman?",
                options=default_answer_options,
            )

        elif is_human == 'No':
            is_humanoid = st.radio(
                label=f"Does this fictional character look like a human?",
                options=default_answer_options,
            )

    elif first_question == 'Real-world person':
        st.write("So, you are thinking of a Real-world person...")

        question, assertions, df, row = ' ', [], None, None
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
                    break

        algorithm_next_question = True
        where = ""
        filter = ""
        index = 0
        while algorithm_next_question:
            algorithm_next_question = False
            question, predicate, object = get_predicate_object(
                where_middle=where, filter=filter, index=index)
            if len(question) > 0:
                try:
                    answer = st.radio(
                        label=question,
                        options=default_answer_options,
                    )
                    answer_bool = answer_mapping.get(answer)

                    if answer_bool:
                        where += '?x <' + predicate + '> <' + object + '>.'
                        index = 0
                    elif not answer_bool:
                        filter = " FILTER NOT EXISTS(?x <" + \
                            predicate + "> <" + object + ">)."
                        index = 0
                    elif not isinstance(answer_bool, bool):
                        index += 1

                    if answer != '-':
                        algorithm_next_question = True
                except DuplicateWidgetID:
                    break

        st.sidebar.write(str(assertions))


if __name__ == "__main__":
    # command to run the app: streamlit run app.py
    app()
