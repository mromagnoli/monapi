from flask import jsonify
from . import api
import psutil

@api.route('/process/')
def show_process():
	response = []
	for pid in psutil.pids():
		p = psutil.Process(pid)
		response.append({
			'pid': pid,
			'name': p.name()
		})

	return jsonify({'pids': response})

@api.route('/process/kill/<int:pid>')
def kill_process(pid):
	p = psutil.Process(pid)
	p.kill()
	return jsonify({
		'status': 'ok'
	}), 200