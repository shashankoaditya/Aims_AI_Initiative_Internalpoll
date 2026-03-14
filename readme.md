# Mentimeter Lite (Streamlit)

A lightweight live polling application built using Streamlit.

## Features

* Presenter landing page with QR code
* Participant join lobby
* Live participant counter
* Start poll button
* Participants can answer once
* Real-time results with bar chart
* Multiple questions supported

## Files

app.py
Main Streamlit application.

questions.json
Contains poll questions and answer options.

responses.csv
Stores participant responses.

participants.csv
Stores participant join records.

state.json
Stores poll state (started / current question).

requirements.txt
Python dependencies for deployment.

## Running Locally

pip install -r requirements.txt
streamlit run app.py

## Participant Link

Participants join using:

?mode=participant

Example:

https://your-app-url/?mode=participant
