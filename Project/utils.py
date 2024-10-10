import time
import pygame

def play_sound(file):
    """ Plays sound using pygame """
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

def get_timestamp():
    """ Returns current timestamp """
    return time.strftime("%Y-%m-%d %H:%M:%S")
