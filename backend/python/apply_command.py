import vlc
import re
import math


class Radio:
    def __init__(self):
        self.player = vlc.MediaPlayer("song.mp3")
        self.volume = 50
        self.set_vol(self.volume)

    def play(self):
        if self.player.is_playing():
            return False

        self.player = vlc.MediaPlayer("song.mp3")
        self.player.play()
        return True

    def pause(self):
        if not self.player.is_playing():
            return False
        self.player.stop()
        return True

    def toggle(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()
        return True

    def set_vol(self, vol):
        if vol < 0 or vol > 16:
            return False

        self.player.audio_set_volume(math.floor(100 / 16 * vol))
        self.volume = vol
        return True

    def vol_up(self):
        return self.set_vol(self.volume + 1)

    def vol_down(self):
        return self.set_vol(self.volume - 1)


radio = Radio()
SET_A3_VOL = re.compile(r'^set A3 vol (\d+)$', re.IGNORECASE)


def apply_command(configuration, command):
    if command == 'on A3':
        return radio.play()
    elif command == 'off A3':
        return radio.pause()
    elif command == 'toggle A3':
        return radio.toggle()
    elif command == 'set A3 vol down':
        return radio.vol_down()
    elif command == 'set A3 vol up':
        return radio.vol_up()
    elif 'A3' in command:
        m_a3_vol = SET_A3_VOL.match(command)
        if m_a3_vol is not None:
            vol = int(m_a3_vol.group(1))
            return radio.set_vol(vol)

    return False
