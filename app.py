import pandas as pd
import streamlit as st


def app():
    st.sidebar.title("Wikinator")
    
    # Streamlit cheat sheet: https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py
    st.sidebar.subheader("Let me guess who you are thinking of!")
    first_question = st.radio(
        "Is it a fictional character or a real-world person?",
        ('Fictional character', 'Real-world person')
    )

    if first_question == 'Fictional character':
        st.write('You selected Fictional character.')
    elif first_question == 'Real-world person':
        st.write("You selected Real-world person.")


if __name__ == "__main__":
    # command to run the app: streamlit run app.py
    app()
