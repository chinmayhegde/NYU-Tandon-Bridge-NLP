FROM python:3

# Copy function code
COPY app.py ./

# Install the function's dependencies using file requirements.txt
COPY requirements.txt  ./
RUN  pip install -r ./requirements.txt 

# Install nltk_data & Vader_lexicon
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader vader_lexicon

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "python","-u","./app.py"] 