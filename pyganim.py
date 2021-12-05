# Pyganim (pyganim.py, ver 1)
# A sprite animation module for Pygame.
#
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pyganim
# Released under a "Simplified BSD" license
#
# There's a tutorial (and sample code) on how to use this library at http://inventwithpython.com/pyganim
# NOTE: This module requires Pygame to be installed to use. Download it from http://pygame.org
#
# This should be compatible with both Python 2 and Python 3. Please email any
# bug reports to Al at al@inventwithpython.com
#


# TODO: Feature idea: if the same image file is specified, re-use the Surface object. (Make this optional though.)

import pygame
import time

# setting up constants
PLAYING = 'playing'
PAUSED = 'paused'
STOPPED = 'stopped'

# These values are used in the anchor() method.
NORTHWEST = 'northwest'
NORTH = 'north'
NORTHEAST = 'northeast'
WEST = 'west'
CENTER = 'center'
EAST = 'east'
SOUTHWEST = 'southwest'
SOUTH = 'south'
SOUTHEAST = 'southeast'


def get_images_from_sprite_sheet(filename, width=None, height=None, rows=None, cols=None, rects=None):
    """Loads several sprites from a single image file (a "spritesheet").

    One (and only one) of the following parameters should be specified:
        * width & height of each sprite (all must be the same size)
        * number of rows and columns of sprites (all must be the same size)
        * rects, which is a list of tuples formatted as (pygame.Rect, index) or (left, top, width, height)
    """

    # there should be exactly 1 set of arguments passed (i.e. don't pass width/height AND rows/cols)
    args_type = ''
    if (width is not None or height is not None) and (args_type == ''):
        args_type = 'width/height'
        assert width is not None and height is not None, 'Both width and height must be specified'
        assert type(
            width) == int and width > 0, 'width arg must be a non-zero positive integer'
        assert type(
            height) == int and height > 0, 'height arg must be a non-zero positive integer'
    if (rows is not None or cols is not None) and (args_type == ''):
        args_type = 'rows/cols'
        assert rows is not None and cols is not None, 'Both rows and cols must be specified'
        assert type(
            rows) == int and rows > 0, 'rows arg must be a non-zero positive integer'
        assert type(
            cols) == int and cols > 0, 'cols arg must be a non-zero positive integer'
    if (rects is not None) and (args_type == ''):
        args_type = 'rects'
        for i, rect in enumerate(rects):
            assert len(
                rect) == 4, 'rect at index %s is not a sequence of four ints: (left, top, width, height)' % (i)

            assert (type(rect[0]), type(rect[1]), type(rect[2]), type(
                rect[3])) == (int, int, int, int), 'rect '
    if args_type == '':
        raise ValueError(
            'Only pass one set of args: width & height, rows & cols, *or* rects')

    sheet_image = pygame.image.load(filename).convert_alpha()
    rects = []
    if args_type == 'rows/cols':
        sprite_width = sheet_image.get_width() // cols
        sprite_height = sheet_image.get_height() // rows

        for y in range(0, sheet_image.get_height(), sprite_height):
            if y + sprite_height > sheet_image.get_height():
                continue
            for x in range(0, sheet_image.get_width(), sprite_width):
                if x + sprite_width > sheet_image.get_width():
                    continue

                rects.append((x, y, sprite_width, sprite_height))

    elif args_type == 'width/height':
        for y in range(0, sheet_image.get_height(), (sheet_image.get_height() // height)):
            if y + height > sheet_image.get_height():
                continue
            for x in range(0, sheet_image.get_width(), (sheet_image.get_width() // width)):
                if x + width > sheet_image.get_width():
                    continue

                rects.append((x, y, width, height))

    # create a list of Surface objects from the sprite sheet
    returned_surfaces = []
    for rect in rects:
        # create Surface with width/height in rect
        surf = pygame.Surface((rect[2], rect[3]), 0,
                              sheet_image).convert_alpha()
        surf.blit(sheet_image, (0, 0), rect, pygame.BLEND_RGBA_ADD)
        returned_surfaces.append(surf)

    return returned_surfaces


class PygAnimation(object):
    def __init__(self, frames, loop=True):
        # Constructor function for the animation object. Starts off in the STOPPED state.
        #
        # @param frames
        #     A list of tuples for each frame of animation, in one of the following format:
        #       (image_of_frame<pygame.Surface>, duration_in_seconds<int>)
        #       (filename_of_image<str>, duration_in_seconds<int>)
        #     Note that the images and duration cannot be changed. A new PygAnimation object
        #     will have to be created.
        # @param loop Tells the animation object to keep playing in a loop.

        # _images stores the pygame.Surface objects of each frame
        self._images = []
        # _durations stores the durations (in seconds) of each frame.
        # e.g. [1, 1, 2.5] means the first and second frames last one second,
        # and the third frame lasts for two and half seconds.
        self._durations = []
        # _startTimes shows when each frame begins. len(self._start_times) will
        # always be one more than len(self._images), because the last number
        # will be when the last frame ends, rather than when it starts.
        # The values are in seconds.
        # So self._start_times[-1] tells you the length of the entire animation.
        # e.g. if _durations is [1, 1, 2.5], then _startTimes will be [0, 1, 2, 4.5]
        self._start_times = None

        # if the sprites are transformed, the originals are kept in _images
        # and the transformed sprites are kept in _transformedImages.
        self._transformed_images = []

        self._state = STOPPED  # The state is always either PLAYING, PAUSED, or STOPPED
        # If True, the animation will keep looping. If False, the animation stops after playing once.
        self._loop = loop
        self._rate = 1.0  # 2.0 means play the animation twice as fast, 0.5 means twice as slow
        # If False, then nothing is drawn when the blit() methods are called
        self._visibility = True

        # the time that the play() function was last called.
        self._playing_start_time = 0
        # the time that the pause() function was last called.
        self._paused_start_time = 0

        # ('_copy' is passed for frames by the getCopies() method)
        if frames != '_copy':
            self.num_frames = len(frames)
            assert self.num_frames > 0, 'Must contain at least one frame.'
            for i in range(self.num_frames):
                # load each frame of animation into _images
                frame = frames[i]
                assert type(frame) in (list, tuple) and len(
                    frame) == 2, 'Frame %s has incorrect format.' % (i)
                assert type(frame[0]) in (
                    str, pygame.Surface), 'Frame %s image must be a string filename or a pygame.Surface' % (i)
                assert frame[1] > 0, 'Frame %s duration must be greater than zero.' % (
                    i)
                if type(frame[0]) == str:
                    frame = (pygame.image.load(
                        frame[0]).convert_alpha(), frame[1])
                self._images.append(frame[0])
                self._durations.append(frame[1])
            self._start_times = self._get_start_times()

    def _get_start_times(self):
        # Internal method to get the start times based off of the _durations list.
        # Don't call this method.
        start_times = [0]
        for i in range(self.num_frames):
            start_times.append(start_times[-1] + self._durations[i])
        return start_times

    def reverse(self):
        # Reverses the order of the animations.
        self.elapsed = self._start_times[-1] - self.elapsed
        self._images.reverse()
        self._transformed_images.reverse()
        self._durations.reverse()

    def get_copy(self):
        # Returns a copy of this PygAnimation object, but one that refers to the
        # Surface objects of the original so it efficiently uses memory.
        #
        # NOTE: Messing around with the original Surface objects will affect all
        # the copies. If you want to modify the Surface objects, then just make
        # copies using constructor function instead.
        return self.get_copies(1)[0]

    def get_copies(self, num_copies=1):
        # Returns a list of copies of this PygAnimation object, but one that refers to the
        # Surface objects of the original so it efficiently uses memory.
        #
        # NOTE: Messing around with the original Surface objects will affect all
        # the copies. If you want to modify the Surface objects, then just make
        # copies using constructor function instead.
        retval = []
        for _ in range(num_copies):
            new_anim = PygAnimation('_copy', loop=self.loop)
            new_anim._images = self._images[:]
            new_anim._transformed_images = self._transformed_images[:]
            new_anim._durations = self._durations[:]
            new_anim._start_times = self._start_times[:]
            new_anim.num_frames = self.num_frames
            retval.append(new_anim)
        return retval

    def blit(self, dest_surface, dest):
        # Draws the appropriate frame of the animation to the destination Surface
        # at the specified position.
        #
        # NOTE: If the visibility attribute is False, then nothing will be drawn.
        #
        # @param dest_surface
        #     The Surface object to draw the frame
        # @param dest
        #     The position to draw the frame. This is passed to Pygame's Surface's
        #     blit() function, so it can be either a (top, left) tuple or a Rect
        #     object.
        if self.is_finished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frame_num = find_start_time(self._start_times, self.elapsed)
        dest_surface.blit(self.get_frame(frame_num), dest)

    def get_frame(self, frame_num):
        # Returns the pygame.Surface object of the frame_num-th frame in this
        # animation object. If there is a transformed version of the frame,
        # it will return that one.
        if self._transformed_images == []:
            return self._images[frame_num]
        else:
            return self._transformed_images[frame_num]

    def get_current_frame(self):
        # Returns the pygame.Surface object of the frame that would be drawn
        # if the blit() method were called right now. If there is a transformed
        # version of the frame, it will return that one.
        return self.get_frame(self.current_frame_num)

    def clear_transforms(self):
        # Deletes all the transformed frames so that the animation object
        # displays the original Surfaces/images as they were before
        # transformation functions were called on them.
        #
        # This is handy to do for multiple transformation, where calling
        # the rotation or scaling functions multiple times results in
        # degraded/noisy images.
        self._transformed_images = []

    def make_transforms_permanent(self):
        self._images = [pygame.Surface(
            surf_obj.get_size(), 0, surf_obj) for surf_obj in self._transformed_images]
        for i in range(len(self._transformed_images)):
            self._images[i].blit(self._transformed_images[i], (0, 0))

    def blit_frame_num(self, frame_num, dest_surface, dest):
        # Draws the specified frame of the animation object. This ignores the
        # current playing state.
        #
        # NOTE: If the visibility attribute is False, then nothing will be drawn.
        #
        # @param frame_num
        #     The frame to draw (the first frame is 0, not 1)
        # @param dest_surface
        #     The Surface object to draw the frame
        # @param dest
        #     The position to draw the frame. This is passed to Pygame's Surface's
        #     blit() function, so it can be either a (top, left) tuple or a Rect
        #     object.
        if self.is_finished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        dest_surface.blit(self.get_frame(frame_num), dest)

    def blit_frame_at_time(self, elapsed, dest_surface, dest):
        # Draws the frame the is "elapsed" number of seconds into the animation,
        # rather than the time the animation actually started playing.
        #
        # NOTE: If the visibility attribute is False, then nothing will be drawn.
        #
        # @param elapsed
        #     The amount of time into an animation to use when determining which
        #     frame to draw. blitFrameAtTime() uses this parameter rather than
        #     the actual time that the animation started playing. (In seconds)
        # @param dest_surface
        #     The Surface object to draw the frame
        # @param dest
        #     The position to draw the frame. This is passed to Pygame's Surface's
        #     blit() function, so it can be either a (top, left) tuple or a Rect
        #     object.        elapsed = int(elapsed * self.rate)
        if self.is_finished():
            self.state = STOPPED
        if not self.visibility or self.state == STOPPED:
            return
        frame_num = find_start_time(self._start_times, elapsed)
        dest_surface.blit(self.get_frame(frame_num), dest)

    def is_finished(self):
        # Returns True if this animation doesn't loop and has finished playing
        # all the frames it has.
        return not self.loop and self.elapsed >= self._start_times[-1]

    def play(self, start_time=None):
        # Start playing the animation.

        # play() is essentially a setter function for self._state
        # NOTE: Don't adjust the self.state property, only self._state

        if start_time is None:
            start_time = time.time()

        if self._state == PLAYING:
            if self.is_finished():
                # if the animation doesn't loop and has already finished, then
                # calling play() causes it to replay from the beginning.
                self._playing_start_time = start_time
        elif self._state == STOPPED:
            # if animation was stopped, start playing from the beginning
            self._playing_start_time = start_time
        elif self._state == PAUSED:
            # if animation was paused, start playing from where it was paused
            self._playing_start_time = start_time - \
                (self._paused_start_time - self._playing_start_time)
        self._state = PLAYING

    def pause(self, start_time=None):
        # Stop having the animation progress, and keep it at the current frame.

        # pause() is essentially a setter function for self._state
        # NOTE: Don't adjust the self.state property, only self._state

        if start_time is None:
            start_time = time.time()

        if self._state == PAUSED:
            return  # do nothing
        elif self._state == PLAYING:
            self._paused_start_time = start_time
        elif self._state == STOPPED:
            right_now = time.time()
            self._playing_start_time = right_now
            self._paused_start_time = right_now
        self._state = PAUSED

    def stop(self):
        # Reset the animation to the beginning frame, and do not continue playing

        # stop() is essentially a setter function for self._state
        # NOTE: Don't adjust the self.state property, only self._state
        if self._state == STOPPED:
            return  # do nothing
        self._state = STOPPED

    def toggle_pause(self):
        # If paused, start playing. If playing, then pause.

        # toggle_pause() is essentially a setter function for self._state
        # NOTE: Don't adjust the self.state property, only self._state

        if self._state == PLAYING:
            if self.is_finished():
                # the one exception: if this animation doesn't loop and it
                # has finished playing, then toggling the pause will cause
                # the animation to replay from the beginning.
                # self._playing_start_time = time.time() # effectively the same as calling play()
                self.play()
            else:
                self.pause()
        elif self._state in (PAUSED, STOPPED):
            self.play()

    def are_frames_same_size(self):
        # Returns True if all the Surface objects in this animation object
        # have the same width and height. Otherwise, returns False
        width, height = self.get_frame(0).get_size()
        return all(
            self.get_frame(i).get_size() == (width, height)
            for i in range(len(self._images))
        )

    def get_max_size(self):
        # Goes through all the Surface objects in this animation object
        # and returns the max width and max height that it finds. (These
        # widths and heights may be on different Surface objects.)
        frame_widths = []
        frame_heights = []
        for i in range(len(self._images)):
            frame_width, frame_height = self._images[i].get_size()
            frame_widths.append(frame_width)
            frame_heights.append(frame_height)
        max_width = max(frame_widths)
        max_height = max(frame_heights)

        return (max_width, max_height)

    def get_rect(self):
        # Returns a pygame.Rect object for this animation object.
        # The top and left will be set to 0, 0, and the width and height
        # will be set to what is returned by getMaxSize().
        max_width, max_height = self.get_max_size()
        return pygame.Rect(0, 0, max_width, max_height)

    def anchor(self, anchor_point=NORTHWEST):
        # If the Surface objects are of different sizes, align them all to a
        # specific "anchor point" (one of the NORTH, SOUTH, SOUTHEAST, etc. constants)
        #
        # By default, they are all anchored to the NORTHWEST corner.
        if self.are_frames_same_size():
            return  # nothing needs to be anchored
            # This check also prevents additional calls to anchor() from doing
            # anything, since anchor() sets all the image to the same size.
            # The lesson is, you can only effectively call anchor() once.

        # clears transforms since this method anchors the original images.
        self.clear_transforms()

        max_width, max_height = self.get_max_size()
        half_max_width = int(max_width / 2)
        half_max_height = int(max_height / 2)

        for i in range(len(self._images)):
            # go through and copy all frames to a max-sized Surface object
            # NOTE: This makes changes to the original images in self._images, not the transformed images in self._transformed_images
            # TODO: this is probably going to have errors since I'm using the default depth.
            new_surf = pygame.Surface((max_width, max_height))

            # set the expanded areas to be transparent
            new_surf = new_surf.convert_alpha()
            new_surf.fill((0, 0, 0, 0))

            frame_width, frame_height = self._images[i].get_size()
            half_frame_width = int(frame_width / 2)
            half_frame_height = int(frame_height / 2)

            # position the Surface objects to the specified anchor point
            if anchor_point == NORTHWEST:
                new_surf.blit(self._images[i], (0, 0))
            elif anchor_point == NORTH:
                new_surf.blit(self._images[i],
                             (half_max_width - half_frame_width, 0))
            elif anchor_point == NORTHEAST:
                new_surf.blit(self._images[i], (max_width - frame_width, 0))
            elif anchor_point == WEST:
                new_surf.blit(self._images[i],
                             (0, half_max_height - half_frame_height))
            elif anchor_point == CENTER:
                new_surf.blit(
                    self._images[i], (half_max_width - half_frame_width, half_max_height - half_frame_height))
            elif anchor_point == EAST:
                new_surf.blit(
                    self._images[i], (max_width - frame_width, half_max_height - half_frame_height))
            elif anchor_point == SOUTHWEST:
                new_surf.blit(self._images[i], (0, max_height - frame_height))
            elif anchor_point == SOUTH:
                new_surf.blit(
                    self._images[i], (half_max_width - half_frame_width, max_height - frame_height))
            elif anchor_point == SOUTHEAST:
                new_surf.blit(
                    self._images[i], (max_width - frame_width, max_height - frame_height))
            self._images[i] = new_surf

    def next_frame(self, jump=1):
        # Set the elapsed time to the beginning of the next frame.
        # You can jump ahead by multiple frames by specifying a different
        # argument for jump.
        # Negative values have the same effect as calling prev_frame()
        self.current_frame_num += int(jump)

    def prev_frame(self, jump=1):
        # Set the elapsed time to the beginning of the previous frame.
        # You can jump ahead by multiple frames by specifying a different
        # argument for jump.
        # Negative values have the same effect as calling next_frame()
        self.current_frame_num -= int(jump)

    def rewind(self, seconds=None):
        # Set the elapsed time back relative to the current elapsed time.
        if seconds is None:
            self.elapsed = 0.0
        else:
            self.elapsed -= seconds

    def fast_forward(self, seconds=None):
        # Set the elapsed time forward relative to the current elapsed time.
        if seconds is None:
            # done to compensate for rounding errors
            self.elapsed = self._start_times[-1] - 0.00002
        else:
            self.elapsed += seconds

    def _make_transformed_surfaces_if_needed(self):
        # Internal-method. Creates the Surface objects for the _transformedImages list.
        # Don't call this method.
        if self._transformed_images == []:
            self._transformed_images = [surf.copy() for surf in self._images]

    # Transformation methods.
    # (These are analogous to the pygame.transform.* functions, except they
    # are applied to all frames of the animation object.

    def flip(self, xbool, ybool):
        # Flips the image horizontally, vertically, or both.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.flip
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.flip(
                self.get_frame(i), xbool, ybool)

    def scale(self, width_height):
        # NOTE: Does not support the DestSurface parameter
        # Increases or decreases the size of the images.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.scale
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.scale(
                self.get_frame(i), width_height)

    def rotate(self, angle):
        # Rotates the image.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotate
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.rotate(
                self.get_frame(i), angle)

    def rotozoom(self, angle, scale):
        # Rotates and scales the image simultaneously.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.rotozoom
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.rotozoom(
                self.get_frame(i), angle, scale)

    def scale2x(self):
        # NOTE: Does not support the DestSurface parameter
        # Double the size of the image using an efficient algorithm.
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.scale2x
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.scale2x(
                self.get_frame(i))

    def smoothscale(self, width_height):
        # NOTE: Does not support the DestSurface parameter
        # Scales the image smoothly. (Computationally more expensive and
        # slower but produces a better scaled image.)
        # See http://pygame.org/docs/ref/transform.html#pygame.transform.smoothscale
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            self._transformed_images[i] = pygame.transform.smoothscale(
                self.get_frame(i), width_height)

    # pygame.Surface method wrappers
    # These wrappers call their analogous pygame.Surface methods on all Surface objects in this animation.
    # They are here for the convenience of the module user. These calls will apply to the transform images,
    # and can have their effects undone by called clear_transforms()
    #
    # It is not advisable to call these methods on the individual Surface objects in self._images.

    def _surface_method_wrapper(self, wrapped_method_name, *args, **kwargs):
        self._make_transformed_surfaces_if_needed()
        for i in range(len(self._images)):
            method_to_call = getattr(
                self._transformed_images[i], wrapped_method_name)
            method_to_call(*args, **kwargs)

    # There's probably a more terse way to generate the following methods,
    # but I don't want to make the code even more unreadable.
    def convert(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.convert
        self._surface_method_wrapper('convert', *args, **kwargs)

    def convert_alpha(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.convert_alpha
        self._surface_method_wrapper('convert_alpha', *args, **kwargs)

    def set_alpha(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_alpha
        self._surface_method_wrapper('set_alpha', *args, **kwargs)

    def scroll(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.scroll
        self._surface_method_wrapper('scroll', *args, **kwargs)

    def set_clip(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_clip
        self._surface_method_wrapper('set_clip', *args, **kwargs)

    def set_colorkey(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.set_colorkey
        self._surface_method_wrapper('set_colorkey', *args, **kwargs)

    def lock(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.unlock
        self._surface_method_wrapper('lock', *args, **kwargs)

    def unlock(self, *args, **kwargs):
        # See http://pygame.org/docs/ref/surface.html#Surface.lock
        self._surface_method_wrapper('unlock', *args, **kwargs)

    # Getter and setter methods for properties

    def _prop_get_rate(self):
        return self._rate

    def _prop_set_rate(self, rate):
        rate = float(rate)
        if rate < 0:
            raise ValueError('rate must be greater than 0.')
        self._rate = rate

    rate = property(_prop_get_rate, _prop_set_rate)

    def _prop_get_loop(self):
        return self._loop

    def _prop_set_loop(self, loop):
        if self.state == PLAYING and self._loop and not loop:
            # if we are turning off looping while the animation is playing,
            # we need to modify the _playingStartTime so that the rest of
            # the animation will play, and then stop. (Otherwise, the
            # animation will immediately stop playing if it has already looped.)
            self._playing_start_time = time.time() - self.elapsed
        self._loop = bool(loop)

    loop = property(_prop_get_loop, _prop_set_loop)

    def _prop_get_state(self):
        if self.is_finished():
            # if finished playing, then set state to STOPPED.
            self._state = STOPPED

        return self._state

    def _prop_set_state(self, state):
        if state not in (PLAYING, PAUSED, STOPPED):
            raise ValueError(
                'state must be one of pyganim.PLAYING, pyganim.PAUSED, or pyganim.STOPPED')
        if state == PLAYING:
            self.play()
        elif state == PAUSED:
            self.pause()
        elif state == STOPPED:
            self.stop()

    state = property(_prop_get_state, _prop_set_state)

    def _prop_get_visibility(self):
        return self._visibility

    def _prop_set_visibility(self, visibility):
        self._visibility = bool(visibility)

    visibility = property(_prop_get_visibility, _prop_set_visibility)

    def _prop_set_elapsed(self, elapsed):
        # NOTE: Do to floating point rounding errors, this doesn't work precisely.
        elapsed += 0.00001  # done to compensate for rounding errors
        # TODO - I really need to find a better way to handle the floating point thing.

        # Set the elapsed time to a specific value.
        if self._loop:
            elapsed = elapsed % self._start_times[-1]
        else:
            elapsed = get_in_between_value(0, elapsed, self._start_times[-1])

        right_now = time.time()
        self._playing_start_time = right_now - (elapsed * self.rate)

        if self.state in (PAUSED, STOPPED):
            self.state = PAUSED  # if stopped, then set to paused
            self._paused_start_time = right_now

    def _prop_get_elapsed(self):
        # NOTE: Do to floating point rounding errors, this doesn't work precisely.

        # To prevent infinite recursion, don't use the self.state property,
        # just read/set self._state directly because the state getter calls
        # this method.

        # Find out how long ago the play()/pause() functions were called.
        if self._state == STOPPED:
            # if stopped, then just return 0
            return 0

        if self._state == PLAYING:
            # if playing, then draw the current frame (based on when the animation
            # started playing). If not looping and the animation has gone through
            # all the frames already, then draw the last frame.
            elapsed = (time.time() - self._playing_start_time) * self.rate
        elif self._state == PAUSED:
            # if paused, then draw the frame that was playing at the time the
            # PygAnimation object was paused
            elapsed = (self._paused_start_time -
                       self._playing_start_time) * self.rate
        if self._loop:
            elapsed = elapsed % self._start_times[-1]
        else:
            elapsed = get_in_between_value(0, elapsed, self._start_times[-1])
        elapsed += 0.00001  # done to compensate for rounding errors
        return elapsed

    elapsed = property(_prop_get_elapsed, _prop_set_elapsed)

    def _prop_get_current_frame_num(self):
        # Return the frame number of the frame that will be currently
        # displayed if the animation object were drawn right now.
        return find_start_time(self._start_times, self.elapsed)

    def _prop_set_current_frame_num(self, frame_num):
        # Change the elapsed time to the beginning of a specific frame.
        if self.loop:
            frame_num = frame_num % len(self._images)
        else:
            frame_num = get_in_between_value(0, frame_num, len(self._images)-1)
        self.elapsed = self._start_times[frame_num]

    current_frame_num = property(
        _prop_get_current_frame_num, _prop_set_current_frame_num)


class PygConductor(object):
    def __init__(self, *animations):
        assert len(animations) > 0, 'at least one PygAnimation object is required'

        self._animations = []
        self.add(*animations)

    def add(self, *animations):
        if type(animations[0]) == dict:
            for k in animations[0].keys():
                self._animations.append(animations[0][k])
        elif type(animations[0]) in (tuple, list):
            for i in range(len(animations[0])):
                self._animations.append(animations[0][i])
        else:
            for i in range(len(animations)):
                self._animations.append(animations[i])

    def _prop_get_animations(self):
        return self._animations

    def _prop_set_animations(self, val):
        self._animations = val

    animations = property(_prop_get_animations, _prop_set_animations)

    def play(self, start_time=None):
        if start_time is None:
            start_time = time.time()

        for anim_obj in self._animations:
            anim_obj.play(start_time)

    def pause(self, start_time=None):
        if start_time is None:
            start_time = time.time()

        for anim_obj in self._animations:
            anim_obj.pause(start_time)

    def stop(self):
        for anim_obj in self._animations:
            anim_obj.stop()

    def reverse(self):
        for anim_obj in self._animations:
            anim_obj.reverse()

    def clear_transforms(self):
        for anim_obj in self._animations:
            anim_obj.clear_transforms()

    def make_transforms_permanent(self):
        for anim_obj in self._animations:
            anim_obj.make_transforms_permanent()

    def toggle_pause(self):
        for anim_obj in self._animations:
            anim_obj.toggle_pause()

    def next_frame(self, jump=1):
        for anim_obj in self._animations:
            anim_obj.next_frame(jump)

    def prev_frame(self, jump=1):
        for anim_obj in self._animations:
            anim_obj.prev_frame(jump)

    def rewind(self, seconds=None):
        for anim_obj in self._animations:
            anim_obj.rewind(seconds)

    def fast_forward(self, seconds=None):
        for anim_obj in self._animations:
            anim_obj.fast_forward(seconds)

    def flip(self, xbool, ybool):
        for anim_obj in self._animations:
            anim_obj.flip(xbool, ybool)

    def scale(self, width_height):
        for anim_obj in self._animations:
            anim_obj.scale(width_height)

    def rotate(self, angle):
        for anim_obj in self._animations:
            anim_obj.rotate(angle)

    def rotozoom(self, angle, scale):
        for anim_obj in self._animations:
            anim_obj.rotozoom(angle, scale)

    def scale2x(self):
        for anim_obj in self._animations:
            anim_obj.scale2x()

    def smoothscale(self, width_height):
        for anim_obj in self._animations:
            anim_obj.smoothscale(width_height)

    def convert(self):
        for anim_obj in self._animations:
            anim_obj.convert()

    def convert_alpha(self):
        for anim_obj in self._animations:
            anim_obj.convert_alpha()

    def set_alpha(self, *args, **kwargs):
        for anim_obj in self._animations:
            anim_obj.set_alpha(*args, **kwargs)

    def scroll(self, dx=0, dy=0):
        for anim_obj in self._animations:
            anim_obj.scroll(dx, dy)

    def set_clip(self, *args, **kwargs):
        for anim_obj in self._animations:
            anim_obj.set_clip(*args, **kwargs)

    def set_colorkey(self, *args, **kwargs):
        for anim_obj in self._animations:
            anim_obj.set_colorkey(*args, **kwargs)

    def lock(self):
        for anim_obj in self._animations:
            anim_obj.lock()

    def unlock(self):
        for anim_obj in self._animations:
            anim_obj.unlock()


def get_in_between_value(lower_bound, value, upper_bound):
    # Returns the value within the bounds of the lower and upper bound parameters.
    # If value is less than lower_bound, then return lower_bound.
    # If value is greater than upper_bound, then return upper_bound.
    # Otherwise, just return value as it is.
    if value < lower_bound:
        return lower_bound
    elif value > upper_bound:
        return upper_bound
    return value


def find_start_time(start_times, target):
    # With start_times as a list of sequential numbers and target as a number,
    # returns the index of the number in start_times that preceeds target.
    #
    # For example, if start_times was [0, 2, 4.5, 7.3, 10] and target was 6,
    # then find_start_time() would return 2. If target was 12, returns 4.
    assert start_times[0] == 0
    lb = 0  # "lb" is lower bound
    ub = len(start_times) - 1  # "ub" is upper bound

    # handle special cases:
    if len(start_times) == 0:
        return 0
    if target >= start_times[-1]:
        return ub - 1

    # perform binary search:
    while True:
        i = int((ub - lb) / 2) + lb

        if start_times[i] == target or (start_times[i] < target and start_times[i+1] > target):
            if i == len(start_times):
                return i - 1
            else:
                return i

        if start_times[i] < target:
            lb = i
        elif start_times[i] > target:
            ub = i
