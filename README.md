# Website monitor

Website monitor is an app that can monitor status of your website. You can register many users and follow any website you want. When your site goes down, you'll get an email notification. You can also check history of followed website to get a better overview of the situation. 

Additionally, it supports running simple attacks, such as slow loris. Comined with the history and live view of the websites status it can be useful tool for administrators.

Website monitor supports:
1. Authetication of users (sign up, login, password change etc.)
2. Following websites
3. Periodically checking website status
4. Overwiew of status history
5. Sending email notification if website goes down
6. Running simple attacks (tests)

# Under the hood

Website monitor uses a couple of python (and JS) libraries to make things work.
- flask - this microframework is the "heart" of the aplication
- flask-login - used for session management and authenticatoin
- flask-sqlalchemy - for handling database
- flask-apcheduler - for handling background tasks
- smtplib - used to send email notification
- chart.js - for displaying charts
- slowloris - to perform attacks
- urllib - for url normalization
- werkzeug.security - to keep your passwords safe

# Clean interface

Everything is just simple and easy to find. Some screenshots:

![1](/screenshots/1.png)
![2](/screenshots/2.png)
![3](/screenshots/3.png)
