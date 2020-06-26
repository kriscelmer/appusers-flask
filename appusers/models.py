"""Data Models module

This module declares Data Models of User and Group Resources.

User Resource is internally stored in User class object.
Group Resource is internally stored in Group class object.

group_schema object provides serialization (dump) and deserialization (load)
of Group Resource.
group_list_schema object provides serialization of arrays
of Group objects to Data Model of List Groups Collection operation
Response Body.

user_schema object provides serialization and deserialization
of User Resource.
user_list_schema object provides serialization of arrays
of User objects to Data Model of List Users Collection operation
Response Body.
"""
from copy import copy
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, post_load, pre_dump


# Marshmallow object is initialized in Application Factory
ma = Marshmallow()

class Group:
    """Internal representation of Group Resource"""
    def __init__(self, groupid, groupname, description):
        self.groupid = groupid
        self.groupname = groupname
        self.description = description

    def update(self, groupname=None, description=None, **kwargs):
        if groupname:
            self.groupname = groupname
        if description:
            self.description = description

    def __repr__(self):
        return f'<Group {self.groupname}>'

class GroupSchema(Schema):
    """Data Model (schema) of external representation of Group Resource"""
    groupid = fields.Integer()
    groupname = fields.Str()
    description = fields.Str()

group_schema = GroupSchema()

class GroupListSchema(GroupSchema):
    """Data Model (schema) of Response Body of List Groups Collection"""
    href = ma.URLFor("groups.retrieve_group", groupid="<groupid>")

group_list_schema = GroupListSchema(many=True)

class User:
    """Internal representation of User Resource"""
    def __init__(self, userid, username, firstname, lastname, email, phone):
        self.userid = userid
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone

    def update(self,
            username=None,
            firstname=None,
            lastname=None,
            email=None,
            phone=None,
            **kwargs):
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

    def __repr__(self):
        return f'<User {self.username}>'

class UserSchema(Schema):
    """Data Model (schema) of external representation of User Resource"""
    userid = fields.Integer()
    username = fields.Str()
    firstname = fields.Str()
    lastname = fields.Str()
    contactInfo = fields.Dict(
        email=fields.Email(),
        phone=fields.Str()
        )

    @pre_dump
    def from_user_class(self, dump_data, **kwargs):
        """Convert email and phone fields to contactInfo"""
        new_data = copy(dump_data)
        new_data.contactInfo = {
            'email': new_data.email,
            'phone': new_data.phone
            }
        del(new_data.email)
        del(new_data.phone)
        return new_data

    @post_load
    def to_user_dict(self, load_data, **kwargs):
        """Covert contactInfo to email and phone fields"""
        new_data = copy(load_data)
        new_data['email'] = new_data['contactInfo']['email']
        new_data['phone'] = new_data['contactInfo']['phone']
        del(new_data['contactInfo'])
        return new_data

user_schema = UserSchema()

class UserListSchema(UserSchema):
    """Data Model (schema) of Response Body of List Users Collection"""
    href = ma.URLFor("users.retrieve_user", userid="<userid>")

user_list_schema = UserListSchema(many=True)
