# SVPOL-DASH

## Purpose
This app presents both analytics on party polling numbers for the Swedish parliamentary election, as well as Swedish political tweets that use the hashtag #svpol. The app also includes a machine learning model which tries to predict political leaning in Swedish text that the user can input via a text field.

The app is built in python using plotly dash, and is hosted on heroku.com as a Docker container.

## TODO:
- [x] Implement basic structure for ML inference part
- [x] Implement basic structure for Tweet analytics
- [x] Implement basic structure for party polling numbers analytics
- [x] Implement DataLoader dataclass to handle all data reading and manipulation
- [ ] Add "% of" analytics on trending hashtags
- [ ] Add trending hashtag horizons (e.g. last 5 days, 10 days)
- [ ] Add vertical lines in line graphs to indicate significant events (e.g. debates)
- [ ] Implement the possibility to supply twitter handles as input for the ML inference
- [ ] Implement CI/CD to automatically publish updated version of the app to Heroku

### heroku stuff
To access the app when it has been pushed to heroku, we need to expose the $PORT environment variable. 
We use this both in `app.py` and in the `Dockerfile`.

### Login and authenticate to Heroku
`sudo heroku login`

#### Build and push the image to Heroku
`sudo heroku container:push web -a svpol-analytics`

#### Release and start the container on Heroku
`sudo heroku container:release web -a svpol-analytics`

#### View the logs of the application
`sudo heroku logs --tail -a svpol-analytics`

#### Take the app down
Go to heroku.com and visit the apps page. Go to "Settings" and toggle "Maintenance Mode".