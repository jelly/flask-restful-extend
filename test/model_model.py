# -*- coding: utf-8 -*-

__all__ = ['db', 'Parent', 'Entity']

from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, desc, text, or_, ForeignKey
from sqlalchemy.orm import relationship, validates
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful_extend.extend_model import extend_model
from project import app


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{db_user}:{db_password}@localhost/{db}'.format(
    db_user='root', db_password='609888', db='flask_restful_extend_test')
# 添加此参数已解决长时间不访问后，再次访问出现 MySQL server has gone away 的问题
app.config['SQLALCHEMY_POOL_RECYCLE'] = 500


extend_model()
db = SQLAlchemy(app)


class Parent(db.Model):
    id = Column(Integer, primary_key=True)
    cstr = Column(String(50), unique=True, nullable=False)

    entities = relationship('Entity', backref='parent', lazy='dynamic')


def trans_cint_n(value):
    return dict(value=value + 1 if value != 20 else 19)


def valid_cint_n(value, arg1):
    return value % arg1 == 0


class Entity(db.Model):
    """
    c{column_type}[_n (nullable)]
    """
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False)
    cint_n = Column(Integer)

    cstr = Column(String(5), nullable=False)
    cstr_n = Column(String(10))

    cfl = Column(Float, nullable=False)
    cfl_n = Column(Float)

    cbl = Column(Boolean, nullable=False)
    cbl_n = Column(Boolean)

    cts = Column(TIMESTAMP, nullable=False)
    cts_n = Column(TIMESTAMP)

    validate_rules = [
        # 检查各个内置验证器是否正常工作
        ('cint_n', 'min', 10),  # 通过对 _n 字段也添加一个验证器，可检查验证器能否正确处理 null 值
        ('cint_n', 'max', 20),
        ('cstr', 'min_length', 1),
        ('cstr', 'max_length', 4),
        ('cstr_n', 'match', '^[a-z]+$'),
        ('cstr_n', 'trans_upper'),
        ('cstr_n', 'match', '^[A-Z]+$'),    # 测试 trans_upper 是否成功转换，以及两个验证器间的交接是否正常

        # 检查自定义验证器能否正常工作
        ('cint_n', trans_cint_n),       # 单数变双数，双数变单数
        ('cint_n', valid_cint_n, 2),    # 对于双数返回 true，对于单数返回 false。
                                        # 结合 trans_cint_n，则 cint_n 原始值必须为单数才能通过检查
    ]