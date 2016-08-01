# -*- coding: utf-8 -*-
from flask import render_template, url_for, redirect, abort, flash, request, make_response
from flask_login import login_required, current_user, current_app

from forms import EditProfileForm, PostForm, CommentForm
from . import main
from .. import db
from ..models import User, Permission, Post, Comment


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # 分页显示博客文章列表
    page = request.args.get('page', 1, type=int)
    current_app.config['HelloFlask_POSTS_PER_PAGE'] = 10
    # 显示所有博客文章或者只有关注者的文章
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['HelloFlask_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form,show_followed=show_followed, posts=posts, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


# 修改用户资料
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('You profile has been updated')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 博客文章评论路由
@main.route('/post/<_id>', methods=['GET', 'POST'])
def post(_id):
    post = Post.query.get_or_404(_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (Post.comments.count - 1) / current_app.config['HelloFlask_COMMENT_PER_PAGE'] + 1
    pagination = Post.comments.order_by(Comment.timestamp.asc())\
        .pagination(page,
                    per_page=current_app.config['HelloFlask_COMMENTS_PER_PAGE'],
                    error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


# “关注”路由
@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


# 关注者路由
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config('HelloFlask_FOLLOWERS_PER_PAGE'),
                                         error_out=False)
    follows = [{'user': item.follower,
                'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='.followers',
                           pagination=pagination, follows=follows)


# 所有文章路由
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', max_age=30 * 24 * 60 * 60)
    return resp


# 关注者的路由
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp



# 评论管理路由
@main.route('/moderate/enable/<_id>')
@login_required
def moderate_enable(_id):
    comment = Comment.query.get_or_404(_id)
    comment.disable = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<_id>')
@login_required
def moderate_disable(_id):
    comment = Comment.query_or_404(_id)
    comment.disable = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
