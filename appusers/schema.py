"""Data Models module

This module declares Data Schema of User and Group Resources.

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

groups_filters_schema object provides deserialization and validation of
List Groups Collection operation Query String parameters.

users_filters_schema object provides deserialization and validation of
List users Collection operation Query String parameters.
"""
from copy import copy
from string import ascii_letters, digits
from flask_marshmallow import Marshmallow
from marshmallow import (Schema, fields, pre_load, post_dump, validate,
    validates, ValidationError)


# Marshmallow object is initialized in Application Factory
ma = Marshmallow()

class GroupSchema(Schema):
    """Data Model (schema) of external representation of Group Resource"""
    groupid = fields.Integer(dump_only=True)
    groupname = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=20),
            validate.Regexp("^[A-Za-z]\w*$")
            ]
        )
    description = fields.Str(required=True)

    @pre_load
    def ignore_groupid(self, load_data, **kwargs):
        """Remove groupid from Request data, if present"""
        new_data = copy(load_data)
        if 'groupid' in new_data:
            del(new_data['groupid'])
        return new_data

group_schema = GroupSchema()

class GroupListSchema(GroupSchema):
    """Data Model (schema) of Response Body of List Groups Collection"""
    href = ma.URLFor("groups.retrieve_group", groupid="<groupid>")

group_list_schema = GroupListSchema(many=True)

class GroupsQueryStringSchema(Schema):
    """Data Model of List Groups Collection operation Query String parameters"""
    groupname = fields.Str()
    offset = fields.Integer(validate=validate.Range(min=0), missing=0)
    limit = fields.Integer(validate=validate.Range(min=1))
    return_fields = fields.Str(data_key='fields')
    sortBy = fields.Str()
    member = fields.Integer(validate=validate.Range(min=0))

    @validates('groupname')
    def validate_groupname(self, data, **kwargs):
        """Validate groupname Query String parameter value"""
        names = data.split(',')
        for n in names:
            if n == '' or set(n).difference(ascii_letters + digits):
                raise ValidationError(
                    f'Unexpected string in Query String "groupname": "{n}"'
                    )
        return True

    @validates('return_fields')
    def validate_return_fields(self, data, **kwargs):
        """Validate fields Query String parameter value"""
        fields_list = set(['groupid', 'groupname', 'description'])
        return_fields = set(data.split(','))
        if return_fields.difference(fields_list):
            raise ValidationError(
                f'Unexpected names in Query String "field": {return_fields.difference(fields_list)}'
                )
        return True

    @validates('sortBy')
    def validate_sort_by(self, data, **kwargs):
        """Validate sortBy Query String parameter value"""
        fields_list = set(['groupid', 'groupname', 'description'])
        sort_fields = set(data.split(','))
        for f in sort_fields:
            if f and f[0] == '-':
                f = f[1:]
            if f not in fields_list:
                raise ValidationError(
                    f'Unexpected names in Query String "sortBy": {f}'
                    )
        return True

groups_filters_schema = GroupsQueryStringSchema()

class UserSchema(Schema):
    """Data Model (schema) of external representation of User Resource"""
    userid = fields.Integer(dump_only=True)
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=20),
            validate.Regexp("^[A-Za-z]\w*$")
            ]
        )
    firstname = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=30),
            validate.Regexp("^\w[\w\-]*$")
            ]
        )
    lastname = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=30),
            validate.Regexp("^\w[\w\-]*$")
            ]
        )
    email=fields.Email(
        required=True
        )
    phone=fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=20),
            validate.Regexp("^[0-9\+][0-9\-\.]+$")
            ]
        )

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
        """Covert contactInfo to email and phone fields and ignore userid"""
        new_data = copy(load_data)
        # Handle partial User Data Model in Update User Resource operation
        if 'contactInfo' in new_data:
            if 'email' in new_data['contactInfo']:
                new_data['email'] = new_data['contactInfo']['email']
            if 'phone' in new_data['contactInfo']:
                new_data['phone'] = new_data['contactInfo']['phone']
            del(new_data['contactInfo'])
        # Ignore 'userid' if present in Request data
        if 'userid' in new_data:
            del(new_data['userid'])
        return new_data

user_schema = UserSchema()

class UserListSchema(UserSchema):
    """Data Model (schema) of Response Body of List Users Collection"""
    href = ma.URLFor("users.retrieve_user", userid="<userid>")

user_list_schema = UserListSchema(many=True)

class UsersQueryStringSchema(Schema):
    """Data Model of List Users Collection operation Query String parameters"""
    username = fields.Str()
    first = fields.Str()
    last = fields.Str()
    email = fields.Email(validate=validate.Email())
    phone = fields.Str(validate=[
        validate.Length(min=6, max=20),
        validate.Regexp("^[0-9\+][0-9\-\.]+$")
        ])
    offset = fields.Integer(validate=validate.Range(min=0), missing=0)
    limit = fields.Integer(validate=validate.Range(min=1))
    return_fields = fields.Str(data_key='fields')
    sortBy = fields.Str(missing='userid')
    locked = fields.Boolean(truthy={'true'}, falsy={'false'})
    admin = fields.Boolean(truthy={'true'}, falsy={'false'})

    @validates('username')
    def validate_username(self, data, **kwargs):
        """Validate username Query String parameter value"""
        names = data.split(',')
        for n in names:
            if n == '' or set(n).difference(ascii_letters + digits):
                raise ValidationError(
                    f'Unexpected string in Query String "username": "{n}"'
                    )
        return True

    @validates('first')
    def validate_first(self, data, **kwargs):
        """Validate first Query String parameter value"""
        names = data.split(',')
        for n in names:
            if n == '' or set(n).difference(ascii_letters + digits + '-'):
                raise ValidationError(
                    f'Unexpected string in Query String "first": "{n}"'
                    )
        return True

    @validates('last')
    def validate_first(self, data, **kwargs):
        """Validate first Query String parameter value"""
        names = data.split(',')
        for n in names:
            if n == '' or set(n).difference(ascii_letters + digits + '-'):
                raise ValidationError(
                    f'Unexpected string in Query String "first": "{n}"'
                    )
        return True

    @validates('return_fields')
    def validate_return_fields(self, data, **kwargs):
        """Validate fields Query String parameter value"""
        fields_list = set(['userid', 'username', 'firstname',
                'lastname', 'email', 'phone'])
        return_fields = set(data.split(','))
        if return_fields.difference(fields_list):
            raise ValidationError(
                f'Unexpected names in Query String "field": {return_fields.difference(fields_list)}'
                )
        return True

    @validates('sortBy')
    def validate_sort_by(self, data, **kwargs):
        """Validate sortBy Query String parameter value"""
        fields_list = set(['userid', 'username', 'firstname',
                'lastname', 'email', 'phone'])
        sort_fields = set(data.split(','))
        for f in sort_fields:
            if f and f[0] == '-':
                f = f[1:]
            if f not in fields_list:
                raise ValidationError(
                    f'Unexpected names in Query String "sortBy": {f}'
                    )
        return True

users_filters_schema = UsersQueryStringSchema()
