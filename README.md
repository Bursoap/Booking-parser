Use only virtualenv virtual environment, not pipenv and another.
Virtualenv should be install in project root dir as .venv.
In your_project/src/booking/booking must be env.py with parameters like in env-example.py
Install dependencies from requirement.txt.
If Windows is your system: to activate virtual enviroment you can run in console from project root: activate

Usage:

1. In console select your_project_dir/src/booking/bookig and run:

        $python models.py

   It will create tables in your database.

2. In console select your_project_dir/src/booking/bookig and run with your parameters, example:

	    $python start.py -p -t Phoenix -c USA -i 2018-10-10 -o 2018-10-12

	parameters:
	
		-p -enable proxy
		-t -destination town
		-c -destination country
		-i -check in date in format YYYY-MM-DD
		-o -check out date in same format
		-r -number of rooms
		-a -number of adults
		-ch -number of children

3. If you want set logging level go to settings and set level in LOG_LEVEL.