# My Restaurant Menu App #

This application is one of the Udacity Full Stack Web Developer Nanodegree program.

The app makes use of python, sqlite and Flask. It creates a list of restaurants and for each restaurant it is possible to add a menu.

### Starting the App ###

Before running the application, create a configure the database:

 `python database_setup.py`

Then you need to insert your credentials for the geocoder API and the login options:

* Create a file called config.py and insert the following code:

  `GEOCODER_API_KEY= <YOUR-API-KEY>`
* Insert the API key in restaurants.html to display Google maps
* Download the json file from the Google Developer console in the Credentials dashboard and rename it as "client_secrets.json" :

  ```
  {"web":
    {
      "client_id":"<YOUR-CLIENT-ID>.apps.googleusercontent.com",
      "project_id":"<YOUR-PROJECT-ID>",
      "auth_uri":"https://accounts.google.com/o/oauth2/auth",
      "token_uri":"https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
      "client_secret":"<YOUR-CLIENT-SECRET>",
      "redirect_uris":["http://localhost:5000/restaurants/"],
      "javascript_origins":["http://localhost:5000"]
    }
  }
  ```

* Create another json file called fb_client_secrets.json for Facebook login:

```
  {
    "web": {
      "app_id": "<YOUR-APP-ID>",
      "app_secret": "YOUR-APP-SECRET",
      "app_vers": "v3.2"
    }
  }
```

After the initial setup is complete, you can start the application with:

`python app.py`


Some of the CRUD functionality (Create, Update and Delete) are restricted to Logged in users only.


### Map display ###
When inserting a new restaurant, it is important to insert the address of the location. After inserting the address, you need to click the Validate button before saving to the database.
The Validate method will call the Geocoder API and retrieve the coordinates for that address.
The coordinates are necessary to display Google Map centered at the restaurant location in the home page.
Restaurants details can be edited only by the users who created them.

### Menu Items ###
Menu items require a picture link. It is recommended to use a landscape picture.
Menu Items can only be edited or deleted from the user have created them.
