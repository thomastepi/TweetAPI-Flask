from flask import Blueprint, request, json
from mocks import DB_FILE_PATH
from entities import SqlLiteDbWrapper

blueprint = Blueprint('api', __name__, url_prefix='/basic_api')


@blueprint.route('/users/<id>')
def get_user_by_id(id):
    with SqlLiteDbWrapper(DB_FILE_PATH) as db:
        return db.get_user(id)


@blueprint.route('/users', methods=['GET', 'POST'])
def users():
    with SqlLiteDbWrapper(DB_FILE_PATH) as db:
        if request.method == 'POST':
            data = request.get_json()
            name = data.get("name")
            db.add_user(name)
            return f"user {name} added"
        else:
            get_filter = request.args.get("filter")
            print(f'filter: {get_filter}')
            result = db.get_users(get_filter)
            return result


@blueprint.route('/tweets', methods=['GET', 'POST'])
def tweets():
    # Assignment implementation
    with SqlLiteDbWrapper(DB_FILE_PATH) as db:
        if request.method == 'POST':
            data = request.get_json()
            message = data.get("message")
            user_id = data.get("userId")
            db.add_tweet(message, user_id)
            return f"Tweet '{message}' posted by user with ID: {user_id}"
        else:
            get_filter = request.args.get("filter")
            print(f'filter: {get_filter}')
            result = db.get_tweets(get_filter)
            return result


@blueprint.route('/followers/<followee_id>/<follower_id>', methods=['POST', 'DELETE'])
def follow_unfollow_user(followee_id, follower_id):
    try:
        with SqlLiteDbWrapper(DB_FILE_PATH) as db:
            if request.method == 'POST':
                db.follow(followee_id, follower_id)
                return "Followed successfully", 200
            elif request.method == 'DELETE':
                db.unfollow(followee_id, follower_id)
                return "Unfollowed successfully", 200
    except Exception as e:
        return f"Error occurred: {e}", 500


@blueprint.route('/likes/<tweet_id>/<user_id>', methods=['POST', 'DELETE'])
def add_remove_like(tweet_id, user_id):
    try:
        with SqlLiteDbWrapper(DB_FILE_PATH) as db:
            if request.method == 'POST':
                db.add_like(tweet_id, user_id)
                return "Tweet 'like' ADDED", 200
            elif request.method == 'DELETE':
                db.remove_like(tweet_id, user_id)
                return "Tweet 'like' REMOVED", 200
    except Exception as e:
        return f"Error occurred: {e}", 500


@blueprint.route('/feeds/<user_id>')
def get_feed(user_id):
    try:
        with SqlLiteDbWrapper(DB_FILE_PATH) as db:
            feed = db.get_user_feed(user_id)
            return json.dumps(feed), 200
    except Exception as e:
        return f"Error occurred: {e}", 500


@blueprint.route('/hello_world')
def hello_world():
    message = 'Hello World'
    return message