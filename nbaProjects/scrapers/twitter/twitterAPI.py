import MySQLdb as mdb
import twitter
import pprint

api=twitter.Api(consumer_key='PzuOk2YPzqZ9nwV9LmmIw',
	consumer_secret='1mCyBwjm8CVR4mRJCRYrvV0zDgLULm2sXyU0k20xV34',
	access_token_key='36465802-JywQQyXFNUMjUyqozJFmOG5quq5EoWCOJFmrYcYvc',
	access_token_secret='4tkbcpP9Wgi6AX7ZIx5VbWSdYEuPEiu46gC6SoYThYY')

users = api.GetFriends(user='mzappitello', cursor=-1)

print len(users)

#for u in users:
#	print u.screen_name
