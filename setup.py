#!/usr/bin/python3

from setuptools import setup
from setuptools.command.build_py import build_py
from subprocess import PIPE, run
import glob, os, traceback

import versioneer

APP_ICON_SIZES = (16, 24, 32, 64, 128, 256)
SI_ICON_SIZES = (16, 24, 32)

class BuildPyEx(build_py):
	""" Little extension to install command; Allows --nostdownloader argument """
	user_options = build_py.user_options + [
		# Note to self: use
		# # ./setup.py build_py --nostdownloader install
		# to enable this option
		#
		('nostdownloader', None, 'prevents installing StDownloader module; disables autoupdate capability'),
		('nofinddaemon', None, 'prevents installing FindDaemonDialog module; always uses only default path to syncthig binary'),
	]
	
	def run(self):
		build_py.run(self)
	
	def initialize_options(self):
		build_py.initialize_options(self)
		self.nostdownloader = False
		self.nofinddaemon = False
	
	@staticmethod
	def _remove_module(modules, to_remove):
		for i in modules:
			if i[1] == to_remove:
				modules.remove(i)
				return
		
	
	def find_package_modules(self, package, package_dir):
		rv = build_py.find_package_modules(self, package, package_dir)
		if self.nostdownloader:
			BuildPyEx._remove_module(rv, "stdownloader")
		if self.nofinddaemon:
			BuildPyEx._remove_module(rv, "finddaemondialog")
		return rv

def find_mos(parent, lst=[]):
	for f in os.listdir(parent):
		fp = os.path.join(parent, f)
		if os.path.isdir(fp):
			find_mos(fp, lst)
		elif fp.endswith(".mo"):
			lst += [ fp ]
	return lst

if __name__ == "__main__" : 
	data_files = [
		('share/syncthing-gtk', glob.glob("glade/*.glade") ),
		('share/syncthing-gtk', glob.glob("scripts/syncthing-plugin-*.py") ),
		('share/syncthing-gtk/icons', [
				"icons/%s.svg" % x for x in (
					'add_node', 'add_repo', 'address',
					'announce', 'clock', 'compress', 'cpu', 'dl_rate',
					'eye', 'folder', 'global', 'home', 'ignore', 'lock',
					'ram', 'shared', 'show_id', 'show_id', 'sync', 'thumb_up',
					'up_rate', 'version', 'rescan'
			)] + [
				"icons/%s.png" % x for x in (
					'restart', 'settings', 'shutdown', "st-gtk-logo"
			)]),
		('share/man/man1', glob.glob("doc/*") ),
		('share/icons/hicolor/64x64/emblems', glob.glob("icons/emblem-*.png") ),
		('share/pixmaps', ["icons/syncthing-gtk.png"]),
		('share/applications', ['syncthing-gtk.desktop'] ),
		('share/metainfo', ['me.kozec.syncthingtk.appdata.xml'] ),
	] + [
		(
			'share/icons/hicolor/%sx%s/apps' % (size,size),
			glob.glob("icons/%sx%s/apps/*" % (size,size))
		) for size in APP_ICON_SIZES 
	] + [
		(
			'share/icons/hicolor/%sx%s/status' % (size,size),
			glob.glob("icons/%sx%s/status/*" % (size,size))
		) for size in SI_ICON_SIZES
	] + [
		("share/" + os.path.split(x)[0], (x,)) for x in find_mos("locale/")
	]
	setup(
		name = 'syncthing-gtk',
		version=versioneer.get_version(),
		description = 'GTK3 GUI for Syncthing',
		url = 'https://github.com/syncthing/syncthing-gtk',
		packages = ['syncthing_gtk'],
		install_requires = (
		    'python-dateutil',
		    'bcrypt',
		),
		data_files = data_files,
		scripts = [ "scripts/syncthing-gtk" ],
		cmdclass = { 'build_py': BuildPyEx, 'versioneer': versioneer.get_cmdclass() },
	)
