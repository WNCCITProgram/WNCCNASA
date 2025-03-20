# Facebook_test
import facebook
import facebook_tokens

msg = "Post some things"

# Create facebook GraphAPI object
graph = facebook.GraphAPI(facebook_tokens.ACCESS_TOKEN)

# Post message
graph.put_object(facebook_tokens.PAGE_ID, "feed", message=msg)
