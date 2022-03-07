FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY basic_name_dict.pkl /markov/basic_name_dict.pkl
COPY basic_note_dict.pkl /markov/basic_note_dict.pkl
COPY . /app

WORKDIR /app

CMD python /app/bot.py