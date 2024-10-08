# Paperw8
 Website to track the success of Paperweight.

 ![website_screenshot](https://github.com/user-attachments/assets/bc27f7fb-c049-4979-bd91-a53a3f9c5d17)

# How to install
- Make sure you have the latest Python installation.
- Make sure you have flask installed.
- Run "pip install -r requirements.txt"
- Run "pip install -e ." (e stands for editable, is for development only!)
- Set environment variable: "set FLASK_APP=paperw8/wsgi.py:app" (windows)
- Set environment variable: "set FLASK_ENV=development" if developing
- Set environment variable: "set PAPERW8_SETTINGS=settings.cfg" and create such a file in the instance folder
- Initialize the db: "flask init-db"
- Create an admin account: "flask create-user admin password" (password in quotes is important)
- Run the website on localhost by doing: "flask run"
- Upload the performance file of your portfolio in the /admin/home console

# When creating a blog post
- Make sure the title image is 1280x720
- Title image cannot be changed easily atm
- Always write captions below images, but don't make a new paragraph (go to last character of image link ")" and do shift+enter)
- Tables don't have captions atm

![website_screenshot_blog](https://github.com/user-attachments/assets/b6b6ea83-c2c4-4920-b1ef-c6dbbc532a55)

# When uploading website

- cd to project location
- gcloud run deploy
- use europe-west1 as server
