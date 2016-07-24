# -*- coding: utf-8 -*-
from exceptions import ValidationError
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import UserMixin, AnonymousUserMixin, current_app
from datetime import datetime
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


# 关注着
class Follow(db.Model):
    __tablename='follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # 基础用户资料
    # 用户 id
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    # 电子邮件
    email = db.Column(db.String(64), unique=True, index=True)
    # 登录用户名
    username = db.Column(db.String(64), unique=True, index=True)
    # 用户密码的 hash 值
    password_hash = db.Column(db.String(128))
    # 用户角色 id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 用户是否验证邮件
    confirmed = db.Column(db.Boolean, default=False)

    # 扩充用户资料信息
    # 真实姓名
    name = db.Column(db.String(64))
    # 所在地
    location = db.Column(db.String(64))
    # 关于我
    about_me = db.Column(db.Text())
    # 注册日期
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    # 最后访问日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 博客文章
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # 关注者
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # 关注关系的辅助方法
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = Follow(follower=self, followed=user)
        db.session.add(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    # 定义默认的用户角色
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            current_app.config['HelloFlask_Admin'] = ''
            if self.email == current_app.config['HelloFlask_Admin']:
                self.role = Role.query.filter_by(Permission=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 刷新用户的最后访问日期
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 序列化为json
    def to_json(self):
        json_user = {
            'url':url_for('api.get_post', id=self.id, _external=True),
            'username':self.username,
            'member_since':self.member_since,
            'last_seen':self.last_seen,
            'posts':url_for('api.get_user_followed_posts',
                            id=self.id, _external=True),
            'post_count':self.posts.count()
        }
        return json_user

    # 生成测试数据
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    # 生成 RESTFUL Http 验证令牌
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id':self.id})

    # 验证 RESTFUL Http 令牌
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.load(token)
        except:
            return None
        return User.query.get(data['id'])


# 博客文章
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 博客正文
    body = db.Column(db.Text)
    # 博客发布日期
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # 博客作者
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 序列化为 json
    def to_json(self):
        json_post = {
            'url':url_for('api.get_post', id=self.id, _external=True),
            'body':self.body,
            'body_html':self.body_html,
            'timestamp':self.timestamp,
            'author':url_for('api.get_user', id=self.id, _external=True),
            'comment_count':self.comments.count()
        }
        return json_post

    # 生成测试文章
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentence(),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    # 从json反序列化为对象
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
