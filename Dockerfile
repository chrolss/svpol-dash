FROM continuumio/anaconda3:latest
LABEL Author=ml-boitsu
COPY . /usr/local/python
ENV PORT=8050
EXPOSE $PORT
WORKDIR /usr/local/python
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
CMD python app.py