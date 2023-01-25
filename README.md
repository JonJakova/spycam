# spycam - Security Python Camera

It uses OpenCV to recognize wether a person is been filmed or not.

## Requirements

>- Python > 3.8
>- Pip > 21

## Running

Adviced using a virtual environment to run

>- python3 -m venv env
>- source env/bin/activate
>- pip install -r requirements.txt
>- touch .env
>- fill .env file with your data (like .env.example)
>- flask --app api run

## Endpoints

>- /status - GET - Get the status of the camera
>- /start - POST - Start the camera
>- /stop - POST - Stop the camera
