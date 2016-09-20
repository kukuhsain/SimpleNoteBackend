from google.appengine.ext import ndb
from utils.password_hashing import PasswordHashing
from utils.token_hashing import TokenHashing

class User(ndb.Model):
	email = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	session = ndb.BooleanProperty()
	created_date = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def _check_email_availability(cls, email):
		if cls.get_user_by_email(email):
			return False
		else:
			return True

	@classmethod
	def get_user_by_email(cls, email):
		return cls.query(cls.email==email).get()

	@classmethod
	def register(cls, email, password):
		if cls._check_email_availability(email):
			hashed_password = PasswordHashing().make_hashing_password(email, password)
			user = cls(email=email, password=hashed_password, session=False)
			user.put()
			return user.key.id()
		else:
			return False

	@classmethod
	def login(cls, email, password):
		user = cls.get_user_by_email(email)
		if user:
			password_validation_result = PasswordHashing().validate_password(email, password, user.password)
			if password_validation_result:
				user.session = True
				user.put()
				return TokenHashing().make_secure_value(user.key.id())
			else:
				return False
		else:
			return False

	@classmethod
	def logout(cls, token):
		user_id = TokenHashing().check_secure_value(token)
		user = cls.get_by_id(user_id)
		user.session = False
		user.put()
