"""
General & Geometric Utilities 
"""

import math
import tkinter as tk
from typing import Union
from inspect import getmembers, isfunction

from type_hints import Num_T, Point_T, Point2D_T

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.0.0"


def euclidean_distance(point1: Point_T, point2: Point_T) -> float:
    """(float) Returns the distance between points 'point1' and 'point2'"""
    return sum((a - b) ** 2 for a, b in zip(point1, point2)) ** .5


def vector_length(vector: Point_T) -> float:
    """(float) Returns the length of 'vector'"""
    return sum(i ** 2 for i in vector) ** .5


def angular_difference(angle1: Num_T, angle2: Num_T) -> Num_T:
    """(float) Returns the smallest angle between 'angle2' & 'angle1' (in the range [-pi, +pi])"""
    delta = ((angle2 - angle1 + math.pi) % (2 * math.pi)) - math.pi

    return delta


def angle_between(point1: Point_T, point2: Point_T) -> float:
    """(float) Returns the angle between two points"""
    dx, dy = tuple(b - a for a, b in zip(point1, point2))
    return math.atan2(dy, dx)


def rotate_toward(angle, target, maximum_rotation):
    """(float) Rotates 'angle' toward 'target', by no more than 'maximum_rotation'"""
    delta_angle = angular_difference(angle, target)

    if abs(delta_angle) > maximum_rotation:
        multiplier = 1 if delta_angle > 0 else -1
        return angle + maximum_rotation * multiplier
    else:
        return target


def rectangles_intersect(top_left1: Point2D_T, bottom_right1: Point2D_T,
                         top_left2: Point2D_T, bottom_right2: Point2D_T) -> bool:
    """(bool) Returns True iff two rectangles intersect
    
    Parameters:
        top_left1 (tuple<num, num>): The top-left corner position of rectangle 1
        bottom_right1 (tuple<num, num>): The bottom-right corner position of rectangle 1
        top_left2 (tuple<num, num>): The top-left corner position of rectangle 2
        bottom_right2 (tuple<num, num>): The bottom-right corner position of rectangle 2
    """
    left1, topoint1 = top_left1
    right1, bottom1 = bottom_right1

    left2, topoint2 = top_left2
    right2, bottom2 = bottom_right2

    return not (left1 > right2 or right1 < left2 or topoint1 > bottom2 or bottom1 < topoint2)


def rotate_point(point, angle):
    """(float, float) Returns result of rotating 'point' by 'angle' radians
    
    Parameters:
        point (tuple<num, num>): The (x, y) point to rotate
        angle (num): The angle by which to rotate
    """
    cos = math.cos(angle)
    sin = math.sin(angle)

    x, y = point

    return cos * x - sin * y, sin * x + cos * y


def normalise_vector(vector):
    """(num, ...) Normalises 'vector' (scales to unit vector)"""
    magnitude = vector_length(vector)
    return tuple(i / magnitude for i in vector)


def inherit_docstrings(cls):
    """Class decorator for methods to inherit super classes docstrings

    Parameters:
        cls (Class): The class the wrap with the decorator
    """
    # find all class functions
    for name, func in getmembers(cls, isfunction):
        # ignore methods with docstrings
        if func.__doc__:
            continue

        # find super methods
        for parent in cls.__mro__[1:]:
            if hasattr(parent, name):
                # inject the docstring from the parent
                func.__doc__ = getattr(parent, name).__doc__
    return cls


class Stepper:
    """Emulates non-blocking loop for tkinter GUI application by repeatedly 
    runnning step function after a given interval
    
    Can be stopped/paused
    """

    def __init__(self, master: Union[tk.Widget, tk.Tk], delay: int = 30):
        """Constructor
        
        Parameters:
            master (tk.Widget|tk.Tk): The tkinter master widget
            delay (int): The number of milliseconds between each _step
                         (does not include time taken to run _step)
        """
        self._master = master
        self._step_number = -1
        self._paused = False
        self._delay = delay
        self._after_id = None

    def is_started(self):
        return self._after_id is not None

    def is_stopped(self):
        return self._after_id is None and not self._paused

    def is_paused(self):
        return self._paused

    def start(self):
        """Start the stepper"""
        if self.is_started():
            return
        self._paused = False
        self._after_id = self._master.after(self._delay, self._step_manager)

    def stop(self):
        """Stop the stepper & reset steps to 0"""
        if self.is_stopped():
            return
        if not self.is_paused():
            self._paused = False
            self._master.after_cancel(self._after_id)
            self._after_id = None
        self._step_number = -1

    def pause(self):
        """Pause the stepper (does not reset steps to 0)"""
        if self.is_paused() or self.is_stopped():
            return
        self._paused = True
        self._master.after_cancel(self._after_id)
        self._after_id = None

    def _step_manager(self):
        """Internal wrapper around step method to keep track of the number of steps and queue next step"""
        self._step_number += 1

        if self._step() and not self.is_stopped():
            self._after_id = self._master.after(self._delay, self._step_manager)

    def _step(self):
        """(bool) Performs a step
        
        Returns True if stepping should continue
        """
        raise NotImplementedError("_step must be implemented by a subclass")


class Countdown:
    """A simple decrementing counter"""
    current: int = 0
    initial: int

    def __init__(self, initial: int):
        self.initial = initial

    def start(self, initial=None):
        """Starts the countdown"""
        if initial is None:
            initial = self.initial
        self.current = initial

    def is_done(self) -> bool:
        """(bool) Returns True iff this countdown is finished"""
        return self.current == 0

    def step(self):
        """Decrements the counter if possible"""
        if self.current > 0:
            self.current -= 1
