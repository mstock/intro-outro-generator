#!/usr/bin/python3

import subprocess
import os.path
from renderlib import *
from easing import *
from schedulelib import *
from urllib.parse import urlparse

# URL to Schedule-XML
scheduleUrl = 'http://video-archiv.xemo.ch/releases/schedule.xml'
sessionsUrl = 'https://2025.stateofthemap.org/sessions/{0}/'

# For (really) too long titles
titlemap = {
	#708: "Neue WEB-Anwendungen des LGRB Baden-Württemberg im Überblick"
}


def outroFrames(params):
	# 2 Sekunden Fadein Text
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('event-info-background', 'style', 'opacity', 1),
			('license-logo', 'style', 'opacity', 0),
			('license-url', 'style', 'opacity', 0),
			('recorded-by', 'style', 'opacity', 0),
			('recorded-by-background', 'style', 'opacity', 0)
		)

	# 2 Sekunde Fadein Lizenz-Logo/Recorded by
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('event-info-background', 'style', 'opacity', 1),
			('license-logo', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('license-url', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('recorded-by', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('recorded-by-background', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames))
		)

	# 6 Sekunde stehen bleiben
	frames = 6*fps
	for i in range(0, frames):
		yield (
			('event-info-background', 'style', 'opacity', 1),
			('license-logo', 'style', 'opacity', 1),
			('license-url', 'style', 'opacity', 1),
			('recorded-by', 'style', 'opacity', 1),
			('recorded-by-background', 'style', 'opacity', 1)
		)

def introFrames(params):
	# 2 Sekunden Text 1
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('talk-url',   'style', 'opacity', 0),
			('event-info', 'style', 'opacity', 1),
			('event-info-background', 'style', 'opacity', 1),
			('talk-info', 'style', 'opacity', 0),
			('talk-info-background', 'style', 'opacity', 0),
		)

	# 2 Sekunden Fadein Titel und Speaker mit Info-Hintergrund
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('talk-url', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('event-info', 'style', 'opacity', "%.4f" % (1 - easeOutCubic(i, 0, 1, frames))),
			('event-info-background', 'style', 'opacity', "%.4f" % (1 - easeOutCubic(i, 0, 1, frames))),
			('talk-info', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('talk-info-background', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames))
		)

	# 6 Sekunden stehen bleiben
	frames = 6*fps
	for i in range(0, frames):
		yield (
			('talk-url',   'style', 'opacity', 1),
			('event-info', 'style', 'opacity', 0),
			('event-info-background', 'style', 'opacity', 0),
			('talk-info', 'style', 'opacity', 1),
			('talk-info-background', 'style', 'opacity', 1)
		)

def debug():
	render(
		'intro.svg',
		'../intro.ts',
		introFrames,
		{
			'$id': 10069,
			'$title': 'Community growth: What we learned about improving the membership and diversity of OSM Kenya through the community impact microgrants.',
			'$subtitle': '',
			'$personnames': 'Laura Mugeha'
		}
	)

	render(
		'outro.svg',
		'../outro.ts',
		outroFrames
	)

def tasks(queue, args, idlist, skiplist):
	# iterate over all events extracted from the schedule xml-export
	for event in events(scheduleUrl):
		if event['room'] not in ('Apo', 'Mayon', 'Pulag'):
			print("skipping room %s (%s)" % (event['room'], event['title']))
			continue


		if (event['id'] in idlist or not idlist) and not 'intro' in skiplist:
		# generate a task description and put them into the queue
			path = urlparse(event['url']).path
			sessionCode = os.path.basename(os.path.dirname(path))
			url = sessionsUrl.format(sessionCode)
			queue.put(Rendertask(
				infile = 'intro.svg',
				outfile = str(event['id'])+".ts",
				sequence = introFrames,
				parameters = {
					'$id': event['id'],
					'$title': event['title'],
					'$url': url,
					#'$subtitle': event['subtitle'],
					'$personnames': event['personnames']
				}
			))

	if not 'outro' in skiplist:
		# place a task for the outro into the queue
		queue.put(Rendertask(
			infile = 'outro.svg',
			outfile = 'outro.ts',
			sequence = outroFrames
		))
