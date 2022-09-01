#!/usr/bin/python3

import subprocess
import os.path
from renderlib import *
from easing import *
from urllib.parse import urlparse

# URL to Schedule-XML
scheduleUrl = 'http://videocalc.amilis.ch/releases/schedule.xml'
sessionsUrl = 'https://2022.stateofthemap.org/sessions/{0}/'

# For (really) too long titles
titlemap = {
	#708: "Neue WEB-Anwendungen des LGRB Baden-Württemberg im Überblick"
}


def outroFrames(params):
	# 8 Sekunden

	# 2 Sekunden Fadein Text
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('banderole', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames) ),
			('license', 'style', 'opacity', 0)
		)

	# 2 Sekunde Fadein Lizenz-Logo
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('banderole', 'style', 'opacity', 1),
			('license', 'style', 'opacity', "%.4f" % (float(i)/frames))
		)

	# 4 Sekunde stehen bleiben
	frames = 4*fps
	for i in range(0, frames):
		yield (
			('banderole', 'style', 'opacity', 1),
			('license', 'style', 'opacity', 1)
		)

def introFrames(params):
	# 7 Sekunden

	# 2 Sekunden Text 1
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('box-und-text1',   'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('url',   'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('text1', 'style', 'opacity', "%.4f" % 1),
			('text2', 'style', 'opacity', 0)
		)

	# 1 Sekunde Fadeout Text 1
	frames = 1*fps
	for i in range(0, frames):
		yield (
			('box-und-text1',   'style', 'opacity', 1),
			('url',   'style', 'opacity', 1),
			('text1', 'style', 'opacity', "%.4f" % (1-(float(i)/frames))),
			('text2', 'style', 'opacity', 0)
		)

	# 2 Sekunden Text 2
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('box-und-text1',   'style', 'opacity', 1),
			('url',   'style', 'opacity', 1),
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames))
		)

	# 2 Sekunden stehen bleiben
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('box-und-text1',   'style', 'opacity', 1),
			('url',   'style', 'opacity', 1),
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', 1)
		)

def pauseFrames(params):
	# 12 Sekunden

	# 2 Sekunden Text1 stehen
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 1),
			('text2', 'style', 'opacity', 0)
		)

	# 2 Sekunden Fadeout Text1
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', "%.4f" % (1-easeOutCubic(i, 0, 1, frames))),
			('text2', 'style', 'opacity', 0)
		)

	# 2 Sekunden Fadein Text2
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames))
		)

	# 2 Sekunden Text2 stehen
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', 1)
		)

	# 2 Sekunden Fadeout Text2
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', "%.4f" % (1-easeOutCubic(i, 0, 1, frames)))
		)

	# 2 Sekunden Fadein Text1
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', "%.4f" % (easeOutCubic(i, 0, 1, frames))),
			('text2', 'style', 'opacity', 0)
		)

def debug():
	render(
		'intro.svg',
		'../intro.mkv',
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
		'../outro.mkv',
		outroFrames
	)

def tasks(queue, args, idlist, skiplist):
	# iterate over all events extracted from the schedule xml-export
	for event in events(scheduleUrl):
		if event['room'] not in ('Auditorium A', 'Auditorium B', 'Workshops/"Loop-Cinema" - Room 103'):
			print("skipping room %s (%s)" % (event['room'], event['title']))
			continue


		if (event['id'] in idlist or not idlist) and not 'intro' in skiplist:
		# generate a task description and put them into the queue
			path = urlparse(event['url']).path
			sessionCode = os.path.basename(os.path.dirname(path))
			url = sessionsUrl.format(sessionCode)
			queue.put(Rendertask(
				infile = 'intro.svg',
				outfile = str(event['id'])+".mkv",
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
			outfile = 'outro.mkv',
			sequence = outroFrames
		))

	if not 'pause' in skiplist:
		# place the pause-sequence into the queue
		queue.put(Rendertask(
			infile = 'pause.svg',
			outfile = 'pause.mkv',
			sequence = pauseFrames
		))


