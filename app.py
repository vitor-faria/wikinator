import pandas as pd
import streamlit as st


def app():
    st.sidebar.title("Wikinator")
    
    # Streamlit cheat sheet: https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py
    st.sidebar.subheader("Let me guess who you are thinking of!")
    first_question = st.sidebar.selectbox(
        label="Is it a fictional character or a real-world person?",
        options=('Select', 'Fictional character', 'Real-world person'),
    )

    default_answer_options = ("-", "Yes", "No", "I don't know")

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
        is_woman = st.radio(
            label="Is this person a woman?",
            options=default_answer_options,
        )
        is_alive = st.radio(
            label="Is this person alive?",
            options=default_answer_options,
        )


if __name__ == "__main__":
    # command to run the app: streamlit run app.py
    app()
