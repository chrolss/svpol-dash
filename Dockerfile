FROM continuumio/anaconda3:latest
LABEL Author=ml-boitsu
COPY . /usr/local/python
# Remember to remove ENV when going to Heroku
#ENV PORT=8050
EXPOSE $PORT
WORKDIR /usr/local/python
RUN pip install -r requirements.txt
CMD python app.py