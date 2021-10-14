# GrassbergerPartners
 Website to track the success of Grassberger Partners.

# How to install
- Make sure you have the latest Python installation.
- Make sure you have flask installed.
- Run "pip install -r requirements.txt"
- Run "pip install -e ." (e stands for editable, is for development only!)
- Set environment variable: "set FLASK_APP=gbpartners/wsgi.py:app" (windows)
- Set environment variable: "set FLASK_ENV=development" if developing
- Set environment variable: "set GBPARTNERS_SETTINGS=settings.cfg" and create such a file in the instance folder
- Initialize the db: "flask init-db"
- Create an admin account: "flask create-user admin 'password'" (password in quotes is important)
- Run the website on localhost by doing: "flask run"
- Upload the performance file of your portfolio in the /admin/home console

# Additional stuff
For the download to work you need to have wkhtmltopdf.