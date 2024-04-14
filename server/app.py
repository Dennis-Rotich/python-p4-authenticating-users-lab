#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username',type=str)
        data = parser.parse_args()

        user = User.query.filter_by(username=data.get("username")).first()
        session['user_id'] = user.id
        response_body = {
            'id': user.id,
            'username': user.username
        }
        status_code = 200
        headers = {}
        return make_response(response_body, status_code, headers)

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return make_response({},204,{})

class CheckSession(Resource):
    def get(self):
        if session['user_id'] != None:
            user = User.query.filter_by(id=session.get('user_id')).first()
            response_body = {'id':user.id, 'username':user.username}
            status_code = 200
            headers = {}
            return make_response(response_body, status_code, headers)
        else:
            return make_response({},401,{})       

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
