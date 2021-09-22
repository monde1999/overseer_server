
# Setup

    python -m venv env
    env\Scripts\activate
    pip install django
    pip install djangorestframework
    pip install Pillow
    pip install requests
    python manage.py migrate
    python manage.py runserver


# Account

SIGNUP [POST]: /account/signup/
{
    "username": "",
    "password": "",
    "firstname": "",
    "lastname": ""
}
    ---> return: 'flag': 'true' (success), 'false' (fail)

LOGIN [POST]: /account/login/
{
    "username": "",
    "password": ""
}
    ---> return: 'flag': 'true' (success), 'false' (wrong credentials), 'wrong_password' (wrong password)


# Report and React

REPORT [POST]: /report/create/
{
    "user": "", //user id
    "description": "",
    "floodLevel": "",
    "latitude": "",
    "longitude": ""
}

REACT [POST]: /report/react/
{
    "report": "", //report id
    "user": "", //user id
    "isPositive": ""
}


# FloodForecast Data

AREAS [GET]: /forecast/flood-prone-areas/?latitude=XXX&longitude=YYY
    ---> param: center location
    ---> return: areas around 500 meters

REPORTS [GET]: /forecast/reports/?latitude=XXX&longitude=YYY
    ---> param: Area location
    ---> return: reports

REPORT_IMAGES [GET]: /forecast/report-images/?report_id=XXX
    ---> param: report id
    ---> return: image links

REPORT_REACTIONS [GET]: /forecast/report-reactions/?report_id=XXX&user_id=YYY
    ---> param: report id and user id
    ---> return: the reaction of a certain user to a certain report; may be empty