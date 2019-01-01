from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

from info import  constants
from . import db


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间

#定义设备和房屋的多对多关系白表
tb_HouseFacility=db.Table(
    "info_housefacility",
    db.Column('house_id',db.Integer,db.ForeignKey('ih_house_info.id'),primary_key=True),
    db.Column('facility_id',db.Integer,db.ForeignKey('ih_facility_info.id'),primary_key=True)
)


# 定义房屋模型类 -------------------------------
class House(BaseModel, db.Model):
    __tablename__='ih_house_info'
    id=db.Column(db.Integer,primary_key=True)                                                               # 房屋id  主键
    user_id=db.Column(db.Integer,db.ForeignKey('ih_user_profile.id'))                       #房屋所有人id，外键
    area_id=db.Column(db.Integer,db.ForeignKey('ih_area_info.id'))                            #房屋所在城区id，外键
    title=db.Column(db.String(80),nullable=False)                                  #房屋标题
    price=db.Column(db.String(15),nullable=False)                               #价格
    address=db.Column(db.String(200),nullable=False)                      #地址
    room_count=db.Column(db.Integer)                                                   #出租的房间数量
    acreage=db.Column(db.Integer)                                                         #面积
    unit=db.Column(db.String(60),nullable=False)                                        #房屋户型
    capacity=db.Column(db.Integer,nullable=False)                             #住的人数
    beds=db.Column(db.String(60))                                                        #床类型信息（双人床/单人床）
    deposit=db.Column(db.String(15),nullable=False)                             #押金
    order_count=db.Column(db.Integer)                                              #订单数据
    min_days=db.Column(db.Integer)                                                   #出租的最短时间
    max_days=db.Column(db.Integer)                                                 #出租的最长时间,0表示不限制
    index_image_url=db.Column(db.String(128))                              #房屋主页图片存储地址

    image_urls=db.relationship('HouseImage',backref='house')                              #房屋图片地址，定义与房屋图片（ih_house_image）的关系
    orders=db.relationship('Order',backref='house')                                                 #我的订单，定义与订单（ih_order_info）的关系

    facilities=db.relationship('Facility',secondary=tb_HouseFacility,backref=db.backref('houses'), lazy="dynamic")
    def to_dict(self):
        resp_dict={
            "id":self.id,
            "title":self.title,
            "price":self.price,
            "address":self.address,
            "room_count":self.room_count,
            "acreage":self.acreage,
            "unit":self.unit,
            "capacity":self.capacity,
            "beds":self.beds,
            "deposit":self.deposit,
            "index_image_url":constants.QINIU_DOMIN_PREFIX+self.index_image_url if self.index_image_url else "",
            "order_count":self.order_count,
            "min_days":self.min_days,
            "max_days":self.max_days,
            "user_id":self.user_id,
            "area_id":self.area_id
        }
        return resp_dict

# 定义用户模型类 -------------------------------
class User(BaseModel, db.Model):
    __tablename__ = 'ih_user_profile'
    id = db.Column(db.Integer, primary_key=True)  # 用户id  主键
    name = db.Column(db.String(30),nullable=False)  # 登录名
    password_hash = db.Column(db.String(100),nullable=False)  # 密码加密后
    mobile = db.Column(db.String(20),unique=True,nullable=False)  # 手机号
    real_name = db.Column(db.String(20))  # 真实姓名
    id_card = db.Column(db.String(30))  # 身份证
    avatar_url = db.Column(db.String(80))  # 头像图片存储地址


    orders=db.relationship('Order',backref='user')#我的订单，定义了与订单（ih_order_info）的关系
    houses=db.relationship('House',backref='user')#我的房屋，定义了与房屋（ih_house_info）的关系

    @property
    def password(self):
        raise AttributeError("当前属性不可读")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "password_hash":self.password_hash,
            "avatar_url": constants.QINIU_DOMIN_PREFIX + self.avatar_url if self.avatar_url else "",
            "mobile": self.mobile,
            "real_name":self.real_name,
            "id_card":self.id_card
        }
        return resp_dict

# 定义订单模型类 -------------------------------
class Order(BaseModel, db.Model):
    __tablename__ = 'ih_order_info'
    id=db.Column(db.Integer,primary_key=True) #订单编号
    begin_date=db.Column(db.DateTime, default=datetime.now)#订单创建时间
    end_date=db.Column(db.DateTime)#订单完成时间
    days=db.Column(db.Integer,nullable=False)#入住天数
    house_price=db.Column(db.String(15),nullable=False)#房屋价格
    amount=db.Column(db.String(15))#订单总金额
    status=db.Column(db.String(20))#订单状态，待接单/已接单
    comment=db.Column(db.String(128))#用户评论
    user_id = db.Column(db.Integer, db.ForeignKey('ih_user_profile.id'))#用户id  外键   -----------users
    house_id=db.Column(db.Integer,db.ForeignKey("ih_house_info.id"))#房屋id  外键  -------------houses

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "begin_date": self.begin_date,
            "end_date": self.end_date,
            "days": self.days,
            "house_price": self.house_price,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment,
            "user_id":self.user_id,
            "house_id":self.house_id
        }
        return resp_dict

# 定义城区模型类 -------------------------------
class Area(BaseModel, db.Model):
    __tablename__ = 'ih_area_info'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False)

    houses=db.relationship('House',backref='area')

    def to_dict(self):
        resp_dict={
            "id":self.id,
            "name":self.name
        }
        return resp_dict

# 定义HouseImage -------------------------------
class HouseImage(BaseModel, db.Model):
    __tablename__ = 'ih_house_image'
    id=db.Column(db.Integer,primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey('ih_house_info.id'))
    url=db.Column(db.String(100))


    def to_dict(self):
        resp_dict={
            "id":self.id,
            'url':constants.QINIU_DOMIN_PREFIX+self.url if self.url else "",
        }
        return resp_dict

#定义Facility ---------------------------------------
class Facility(BaseModel, db.Model):
    __tablename__='ih_facility_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))


    def to_dict(self):
        resp_dict={
            "id":self.id,
            "name":self.name
        }
        return resp_dict



