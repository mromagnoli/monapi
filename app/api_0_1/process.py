from flask import jsonify
from flask import url_for
from . import api
import psutil
import datetime

@api.route('/process/')
def show_processes():
	response = []
	try:
		for pid in psutil.pids():
			response.append(_makeProcessResponse(pid))
		return jsonify({
			'_status': 'ok',
			'_count': len(response),
			'_data': response
		}), 200
	except Exception, e:
		return jsonify({
			'_status': 'fail',
			'_reason': 'Cannot retrieve info from processes.',
		}), 404

@api.route('/process/<int:pid>')
def show_process(pid):
	try:
		return jsonify({
			'_status': 'ok',
			'_data': _makeProcessResponse(pid)
		}), 200
	except Exception, e:
		return jsonify({
			'_status': 'fail',
			'_reason': 'Cannot retrieve info from processes.',
		}), 404

@api.route('/process/<int:pid>/kill', methods=['GET', 'DELETE'])
def kill_process(pid):
	try:
		p = psutil.Process(pid)
		p.kill()
		return jsonify({
			'_status': 'ok'
		}), 200

	except Exception, e:
		return jsonify({
			'_status': 'fail',
			'_reason': str(e)
		}), 404

@api.route('/process/<int:pid>/renice', methods=['GET'])
@api.route('/process/<int:pid>/renice/<value>', methods=['GET'])
def nice(pid, value=''):
	try:
		p = psutil.Process(pid)
		if not value or value is '':
			value = p.nice() + 1

		value = int(value)
		if value > 20:
			value = 20
		if value < -20:
			value = -20

		p.nice(value)

		return jsonify({
			'_status': 'ok'
		}), 200
	except Exception:
		return jsonify({
			'_status': 'fail',
			'_reason': 'Access denied for process'
		}), 404


def _makeProcessResponse(pid):
	p = psutil.Process(pid)
	return {
		'pid': pid,
		'name': p.name(),
		'user': p.username(),
		'cpu_in_percent': p.cpu_percent(),
		'mem_in_percent': p.memory_percent(),
		'vsz': p.memory_info()[1],
		'rss': p.memory_info()[0],
		'tty': p.terminal(),
		'status': p.status(),
		'nice': p.nice(),
	}