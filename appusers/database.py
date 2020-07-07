"""Database module

This module declares Database Models of User and Group Resources.

User Resource is internally stored in User class object.
Group Resource is internally stored in Group class object.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import load_only


# Database object is initialized in Application Factory
db = SQLAlchemy()

# This table stores Group-User membership records
members = db.Table('members',
    db.Column('groupid', db.Integer, db.ForeignKey('group.groupid'),
        primary_key=True),
    db.Column('userid', db.Integer, db.ForeignKey('user.userid'),
        primary_key=True)
    )

class Group(db.Model):
    """Database Model of Group Resource"""

    groupid = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    # 'users' value is a list of User objects
    users = db.relationship('User', back_populates='groups', secondary=members)

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

    def add_member(self, user):
        """Add user to this Group members"""
        if user:
            self.users.append(user)
            db.session.commit()

    def remove_member(self, user):
        """Remove user from Group members"""
        if user and user in self.users:
            self.users.remove(user)
            db.session.commit()

    def list_members(self):
        return User.query.filter(User.groups.any(groupid=self.groupid)).all()

    @classmethod
    def retrieve(cls, groupid):
        """Retrieve Group Object with groupid from Database"""
        return cls.query.get(groupid)

    @classmethod
    def get_list(cls, filters):
        """Retrieve a filtered list of Group Objects from Database"""
        query = cls.query

        if 'groupname' in filters:
            groupnames = filters['groupname'].split(',')
            query = query.filter(Group.groupname.in_(groupnames))
        if 'member' in filters:
            query = query.filter(Group.users.any(userid=filters['member']))
        if 'sortBy' in filters:
            # query.order_by() must be called before offset() or limit()
            sort_by = []
            for col in filters['sortBy'].split(','):
                if col[0] == '-':
                    col = text(f'{col[1:]} DESC')
                else:
                    col = text(col)
                sort_by.append(col)
            query = query.order_by(*sort_by)
        if 'offset' in filters:
            query = query.offset(filters['offset'])
        if 'limit' in filters:
            query = query.limit(filters['limit'])

        return query.all()

    def __repr__(self):
        # Include 'groupid' in representation
        return f'<Group {self.groupname}, groupid={self.groupid}>'

class User(db.Model):
    """Database Model of User Resource"""

    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(30), nullable=False)
    lastname = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    # 'groups' value is a list of Group objects
    groups = db.relationship(Group, back_populates='users', secondary=members)
    password = db.Column(db.String(120), server_default='')
    locked = db.Column(db.Boolean, server_default=False)
    failed_logins = db.Column(db.Integer, server_default=0)
    last_failed_login = db.Column(db.DateTime())
    admin = db.Column(db.Boolean, server_default=False)

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

    def add_to_group(self, group):
        """Add this User to group"""
        if group:
            self.groups.append(group)
            db.session.commit()

    def remove_from_group(self, group):
        """Remove this User from group"""
        if group and group in self.groups:
            self.groups.remove(group)
            db.session.commit()

    def set_password(self, password):
        """Set new password for this User"""
        self.password = password
        db.session.commit()

    def get_lock(self):
        """Return lock status of this User"""
        return self.locked

    def set_lock(self):
        """Lock this User"""
        self.locked = True
        db.session.commit()

    def unlock(self):
        """Unlock this User"""
        self.locked = False
        db.session.commit()

    def get_admin(self):
        """Return admin status of this User"""
        return self.admin

    def grant_admin(self):
        """Grant admin status to this User"""
        self.admin = True
        db.session.commit()

    def revoke_admin(self):
        """Revoke admin status of this User"""
        self.admin = False
        db.session.commit()

    @classmethod
    def retrieve(cls, userid):
        """Retrieve User Object with userid from Database"""
        return cls.query.get(userid)

    @classmethod
    def get_list(cls, filters):
        """Retrieve a filtered list of User Objects from Database"""
        query = cls.query

        if 'username' in filters:
            usernames = filters['username'].split(',')
            query = query.filter(User.username.in_(usernames))
        if 'firstname' in filters:
            firstnames = filters['firstname'].split(',')
            query = query.filter(User.firstname.in_(firstnames))
        if 'lastname' in filters:
            lastnames = filters['lastname'].split(',')
            query = query.filter(User.lastname.in_(lastnames))
        if 'email' in filters:
            query = query.filter(User.email == filters['email'])
        if 'phone' in filters:
            query = query.filter(User.phone == filters['phone'])
        if 'sortBy' in filters:
            # query.order_by() must be called before offset() or limit()
            sort_by = []
            for col in filters['sortBy'].split(','):
                if col[0] == '-':
                    col = text(f'{col[1:]} DESC')
                else:
                    col = text(col)
                sort_by.append(col)
            query = query.order_by(*sort_by)
        if 'offset' in filters:
            query = query.offset(filters['offset'])
        if 'limit' in filters:
            query = query.limit(filters['limit'])

        return query.all()

    def __repr__(self):
        # Include 'groupid' in Object representation
        return f'<User {self.username}, id={self.userid}>'
