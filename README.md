# FlaskTweetApp API
This FlaskTweetApp is a Flask-based application for managing users, tweets, followers, and likes.

## Overview
This API provides endpoints for basic user and tweet management, allowing users to add, retrieve, and interact with tweets, follow other users, and manage likes.

## Quick Start

1. **Install dependencies:** `pip install flask flask-cors flask-swagger-ui`
2. **Run the application:** `python app.py`
3. **Access the Swagger UI:** Open your browser and navigate to http://127.0.0.1:5000/swagger.

# Endpoints

**Users**
 - GET /users/{id}: Get user details by ID.
 - POST /users: Add a new user.
 - GET /users: Get a list of users.

**Tweets**
 - POST /tweets: Add a new tweet.
 - GET /tweets: Get a list of tweets.

**Followers**
 - POST /followers/{followee_id}/{follower_id}: Follow a user.
 - DELETE /followers/{followee_id}/{follower_id}: Unfollow a user.

**Likes**
 - POST /likes/{tweet_id}/{user_id}: Add a like for a tweet.
 - DELETE /likes/{tweet_id}/{user_id}: Remove a like from a tweet.

**Feeds**
 - GET /feeds/{user_id}: Get the user feed.
