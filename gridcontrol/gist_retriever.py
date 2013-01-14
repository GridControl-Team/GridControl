import requests
from django.conf import settings
class GistRetriever:
	""" A class that retrieves gists for a given github user."""

	def __init__(self, username):
		""" Initialize the GistRetriever object with the username whose gists you wish to retrieve """

		self.user = username

	def get_gist_list(self):
		"""	Retrieves all the public gists for the user. Gists are returned as a list of dictionaries. Each dictionary corresponds to a gist. 
			Dictionaries have the following keys:
				id: the ID of the gist
				description: the (user specified) description
				files: a dictionary where the keys are filenames and the values are dictionaries containing the URL to the file, the file size and the file name (again)
		"""
		if settings.GRIDCONTROL_GIST_MAX_SIZE:
			max_size = settings.GRIDCONTROL_GIST_MAX_SIZE * 1024
		else:
			max_size = DEFAULT_MAX_SIZE * 1024
		gist_response = requests.get("https://api.github.com/users/%s/gists" % self.user)
		gist_json = gist_response.json()
		return [{'id': g['id'], 'description': g['description'], 'files': g['files']} for g in gist_json]


	def get_file_text(self, raw_url):
		file_text = requests.get(raw_url).text
		return file_text
