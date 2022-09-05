# # Convert user token to page token
# import requests

page_id = "106479581966092"
# f_access_token = "EAAJY4xlZCWQkBAJWeAXE4CirZCBFCbwUVPN55aWBPTQ1VG6M2NVgEUZAkPA5PThdlMfaeZBfh0fkM5Wc2ZAHq7ilyynSHjdARqdkv3bsGeoZAZBskRg9SVToe5YjvEJVivf7ZCQ2v7kojoSPG5FMuXX8UJ8dCXvzCIefMj07pKhpnsgn7BZBTdoSL"
# r = requests.get(
#     f"https://graph.facebook.com/{page_id}?fields=access_token={f_access_token}")

# print(r.json())


# Convert user token to page token
import requests

facebook_access_token = "EAAJY4xlZCWQkBAAekX9vCstTT9IIEgU8wfymrFb5KJnDdrCKxp8X4cjKXq4d6SaCLRKxbsGz15yL3ZBgrYrSXsKP1B1u3boMZABqAXTBnRZAgnHWzC5BLx5gLIS28DWAQN67Kl3TBzZCg35n3vn1COYQgLSclaGzVzHyznZCw8tBDZBnsXHRVKO"

r = requests.get(f"https://graph.facebook.com/{page_id}?fields=access_token&access_token={facebook_access_token}")

print(r.json())