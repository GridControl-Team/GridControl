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
		gist_json = gist_response.json()
		gists = []
		for gist_map in gist_json:
			gists.append({'id': gist_map['id'], 'description': gist_map['description'], 'files': gist_map['files']})
		return gists

	def get_file_text(self, raw_url):
		file_text = requests.get(raw_url).text
		return file_text
