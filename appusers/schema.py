"""Data Schema module

This module declares Data Schema of User and Group Resources.
group_schema object provides serialization (dump) of Group Resource from Python
object to dict.
group_list_schema object provides serialization of lists
of Group objects to Data Model of List Groups Collection operation
Response Body.

user_schema object provides serialization of User Resource.
user_list_schema object provides serialization of lists
of User objects to Data Model of List Users Collection operation
Response Body.
"""
from copy import copy
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, pre_load, post_dump, validate


# Marshmallow object is initialized in Application Factory
ma = Marshmallow()

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

class UserSchema(Schema):
    """Data Model (schema) of external representation of User Resource"""
    userid = fields.Integer()
    username = fields.Str()
    firstname = fields.Str()
    lastname = fields.Str()
    email = fields.Email()
    phone = fields.Str()

    @post_dump
    def from_user_class(self, dump_data, **kwargs):
        """Convert email and phone fields to contactInfo"""
        new_data = copy(dump_data)
        new_data['contactInfo'] = {
            'email': new_data['email'],
            'phone': new_data['phone']
            }
        del(new_data['email'])
        del(new_data['phone'])
        return new_data

    @pre_load
    def to_user_dict(self, load_data, **kwargs):
        """Covert contactInfo to email and phone fields"""
        new_data = copy(load_data)
        # Handle partial User Data Model in Update User Resource operation
        if 'contactInfo' in new_data:
            if 'email' in new_data['contactInfo']:
                new_data['email'] = new_data['contactInfo']['email']
            if 'phone' in new_data['contactInfo']:
                new_data['phone'] = new_data['contactInfo']['phone']
            del(new_data['contactInfo'])
        return new_data

user_schema = UserSchema()

class UserListSchema(UserSchema):
    """Data Model (schema) of Response Body of List Users Collection"""
    href = ma.URLFor("users.retrieve_user", userid="<userid>")

user_list_schema = UserListSchema(many=True)
