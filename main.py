import os
import requests

from flask import Flask, request, make_response, jsonify, abort
from flask_cors import CORS, cross_origin

from google.appengine.ext import ndb

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

class Yelp(ndb.Model):
    consumer_key    = ndb.StringProperty()
    consumer_secret = ndb.StringProperty()
    token           = ndb.StringProperty()
    token_secret    = ndb.StringProperty()

class AllowedUrl(ndb.Model):
    origin  = ndb.StringProperty()
    referer = ndb.StringProperty()

app = Flask(__name__)

@app.route('/get_yelp_info/<yelp_id>')
@cross_origin()
def get_yelp_info(yelp_id):
    origin  = request.headers.get('Origin')
    referer = request.headers.get('Referer')

    if origin is None or referer is None:
        return abort(404)

    allowed_url = AllowedUrl.query(AllowedUrl.origin == origin,
                                   AllowedUrl.referer == referer)

    if allowed_url is None:
        return abort(404)

    yelp_key = Yelp.query().get()

    if yelp_key is None:
        return abort(404)

    auth = Oauth1Authenticator(
            consumer_key=yelp_key.consumer_key,
            consumer_secret=yelp_key.consumer_secret,
            token=yelp_key.token,
            token_secret=yelp_key.token_secret
            )

    client = Client(auth)
    result = client.get_business(yelp_id).business
    response = {}
    response['url'] = result.url
    response['image_url'] = result.image_url
    response['rating_img_url'] = result.rating_img_url

    return jsonify(response)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', port=8080)
