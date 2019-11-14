import sys
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import yaml

from resolve_command import resolve_command
from apply_command import apply_command


def main():
    app = Flask(__name__)
    
    if len(sys.argv) == 1:
        print('First argument must be path to ".yaml" configuration file')
        return -1

    configuration_file_path = sys.argv[1]
    if not configuration_file_path.endswith('.yaml') or not os.path.isfile(configuration_file_path):
        print('First argument must be path to ".yaml" configuration file')
        return -1
        
    with open(configuration_file_path, 'r') as stream:
        configuration = yaml.safe_load(stream)
    
    @app.route('/command', methods=['POST'])
    def execute_command():
        transcript = request.get_json()['transcript']
        command = resolve_command(configuration, transcript)
        apply_command(configuration, command)
        return jsonify({ "command": command })
        
    CORS(app)
    app.run(host="0.0.0.0")
    

if __name__ == '__main__':
    main()
