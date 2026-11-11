# Flask documentation:
# https://flask.palletsprojects.com/en/stable/quickstart/
from flask import Flask, request, render_template;
from database import database
from logger import logger

app = Flask(__name__)
db: database.DB = database.DB()

# based on code shown here:
# https://www.geeksforgeeks.org/python/how-to-serve-static-files-in-flask/
@app.route("/", methods=["get"])
def index():
    records = None
    averages = None

    try:
        # Get the user and page number from the query parameters
        user = request.args.get('name')
        page = request.args.get('page')

        try:
            page = int(page)
        except:
            page = 0

        # If we don't have a user, we can't get any data for them, so we return a 400 error
        if not user:
            return abort(400)
        
        records = db.get_data_for_user(user, page)

        # This function hasn't been implemented yet it should return the average lux, pressure, temperature and humidity for the user
        averages = db.get_average_data_for_user(user)
        
    except Exception as e:
        logger.error("Failed to get data for user: " + str(e))
        pass

    logger.debug(records)
    logger.info(averages)

    # This part is somewhat arcane, the first argument is the filename of the template we want to render
    # the second argument is the data we want to pass to the template 
    # The template files live in ./templates, so in this case we are rendering ./templates/index.html
    return render_template(
        'index.html',
        name=user,
        records=records,
        averages=averages
    )

# configure an endpoint to accept data from other devices
@app.route("/<name>", methods=["post"])
def recieve_data(name):
    try:

        # Get the data from the request body, this is the data logged from your sensors
        content = request.get_json()
        logger.debug(f"Recieved {name} {content}")

        db.write_data_for_user(
            user=name,
            lux=content['lux'],
            pressure=content['pressure_hpa'],
            temp=content['temp_c'],
            humidity=content['humidity_pct'],
        )

        return "Success"

    except Exception as e:
        logger.error(e)
        raise e

# This starts the server, we shouldn't need to make any changes here
def serve():
    from waitress import serve
    logger.info('SERVING')
    serve(app, host="0.0.0.0", port=5000)