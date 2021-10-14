# SVPOL-DASH

### heroku stuff
To access the app when it has been pushed to heroku, we need to expose the $PORT environment variable. 
We use this both in `app.py` and in the `Dockerfile`.

#### Build and push the image to Heroku
`sudo heroku container:push web -a svpol-analytics`

#### Release and start the container on Heroku
`sudo heroku container:release web -a svpol-analytics`

#### View the logs of the application
`sudo heroku logs --tail`

#### Take the app down
Go to heroku.com and visit the apps page. Go to "Settings" and toggle "Maintenance Mode".