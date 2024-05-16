# Follow these steps to install


## Step 1. create virtual env to start clean

either with conda 
1. `conda create -n chatbot-playground python==3.11` 
2. `conda activate chatbot-playground`

or with venv

1. `python3 -m venv chatbot-playground`
2. `source chatbot-playground/bin/activate`


## Step 2. install package

`pip install -r requirements.txt`

## Step 3. export keys 

`export OPENAI_API_KEY=sk-proj-...`
`export LANGCHAIN_API_KEY=lsv2_`

## Step 4. run it!
`chainlit run app.py -w`


