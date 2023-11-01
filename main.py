import pygame.midi
import pygame.mixer
import os


def find_active_midi_input():
    pygame.midi.init()
    num_inputs = pygame.midi.get_count()
    for i in range(num_inputs):
        input_info = pygame.midi.get_device_info(i)
        if input_info[2]:
            print(f"Input Device {i}: {input_info[1].decode()}")
            return i


def get_sound_file_name(note):
    base_sound_file = "sound_{}.wav"
    return base_sound_file.format(note)


def main():
    input_device_index = find_active_midi_input()

    if input_device_index is not None:
        midi_input = pygame.midi.Input(input_device_index)
        print("Listening for MIDI input...")

        pygame.mixer.init()  # Initialize the mixer for playing sounds

        # Create a dictionary to track the state of each key (on/off) and the channel playing the sound
        key_state = {}
        key_channels = {}

        while True:
            if midi_input.poll():
                midi_events = midi_input.read(10)
                for event in midi_events:
                    status, key, velocity, _ = event[0]
                    if status == 144:
                        # 144 represents note-on event
                        if velocity > 0:
                            print(f"Note {key} pressed")
                            if key in key_state and key_state[key]:
                                # Key was already pressed, stop the sound
                                key_state[key] = False
                                if key in key_channels:
                                    key_channels[key].stop()
                            else:
                                # Key was not pressed, start the sound
                                key_state[key] = True
                                sound_file = get_sound_file_name(key)
                                if os.path.exists(sound_file):
                                    channel = pygame.mixer.Sound(sound_file).play()
                                    key_channels[key] = channel

                # Check for channels that have finished playing and reset their key state and channel
                finished_keys = [
                    k for k, channel in key_channels.items() if not channel.get_busy()
                ]
                for finished_key in finished_keys:
                    key_state[finished_key] = False
                    key_channels.pop(finished_key, None)

        midi_input.close()


if __name__ == "__main__":
    main()
