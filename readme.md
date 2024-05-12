# Secure Coding

Tiny Shopping Mall Website.


## requirements

miniconda가 설치되어 있지 않다면 아래 url로 설치를 진행합니다.
https://docs.anaconda.com/free/miniconda/index.html

```
conda create -n secure_coding python=3.9
conda activate secure_coding
pip install streamlit
pip install fastapi uvicorn
pip import pandas
```
기존의 내용에 import pandas가 추가되었습니다.

## usage

run the front and backend processes.

```
streamlit run streamlit_app.py
uvicorn fastapi_app:app --reload
```

if you want to test on external machine, you can utilize the ngrok to forwarding the url.
```
# optional
ngrok http 8501
```