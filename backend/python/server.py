import sys
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from dotenv import load_dotenv
load_dotenv()

from resolve_command import resolve_command, find_room_setup, find_device_setup, find_command_setup, find_command_value_setup
from apply_command import apply_command


def main():
    app = Flask(__name__)
    CORS(app)

    if len(sys.argv) == 1:
        print('First argument must be path to ".json" configuration file')
        return -1

    configuration_file_path = sys.argv[1]
    if not configuration_file_path.endswith('.json') or not os.path.isfile(configuration_file_path):
        print('First argument must be path to ".json" configuration file')
        return -1
        
    with open(configuration_file_path, 'r', encoding='utf-8') as conf_file:
        print('Processing configuration...')
        configuration = json.loads(conf_file.read())
        r_setup = find_room_setup(configuration)
        d_setup = find_device_setup(configuration)
        c_setup = find_command_setup(configuration)
        cv_setup = find_command_value_setup(configuration)
        all_dict = list(set(r_setup[2] + d_setup[1] + c_setup[1] + cv_setup[1]))
        print('Finished processing configuration...')

    @app.route('/command', methods=['POST'])
    def execute_command():
        transcript = request.get_json()['transcript']
        print(f'Transcript: {transcript}')
        command = resolve_command(transcript, r_setup, d_setup, c_setup, cv_setup, all_dict)
        if command is None:
            print(f'Command not recognized')
            return jsonify({"success": False})

        print(f'Command: {command}')
        apply_success = apply_command(configuration, command)
        print(f'Command application: {"success" if apply_success else "failure"}')
        return jsonify({"command": command, "success": apply_success})

    app.run(host="0.0.0.0")
    

if __name__ == '__main__':
    main()
