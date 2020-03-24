#/usr/bin/env python3
"""
Syncthing-GTK - IDDialog

Dialog with Device ID and generated QR code
"""

from syncthing_gtk.uibuilder import UIBuilder
import urllib, ssl
import os, tempfile, logging
log = logging.getLogger("IDDialog")

#This is only needed for QR code reading
ssl._create_default_https_context = ssl._create_unverified_context

class IDDialog(object):
	""" Dialog with Device ID and generated QR code """
	def __init__(self, app, device_id):
		self.app = app
		self.device_id = device_id
		self.setup_widgets()
		self.load_data()
	
	def __getitem__(self, name):
		""" Convince method that allows widgets to be accessed via self["widget"] """
		return self.builder.get_object(name)
	
	def show(self, parent=None):
		if not parent is None:
			self["dialog"].set_transient_for(parent)
		self["dialog"].show_all()
	
	def close(self):
		self["dialog"].hide()
		self["dialog"].destroy()
	
	def setup_widgets(self):
		# Load glade file
		self.builder = UIBuilder()
		self.builder.add_from_file(os.path.join(self.app.gladepath, "device-id.glade"))
		self.builder.connect_signals(self)
		self["vID"].set_text(self.device_id)
	
	def load_data(self):
		""" Loads QR code from Syncthing daemon """
		uri = "%s/qr/?text=%s" % (self.app.daemon.get_webui_url(), self.device_id)
		api_key = self.app.daemon.get_api_key()
		opener = urllib.request.build_opener(urllib.request.HTTPSHandler())
		if not api_key is None:
			opener.addheaders = [("X-API-Key", api_key)]
		a = opener.open(uri)
		data = a.read()
		tf = tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False)
		tf.write(data)
		tf.close()
		self["vQR"].set_from_file(tf.name)
		os.unlink(tf.name)
	
	def cb_btClose_clicked(self, *a):
		self.close()
	
	def cb_syncthing_qr(self, io, results, *a):
		"""
		Called when QR code is loaded or operation fails. Image is then
		displayed in dialog, failure is silently ignored.
		"""
		try:
			ok, contents, etag = io.load_contents_finish(results)
			if ok:
				# QR is loaded, save it to temp file and let GTK to handle
				# rest
				tf = tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False)
				tf.write(contents)
				tf.close()
				self["vQR"].set_from_file(tf.name)
				os.unlink(tf.name)
		except Exception as e:
			log.exception(e)
			return
		finally:
			del io


