#!flask/bin/python
from app import application

application.run(debug=True, port=7777, host="0.0.0.0")
