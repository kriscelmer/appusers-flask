"""Database module

This module declares Database Models of User and Group Resources.

User Resource is internally stored in User class object.
Group Resource is internally stored in Group class object.
"""
from flask_sqlalchemy import SQLAlchemy


# Database object is initialized in Application Factory
db = SQLAlchemy()

class Group(db.Model):
    """Database Model of Group Resource"""

    groupid = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(20), unique=True, nullable=False) # zmien na maksymalna dlugosc z models.GroupSchema
    description = db.Column(db.Text)

    def __init__(self, **kwargs):
        """Group Object constructor automatically inserts to Database"""
        super(Group, self).__init__(**kwargs)
        db.session.add(self)
        db.session.commit()

    def update(self, groupname=None, description=None, **kwargs):
        """Update Group Object and commit to Database"""
        if groupname:
            self.groupname = groupname
        if description:
            self.description = description
        db.session.commit()

    def remove(self):
        """Permanently remove Group Object from Database"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def retrieve(cls, groupid):
        """Retrieve Group Object with groupid from Database"""
        return cls.query.get(groupid)

    @classmethod
    def get_list(cls, filters):
        """Retrieve a filtered list of Group Objects from Database"""
        # Mock-up
        return cls.query.all()

    def __repr__(self):
        return f'<Group {self.groupname}>'

class User(db.Model):
    """Database Model of User Resource"""

    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False) # zmien na maksymalna dlugosc z models.UserSchema
    firstname = db.Column(db.String(30), nullable=False) # zmien na maksymalna dlugosc z models.UserSchema
    lastname = db.Column(db.String(30), nullable=False) # zmien na maksymalna dlugosc z models.UserSchema
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20)) # zmien na maksymalna dlugosc z models.UserSchema

    def __init__(self, **kwargs):
        """User Object constructor automatically inserts to Database"""
        super(User, self).__init__(**kwargs)
        db.session.add(self)
        db.session.commit()

    def update(self,
            username=None,
            firstname=None,
            lastname=None,
            email=None,
            phone=None,
            **kwargs):
        """Update User Object and commit to Database"""
        if username:
            self.username = username
        if firstname:
            self.firstname = firstname
        if lastname:
            self.lastname = lastname
        if email:
            self.email = email
        if phone:
            self.phone = phone
        db.session.commit()

    def remove(self):
        """Permanently remove User Object from Database"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def retrieve(cls, userid):
        """Retrieve User Object with userid from Database"""
        return cls.query.get(userid)

    @classmethod
    def get_list(cls, filters):
        """Retrieve a filtered list of User Objects from Database"""
        # Mock-up
        return cls.query.all()

    def __repr__(self):
        return f'<User {self.username}>'
