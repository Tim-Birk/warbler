# Step 7: Research and Understand Login Strategy

- How is the logged in user being kept track of?
  - When the user is either authenticated or created, their user id is added to a key in the Flask session called CURR_USER_KEY
- What is Flask’s g object?
  - Flask's g object is a proxie within Flask's application context which keeps track of application-level data during a request.
  - It is typically used as a place to store common data during a request or CLI command
  - It is a simple namespace object that has the same lifetime as an application context.
  - [source](https://flask.palletsprojects.com/en/1.1.x/appcontext/)
- What is the purpose of add_user_to_g?
  - The purpose of this function is to make the current user is accessible across each request that is made by adding them to the g (global) object within the application context
- What does @app.before_request mean?
  - It is literally a function that runs before each request
  - In this case, we are using it to add the currently logged in user to the g object in flask so we have access to it in every request that is made
  - [source](https://flask.palletsprojects.com/en/1.1.x/api/)