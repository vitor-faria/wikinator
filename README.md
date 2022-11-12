## Wikinator - Streamlit KG Application 

Simple streamlit application inspired on the webgame Akinator, 
that uses Wikipedia's infoboxes data to guess which fictional character 
or real-world person the user is thinking of, using Yes/No questions that 
are translated into SPARQL queries.

## Development Environment

To create the development environment it's recommended to use conda.

Run the following commands to get the environment ready

```
conda create -n ENVIRONMENT_NAME python=3.8
conda activate ENVIRONMENT_NAME
pip install -r requirements.txt
```

#### Running Locally

To run the streamlit application in your local host use

```
streamlit run app.py
```

## Application URL

Production: https://kg-wikinator.herokuapp.com/
