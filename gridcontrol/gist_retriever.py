import requests
class GistRetriever:
	""" A class that retrieves gists for a given github user """

	def __init__(self, username):
		""" Initialize the GistRetriever object with the username whose gists you wish to retrieve """

		self.user = username

	def get_gist_list(self):
		""" Retrieves all the public gists for the user. Gists are returned as a sequence of (gist_description, gist_files) tuples.
		If anything goes wrong, we return None. """

		gist_response = requests.get("https://api.github.com/users/%s/gists" % self.user)
		gist_json = gist_response.json
		gists = [(gist_map['description'], gist_map['files']) for gist_map in gist_json]
		return gists
