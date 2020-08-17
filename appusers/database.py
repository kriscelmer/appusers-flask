"""Database Module

This Module implements internal abstraction of User and Group Resources as
Python objects.
Database is simulated in application memory.

User Resource is internally stored in User class object.
Group Resource is internally stored in Group class object.
"""

class Index:
    """Simple index for in-memory Database simulation"""
    def __init__(self):
        self.value = -1

    def next(self):
        self.value += 1
        return self.value

class Group:
    """Internal representation of Group Resource"""

    # Shared (mutable) class attributes
    _db = dict([])
    _index = Index()

    def __init__(self, groupname, description):
        """Group Object constructor automatically inserts to Database"""
        self.groupid = self._index.next()
        self.groupname = groupname
        self.description = description
        self._db[self.groupid] = self

    def update(self, groupname=None, description=None, **kwargs):
        """Update Group Object and commit to Database"""
        if groupname:
            self.groupname = groupname
        if description:
            self.description = description

    def remove(self):
        """Permanently remove Group Object from Database"""
        del self._db[self.groupid]

    @classmethod
    def retrieve(cls, groupid):
         """Retrieve Group Object with groupid from Database"""
         if groupid in cls._db:
             return cls._db[groupid]
         else:
             return None

    @classmethod
    def get_list(cls, filters):
        """Retrieve a filtered list of Group Objects from Database"""
        # filters parameter is ignored in this version
        return list(cls._db.values())

    def __repr__(self):
        return f'<Group {self.groupname}>'

# Initialize some data
admins = Group(
    groupname='admins',
    description='Administrators'
    )
friends = Group(
    groupname='friends',
    description='Friends and Family'
)

class User:
    """Internal representation of User Resource"""

    # Shared (mutable) class attributes
    _db = dict([])
    _index = Index()

    def __init__(self, username, firstname, lastname, email, phone):
        """User Object constructor automatically inserts to Database"""
        self.userid = self._index.next()
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self._db[self.userid] = self

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

    def remove(self):
        """Update User Object and commit to Database"""
        del self._db[self.userid]

    @classmethod
    def retrieve(cls, userid):
        """Retrieve User Object with userid from Database"""
        if userid in cls._db:
            return cls._db[userid]
        else:
            return None

    @classmethod
    def get_list(cls, filters):
        """Retrieve a filtered list of User Objects from Database"""
        # filters parameter is ignored in this version
        return list(cls._db.values())

    def __repr__(self):
        return f'<User {self.username}>'

# Initialize some data
johne = User(
    username='johne',
    firstname='John',
    lastname='Example',
    email='johne@example.com',
    phone='123-444-5555'
    )
lindas = User(
    username='lindas',
    firstname='Linda',
    lastname='Someone',
    email='lindas@example.com',
    phone='123-444-6666'
    )
