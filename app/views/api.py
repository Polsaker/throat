""" /api/ """

import re
import datetime
import bcrypt
from flask import Blueprint, jsonify, abort, request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from marshmallow import Schema, fields, ValidationError, pre_load

from ..models import db, User, Sub, SubPost, Message, SubPostComment
from ..models import subpost_schema, subposts_schema, sub_schema, subs_schema
# from ..models import SubPostVote, SubMetadata, SubPostMetadata, SubStylesheet
# from ..models import UserMetadata, UserBadge
from flask_login import login_user, login_required, logout_user, current_user
# from ..misc import SiteUser

api = Blueprint('api', __name__)

""" /api/v1/ """

@api.route("/api/v1/status", methods=['GET'])
def status():
    """ status endpoint """
    data = {'status': 'active', 'version': '1.0'}
    resp = jsonify(data)
    resp.status_code = 200
    return resp


@api.route("/api/v1/u/<user>", methods=['GET'])
@login_required
def view_user(user):
    """ Get user info """
    user = User.query.filter_by(name=user).first()
    if not user:
        abort(404)
    else:
        data = {'name': user.name,
                'joindate': user.joindate,
                'status': user.status}
        resp = jsonify(data)
        resp.status_code = 200
        return resp


@api.route("/api/v1/s/<sub>", methods=['GET'])
def view_sub(sub):
    """ Get sub """
    sub = Sub.query.filter_by(name=sub).first()
    if not sub:
        abort(404)
    else:
        data = {'name': sub.name,
                'title': sub.title,
                'created': sub.getSubCreation,
                'posts': sub.getSubPostCount,
                'mod': sub.getModName,
                'status': sub.status,
                'nsfw': sub.isNSFW}
        resp = jsonify(data)
        resp.status_code = 200
        return resp


@api.route("/api/v1/s/<sub>/<pid>", methods=['GET'])
def view_post(sub, pid):
    """ Get post """
    post = SubPost.query.filter_by(pid=pid).first()
    if not post or post.sub.name != sub:
        abort(404)
    else:
        data = {
                'id': post.pid,
                'title': post.title,
                'link': post.link,
                'content': post.content,
                'user': post.user.name,
                'posted': post.posted,
                'ptype': post.ptype,
                'votes': post.voteCount}
        resp = jsonify(data)
        resp.status_code = 200
        return resp


""" marshmallow """

@api.route('/api/v1/subs')
def get_subs():
    subs = Sub.query.order_by(Sub.name.asc()).all()
    for sub in Sub.query:
        sub.sid = sub.name
    result = subposts_schema.dump(subs)
    return jsonify({'subs': result.data})


@api.route('/api/v1/posts')
def get_posts():
    posts = SubPost.query.order_by(SubPost.posted.desc()).all()
    for post in SubPost.query:
        # post.sid = post.sub.name
        post.uid = post.user.name
    result = subposts_schema.dump(posts)
    return jsonify({'posts': result.data})


@api.route("/api/v1/post/<int:pid>")
def get_post(pid):
    post = SubPost.query.filter_by(pid=pid).first()
    if not post:
        abort(404)
    # post.sid = post.sub.name
    post.uid = post.user.name
    post_result = subpost_schema.dump(post)
    return jsonify({'post': post_result.data})


@api.errorhandler(404)
def not_found(error):
        data = {'error': 'not found'}
        resp = jsonify(data)
        resp.status_code = 404
        return resp
