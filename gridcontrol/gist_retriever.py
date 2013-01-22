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
		gist_response = requests.get("https://api.github.com/users/%s/gists" % self.user)
		gist_json = gist_response.json()
		return [{'id': g['id'], 'description': g['description'], 'files': g['files']} for g in gist_json]

	def get_gist_history(self, gist_id):
		""" This method retrieves the revision history for a given gist.
		History is returned as a list of (revision, URL) tuples."""
		gist_response = requests.get("https://api.github.com/gists/%s" % str(gist_id))
		gist_json = gist_response.json()
		return [(revision["url"], revision["version"]) for revision in gist_json["history"]]
	
	def get_gist_version(self, gist_id, gist_version):
		"""This method retrieves the raw URL of a specific version of a gist, given the URL to that version"""
		url = "https://api.github.com/gists/%s/%s" % (str(gist_id), str(gist_version))
		gist_info = requests.get(url).json()
		return [{"filename": file_info["filename"], "text_url": file_info["raw_url"]} for file_info in gist_info["files"].values()] 


	def get_file_text(self, raw_url):
		file_text = requests.get(raw_url).text
		return file_text
