FROM python:3.8-slim-buster

COPY ./requirements.txt ./

# Install dependenceis
RUN apt-get -y update && \
    pip install -r requirements.txt && \
    apt-get -y autoremove

# Change working directory
WORKDIR /

# Copy the latest version of the bot 
COPY 4_bot.py 4_bot.py

# Copy Processed Notes
COPY processed_data/basic_dict.pkl processed_data/basic_dict.pkl
COPY processed_data/basic_name_dict.pkl processed_data/basic_name_dict.pkl

# Run the shell file
CMD ["python", "4_bot.py"]
