import os


def list_audio_devices():
    import pyaudio as pa
    a = pa.PyAudio()

    for ndx in range(a.get_device_count()):
        print(a.get_device_info_by_index(ndx))
        print()


ENV_VAR_INFO = [
    {
        'name': 'SHH_API_PORT',
        'desc': 'Port to run the API on',
        'default': '5000'
    },
    {
        'name': 'SHH_API_KEY',
        'desc': 'API Key to use for authorization to access the API',
        'default': 'tmp_key'
    },
    {
        'name': 'SHH_CONFIG_BASE_DIR',
        'desc': 'Base directory for config files to be stored',
        'default': 'config/'
    },
    {
        'name': 'SHH_MIC_DEVICE_INDEX',
        'desc': 'Index of the microphone audio device, as given by PyAudio',
        'default': 'none',
        'additional_info_func': list_audio_devices
    },
    {
        'name': 'SHH_RG_EMAIL',
        'desc': 'A Reelgood email to use if using the account functionality'
    },
    {
        'name': 'SHH_RG_PASS',
        'desc': 'The password for the associated Reelgood account (if used)'
    }
]


def main():
    if '.env' in os.listdir('.'):
        print('.env already exists, skipping')
        exit(1)

    env_vars = {}

    for env_var in ENV_VAR_INFO:
        print(f"Adding {env_var['name']}...")
        print(f"Description: {env_var['desc']}")
        print(f"Default (if prompt left blank): {env_var['default']}")
        if 'additional_info_func' in env_var:
            env_var['additional_info_func']()

        input_str = input(f"Give a value for {env_var['name']}: ")

        if len(input_str.strip()) > 0:
            env_vars[env_var['name']] = input_str.strip()
        elif env_var.get('default') is not None:
            env_vars[env_var['name']] = env_var['default']

    print('Writing to .env')
    with open('.env', 'w') as env_file:
        for ev_name, ev_val in env_vars.items():
            env_file.write(f"{ev_name}={ev_val}\n")


if __name__ == '__main__':
    main()
