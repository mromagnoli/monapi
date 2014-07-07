from flask import jsonify
from flask import url_for
from . import api
from flask import request
from subprocess import PIPE
import psutil
import threading
import shlex

import sys

@api.route('/process', methods=['GET', 'POST'])
def process():
    """Method used either by GET or POST requests

    """
    if request.method == 'GET':
        return _retrieve_all_process()
    elif request.method == 'POST':
        return _create_process()
    else:
        return jsonify({
                '_status': 'fail',
                '_reason': 'Internal server error.',
            }), 500

@api.route('/process/<int:pid>')
def show_process(pid):
    """Get process info by PID.

    :param pid: The Process ID to retrieve
    :type pid: int

    :return Process info as JSON
    """
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
    """Kill a process given

    :param pid: The Process ID to retrieve
    :type pid: int

    :return JSON
    """

    try:
        p = psutil.Process(pid)
        if (p.status() == psutil.STATUS_ZOMBIE):
            p.terminate()
        else:
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
def renice(pid, value=''):
    """Change priority of a process given

    :param pid: The Process ID to retrieve
    :type pid: int

    :param value: The value to the priority to set if given, otherwise rise by one
    :type pid: int

    :return JSON
    """

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

@api.route('/process/<int:pid>/status', methods=['GET'])
def process_status(pid):
    """Retrieve status of a process given

    :param pid: The Process ID to retrieve
    :type pid: int

    :return JSON
    """
    try:
        p = psutil.Process(pid)

        return jsonify({
            '_status':'ok',
            '_data': {'process_status': p.status()}
        })
    except Exception, e:
        return jsonify({
            '_status': 'fail',
            '_reason': 'Cannot retrieve info from processes.'
        }), 404

@api.route('/connections', methods=['GET'])
def connections():
    """Retrieve all connections opened in system

    :return JSON
    """
    connections = []
    try:
        for conn in psutil.net_connections():
            connections.append(_makeConnectionResponse(conn))
        return jsonify({
            '_status': 'ok',
            '_count': len(connections),
            '_data': connections
        }), 200
    except Exception, e:
        return jsonify({
            '_status': 'fail',
            '_reason': 'Cannot retrieve info from connections.',
        }), 404

def _retrieve_all_process():
    """Get all process running in local system

    :return JSON
    """

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

new_process = None
def _create_process():
    """Create a new process based on POSTed data from user.

    POSTed format: {"path": "/path/to/exec", "params": "-as -in /shell/format --optional"}

    :return JSON
    """

    try:
        path = request.get_json(force=True)['path']
        params = request.get_json(force=True)['params']
        if path is not None or path == '':
            try:
                t = threading.Thread(target = __launch_process, args = (path, params))
                t.start()
                t.join()
            except Exception, e:
                raise Exception

            if not type(new_process) is psutil.Popen:
                raise Exception

            return jsonify({
                '_status': 'ok',
                'pid': new_process.pid
            })
        else:
            raise Exception
    except Exception, e:
        return jsonify({
            '_status': 'fail',
            '_reason': 'Cannot create new process.',
        }), 400

def __launch_process(path, params):
    """Create a new process. Intended for thread usage.

    :param path: The path of the command to execute
    :type path: str

    :param params: The params for the command if needed
    :type params: str

    :return void
    """

    try:
        if path is None or \
            path == '' or \
            params is None:
             raise Exception

        global new_process
        args = shlex.split(path + ' ' + params)
        new_process = psutil.Popen(args, stdout=PIPE)
    except Exception, e:
        new_process = e

    return


def _makeProcessResponse(pid):
    """Generate a dict with data of a process given

    :param pid: The Process ID
    :type pid: int

    :return dict
    """

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

def _makeConnectionResponse(conn):
    """Generate a dict with data of a connection given

    :param conn: The connection data
    :type conn: pconn

    :return dict
    """
    import socket
    FAMILY = {
        socket.AF_INET: 'AF_INET',
        socket.AF_INET6: 'AF_INET6',
        socket.AF_UNIX: 'AF_UNIX',
    }
    TYPE = {
        socket.SOCK_STREAM: 'SOCK_STREAM',
        socket.SOCK_DGRAM: 'SOCK_DGRAM'
    }

    return {
        'fd': conn.fd,
        'family': FAMILY[conn.family],
        'type': TYPE[conn.type],
        'local_addr': conn.laddr,
        'remote_addr': conn.raddr,
        'status': conn.status,
        'pid': conn.pid
    }
