# -*- coding: utf-8 -*-
from errors import forbidden
from ..models import Permission
from .. import db
from flask import jsonify, request, g, url_for, current_app
from ..models import Post
from . import api
from authentication import http_auth
from decorators import permission_required


# 文章资源 GET 请求
@api.route('/posts/', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    current_app.config['HelloFlask_POSTS_PER_PAGE'] = 10
    pagination = Post.query.paginate(page,
                                     per_page=current_app.config['HelloFlask_POSTS_PER_PAGE'],
                                     error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page - 1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_posts', page=page + 1, _external=True)
    return jsonify({'posts': [post.to_json for post in posts],
                    'prev': prev,
                    'next': _next,
                    'count': pagination.total
                    })


# 由文章id获取单篇资源
@api.route('/posts/<int:id>', methods=['GET'])
@http_auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


# 文章资源 POST 更新
@api.route('/posts', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.currents_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
           {'Location': url_for('api.get_post', id=post.id, _external=True)}


# 文章资源PUT跟新
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())

