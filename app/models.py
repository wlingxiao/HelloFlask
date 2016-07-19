# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import UserMixin, AnonymousUserMixin, current_app
from . import login_manager
from datetime import datetime


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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

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

    # 定义默认的用户角色
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
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


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
