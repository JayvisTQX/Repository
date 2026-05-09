import os
import sys

# --- MULTI-CORE OPTIMIZATION (Must be before other imports) ---
# FORCE USE OF ALL DETECTED CORES
all_cores = str(os.cpu_count())
os.environ["OMP_NUM_THREADS"] = all_cores
os.environ["MKL_NUM_THREADS"] = all_cores
os.environ["OPENBLAS_NUM_THREADS"] = all_cores
os.environ["VECLIB_MAXIMUM_THREADS"] = all_cores
os.environ["NUMEXPR_NUM_THREADS"] = all_cores

import time
import math
import random
import threading
import multiprocessing # Added for CPU count access
import json
import tkinter as tk
from tkinter import filedialog

import pygame
import numpy as np
import pyaudio
from pydub import AudioSegment
import cv2
# --- ENABLE GPU ACCELERATION FOR OPENCV ---
if cv2.ocl.haveOpenCL():
    cv2.ocl.setUseOpenCL(True)
    print("OpenCV: OpenCL (GPU) Acceleration Enabled")

# --- CRITICAL FIX FOR FFMPEG PATHS ---
script_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] += os.pathsep + script_dir

ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
ffprobe_path = os.path.join(script_dir, "ffprobe.exe")
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1280, 720
# This controls the refresh rate of the Pygame Window.
# If you load a 30fps video, it will look smooth (frames will be drawn twice).
# If you load a 60fps video, it will look smooth (1:1 match).
# If you load a 120fps video, it will look like 60fps (because Pygame is limited to 60).
# If you want to ensure maximum smoothness for high-refresh-rate videos, change the line at the top of your script to something like 120 fps.
# However, keeping it at 60 is usually best for performance unless you have a specific high-refresh-rate monitor and powerful CPU.
FPS = 144
CHUNK = 2048
RATE = 44100
UI_PANEL_HEIGHT = 210  # Increased to space elements out vertically

# --- OPTIMIZATION: MASSIVE PARTICLE COUNT ---
# Your CPU is powerful. Let's increase particles to utilize it.
MAX_PARTICLES = 1500  # Increased from 180

# --- MODES ---
COLOR_MODES = sorted([
    'Rainbow', 'Cyberpunk', 'Sunset', 'Aurora', 'Cotton Candy', 'Fire',
    'Fire & Ice', 'Toxic', 'Patriot', 'Custom',
    'Thermal', 'Oceanic', 'Jungle', 'Noir', 'Vaporwave',
    'Gold Rush', 'Nebula', 'Blueprint', 'Crimson Tide', 'Radioactive',
    'Candy Cane', 'Midnight City', 'Heatmap', 'Prism', 'Zenith',
    'Obsidian', 'Plasma', 'Emerald City', 'Solar Flare', 'Bismuth',
    'Neon Demon', 'Gaia', 'Event Horizon', 'Rust Belt', 'Warhol',
    'Bioluminescence', 'Royal Velvet', 'Glitch Art', 'Magma Core', 'Glacial Fracture',
    'Dreamscape', 'Supernova', 'Sin City', 'The Grid', 'Lollipop',
    'Chakra Alignment', 'Blood Moon', 'Golden Hour', 'Acid Rain', 'Sumi-e',
    'Midas Touch', 'Quantum Field', 'Ethereal Plane', 'Vantablack & Neon', 'Gossamer',
    'Molten Steel', 'Holo-Foil', 'Art Deco', 'Sakura Bloom', 'Toxic Waste',
    'Infrared Hunter', 'Velvet Rope', 'Deep Sea Vent', 'Urban Concrete', 'Retro-Future',
    'Spirit World', 'Candy Apple', 'Storm Cell', 'Kaleidoscope', 'Mosaic',
    'Tarragon Void', 'Paladin Aura', 'Necromancer', 'Synth Sunset',
    'Copper Oxide', 'Dragon Scale', 'Marble Statue', 'Laser Tag',
    'Coffee Shop', 'Tiffany Glass', 'Circuit Breaker', 'Polychrome Glitch',
    'Amber Fossil', 'Moon Crystal', 'Rust Bucket', 'Berry Smoothie',
    'Oil Slick', 'Blueprint Inverted', 'Thermal Camo', 'Ultraviolet'
    'Crimson Lotus', 'Vice City', 'Clockwork Gear', 'Digital Rain', 'Pompeii',
    'Polaris', 'Bumblebee', 'Koi Pond', 'Candy Corn', 'Noir Detective',
    'Sunken Ship', 'Unicorn Frappe', 'High Voltage', 'Zen Garden', 'Sahara Night',
    '90s Jazz Cup', 'Vampire Hunter', 'Molten Glass', 'Void Purple', 'Golden Fleece',
    'Toxic Jungle', 'Cyber Samurai', 'Frozen Wasteland', 'Blood Orange', 'Disco Floor',
    'Radioactive Hazard', 'Emerald Tablet', 'Checkmate', 'Horizon Zero', 'Prism Fracture',
    'Quantum Superposition', 'Rococo Pastel', 'Cyber-Goth', 'Confetti Cannon', 'Ancient Hieroglyph',
    'Vapor-Grid', 'Nuclear Fallout', 'Kaleidoscope Fracture', 'Dragonfruit', 'Tuxedo Night',
    'Bismuth Geode', 'Heat Vision', 'Miami Hotline', 'Singularity Event', 'Fiber Optic',
    'Cathedral Glass', 'Peppermint Swirl', 'Digital Distortion', 'Forest Fire', 'Arctic Aurora',
    'Stealth Mode', 'Velvet Lounge', 'X-Ray Vision', 'Koi Stream', 'Emerald Cavern',
    'Caution Tape', 'Starry Night', '8-Bit Hero', 'Blood Diamond', 'Rainbow Road',
    'Neural Network', 'Holographic Data', 'Cryo-Chamber', 'Dyson Sphere', 'Warp Drive',
    'Nanobot Swarm', 'Cybernetic Implant', 'Hard Light Bridge', 'Plasma Cannon', 'Force Field',
    'Bioluminescent Algae', 'Volcanic Lightning', 'Monsoon Season', 'Tundra Permafrost', 'Desert Bloom',
    'Deep Cave Crystals', 'Geyser Eruption', 'Tornado Alley', 'Morning Dew', 'Autumn Canopy',
    'Bauhaus Construct', 'De Stijl Grid', 'Pointillism', 'Surrealist Dream', 'Art Nouveau Gold',
    'Brutalist Concrete', 'Pop Art Halftone', 'Impressionist Water', 'Cubist Fracture', 'Vaporwave Statue',
    'Liquid Mercury', 'Damascus Steel', 'Carbon Fiber', 'Brushed Aluminum', 'Oxidized Copper',
    'Stained Glass Window', 'Mosaic Tile', 'Royal Tapestry', 'Denim & Leather', 'Rusty Chain',
    'Doppler Effect', 'Sonic Boom', 'Interference Pattern', 'Chaos Theory', 'Fractal Boundary',
    'String Theory', 'Dark Energy', 'Antimatter Containment', 'Schrodinger\'s Cat', 'Time Dilation',
    'Quantum Realm', 'Viking Fire', 'Cyber Wasp', 'Hyper-Loop', 'Alien Flora',
    'Tesla Coil', 'Coronal Mass', 'Police Chase', 'Glitch Mob', 'Void Glass',
    'Raw Copper', 'Neon Skyline', 'Marshmallow', 'Radioactive Isotope', 'Steampunk Gear',
    'Samurai Lacquer', 'Biolum Jellyfish', 'Tartan Plaid', 'Honeycomb Gold', 'Pastel Goth',
    'Urban Neon', 'Frozen Lake', 'Blood Cells', 'Graffiti Wall', 'Aurora Veil',
    'Roulette Wheel', 'Blueprint Tech', 'Sonar Radar', 'Glitch TV', 'Traffic Light',
    'Peppermint Candy', 'Construction Zone', 'Night Vision Goggles', 'CMYK Process', 'Vapor Grid',
    'Radioactive Decay', 'Gold Bullion', 'Cyber Circuit', 'Red Alert', 'Mariana Trench',
    'Jungle Camo', 'Ruby Geode', 'Firefly Night', 'Pixel Art', 'Barcode',
    'Brass Knuckles', 'Ice Shard', 'Neon Sign', 'Petrol Station', 'Sepia Memories',
    'Cybernetic Heart', 'Aurora Borealis II', 'Gothic Stained Glass', 'Synthwave Grid', 'Biohazard Warning',
    'Liquid Gold', 'Cherry Blossom', 'Abyssal Biolum', '8-Bit Arcade', 'Magma Chamber',
    'Prism Refraction', 'Midnight Rain', 'Steampunk Brass', 'Holo-Glitch', 'Predator Thermal',
    'Cotton Candy Dream', 'Radio Wave Interference', 'Toxic Sludge', 'Cosmic Nebula', 'Art Deco Luxury',
    'Vampire Velvet', 'Moving Candy Cane', 'The Matrix', 'Oil Slick Shimmer', 'Architectural Blueprint',
    'Pharaoh\'s Tomb', 'Fatal Error', 'Karesansui', 'Oxidized Statue', 'South Beach',
    'Sugar Rush', 'Mainframe', 'Eldritch Void', 'Mother of Pearl', 'Solar Storm',
    'Memphis Design', 'Bioluminescent Bay', 'Chromatic Aberration', 'Server Room', 'Malachite',
    'Liquid Nitrogen', 'Retro Wallpaper', 'Diamond Heist', 'Sushi Platter', 'Volcanic Ash',
    'Shepard Tone', 'Syntax Highlighting', 'Gothic Noir', 'Radioactive Decay II', 'God Mode'
])
BAR_STYLES = [
    'Solid', 'Border (White)', 'Border (Theme)', 'Hollow (1px)', 'Hollow (Thick)',
    'Horizontal Line (Center)', 'Horizontal Line (Double)', 'Segmented (Blocks)',
    'Crossed', 'Gradient Fill', 'Inverted Fill']
VISUAL_MODES = ['Linear', 'Linear (Pointy)', 'Linear (Round)', 'Linear (Blocks)', 'Linear (Needle)',
                'Reflex', 'Radial', 'Orb', 'Waveform']
BG_IMAGE_OPTIONS = ['None', 'Select Image', 'Select Video', 'Image & Video', 'Select Image Carousel']
BG_IMAGE_ANIMS = ['Static', 'Pulse', 'Cyclic']
SORT_MODES = ['Notes Placement', 'Bass & Melody', 'Experimental Bass & Melody', 'Experimental Outward',
              'Order: Pyramid (Center)', 'Order: Valley (Edges)',
              'Experimental Bass & Melody (Left-Right)', 'Experimental Bass & Melody (Right-Left)']
COLLAPSE_MODES = ['Linear', 'Exponential', 'Inv. Exponential', 'Sine', 'Cosine', 'Bouncy']
IDLE_MODES = ['Original', 'Disappear', 'Match Dock']
BG_MODES = [
    'None', 'Solid Dark', 'Deep Space', 'Rain Effect', 'Tilted Rain',
    'Snow Effect', 'Magic Particles', 'White Magic',
    'Warp Speed', 'Matrix Rain', 'Sparks', 'Fire',
    'Floating Embers', 'White Embers',
    'Fog',
    'Magic Inferno', 'Magic Ocean', 'Magic Nature', 'Magic Royal', 'Magic Candy',
    'Magic Sunset', 'Magic Frost', 'Magic Venom', 'Magic Love', 'Magic Bumblebee',
    'Magic Patriot', 'Magic Matrix', 'Magic Cyber', 'Magic Toxic', 'Magic Lavender',
    'Magic Midas', 'Magic Vampire', 'Magic Galaxy', 'Magic Citrus', 'Magic Mint']
UI_PATTERN_MODES = ['None', 'Grid', 'Dots', 'Hexagon', 'Stripes', 'Circuit',
                    'Checkers', 'Crosshatch', 'Waves', 'ZigZag', 'Binary',
                    'Bubbles', 'Bricks', 'Stars', 'Noise', 'Triangles']
IDLE_MODES = ['Original', 'Disappear', 'Theme Color']
SORT_ALGO = ['Name (A-Z)', 'Name (Z-A)', 'File Size (Small)', 'File Size (Large)']
COLOR_CYCLE_MODES = ['Static', 'Random Cycle']


class Particle:
    """Dynamic Particle System - Optimized with Slots and Surface Caching"""
    __slots__ = ('w', 'h', 'mode', 'x', 'y', 'life', 'decay',
                 'base_size', 'size', 'vx', 'vy', 'base_vy', 'color', 'z', 'alpha')

    # --- OPTIMIZATION: Class-level cache to prevent creating surfaces every frame ---
    surf_cache = {}

    def __init__(self, w, h, mode):
        self.w, self.h = w, h
        self.mode = mode
        self.reset()

    def reset(self, params=None):
        # Default center
        cx_ratio = params.get('center_x', 0.5) if params else 0.5
        cy_ratio = params.get('center_y', 0.5) if params else 0.5

        self.x = random.randint(0, self.w)
        self.y = random.randint(0, self.h)
        self.life = 255
        self.decay = random.randint(2, 5)
        self.base_size = random.randint(2, 6)
        self.size = self.base_size
        self.vx, self.vy = 0, 0
        self.alpha = 255

        # Helper to determine if it's a Magic Variant
        is_magic_variant = self.mode.startswith('Magic ') and self.mode != 'Magic Particles'

        # --- COLOR & PHYSICS CALCULATION ---
        if self.mode == 'Rain Effect':
            self.y = -random.randint(10, 50)
            self.base_vy = random.randint(10, 20)
            base_c = (150, 150, 200)
        elif self.mode == 'Tilted Rain':
            self.y = -random.randint(10, 50)
            self.base_vy = random.randint(10, 20)
            self.vx = random.uniform(3, 5)  # Horizontal tilt
            base_c = (150, 150, 200)
        elif self.mode == 'Snow Effect':
            self.y = -10
            self.base_vy = random.uniform(1, 3)
            self.vx = random.uniform(-1, 1)
            base_c = (240, 240, 240)
        elif self.mode == 'Deep Space':
            self.z = random.uniform(0.5, 2.0)
            self.base_size = random.randint(1, 3)
            self.base_vy = 0.2 * self.z
            self.life = random.randint(150, 255)
            self.decay = random.choice([-2, 2])
            base_c = (255, 255, 255)
        elif self.mode == 'Magic Particles' or self.mode == 'White Magic' or is_magic_variant:
            self.y = self.h + 10
            self.base_vy = random.uniform(-3, -1)
            self.vx = random.uniform(-1, 1)

            if self.mode == 'White Magic':
                base_c = (255, 255, 255)
            elif self.mode == 'Magic Inferno':
                base_c = random.choice([(255, 0, 0), (255, 140, 0), (50, 0, 0)])
            elif self.mode == 'Magic Ocean':
                base_c = random.choice([(0, 0, 255), (0, 255, 255), (0, 100, 200)])
            elif self.mode == 'Magic Nature':
                base_c = random.choice([(0, 255, 0), (34, 139, 34), (154, 205, 50)])
            elif self.mode == 'Magic Royal':
                base_c = random.choice([(75, 0, 130), (218, 165, 32), (148, 0, 211)])
            elif self.mode == 'Magic Candy':
                base_c = random.choice([(255, 105, 180), (0, 255, 255), (255, 255, 255)])
            elif self.mode == 'Magic Sunset':
                base_c = random.choice([(255, 0, 127), (255, 165, 0), (100, 0, 100)])
            elif self.mode == 'Magic Frost':
                base_c = random.choice([(200, 255, 255), (255, 255, 255), (100, 200, 255)])
            elif self.mode == 'Magic Venom':
                base_c = random.choice([(20, 20, 20), (0, 255, 0), (50, 50, 50)])
            elif self.mode == 'Magic Love':
                base_c = random.choice([(255, 0, 0), (255, 192, 203), (100, 0, 0)])
            elif self.mode == 'Magic Bumblebee':
                base_c = random.choice([(255, 255, 0), (40, 40, 40), (200, 200, 0)])
            elif self.mode == 'Magic Patriot':
                base_c = random.choice([(255, 0, 0), (255, 255, 255), (0, 0, 255)])
            elif self.mode == 'Magic Matrix':
                base_c = random.choice([(0, 255, 0), (0, 50, 0), (200, 255, 200)])
            elif self.mode == 'Magic Cyber':
                base_c = random.choice([(0, 255, 255), (255, 0, 255), (10, 10, 30)])
            elif self.mode == 'Magic Toxic':
                base_c = random.choice([(173, 255, 47), (255, 255, 0), (0, 100, 0)])
            elif self.mode == 'Magic Lavender':
                base_c = random.choice([(230, 230, 250), (147, 112, 219), (255, 255, 255)])
            elif self.mode == 'Magic Midas':
                base_c = random.choice([(255, 215, 0), (184, 134, 11), (255, 255, 200)])
            elif self.mode == 'Magic Vampire':
                base_c = random.choice([(139, 0, 0), (0, 0, 0), (255, 0, 0)])
            elif self.mode == 'Magic Galaxy':
                base_c = random.choice([(25, 25, 112), (75, 0, 130), (255, 0, 255)])
            elif self.mode == 'Magic Citrus':
                base_c = random.choice([(255, 165, 0), (255, 255, 0), (50, 205, 50)])
            elif self.mode == 'Magic Mint':
                base_c = random.choice([(152, 251, 152), (240, 255, 240), (0, 255, 255)])
            else:
                # Default Magic Particles
                base_c = (random.randint(100, 255), random.randint(100, 255), random.randint(200, 255))

        elif self.mode == 'Warp Speed':
            self.x = self.w * cx_ratio
            self.y = self.h * cy_ratio
            angle = random.uniform(0, 6.28)
            speed = random.uniform(2, 8)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            base_c = (200, 255, 255)
            self.decay = random.randint(1, 3)
        elif self.mode == 'Matrix Rain':
            self.y = -random.randint(10, 50)
            self.base_vy = random.randint(8, 15)
            base_c = (0, 255, 50)
            self.size = random.randint(1, 3)
        elif self.mode == 'Sparks':
            self.x = random.randint(0, self.w)
            self.y = self.h
            self.base_vy = random.uniform(-5, -15)
            self.vx = random.uniform(-3, 3)
            self.decay = random.randint(5, 15)
            self.base_size = random.randint(1, 3)
            base_c = (255, random.randint(200, 255), 150)
        elif self.mode == 'Fire':
            self.x = random.randint(0, self.w)
            self.y = self.h + random.randint(0, 20)
            self.base_vy = random.uniform(-2, -6)
            self.vx = random.uniform(-1, 1)
            self.decay = random.randint(3, 8)
            self.base_size = random.randint(4, 12)
            base_c = (255, random.randint(0, 100), 0)
        elif self.mode == 'Floating Embers' or self.mode == 'White Embers':
            self.x = random.randint(0, self.w)
            self.y = self.h + 10
            self.base_vy = random.uniform(-1, -2)
            self.vx = random.uniform(-0.5, 0.5)
            self.decay = random.randint(1, 3)
            self.base_size = random.randint(2, 4)
            if self.mode == 'White Embers':
                base_c = (255, 255, 255)
            else:
                base_c = (255, 100, 50)
        elif self.mode == 'Fog':
            self.x = random.randint(-100, self.w)
            self.y = random.randint(0, self.h)
            self.base_vy = random.uniform(-0.1, 0.1)
            self.vx = random.uniform(0.5, 2.0)
            self.decay = 0
            self.base_size = random.randint(150, 300)
            self.life = random.randint(50, 150)
            g = random.randint(180, 220)
            base_c = (g, g, g + 20)
        else:
            self.z = random.randint(1, 3)
            self.base_vy = 0.5 * self.z
            base_c = (200, 200, 200)

        self.color = base_c

    def update(self, energy_multiplier, params, screen_w, screen_h):
        self.w, self.h = screen_w, screen_h
        rate = params.get('rate', 1.0)
        size_mult = params.get('size', 1.0)
        jit = params.get('jitter', 0.0) * 5.0

        reaction = 1.0 + (energy_multiplier * 3.0)
        current_base_size = self.base_size * size_mult

        if self.mode == 'Warp Speed':
            self.x += self.vx * reaction * rate
            self.y += self.vy * reaction * rate
            self.size = current_base_size + (energy_multiplier * 5 * size_mult)
        elif self.mode == 'Fog':
            self.x += self.vx * rate
            self.y += self.base_vy * rate
            self.size = current_base_size
            if self.x > self.w + self.size: self.x = -self.size
        elif self.mode == 'Deep Space':
            self.life += self.decay
            if self.life >= 255 or self.life <= 100: self.decay *= -1
            self.y += self.base_vy * rate
        else:
            vx_now = self.vx * rate if hasattr(self, 'vx') else 0
            vy_now = (self.base_vy if hasattr(self, 'base_vy') else 0) * rate
            self.x += vx_now * reaction
            self.y += vy_now * reaction
            self.size = current_base_size

        if jit > 0 and self.mode != 'Fog':
            self.x += random.uniform(-jit, jit)
            self.y += random.uniform(-jit, jit)

        # Check for specific modes or any "Magic" variant (excluding White Magic which might want different decay, but here we treat it same)
        is_magic = 'Magic' in self.mode or self.mode == 'White Magic'
        if is_magic or self.mode in ['Warp Speed', 'Sparks', 'Fire']:
            self.life -= abs(self.decay)
            if self.life <= 0: self.reset(params)

        margin = 200 if self.mode == 'Fog' else 50
        if (self.y > self.h + margin) or (self.y < -margin) or (self.x < -margin) or (self.x > self.w + margin):
            self.reset(params)

    def draw(self, surface, params):
        length_mult = params.get('length', 1.0)

        # --- RGB SLIDER LOGIC ---
        # Sliders default to 0.5. Multiplying by 2 allows us to darken (0.0-0.49) or brighten/tint (0.51-1.0).
        # We skip this for Magic Particles variants to preserve their multi-color schemes.
        is_multi_color_magic = (self.mode.startswith(
            'Magic ') and self.mode != 'Magic Particles') or self.mode == 'Magic Particles'

        draw_color = self.color

        if not is_multi_color_magic and self.mode != 'Fog':
            r_mult = params.get('red', 0.5) * 2
            g_mult = params.get('green', 0.5) * 2
            b_mult = params.get('blue', 0.5) * 2

            draw_color = (
                min(255, int(self.color[0] * r_mult)),
                min(255, int(self.color[1] * g_mult)),
                min(255, int(self.color[2] * b_mult))
            )

        # --- FOG RENDERING ---
        if self.mode == 'Fog':
            fog_tex = params.get('fog_texture')
            if fog_tex:
                scale_size = int(self.size)
                if scale_size > 0:
                    draw_surf = pygame.transform.scale(fog_tex, (scale_size, scale_size))
                    r_u, g_u, b_u = params.get('red', 0.5), params.get('green', 0.5), params.get('blue', 0.5)
                    color_surf = pygame.Surface(draw_surf.get_size(), pygame.SRCALPHA)
                    f_alpha = max(0, min(255, int(self.life)))
                    color_surf.fill((int(r_u * 255), int(g_u * 255), int(b_u * 255), f_alpha))
                    draw_surf.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    surface.blit(draw_surf, (self.x - scale_size // 2, self.y - scale_size // 2))
            return

        # --- STANDARD DRAWING ---
        thick_mult = params.get('thick', 1.0)
        draw_thick = max(1, int(self.size * thick_mult))

        # Handle Line-based particles
        if self.mode in ['Rain Effect', 'Matrix Rain', 'Warp Speed', 'Tilted Rain']:
            if self.mode == 'Warp Speed':
                trail_x = self.vx * 2 * length_mult
                trail_y = self.vy * 2 * length_mult
                cx = surface.get_width() * params.get('center_x', 0.5)
                cy = surface.get_height() * params.get('center_y', 0.5)
                should_draw = True
                if params.get('hide_center', False):
                    dist = math.hypot(self.x - cx, self.y - cy)
                    if dist < 80: should_draw = False
                if should_draw:
                    pygame.draw.line(surface, draw_color, (self.x, self.y),
                                     (self.x - trail_x, self.y - trail_y), draw_thick)
            elif self.mode == 'Tilted Rain':
                # Draw angled line
                base_len = 15 + (self.base_vy * 0.5)
                draw_len = base_len * length_mult
                # Calculate tail position based on velocity
                tail_x = self.x - (self.vx * length_mult)
                pygame.draw.line(surface, draw_color, (self.x, self.y), (tail_x, self.y + draw_len), draw_thick)
            else:
                # Standard Rain
                base_len = 15 + (self.base_vy * 0.5)
                draw_len = base_len * length_mult
                pygame.draw.line(surface, draw_color, (self.x, self.y), (self.x, self.y + draw_len), draw_thick)
            return

        # --- OPTIMIZED CIRCLE DRAWING ---
        # Determine Alpha
        alpha_val = 255
        if self.mode == 'Deep Space' or self.life < 255:
            alpha_val = max(0, min(255, int(self.life)))

        size_int = int(self.size)
        if size_int < 1: return

        # 1. Opaque drawing (Fastest, no cache needed)
        if alpha_val == 255:
            pygame.draw.circle(surface, draw_color, (int(self.x), int(self.y)), size_int)

        # 2. Transparent drawing (Needs Caching)
        else:
            # Create Key: (radius, color_tuple, alpha_value)
            cache_key = (size_int, draw_color, alpha_val)

            # Fix for KeyError: Check existence first
            if cache_key not in Particle.surf_cache:
                # Memory Safety: Clear cache if it explodes (e.g. Rainbow mode with changing colors)
                if len(Particle.surf_cache) > 1500:
                    Particle.surf_cache.clear()

                # Create Surface
                s = pygame.Surface((size_int * 2, size_int * 2), pygame.SRCALPHA)
                # Draw circle on transparent surface
                pygame.draw.circle(s, (*draw_color, alpha_val), (size_int, size_int), size_int)
                # Store
                Particle.surf_cache[cache_key] = s

            # Blit from Cache
            surface.blit(Particle.surf_cache[cache_key], (self.x - size_int, self.y - size_int))

import queue
from collections import deque

class ThreadedVideo:
    def __init__(self, path):
        cv2.setNumThreads(0)

        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0 or math.isnan(self.fps): self.fps = 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps

        self.running = True
        self.lock = threading.Lock()

        self.frame_cnt = 0
        self.frame_buffer = deque(maxlen=64)  # Buffer ~1-2 seconds

        # The time the song is currently at (updated by main loop)
        self.external_time_ref = 0.0
        self.hard_seek_req = -1

        # High Quality Resolution Cap (1080p)
        self.process_dim = (1920, 1080)

        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()


    def update(self):
        while self.running:
            # 1. HANDLE HARD SEEK (User clicked progress bar)
            with self.lock:
                req = self.hard_seek_req
                ref_time = self.external_time_ref

            if req != -1:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, req)
                self.frame_cnt = req
                with self.lock:
                    self.frame_buffer.clear()
                    self.hard_seek_req = -1
                continue

            # 2. CALCULATE SYNC
            # Current time of the frame the decoder is sitting on
            decoder_time = self.frame_cnt / self.fps

            # If decoder is WAY ahead (buffer full), sleep
            if decoder_time > ref_time + 2.0 and len(self.frame_buffer) > 30:
                time.sleep(0.02)
                continue

            # 3. SMART SKIP (The Fix for Slow Motion)
            # If decoder is BEHIND the song by > 0.1s, skip decoding this frame.
            # cap.grab() is extremely fast (just moves pointer).
            if decoder_time < ref_time - 0.1:
                self.cap.grab()  # Skip heavy decoding
                self.frame_cnt += 1
                continue

            # 4. DECODE
            # If we are in the "sweet spot" (near current time or slightly future), decode fully.
            ret, frame = self.cap.read()
            if ret:
                self.frame_cnt += 1
                timestamp = (self.frame_cnt - 1) / self.fps

                # Resize Logic (1080p Cap)
                h, w = frame.shape[:2]

                if w > 1920 or h > 1080:
                    scale = min(1920 / w, 1080 / h)
                    new_w, new_h = int(w * scale), int(h * scale)
                    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                # Color Convert
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Store
                frame_data = frame.tobytes()
                shape = frame.shape[:2]

                with self.lock:
                    self.frame_buffer.append((timestamp, frame_data, shape))
            else:
                # End of video
                time.sleep(0.05)

    def sync(self, song_time):
        """Main loop tells us where the song is"""
        with self.lock:
            self.external_time_ref = song_time

            # If we are drastically far off (> 5 seconds), trigger hard seek.
            # Otherwise, let the 'Smart Skip' in update() handle the catchup.
            current_decoder_time = self.frame_cnt / self.fps
            if abs(current_decoder_time - song_time) > 5.0:
                self.hard_seek_req = int(song_time * self.fps)

    def get_frame(self, target_time):
        """Returns the best matching frame from buffer"""
        best_data = None
        best_shape = None

        with self.lock:
            if not self.frame_buffer: return None

            # Clean old frames (older than 1 second ago)
            while len(self.frame_buffer) > 1 and self.frame_buffer[0][0] < target_time - 1.0:
                self.frame_buffer.popleft()

            # Find closest frame
            closest_diff = float('inf')

            for ts, data, shape in self.frame_buffer:
                diff = abs(ts - target_time)
                if diff < closest_diff:
                    closest_diff = diff
                    best_data = data
                    best_shape = shape
                else:
                    # Buffer is sorted, so if diff gets worse, we are done
                    break

        return best_data, best_shape

    def release(self):
        self.running = False
        self.thread.join()
        self.cap.release()

class MusicVisualizer:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.quit()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE, vsync=1)
        pygame.display.set_caption("Audio Visualizer")
        self.clock = pygame.time.Clock()

        # Cache for colors
        self.color_cache = {}

        # --- FONT SYSTEM ---
        sys_fonts = pygame.font.get_fonts()
        self.available_fonts = sorted(sys_fonts)
        self.font_name = 'arial'
        if 'segue ui' in self.available_fonts: self.font_name = 'segue ui'

        self.font_size = 12
        self.ui_font = None
        self.title_font = None
        self.bold_font = None

        # Dynamic UI Height & Resizing
        self.ui_panel_height = UI_PANEL_HEIGHT
        self.min_panel_height = 4
        self.is_resizing_panel = False
        self.update_fonts()

        # --- DROPDOWN STATE ---
        self.dropdown_scroll_offset = 0  # Generic offset for any active dropdown
        self.dropdown_max_visible = 8
        self.is_dragging_scrollbar = False
        self.dropdown_track_rect = None
        self.dropdown_thumb_rect = None

        # State
        self.running = True
        self.playing = False
        self.paused = False
        self.loading = False
        self.playlist = []
        self.original_playlist = []
        self.current_song_index = 0
        self.volume = 0.5
        self.shuffle_mode = False
        self.color_flip = False
        self.loop_once = False
        self.loop_forever = False
        self.song_finished_flag = False  # Flag to trigger next song on main thread

        # Audio
        self.current_duration = 1
        self.current_offset = 0
        self.audio_data = np.zeros(CHUNK)
        self.current_energy = 0.0
        self.seek_request = None
        self.previous_fft = np.zeros(60)
        self.peak_heights = np.zeros(60)

        # Improved Beat Detection (Stabilized)
        self.bpm = 0
        self.beat_times = []
        self.beat_intervals = []  # Store history of intervals
        self.last_beat_time = 0
        self.beat_threshold = 0.6
        self.smoothing_factor = 0.6

        # Interaction
        self.is_dragging_seek = False
        self.is_dragging_vol = False
        self.is_dragging_smooth = False  # Smoothing slider drag
        self.drag_progress = 0.0

        # Visuals
        self.current_visual_mode = 0
        self.current_color_mode = 0
        self.current_bg_mode = 1  # Default Layer 1 (Set to 1 so it isn't 'None')
        self.current_bg_mode_2 = 0 # Default Layer 2
        self.current_ui_pattern_mode = 1  # Default to Grid
        self.current_sort_mode = 0  # 0 = Notes Placement (Linear), 1 = Bass & Melody (Center)
        self.current_bar_style = 0  # Default to Solid
        self.current_color_cycle_mode = 0  # 0 = Static, 1 = Random Cycle
        self.show_ui = True
        self.is_fullscreen = False

        # Custom Colors (10 Slots)
        self.custom_colors = [
            (255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0),
            (0, 255, 128), (0, 255, 255), (0, 128, 255), (0, 0, 255),
            (128, 0, 255), (255, 0, 255)
        ]

        self.particles = []

        # UI Rects
        self.btn_play_rect = None
        self.btn_prev_rect = None
        self.btn_next_rect = None
        self.btn_shuffle_rect = None
        self.btn_loop_once_rect = None
        self.btn_loop_forever_rect = None
        self.seek_bar_rect = None
        self.vol_bar_rect = None
        self.smooth_bar_rect = None  # Rect for smoothing slider
        self.resize_handle_rect = None
        self.color_slots_rects = []

        self.btn_font_size_up = None
        self.btn_font_size_down = None
        self.btn_font_type = None

        self.status_msg = ""
        self.status_timer = 0

        self.p = pyaudio.PyAudio()
        self.stream = None
        self.audio_thread = None
        self.stop_audio_flag = False

        self.show_bpm = True  # Toggle for BPM
        self.show_playlist_counter = True  # Toggle for Playlist Counter x/y

        # --- THEME CUSTOMIZATION ---
        # Create a default template
        default_params = {
            'rate': 1.0, 'color': 1.0, 'thick': 1.0,
            'length': 1.0, 'size': 1.0, 'jitter': 0.0,
            'decay': 1.0,
            'threshold': 0.5,
            'collapse_mode': 0,
            'show_line': True,
            'noise_gate': 0.15,
            'idle_mode': 0, # (0 = Original, 1 = Disappear, 2 = Match Dock)
            'hollow_thick': 1.0,
            'bar_count': 60.0
        }

        # Create separate parameters for EACH visual mode
        self.vis_params_sets = {}
        for mode in VISUAL_MODES:
            self.vis_params_sets[mode] = default_params.copy()

        # Create separate parameters for EACH color mode
        # 'color' key here represents variance/spread
        default_color_params = {'rate': 1.0, 'color': 1.0, 'threshold': 1.0}
        self.color_params_sets = {}
        for mode in COLOR_MODES:
            self.color_params_sets[mode] = default_color_params.copy()

        # BG: Background specific params
        self.bg_params = {
            'rate': 1.0, 'size': 1.0,
            'red': 0.5, 'green': 0.5, 'blue': 0.5, 'var': 0.0,
            'center_x': 0.5, 'center_y': 0.5,
            'hide_center': True,
            'img_enabled': 0,
            'img_opacity': 0.5,
            'video_opacity': 1.0,
            'img_anim': 0,
            'img_path': "",
            'video_path': "",
            'carousel_path': "",  # Folder path
            'carousel_fade': 2.0,  # Default fade duration (seconds)
            'video_offset': 0.0,  # With negative offset value
            'video_start_trigger': 0.0,
            'video_pos_x': 0.0,  # X Position (-500 to 500 equivalent)
            'video_pos_y': 0.0,  # Y Position (-500 to 500 equivalent)
            'img_pulse_scale': 0.05,
            'img_bright': 0.0,
            'max_particles': 1500.0,  # Default to max
            'glow_enabled': False,  # Toggle
            'glow_r': 1.0,  # Red
            'glow_g': 0.6,  # Green
            'glow_b': 0.2,  # Blue
            'glow_intensity': 0.5,  # Base Opacity
            'glow_height': 0.4,  # Screen Height percentage
            'glow_pulse': 1.0  # How much it reacts to bass
        }

        # --- GLOW CACHE ---
        self.bg_glow_cache = None
        self.bg_glow_last_params = None # To detect when to redraw the gradient

        self.bg_image_surface = None
        self.bg_original_image = None
        self.bg_image_rect = None
        self.video_cap = None  # Object to hold the video stream

        # --- VIDEO STATE VARIABLES ---
        self.bg_video_fps = 60.0
        self.bg_video_last_update = 0
        self.bg_video_surface_cache = None  # Stores the last frame to draw between updates
        self.bg_crossfade = 0.0  # 0.0 = Image, 1.0 = Video

        # --- IMAGE CAROUSEL STATE ---
        self.bg_prev_image = None
        self.bg_transition_start = 0
        self.bg_is_transitioning = False

        # Add new default params for Pulse and Glow
        if 'img_pulse_scale' not in self.bg_params: self.bg_params['img_pulse_scale'] = 0.05
        if 'img_bright' not in self.bg_params: self.bg_params['img_bright'] = 0.0

        # Persistence for smooth collapse
        self.displayed_fft = np.zeros(60)
        self.fft_snapshot = np.zeros(60)  # Value when music stops
        self.collapse_start_time = None  # Timer for animation

        # UI State for which set we are currently editing ('FG' or 'BG')
        self.settings_target = 'FG'

        # UI Slider Rects storage
        self.param_slider_rects = {}

        self.load_settings()

        # --- OPTIMIZATION: CACHING ---
        self.ui_surface_cache = None
        self.radial_shadow_cache = None  # Added for Radial Mode Optimization
        # Radial Math Lookup Tables (LUT)
        self.rad_lut_num = 0
        self.rad_lut_cos = None
        self.rad_lut_sin = None
        self.rad_lut_indices = None
        self.rad_buffer_points = None  # Pre-allocated memory for points

        self.ui_surface_height_cache = -1
        self.text_cache = {}
        self.fft_window = np.hanning(CHUNK)
        # OPTIMIZATION: Pre-calculate Equalization Curve
        # This replaces the loop inside calculate_fft
        self.fft_eq_curve = 1.0 + (np.arange(60) * 0.04)

        # --- PROCEDURAL FOG TEXTURE ---
        # Pre-render a fuzzy blob for realistic fog
        self.fog_texture = pygame.Surface((200, 200), pygame.SRCALPHA)
        for r in range(100, 0, -2):
            # Gradient alpha from center (40) to edge (0)
            alpha = int((100 - r) * 0.4)
            pygame.draw.circle(self.fog_texture, (200, 200, 220, alpha), (100, 100), r)
        self.bg_params['fog_texture'] = self.fog_texture

        # --- UI STATE ---
        self.show_settings = False
        self.active_dropdown = None
        self.settings_changed = False
        self.active_input = None
        self.input_text = ""

        self.ui_buttons = {}
        self.ui_toggles = {}
        self.ui_dropdowns = {}
        self.ui_dropdown_options_rects = []

    # --- SETTINGS ---
    def update_fonts(self):
        self.ui_font = pygame.font.SysFont(self.font_name, self.font_size)
        self.title_font = pygame.font.SysFont(self.font_name, self.font_size + 8, bold=True)
        self.bold_font = pygame.font.SysFont(self.font_name, self.font_size + 2, bold=True)

    def save_settings(self):
        # --- FIX: Sanitize bg_params ---
        # Create a copy so we don't delete the texture from the actual running app
        bg_params_safe = self.bg_params.copy()

        # Remove the pygame.Surface object which cannot be saved to JSON
        if 'fog_texture' in bg_params_safe:
            del bg_params_safe['fog_texture']

        data = {
            "volume": self.volume,
            "smoothing": self.smoothing_factor,
            "font_size": self.font_size,
            "font_name": self.font_name,
            "ui_height": self.ui_panel_height,
            "shuffle": self.shuffle_mode,
            "loop_once": self.loop_once,
            "loop_forever": self.loop_forever,
            "show_bpm": self.show_bpm,
            "show_playlist_counter": self.show_playlist_counter,
            "vis_params_sets": self.vis_params_sets,
            "color_params_sets": self.color_params_sets,
            "bg_params": bg_params_safe,  # <--- Save the sanitized version
            "visual_mode": self.current_visual_mode,
            "color_mode": self.current_color_mode,
            "bg_mode": self.current_bg_mode,
            "bg_mode_2": self.current_bg_mode_2,
            "ui_pattern_mode": self.current_ui_pattern_mode,
            "sort_mode": self.current_sort_mode,
            "bar_style": self.current_bar_style,
            "color_cycle_mode": self.current_color_cycle_mode,
            "custom_colors": self.custom_colors
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(data, f)
            self.set_status("Settings Saved!")
        except Exception as e:
            print(f"Save Error: {e}")
            self.set_status("Save Error!")

    def load_settings(self):
        if not os.path.exists("settings.json"): return
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
            self.volume = data.get("volume", 0.5)
            self.smoothing_factor = data.get("smoothing", 0.6)
            self.font_size = data.get("font_size", 12)
            saved_font = data.get("font_name", 'arial')
            if saved_font in self.available_fonts:
                self.font_name = saved_font

            self.ui_panel_height = max(self.min_panel_height, min(UI_PANEL_HEIGHT, data.get("ui_height", UI_PANEL_HEIGHT)))
            self.shuffle_mode = data.get("shuffle", False)
            self.loop_once = data.get("loop_once", False)
            self.loop_forever = data.get("loop_forever", False)
            self.show_bpm = data.get("show_bpm", True)
            self.show_playlist_counter = data.get("show_playlist_counter", True)

            # Load params if they exist
            if "vis_params_sets" in data:
                # Load specific sets per mode
                loaded_sets = data["vis_params_sets"]
                for mode, p in loaded_sets.items():
                    if mode in self.vis_params_sets:
                        self.vis_params_sets[mode].update(p)
                        if 'hollow_thick' not in self.vis_params_sets[mode]:
                            self.vis_params_sets[mode]['hollow_thick'] = 1.0
            if "color_params_sets" in data:
                loaded_colors = data["color_params_sets"]
                for mode, p in loaded_colors.items():
                    if mode in self.color_params_sets:
                        self.color_params_sets[mode].update(p)
            elif "fg_params" in data:
                # Legacy migration: apply old single settings to ALL modes
                for mode in self.vis_params_sets:
                    self.vis_params_sets[mode].update(data["fg_params"])

            if "bg_params" in data:
                self.bg_params.update(data["bg_params"])

            self.current_visual_mode = data.get("visual_mode", 0)
            self.current_color_mode = data.get("color_mode", 0)
            self.current_bg_mode = data.get("bg_mode", 1)
            self.current_bg_mode_2 = data.get("bg_mode_2", 0)
            self.current_ui_pattern_mode = data.get("ui_pattern_mode", 1)
            self.current_sort_mode = data.get("sort_mode", 0)
            self.current_bar_style = data.get("bar_style", 0)
            self.current_color_cycle_mode = data.get("color_cycle_mode", 0)
            if "custom_colors" in data:
                self.custom_colors = [tuple(c) for c in data["custom_colors"]]
            self.update_fonts()
        except:
            pass

    # --- UTILS ---
    def set_status(self, msg):
        self.status_msg = msg;
        self.status_timer = time.time() + 2.5

    def lerp_color(self, c1, c2, t):
        """Linear interpolation between two RGB tuples"""
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    def get_ease_value(self, t, mode_index):
        """ Returns a value from 0.0 to 1.0 based on time t (0.0 to 1.0) """
        mode = COLLAPSE_MODES[mode_index]
        t = max(0.0, min(1.0, t))

        if mode == 'Linear':
            return t
        elif mode == 'Exponential':
            return t * t * t * t
        elif mode == 'Inv. Exponential':
            return 1 - (1 - t) ** 4
        elif mode == 'Sine':
            return math.sin(t * math.pi / 2)
        elif mode == 'Cosine':
            return 1 - math.cos(t * math.pi / 2)
        elif mode == 'Bouncy':
            if t < (1 / 2.75):
                return 7.5625 * t * t
            elif t < (2 / 2.75):
                t -= (1.5 / 2.75)
                return 7.5625 * t * t + 0.75
            elif t < (2.5 / 2.75):
                t -= (2.25 / 2.75)
                return 7.5625 * t * t + 0.9375
            else:
                t -= (2.625 / 2.75)
                return 7.5625 * t * t + 0.984375
        return t

    def render_text(self, text, font, color):
        """Cached text rendering to prevent massive FPS drops"""
        key = (text, font, color)
        if key not in self.text_cache:
            self.text_cache[key] = font.render(text, True, color)
        return self.text_cache[key]

    # --- PLAYLIST ---
    def save_playlist(self):
        if not self.playlist: return
        root = tk.Tk();
        root.withdraw()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, 'w') as f:
                    json.dump(self.playlist, f)
                self.set_status("Playlist Saved!")
            except:
                self.set_status("Error Saving!")

    def load_playlist(self):
        root = tk.Tk();
        root.withdraw()
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, 'r') as f:
                    loaded = json.load(f)
                valid = []
                for entry in loaded:
                    p = entry.get("path", "") if isinstance(entry, dict) else entry
                    if p and os.path.exists(p): valid.append(p)
                if valid:
                    self.playlist = valid
                    self.original_playlist = self.playlist.copy()
                    self.set_status(f"Loaded {len(valid)} Songs")
                    self.stop_audio_flag = True
                    if self.audio_thread: self.audio_thread.join()
                    self.start_song(0)
            except:
                self.set_status("Error Loading!")

    def clear_playlist(self):
        self.playlist = [];
        self.stop_audio_flag = True;
        self.playing = False;
        self.set_status("Cleared")

    def get_files(self):
        root = tk.Tk();
        root.withdraw()
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav")])
        if files:
            self.playlist.extend(list(files))
            self.original_playlist = self.playlist.copy()
            self.set_status(f"Added {len(files)} files")
            if not self.playing: self.start_song(0)

    def get_folder(self):
        root = tk.Tk();
        root.withdraw()
        folder = filedialog.askdirectory()
        if folder:
            for r, d, f in os.walk(folder):
                for file in f:
                    if file.lower().endswith(('.mp3', '.wav')): self.playlist.append(os.path.join(r, file))
            self.original_playlist = self.playlist.copy()
            if not self.playing and self.playlist: self.start_song(0)

    # --- AUDIO ---
    def toggle_shuffle(self):
        if not self.playlist: return
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode:
            curr = self.playlist[self.current_song_index]
            rest = [x for x in self.playlist if x != curr]
            random.shuffle(rest)
            self.playlist = [curr] + rest
            self.current_song_index = 0
            self.set_status("Shuffle ON")
        else:
            curr = self.playlist[self.current_song_index]
            self.playlist = self.original_playlist.copy()
            try:
                self.current_song_index = self.playlist.index(curr)
            except:
                self.current_song_index = 0
            self.set_status("Shuffle OFF")

    def next_song(self):
        if self.playlist: self.start_song((self.current_song_index + 1) % len(self.playlist))

    def prev_song(self):
        if self.playlist: self.start_song((self.current_song_index - 1) % len(self.playlist))

    def handle_song_end(self):
        """Decides what to do when a song finishes naturally"""

        # --- CAROUSEL TRIGGER ---
        # If in Carousel mode (index 4), pick a new image
        if self.bg_params.get('img_enabled') == 4:
            self.trigger_carousel_switch()

        if self.loop_forever:
            self.start_song(self.current_song_index)
        elif self.loop_once:
            self.loop_once = False  # Disable after one loop
            self.start_song(self.current_song_index)
            self.set_status("Loop Once: Done")
        else:
            self.next_song()

    def sort_playlist(self, mode_index):
        if not self.playlist: return

        # 1. Remember the currently playing song so we don't lose it
        current_path = self.playlist[self.current_song_index]

        mode = SORT_ALGO[mode_index]

        if mode == 'Name (A-Z)':
            self.playlist.sort(key=lambda x: os.path.basename(x).lower())
        elif mode == 'Name (Z-A)':
            self.playlist.sort(key=lambda x: os.path.basename(x).lower(), reverse=True)
        elif mode == 'File Size (Small)':
            self.playlist.sort(key=lambda x: os.path.getsize(x))
        elif mode == 'File Size (Large)':
            self.playlist.sort(key=lambda x: os.path.getsize(x), reverse=True)

        # 2. Find where the current song moved to
        try:
            self.current_song_index = self.playlist.index(current_path)
        except ValueError:
            self.current_song_index = 0

        self.set_status(f"Sorted: {mode}")

    def start_song(self, index):
        if 0 <= index < len(self.playlist):
            self.current_song_index = index
            # --- COLOR CYCLE LOGIC ---
            if self.current_color_cycle_mode == 1: # Random Cycle
                # Pick a random color mode
                self.current_color_mode = random.randint(0, len(COLOR_MODES) - 1)
                # Force Dock Redraw (Update Divider Line Color)
                self.ui_surface_cache = None
            self.loading = True
            self.stop_audio_flag = True
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join()
            self.stop_audio_flag = False
            self.song_finished_flag = False
            self.paused = False
            self.audio_thread = threading.Thread(target=self.play_audio_logic)
            self.audio_thread.start()

    def play_audio_logic(self):
        try:
            path = self.playlist[self.current_song_index]

            # 1. Load Audio
            audio = AudioSegment.from_file(path)

            # 2. Convert if necessary
            if audio.frame_rate != RATE:
                audio = audio.set_frame_rate(RATE)
            if audio.channels != 1:
                audio = audio.set_channels(1)

            raw = audio.raw_data
            self.current_duration = len(raw)
            self.current_offset = 0
            bpc = CHUNK * 2

            # --- CHANGE 1: Do NOT open the stream here yet. ---
            # We initialize these to None so the loop handles the startup.
            self.stream = None
            # Ensure self.p is cleared if it existed from a previous run
            if hasattr(self, 'p') and self.p is not None:
                try:
                    self.p.terminate()
                except:
                    pass
            self.p = None

            self.playing = True
            self.loading = False

            # BPM Vars
            energy_history = []

            while self.current_offset < len(raw):
                if self.stop_audio_flag: break

                # Handle Seek
                if self.seek_request is not None:
                    seek_pos = int(self.seek_request)
                    self.current_offset = seek_pos - (seek_pos % bpc)
                    self.seek_request = None

                # --- CHANGE 2: DYNAMIC PAUSE/UNPAUSE LOGIC ---
                if self.paused:
                    # If we are paused, but the stream is still open, CLOSE IT.
                    # This releases the audio device so we can switch to Bluetooth.
                    if self.stream is not None:
                        self.stream.stop_stream()
                        self.stream.close()
                        self.stream = None
                        # Terminate PyAudio to force a device refresh next time
                        if self.p is not None:
                            self.p.terminate()
                            self.p = None

                    # Sleep to save CPU while paused
                    time.sleep(0.1)
                    continue

                # If we are NOT paused (playing), but the stream is closed (startup or just unpaused),
                # OPEN IT. This detects the CURRENT default device (e.g. Bluetooth).
                if self.stream is None:
                    self.p = pyaudio.PyAudio()
                    self.stream = self.p.open(format=self.p.get_format_from_width(audio.sample_width),
                                              channels=1, rate=RATE, output=True)

                # --- STANDARD PLAYBACK ---
                data = raw[self.current_offset:self.current_offset + bpc]
                if len(data) < bpc: break

                # Convert to numpy
                sig = np.frombuffer(data, dtype=np.int16)

                # --- VISUALS GET RAW SIGNAL, SPEAKERS GET VOLUME SIGNAL ---
                self.audio_data = sig  # Visualizer gets full strength signal

                # Create separate signal for audio output
                output_sig = sig

                # Apply Volume to Output only
                if self.volume != 1.0:
                    output_sig = sig * self.volume
                    output_sig = output_sig.astype(np.int16)

                # Write to stream
                if self.stream:
                    self.stream.write(output_sig.tobytes())

                self.current_offset += bpc

                # --- BPM DETECTION ---
                rms = np.mean(np.abs(sig[::4]))
                self.current_energy = min(1.0, rms / 8000.0)

                if rms > 500:
                    energy_history.append(rms)
                    if len(energy_history) > 40: energy_history.pop(0)
                    avg_energy = np.mean(energy_history) if energy_history else 0

                    curr_time = time.time()
                    if rms > avg_energy * 1.3 and (curr_time - self.last_beat_time) > 0.3:
                        interval = curr_time - self.last_beat_time
                        self.last_beat_time = curr_time

                        if 0.3 < interval < 1.5:
                            self.beat_intervals.append(interval)
                            if len(self.beat_intervals) > 12: self.beat_intervals.pop(0)

                        if len(self.beat_intervals) >= 4:
                            med_interval = np.median(self.beat_intervals)
                            new_bpm = int(60 / med_interval)
                            if self.bpm == 0:
                                self.bpm = new_bpm
                            elif abs(new_bpm - self.bpm) > 2:
                                self.bpm = int((self.bpm * 0.7) + (new_bpm * 0.3))

            # Cleanup at end of song
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            if self.p:
                self.p.terminate()
                self.p = None

            self.playing = False
            if not self.stop_audio_flag:
                self.song_finished_flag = True
        except Exception as e:
            print(f"Audio Error: {e}")
            self.playing = False

    # --- VISUALS ---
    def calculate_fft(self):
        if len(self.audio_data) == 0: return np.zeros(60)

        n = len(self.audio_data)
        if len(self.fft_window) != n:
            self.fft_window = np.hanning(n)

        fft_res = np.fft.rfft(self.audio_data * self.fft_window)
        mag = np.abs(fft_res) / CHUNK

        # 1. Logarithmic Boost
        mag = np.log10(np.maximum(mag, 1)) * 20

        # --- DYNAMIC BAR COUNT LOGIC ---
        # Retrieve target count from current mode settings
        cur_mode = VISUAL_MODES[self.current_visual_mode]
        target_count = int(self.vis_params_sets[cur_mode].get('bar_count', 60))
        target_count = max(10, min(300, target_count))  # Clamp 10-300

        # Slice or Interpolate to match target_count
        # Simple slicing is fastest for visualizer
        if len(mag) > target_count:
            mag = mag[:target_count]
        else:
            # Pad if we somehow have fewer frequencies than bars (rare with current CHUNK)
            mag = np.pad(mag, (0, target_count - len(mag)), 'constant')

        # --- DYNAMIC EQUALIZATION ---
        # Generate curve on the fly based on current count
        eq_curve = 1.0 + (np.linspace(0, 2.4, len(mag)))
        mag *= eq_curve

        # Apply User Smoothing
        s = self.smoothing_factor

        # Handle Array Size Mismatch (if slider changed while playing)
        if len(self.previous_fft) != len(mag):
            self.previous_fft = np.zeros(len(mag))
            # Also resize peak heights immediately to prevent crash in draw_visuals
            self.peak_heights = np.zeros(len(mag))

        # Vectorized smoothing
        mag = mag * (1.0 - s) + self.previous_fft * s

        self.previous_fft = mag
        return mag

    def get_bar_color(self, val, i, total):
        mode = COLOR_MODES[self.current_color_mode]
        params = self.color_params_sets[mode]

        rate_mult = params['rate']
        col_var = params['color']
        thresh = params.get('threshold', 0.5)

        # Time-based variable for animation
        t = pygame.time.get_ticks() * 0.005 * rate_mult

        # Handle Mirror/Reversion (Horizontal Flip)
        calc_i = i
        if self.color_flip:
            calc_i = total - i

        # Standard Horizontal Ratio (0.0 to 1.0 across the screen)
        ratio = (calc_i / total) * (col_var * 1.5)
        ratio = ratio % 1.0

        # Vertical Ratio (0.0 to 1.0 based on volume height)
        h_ratio = min(1.0, val / 80.0)

        # --- FIX: Handle Vertical Flip for Intensity-based modes ---
        # If flipped, invert h_ratio so colors run Top-to-Bottom instead of Bottom-to-Top
        if self.color_flip:
            h_ratio = 1.0 - h_ratio

        # --- 1. Custom ---
        if mode == 'Custom':
            cycle_speed = 0.5 * rate_mult
            now = time.time() * cycle_speed
            idx = int(now) % len(self.custom_colors)
            next_idx = (idx + 1) % len(self.custom_colors)
            blend = now - int(now)
            return self.lerp_color(self.custom_colors[idx], self.custom_colors[next_idx], blend)

        # --- 2. Sunset ---
        if mode == 'Sunset': return self.lerp_color((45, 0, 100), (255, 150, 0), ratio)

        # --- 3. Cotton Candy ---
        if mode == 'Cotton Candy': return self.lerp_color((255, 100, 200), (0, 255, 255), ratio)

        # --- 4. Fire & Ice ---
        if mode == 'Fire & Ice':
            if ratio < thresh:
                sub_ratio = ratio / max(0.01, thresh)
                return self.lerp_color((255, 50, 0), (255, 200, 0), sub_ratio)
            else:
                sub_ratio = (ratio - thresh) / max(0.01, (1.0 - thresh))
                return self.lerp_color((0, 100, 255), (200, 255, 255), sub_ratio)

        # --- 5. Toxic ---
        if mode == 'Toxic': return self.lerp_color((50, 255, 0), (100, 0, 255), ratio)

        # --- 6. Patriot ---
        if mode == 'Patriot':
            if ratio < 0.33:
                return (255, 0, 0)
            elif ratio < 0.66:
                return (255, 255, 255)
            else:
                return (0, 0, 255)

        # --- 7. Aurora ---
        if mode == 'Aurora':
            if ratio < thresh:
                sub_ratio = ratio / max(0.01, thresh)
                return self.lerp_color((0, 255, 100), (0, 100, 255), sub_ratio)
            else:
                sub_ratio = (ratio - thresh) / max(0.01, (1.0 - thresh))
                return self.lerp_color((0, 100, 255), (150, 0, 255), sub_ratio)

        # --- 8. Rainbow ---
        if mode == 'Rainbow':
            hue = (calc_i * 3 * col_var + (t * 50)) % 360
            c = pygame.Color(0)
            c.hsla = (hue, 100, 50, 100)
            return (c.r, c.g, c.b)

        # --- 9. Cyberpunk ---
        if mode == 'Cyberpunk':
            # FIX: Use h_ratio so it respects the Color Flip
            intensity = h_ratio
            base = (0, 255, 255)
            return (max(int(base[0] * intensity), 20), max(int(base[1] * intensity), 20),
                    max(int(base[2] * intensity), 20))

        # --- 10. Fire ---
        if mode == 'Fire':
            # FIX: Use h_ratio so it respects the Color Flip
            intensity = h_ratio
            if intensity > thresh: return (255, 255, 150)
            base = (255, 100, 0)
            return (max(int(base[0] * intensity), 20), max(int(base[1] * intensity), 20),
                    max(int(base[2] * intensity), 20))

        # --- 11. Thermal (Vertical Physics) ---
        if mode == 'Thermal':
            if h_ratio < 0.66:
                return self.lerp_color((0, 0, 150), (0, 255, 0), h_ratio * 3)
            elif h_ratio < 0.99:
                return self.lerp_color((0, 255, 0), (255, 0, 0), (h_ratio - 0.33) * 3)
            else:
                return self.lerp_color((255, 0, 0), (255, 255, 255), (h_ratio - 0.66) * 3)

        # --- 12. Oceanic (Vertical Depth) ---
        if mode == 'Oceanic':
            base_col = self.lerp_color((0, 5, 30), (0, 200, 200), h_ratio)
            if h_ratio > 0.99:
                return self.lerp_color(base_col, (255, 255, 255), (h_ratio - 0.8) * 5)
            return base_col

        # --- 13. Jungle (Texture Pattern) ---
        if mode == 'Jungle':
            is_odd = (calc_i % 2 == 0)
            green_shade = (34, 139, 34) if is_odd else (50, 205, 50)
            return self.lerp_color((101, 67, 33), green_shade, h_ratio)

        # --- 14. Noir (Intensity / Value) ---
        if mode == 'Noir':
            grey = int(h_ratio * 255)
            if h_ratio < 0.66: return (40, 35, 30)
            return (grey, grey, grey)

        # --- 15. Vaporwave (Horizontal Gradient) ---
        if mode == 'Vaporwave':
            return self.lerp_color((255, 105, 180), (0, 255, 255), ratio)

        # --- 16. Gold Rush (Glow) ---
        if mode == 'Gold Rush':
            return self.lerp_color((100, 60, 0), (255, 215, 0), h_ratio)

        # --- 17. Nebula (Randomized Texture) ---
        if mode == 'Nebula':
            sin_v = (math.sin(i * 0.75 + t) + 1) / 2
            col_1 = self.lerp_color((75, 0, 130), (138, 43, 226), sin_v)
            return self.lerp_color(col_1, (255, 0, 200), h_ratio)

        # --- 18. Blueprint (Tech Style) ---
        if mode == 'Blueprint':
            return self.lerp_color((0, 50, 100), (255, 255, 255), h_ratio)

        # --- 19. Crimson Tide (Vertical Gradient) ---
        if mode == 'Crimson Tide':
            return self.lerp_color((50, 0, 0), (255, 100, 100), h_ratio)

        # --- 20. Radioactive (Glow) ---
        if mode == 'Radioactive':
            if h_ratio < 0.80:
                return self.lerp_color((10, 20, 10), (57, 255, 20), h_ratio * 2)
            else:
                return self.lerp_color((57, 255, 20), (255, 255, 0), (h_ratio - 0.5) * 2)

        # --- 21. Candy Cane (Pattern) ---
        if mode == 'Candy Cane':
            pattern = (calc_i + int(val / 10)) % 2
            return (255, 255, 255) if pattern == 0 else (255, 0, 0)

        # --- 22. Midnight City (Dual Colors) ---
        if mode == 'Midnight City':
            return self.lerp_color((10, 10, 50), (255, 0, 128), h_ratio)

        # --- 23. Heatmap (3-Stage Vertical) ---
        if mode == 'Heatmap':
            if h_ratio < 0.95:
                return self.lerp_color((50, 0, 100), (255, 100, 0), h_ratio * 2)
            else:
                return self.lerp_color((255, 100, 0), (255, 255, 100), (h_ratio - 0.5) * 2)

        # --- 24. Prism (Refraction) ---
        if mode == 'Prism':
            sector = calc_i / total
            if sector < 0.75:
                return self.lerp_color((255, 0, 0), (255, 255, 0), h_ratio)
            elif sector < 0.99:
                return self.lerp_color((0, 255, 0), (0, 255, 255), h_ratio)
            else:
                return self.lerp_color((0, 0, 255), (255, 0, 255), h_ratio)

        # --- 25. Zenith (Sky Gradient) ---
        if mode == 'Zenith':
            return self.lerp_color((255, 100, 50), (100, 150, 255), h_ratio)

        # --- 26. Obsidian (Contrast) ---
        if mode == 'Obsidian':
            if h_ratio > 0.9: return (200, 100, 255)
            return self.lerp_color((20, 20, 20), (80, 40, 90), h_ratio)

        # --- 27. Plasma (Energy) ---
        if mode == 'Plasma':
            shift = math.sin(t * 5 + (i / 10))
            col = self.lerp_color((100, 0, 255), (0, 200, 255), (shift + 1) / 2)
            return self.lerp_color((50, 0, 100), col, h_ratio)

        # --- 28. Emerald City (Monochromatic Green) ---
        if mode == 'Emerald City':
            return self.lerp_color((0, 60, 20), (100, 255, 150), h_ratio)

        # --- 29. Solar Flare (Intense) ---
        if mode == 'Solar Flare':
            base = self.lerp_color((100, 0, 0), (255, 140, 0), h_ratio)
            if h_ratio > 0.85: return (255, 255, 255)
            return base

        # --- 30. Bismuth (Geometric) ---
        if mode == 'Bismuth':
            step = int(h_ratio * 5)
            if step == 0: return (255, 0, 128)
            if step == 1: return (255, 255, 0)
            if step == 2: return (0, 255, 0)
            if step == 3: return (0, 0, 255)
            return (128, 0, 255)

        # --- NEW ARTISTIC THEMES ---

        # --- 31. Neon Demon (Synthwave) ---
        # Uses vertical gradient from deep purple to hot pink to cyan tip
        if mode == 'Neon Demon':
            if h_ratio < 0.6:
                return self.lerp_color((20, 0, 40), (255, 0, 128), h_ratio * 1.66)
            else:
                return self.lerp_color((255, 0, 128), (0, 255, 255), (h_ratio - 0.6) * 2.5)

        # --- 32. Gaia (Organic Texture) ---
        # Uses index modulo for "grass blade" variance, earth bottom, floral top
        if mode == 'Gaia':
            # Texture variance based on index
            variance = 20 if (calc_i % 2 == 0) else 0
            if h_ratio < 0.3:  # Soil
                return (60 + variance, 40 + variance, 20)
            elif h_ratio < 0.8:  # Vegetation
                return self.lerp_color((34, 139, 34), (154, 205, 50), (h_ratio - 0.3) * 2)
            else:  # Flowers/Bloom
                return self.lerp_color((154, 205, 50), (255, 105, 180), (h_ratio - 0.8) * 5)

        # --- 33. Event Horizon (Cosmic) ---
        # Vantablack base, accretion disk blue, blinding white center
        if mode == 'Event Horizon':
            if h_ratio < 0.5: return (0, 0, 5)  # Void
            if h_ratio < 0.9:
                return self.lerp_color((0, 0, 20), (0, 100, 255), (h_ratio - 0.5) * 2.5)
            return (255, 255, 255)  # Singularity

        # --- 34. Rust Belt (Industrial) ---
        # Gritty texture using noise, orange sparks on grey metal
        if mode == 'Rust Belt':
            # Simulating noise with high frequency sine
            noise = (math.sin(calc_i * 99) + 1) / 2
            metal_grey = 40 + int(noise * 40)
            base = (metal_grey, metal_grey, metal_grey + 10)
            if h_ratio > thresh:  # Sparks
                return self.lerp_color((150, 50, 0), (255, 150, 0), (h_ratio - thresh) / (1 - thresh))
            return base

        # --- 35. Warhol (Pop Art) ---
        # Color banding based on horizontal sections, hard edges
        if mode == 'Warhol':
            section = int((calc_i / total) * 4)  # 4 distinct zones
            if section == 0: return (255, 0, 0)  # Red
            if section == 1: return (255, 255, 0)  # Yellow
            if section == 2: return (0, 255, 255)  # Cyan
            return (255, 0, 255)  # Magenta

        # --- 36. Bioluminescence (Deep Sea) ---
        # Dark water base, glowing neon tips only at high energy
        if mode == 'Bioluminescence':
            deep_sea = (0, 10, 30)
            if h_ratio < 0.7: return deep_sea
            # Sudden glow activation
            glow = self.lerp_color((0, 100, 100), (50, 255, 200), (h_ratio - 0.7) * 3.3)
            return glow

        # --- 37. Royal Velvet (Luxury) ---
        # Deep violet with Gold gradient at top
        if mode == 'Royal Velvet':
            return self.lerp_color((48, 25, 52), (212, 175, 55), h_ratio)

        # --- 38. Glitch Art (Chaos) ---
        # Random inversions at high intensity
        if mode == 'Glitch Art':
            base_green = (0, 255, 0)
            # If loud, randomize color
            if h_ratio > 0.7:
                if random.random() > 0.5: return (255, 0, 255)  # Glitch magenta
                if random.random() > 0.5: return (255, 255, 255)  # Glitch white
            return self.lerp_color((0, 20, 0), base_green, h_ratio)

        # --- 39. Magma Core (Geology) ---
        # Inverted Fire: Bright core (bottom) cooling to dark crust (top)
        if mode == 'Magma Core':
            # Reverse logic: Hot bottom, cold top
            return self.lerp_color((255, 200, 100), (40, 20, 20), h_ratio)

        # --- 40. Glacial Fracture (Cold) ---
        # White top (Snow), Deep Cyan middle (Ice), Navy Bottom (Water)
        if mode == 'Glacial Fracture':
            if h_ratio < 0.5:
                return self.lerp_color((0, 10, 40), (0, 255, 255), h_ratio * 2)
            else:
                return self.lerp_color((0, 255, 255), (255, 255, 255), (h_ratio - 0.5) * 2)

        # --- 41. Dreamscape (Pastel) ---
        # Soft pink and soft blue gradients
        if mode == 'Dreamscape':
            return self.lerp_color((255, 182, 193), (173, 216, 230), h_ratio)

        # --- 42. Supernova (Intensity) ---
        # Exponential brightness curve
        if mode == 'Supernova':
            # Uses power function to stay dark until the very end
            brightness = h_ratio ** 3
            return (int(255 * brightness), int(100 * brightness), int(255 * brightness))

        # --- 43. Sin City (Selective Color) ---
        # Pure Greyscale until 85% volume, then Pure Red
        if mode == 'Sin City':
            if h_ratio > 0.85: return (255, 0, 0)
            grey = int(h_ratio * 200)
            return (grey, grey, grey)

        # --- 44. The Grid (Tron) ---
        # Dark bars with bright cyan outline (Requires simple trick: Top is bright, bottom is black)
        if mode == 'The Grid':
            # Since we draw a bar, making the 'color' mostly black works if we rely on the peak line
            # But to make the bar look cool:
            if h_ratio > 0.95: return (0, 255, 255)  # Rim light
            return (0, 55, 55)  # Dark body

        # --- 45. Lollipop (Swirls) ---
        # Diagonal bands of color moving upward with volume
        if mode == 'Lollipop':
            # Create diagonal stripes based on Index + Volume
            stripe_idx = int(calc_i + (val / 5)) % 3
            if stripe_idx == 0: return (255, 0, 100)  # Pink
            if stripe_idx == 1: return (255, 255, 0)  # Yellow
            return (0, 200, 255)  # Blue

        # --- 46. Chakra Alignment (Spiritual) ---
        # Maps height to the 7 chakra colors strictly
        if mode == 'Chakra Alignment':
            if h_ratio < 0.14:
                return (255, 0, 0)  # Root
            elif h_ratio < 0.28:
                return (255, 127, 0)  # Sacral
            elif h_ratio < 0.42:
                return (255, 255, 0)  # Solar
            elif h_ratio < 0.57:
                return (0, 255, 0)  # Heart
            elif h_ratio < 0.71:
                return (0, 0, 255)  # Throat
            elif h_ratio < 0.85:
                return (75, 0, 130)  # Third Eye
            else:
                return (148, 0, 211)  # Crown

        # --- 47. Blood Moon (Atmospheric) ---
        # Black to Dark Red gradient, but tips turn bright Orange/White
        if mode == 'Blood Moon':
            base = self.lerp_color((0, 0, 0), (139, 0, 0), h_ratio)
            if h_ratio > 0.9: return (255, 69, 0)
            return base

        # --- 48. Golden Hour (Photography) ---
        # Purple shadows -> Orange midtones -> Yellow highlights
        if mode == 'Golden Hour':
            if h_ratio < 0.5:
                return self.lerp_color((40, 20, 60), (255, 140, 0), h_ratio * 2)
            else:
                return self.lerp_color((255, 140, 0), (255, 255, 200), (h_ratio - 0.5) * 2)

        # --- 49. Acid Rain (Chemical) ---
        # Toxic Green with Yellow bubbling texture
        if mode == 'Acid Rain':
            # Use Sine wave to simulate bubbles moving up
            bubble = math.sin(h_ratio * 10 + t * 5)
            base_green = (50, 205, 50)
            if bubble > 0.8: return (255, 255, 0)  # Yellow Bubble
            return self.lerp_color((0, 50, 0), base_green, h_ratio)

        # --- 50. Sumi-e (Ink Wash) ---
        # White background (handled by drawing) implies we need black bars.
        # But since visualizer bg is dark, we invert: Black BG -> White Ink
        # Variance in greyscale to simulate brush pressure
        if mode == 'Sumi-e':
            pressure = (math.sin(calc_i * 0.5) + 1) / 2  # Brush texture
            ink_val = int(255 * h_ratio * pressure)
            return (ink_val, ink_val, ink_val)

        # --- 51. Midas Touch (Metallic Gold) ---
        if mode == 'Midas Touch':
            # Dark bronze base -> Bright Gold -> White Sparkle
            if h_ratio < 0.6:
                return self.lerp_color((50, 30, 10), (218, 165, 32), h_ratio * 1.66)
            return self.lerp_color((218, 165, 32), (255, 255, 220), (h_ratio - 0.6) * 2.5)

        # --- 52. Quantum Field (Fluctuating Physics) ---
        if mode == 'Quantum Field':
            # Violet/Blue base that shifts based on index (interference pattern)
            interference = (math.sin(calc_i * 0.8) + 1) / 2
            base = self.lerp_color((0, 0, 50), (50, 0, 100), interference)
            # Energy spikes are bright cyan
            return self.lerp_color(base, (0, 255, 255), h_ratio)

        # --- 53. Ethereal Plane (Ghostly) ---
        if mode == 'Ethereal Plane':
            # Teal/White mist, low saturation
            return self.lerp_color((0, 40, 40), (200, 255, 255), h_ratio)

        # --- 54. Vantablack & Neon (High Contrast) ---
        if mode == 'Vantablack & Neon':
            # Pure black body, only the top 10% has color
            if h_ratio < 0.90: return (5, 5, 5)
            return (57, 255, 20) # Neon Green tips

        # --- 55. Gossamer (Delicate) ---
        if mode == 'Gossamer':
            # Very faint pink/white transparency effect simulated by grey mix
            return self.lerp_color((30, 20, 30), (255, 240, 245), h_ratio)

        # --- 56. Molten Steel (Industrial) ---
        if mode == 'Molten Steel':
            # Grey metal -> Red Heat -> Orange Glow
            if h_ratio < 0.5:
                return self.lerp_color((40, 40, 50), (100, 0, 0), h_ratio * 2)
            return self.lerp_color((100, 0, 0), (255, 140, 0), (h_ratio - 0.5) * 2)

        # --- 57. Holo-Foil (Iridescent) ---
        if mode == 'Holo-Foil':
            # shifts color based on viewing angle (simulated by index + time)
            angle = (calc_i * 0.1) + (t * 2)
            r = int(math.sin(angle) * 127 + 128)
            g = int(math.sin(angle + 2) * 127 + 128)
            b = int(math.sin(angle + 4) * 127 + 128)
            return self.lerp_color((r, g, b), (255, 255, 255), h_ratio * 0.5)

        # --- 58. Art Deco (Luxury Pattern) ---
        if mode == 'Art Deco':
            # Gold and Black banding
            segment = int(val / 10) % 2
            if segment == 0: return (10, 10, 10) # Black
            return (191, 148, 62) # Gold

        # --- 59. Sakura Bloom (Nature) ---
        if mode == 'Sakura Bloom':
            # Brown branch -> Pink flowers
            if h_ratio < 0.3: return (60, 40, 20)
            return self.lerp_color((255, 183, 197), (255, 240, 245), h_ratio)

        # --- 60. Toxic Waste (Hazard) ---
        if mode == 'Toxic Waste':
            # Chartreuse and Brown
            return self.lerp_color((40, 30, 0), (127, 255, 0), h_ratio)

        # --- 61. Infrared Hunter (Thermal Vision) ---
        if mode == 'Infrared Hunter':
            # White/Yellow (Hot) -> Purple/Black (Cold) - REVERSED logic for effect
            return self.lerp_color((20, 0, 40), (255, 255, 255), h_ratio)

        # --- 62. Velvet Rope (Club) ---
        if mode == 'Velvet Rope':
            # Deep Royal Purple -> Ruby Red
            return self.lerp_color((40, 0, 60), (220, 20, 60), h_ratio)

        # --- 63. Deep Sea Vent (Abyss) ---
        if mode == 'Deep Sea Vent':
            # Navy Blue -> Bioluminescent Aqua
            if h_ratio < 0.7: return self.lerp_color((0, 0, 10), (0, 0, 80), h_ratio/0.7)
            return (0, 255, 200)

        # --- 64. Urban Concrete (Street) ---
        if mode == 'Urban Concrete':
            # Grey scale with graffiti splashes
            if random.random() > 0.98 and h_ratio > 0.5: return (255, 0, 255) # Spray paint
            grey = 40 + int(h_ratio * 100)
            return (grey, grey, grey)

        # --- 65. Retro-Future (Synth) ---
        if mode == 'Retro-Future':
            # Chrome -> Laser Grid
            if h_ratio < 0.5: return self.lerp_color((10, 10, 30), (100, 100, 150), h_ratio * 2)
            return (255, 0, 100)

        # --- 66. Spirit World (Animism) ---
        if mode == 'Spirit World':
            # Deep Forest Green -> Spirit Blue
            return self.lerp_color((10, 30, 10), (100, 240, 255), h_ratio)

        # --- 67. Candy Apple (Gloss) ---
        if mode == 'Candy Apple':
            # Deep Red -> Bright Red -> White highlight
            if h_ratio < 0.8: return self.lerp_color((50, 0, 0), (255, 0, 0), h_ratio * 1.25)
            return (255, 255, 255)

        # --- 68. Storm Cell (Weather) ---
        if mode == 'Storm Cell':
            # Dark Cloud Grey -> Lightning Yellow
            base = (40, 45, 50)
            if h_ratio > 0.8 + (math.sin(t*10)*0.1): return (255, 255, 200) # Lightning flash
            return self.lerp_color((10, 10, 15), base, h_ratio)

        # --- 69. Kaleidoscope (Geometric) ---
        if mode == 'Kaleidoscope':
            # 3-way color split based on index modulo
            mod = i % 3
            if mod == 0: return self.lerp_color((255, 0, 0), (255, 200, 0), h_ratio)
            if mod == 1: return self.lerp_color((0, 255, 0), (0, 255, 255), h_ratio)
            return self.lerp_color((0, 0, 255), (255, 0, 255), h_ratio)

        # --- 70. Mosaic (Tile) ---
        if mode == 'Mosaic':
            # Random solid colors that stay consistent per bar
            random.seed(i) # Consistent color per index
            r_base = random.randint(50, 255)
            g_base = random.randint(50, 255)
            b_base = random.randint(50, 255)
            random.seed(None)
            return self.lerp_color((r_base//4, g_base//4, b_base//4), (r_base, g_base, b_base), h_ratio)

        # --- 71. Tarragon Void (Sci-Fi Interference) ---
        # Dark Green/Black interference pattern with bright mint peaks
        if mode == 'Tarragon Void':
            # Create a moving "interference" pattern
            interf = (math.sin(calc_i * 0.2 + t * 2) + 1) / 2
            base = self.lerp_color((0, 20, 10), (0, 60, 30), interf)
            if h_ratio > 0.8: return (180, 255, 200)  # Mint tip
            return self.lerp_color(base, (50, 120, 70), h_ratio)

        # --- 72. Paladin Aura (Fantasy) ---
        # Gold base transitioning to Holy White light
        if mode == 'Paladin Aura':
            # Metallic Gold to Pure White
            if h_ratio < 0.6:
                return self.lerp_color((184, 134, 11), (255, 215, 0), h_ratio * 1.66)
            return self.lerp_color((255, 215, 0), (255, 255, 240), (h_ratio - 0.6) * 2.5)

        # --- 73. Necromancer (Fantasy) ---
        # Toxic Green ground, rising into Purple/Black mist
        if mode == 'Necromancer':
            # Reverse logic: Bright green bottom (magic circle), dark purple top (smoke)
            if h_ratio < 0.3: return self.lerp_color((50, 255, 50), (20, 0, 40), h_ratio * 3.3)
            return self.lerp_color((20, 0, 40), (0, 0, 0), (h_ratio - 0.3) * 1.4)

        # --- 74. Synth Sunset (Retrowave Directional) ---
        # A 4-stage horizontal banding representing a horizon
        if mode == 'Synth Sunset':
            # Deep Purple -> Red -> Orange -> Yellow (Vertical)
            if h_ratio < 0.25: return (45, 0, 75)
            if h_ratio < 0.50: return (200, 0, 50)
            if h_ratio < 0.75: return (255, 100, 0)
            return (255, 220, 0)

        # --- 75. Copper Oxide (Material) ---
        # Raw Copper bottom oxidizing into Teal Patina at the top
        if mode == 'Copper Oxide':
            copper = (184, 115, 51)
            patina = (64, 224, 208)
            # Noise factor for irregular oxidation
            noise = (math.sin(calc_i * 80) + 1) / 2
            limit = 0.5 + (noise * 0.2)
            if h_ratio < limit: return copper
            return self.lerp_color(copper, patina, (h_ratio - limit) * 2)

        # --- 76. Dragon Scale (Iridescent) ---
        # Shifting Green/Gold/Red based on angle (simulated by index)
        if mode == 'Dragon Scale':
            angle = (calc_i * 0.15) + t
            r = int(math.sin(angle) * 100 + 155)
            g = int(math.sin(angle + 2) * 100 + 155)
            b = 0  # Low blue for gold/red/green spectrum
            scale_col = (r, g, b)
            # Darken at bottom, brighten at top
            return self.lerp_color((20, 20, 0), scale_col, h_ratio)

        # --- 77. Marble Statue (Classical) ---
        # Cool White base with veins of Grey and Gold
        if mode == 'Marble Statue':
            # Procedural marble veins
            vein = (math.sin(calc_i * 0.4) + math.cos(h_ratio * 10))
            if vein > 1.5: return (218, 165, 32)  # Gold inlay
            if vein < -0.5: return (100, 100, 110)  # Grey vein
            return (240, 240, 245)  # White marble

        # --- 78. Laser Tag (Arcade) ---
        # Pitch black room with sharp, high-contrast Red/Blue/Green beams
        if mode == 'Laser Tag':
            if h_ratio < 0.1: return (10, 10, 10)  # Floor
            # Split into teams based on index
            team = calc_i % 3
            if team == 0: return (255, 0, 0)
            if team == 1: return (0, 255, 0)
            return (0, 0, 255)

        # --- 79. Coffee Shop (Cozy) ---
        # Deep Espresso -> Mocha -> Cream Foam
        if mode == 'Coffee Shop':
            espresso = (40, 20, 10)
            latte = (150, 100, 70)
            foam = (255, 240, 220)
            if h_ratio < 0.5:
                return self.lerp_color(espresso, latte, h_ratio * 2)
            return self.lerp_color(latte, foam, (h_ratio - 0.5) * 2)

        # --- 80. Tiffany Glass (Art Nouveau) ---
        # Stained glass effect: Random colored shards with black borders
        if mode == 'Tiffany Glass':
            # Use large sections for "glass pieces"
            shard_id = int((calc_i / total) * 12) + int(h_ratio * 4)
            random.seed(shard_id)
            # Pastels
            r_c = random.choice([(100, 200, 255), (255, 100, 200), (255, 255, 100), (100, 255, 150)])
            random.seed(None)
            return self.lerp_color((10, 10, 10), r_c, h_ratio)

        # --- 81. Circuit Breaker (Tech) ---
        # Dark Blue PCB Board with bright Orange sparks at high energy
        if mode == 'Circuit Breaker':
            pcb_blue = (0, 20, 60)
            trace_cyan = (0, 100, 100)
            spark_orange = (255, 165, 0)

            # Circuit traces pattern
            if (calc_i % 4) == 0:
                base = trace_cyan
            else:
                base = pcb_blue

            if h_ratio > 0.85: return spark_orange  # Overload
            return base

        # --- 82. Polychrome Glitch (Digital Art) ---
        # Separation of RGB channels based on height
        if mode == 'Polychrome Glitch':
            # Red base, Green mid, Blue top (unnatural separation)
            if h_ratio < 0.33: return (255, 0, 0)
            if h_ratio < 0.66: return (0, 255, 0)
            return (0, 0, 255)

        # --- 83. Amber Fossil (Organic) ---
        # Translucent Orange/Yellow with dark "inclusions"
        if mode == 'Amber Fossil':
            # Bubbles/Inclusions
            inclusion = math.sin(calc_i * 50 + h_ratio * 20)
            if inclusion > 0.9: return (30, 10, 0)  # Insect/Dirt
            return self.lerp_color((180, 100, 0), (255, 200, 50), h_ratio)

        # --- 84. Moon Crystal (Sailor Style) ---
        # Silver -> Lavender -> Translucent Blue
        if mode == 'Moon Crystal':
            return self.lerp_color((192, 192, 220), (230, 230, 250), h_ratio)

        # --- 85. Rust Bucket (Decay) ---
        # Iron Grey -> Orange Rust -> Brown Corrosion
        if mode == 'Rust Bucket':
            # Patchy rust based on index
            is_rusty = (calc_i % 7) > 2
            if not is_rusty: return (80, 80, 90)  # Clean Iron
            return self.lerp_color((160, 80, 40), (100, 40, 20), h_ratio)

        # --- 86. Berry Smoothie (Food) ---
        # Swirls of Purple, Pink, and Red
        if mode == 'Berry Smoothie':
            # Sine wave swirl
            swirl = (math.sin(t * 2 + calc_i * 0.1) + 1) / 2
            col1 = (100, 0, 100)  # Purple
            col2 = (255, 0, 100)  # Pink
            base = self.lerp_color(col1, col2, swirl)
            return self.lerp_color(base, (255, 200, 200), h_ratio)

        # --- 87. Oil Slick (Pollution) ---
        # Rainbow interference pattern on black liquid
        if mode == 'Oil Slick':
            if h_ratio < 0.2: return (10, 10, 10)  # Black Oil
            # High frequency rainbow cycling
            hue = (calc_i * 10 + (h_ratio * 100)) % 360
            c = pygame.Color(0)
            c.hsla = (hue, 100, 50, 100)
            return (c.r, c.g, c.b)

        # --- 88. Blueprint Inverted (Architect) ---
        # White Paper background (implied) -> Blue Lines
        # Since background is dark, we make the bars White paper color, with blue ink at edges
        if mode == 'Blueprint Inverted':
            # White body, Blue outline (simulated by peak)
            if h_ratio > 0.95: return (0, 0, 200)  # Ink
            return (240, 240, 255)  # Paper

        # --- 89. Thermal Camo (Military) ---
        # Pixelated blocks of Thermal colors
        if mode == 'Thermal Camo':
            # Quantize height to blocks
            block_h = int(h_ratio * 5)
            if block_h == 0: return (0, 0, 128)  # Cold Blue
            if block_h == 1: return (128, 0, 128)  # Purple
            if block_h == 2: return (200, 0, 0)  # Red
            if block_h == 3: return (255, 165, 0)  # Orange
            return (255, 255, 200)  # Hot White

        # --- 90. Ultraviolet (Club) ---
        # Deep Purple base with Fluorescent Blue/White highlights
        if mode == 'Ultraviolet':
            if h_ratio < 0.7:
                return self.lerp_color((20, 0, 40), (80, 0, 255), h_ratio / 0.7)
            else:
                return self.lerp_color((80, 0, 255), (200, 255, 255), (h_ratio - 0.7) * 3.3)

        # --- 91. Crimson Lotus (Nature/Dark) ---
        # Dark Red base fading into white tips with a black "outline" effect
        if mode == 'Crimson Lotus':
            # Petal texture
            if h_ratio < 0.1: return (10, 20, 10) # Stem
            if h_ratio < 0.8: return self.lerp_color((100, 0, 0), (220, 20, 60), (h_ratio - 0.1) * 1.4)
            return self.lerp_color((220, 20, 60), (255, 255, 255), (h_ratio - 0.8) * 5)

        # --- 92. Vice City (Vaporwave Variant) ---
        # Teal Bottom, Sharp Pink Top
        if mode == 'Vice City':
            if h_ratio < 0.5:
                return self.lerp_color((0, 50, 50), (0, 255, 255), h_ratio * 2)
            else:
                return self.lerp_color((255, 0, 255), (255, 150, 255), (h_ratio - 0.5) * 2)

        # --- 93. Clockwork Gear (Steampunk) ---
        # Bronze/Brass with a "toothed" texture using modulo
        if mode == 'Clockwork Gear':
            is_tooth = (calc_i % 2) == 0
            bronze = (205, 127, 50)
            brass = (181, 166, 66)
            base = bronze if is_tooth else brass
            # Darken based on height to look like metal shading
            shade = 0.5 + (h_ratio * 0.5)
            return (int(base[0]*shade), int(base[1]*shade), int(base[2]*shade))

        # --- 94. Digital Rain (Matrix Style) ---
        # Black background, falling green characters effect
        if mode == 'Digital Rain':
            # Create "falling" trail effect using time and height
            trail = (h_ratio * 10 - t * 2) % 1.0
            if trail > 0.8: return (200, 255, 200) # Bright Leader
            if trail > 0.3: return (0, 255, 0) # Body
            return (0, 50, 0) # Trail

        # --- 95. Pompeii (Disaster) ---
        # Grey Ash bottom -> Magma Red Top -> Black Smoke tips
        if mode == 'Pompeii':
            if h_ratio < 0.4: return (80, 80, 80) # Ash
            if h_ratio < 0.85: return self.lerp_color((255, 50, 0), (255, 200, 0), (h_ratio - 0.4) * 2.2)
            return (20, 20, 20) # Smoke

        # --- 96. Polaris (Aurora) ---
        # Green to Purple shifting gradient
        if mode == 'Polaris':
            return self.lerp_color((0, 255, 128), (128, 0, 255), h_ratio)

        # --- 97. Bumblebee (High Contrast) ---
        # Black and Yellow stripes
        if mode == 'Bumblebee':
            stripe = int(h_ratio * 10) % 2
            return (255, 225, 0) if stripe == 0 else (10, 10, 10)

        # --- 98. Koi Pond (Artistic) ---
        # Blue water with random Orange/White spots
        if mode == 'Koi Pond':
            random.seed(calc_i + int(t)) # Moving fish
            is_fish = random.random() > 0.85
            random.seed(None)
            water = self.lerp_color((0, 10, 40), (0, 100, 200), h_ratio)
            if is_fish and h_ratio < 0.8:
                return (255, 100, 0) # Orange Fish
            return water

        # --- 99. Candy Corn (Seasonal) ---
        # Yellow Bottom -> Orange Mid -> White Top
        if mode == 'Candy Corn':
            if h_ratio < 0.33: return (255, 255, 0)
            if h_ratio < 0.66: return (255, 165, 0)
            return (255, 255, 255)

        # --- 100. Noir Detective (Cinema) ---
        # Black & White, but sudden Red if volume spikes high (Gunshot/Drama)
        if mode == 'Noir Detective':
            if h_ratio > 0.95: return (200, 0, 0) # Blood
            grey = int(h_ratio * 200) + 20
            return (grey, grey, grey)

        # --- 101. Sunken Ship (Atmospheric) ---
        # Rust Orange bottom, Murky Teal top
        if mode == 'Sunken Ship':
            return self.lerp_color((139, 69, 19), (0, 128, 128), h_ratio)

        # --- 102. Unicorn Frappe (Pastel) ---
        # Pastel Blue and Pink swirl
        if mode == 'Unicorn Frappe':
            # Horizontal swirl
            swirl = (math.sin(calc_i * 0.2 + t) + 1) / 2
            base = self.lerp_color((173, 216, 230), (255, 182, 193), swirl)
            return self.lerp_color(base, (255, 255, 255), h_ratio * 0.5)

        # --- 103. High Voltage (Energy) ---
        # Dark Blue core, jagged Electric Blue/White outer
        if mode == 'High Voltage':
            # Jagged electricity
            bolt = math.sin(h_ratio * 20 + t * 10)
            if bolt > 0.8: return (255, 255, 255)
            return self.lerp_color((0, 0, 50), (0, 100, 255), h_ratio)

        # --- 104. Zen Garden (Minimalist) ---
        # Stone Grey body, Moss Green tips
        if mode == 'Zen Garden':
            if h_ratio < 0.9: return (100, 100, 100)
            return (85, 107, 47)

        # --- 105. Sahara Night (Landscape) ---
        # Golden Sand bottom, Dark Blue Night Sky top
        if mode == 'Sahara Night':
            if h_ratio < 0.4: return (237, 201, 175) # Sand
            return self.lerp_color((25, 25, 112), (0, 0, 0), (h_ratio - 0.4) * 1.6)

        # --- 106. 90s Jazz Cup (Retro Design) ---
        # Teal and Purple scribble pattern
        if mode == '90s Jazz Cup':
            # "Scribble" math
            scribble = math.sin(calc_i * 0.5) + math.cos(h_ratio * 10)
            if scribble > 0.5: return (0, 200, 200) # Teal
            return (150, 0, 150) # Purple

        # --- 107. Vampire Hunter (Fantasy) ---
        # Silver Metal base, Deep Red Blood top
        if mode == 'Vampire Hunter':
            if h_ratio < 0.7:
                # Silver
                v = int(100 + h_ratio * 100)
                return (v, v, v + 20)
            else:
                return (180, 0, 0)

        # --- 108. Molten Glass (Material) ---
        # Translucent Orange/Yellow glow
        if mode == 'Molten Glass':
            return self.lerp_color((255, 140, 0), (255, 255, 200), h_ratio)

        # --- 109. Void Purple (Cosmic) ---
        # Pitch Black bottom, Purple Mid, White Top
        if mode == 'Void Purple':
            if h_ratio < 0.3: return (0, 0, 0)
            if h_ratio < 0.8: return self.lerp_color((50, 0, 100), (150, 50, 255), (h_ratio - 0.3) * 2)
            return (255, 255, 255)

        # --- 110. Golden Fleece (Mythology) ---
        # All Gold, but shimmering
        if mode == 'Golden Fleece':
            shimmer = (math.sin(calc_i + t * 5) + 1) / 2
            base = (218, 165, 32)
            highlight = (255, 255, 224)
            return self.lerp_color(base, highlight, shimmer * h_ratio)

        # --- 111. Toxic Jungle (Fantasy Env) ---
        # Dark Purple vegetation with Neon Green smog
        if mode == 'Toxic Jungle':
            if h_ratio < 0.6: return self.lerp_color((20, 0, 40), (80, 0, 120), h_ratio * 1.6)
            return (57, 255, 20)

        # --- 112. Cyber Samurai (Sci-Fi) ---
        # Red, Black, and Gold accents
        if mode == 'Cyber Samurai':
            if h_ratio < 0.8: return (200, 0, 0) # Red Armor
            if h_ratio < 0.9: return (10, 10, 10) # Black Trim
            return (255, 215, 0) # Gold Crest

        # --- 113. Frozen Wasteland (Environment) ---
        # White Snow, Pale Blue Ice, Deep Blue Water
        if mode == 'Frozen Wasteland':
            if h_ratio < 0.3: return (0, 0, 139) # Deep Water
            if h_ratio < 0.7: return (173, 216, 230) # Ice
            return (255, 250, 250) # Snow

        # --- 114. Blood Orange (Fruit/Gradient) ---
        # Deep Orange -> Red -> Purple Gradient
        if mode == 'Blood Orange':
            if h_ratio < 0.5:
                return self.lerp_color((255, 100, 0), (200, 0, 0), h_ratio * 2)
            else:
                return self.lerp_color((200, 0, 0), (100, 0, 100), (h_ratio - 0.5) * 2)

        # --- 115. Disco Floor (Pattern) ---
        # Random colored checkerboard that changes with height
        if mode == 'Disco Floor':
            check = (calc_i + int(h_ratio * 5)) % 3
            if check == 0: return (0, 255, 255)
            if check == 1: return (255, 0, 255)
            return (255, 255, 0)

        # --- 116. Radioactive Hazard (Warning Sign) ---
        # Yellow and Black Chevrons
        if mode == 'Radioactive Hazard':
            # Chevron pattern using x and y
            chevron = (int(calc_i) + int(h_ratio * 20)) % 4
            if chevron < 2: return (255, 255, 0)
            return (0, 0, 0)

        # --- 117. Emerald Tablet (Mystic) ---
        # Stone Green with glowing bright green runes
        if mode == 'Emerald Tablet':
            base = (40, 80, 60)
            # Simulate "Runes" with high frequency sine
            rune = math.sin(calc_i * 25 + t)
            if rune > 0.9: return (100, 255, 100) # Glowing rune
            return self.lerp_color((20, 40, 30), base, h_ratio)

        # --- 118. Checkmate (Game) ---
        # Black and White Checkerboard
        if mode == 'Checkmate':
            check = (calc_i % 2) + (int(h_ratio * 10) % 2)
            return (255, 255, 255) if check % 2 == 0 else (20, 20, 20)

        # --- 119. Horizon Zero (Tech Landscape) ---
        # Orange/Pink Horizon line in middle of Blue
        if mode == 'Horizon Zero':
            # Create a "Horizon" line at 0.6 height
            dist = abs(h_ratio - 0.6)
            if dist < 0.05: return (255, 100, 100) # Horizon Sun
            if h_ratio < 0.6: return self.lerp_color((0, 0, 20), (0, 50, 100), h_ratio * 1.6) # Ground
            return self.lerp_color((100, 50, 100), (0, 200, 255), (h_ratio - 0.6) * 2.5) # Sky

        # --- 120. Prism Fracture (Optics) ---
        # White light splitting into RGB
        if mode == 'Prism Fracture':
            if h_ratio < 0.5: return (255, 255, 255) # White beam
            # Split
            split = calc_i % 3
            if split == 0: return (255, 0, 0)
            if split == 1: return (0, 255, 0)
            return (0, 0, 255)

        # --- 121. Quantum Superposition (Sci-Fi) ---
        # Flickering duality: Blue state vs Orange state based on probability (noise)
        if mode == 'Quantum Superposition':
            # Use index and time to create a "probability field"
            prob = math.sin(calc_i * 0.9 + t * 5)
            # High energy creates white "observation" spikes
            if h_ratio > 0.9: return (255, 255, 255)
            if prob > 0:
                return self.lerp_color((0, 20, 50), (0, 150, 255), h_ratio)
            else:
                return self.lerp_color((50, 20, 0), (255, 100, 0), h_ratio)

        # --- 122. Rococo Pastel (Art History) ---
        # Ornate Gold trim with soft Powder Blue and Pale Pink body
        if mode == 'Rococo Pastel':
            # Gold filigree pattern at specific intervals
            filigree = (calc_i % 6) == 0 or (calc_i % 6) == 5
            if filigree:
                # Gold gradient
                return self.lerp_color((184, 134, 11), (255, 223, 0), h_ratio)
            # Soft gradient body
            return self.lerp_color((176, 224, 230), (255, 192, 203), h_ratio)

        # --- 123. Cyber-Goth (Subculture) ---
        # Industrial Black/Grey base with Neon Green and Hot Pink highlights
        if mode == 'Cyber-Goth':
            if h_ratio < 0.5:
                # Industrial Grey
                g = int(h_ratio * 100)
                return (g, g, g + 10)
            else:
                # Alternating Neon Hair falls
                if calc_i % 2 == 0:
                    return (57, 255, 20)  # Neon Green
                else:
                    return (255, 0, 255)  # Hot Pink

        # --- 124. Confetti Cannon (Party) ---
        # Random colored speckles that move upwards
        if mode == 'Confetti Cannon':
            # "Random" color based on position in grid (Index + Height)
            seed_val = int(calc_i + (val / 5) + (t * 2))
            random.seed(seed_val)
            r = random.randint(100, 255)
            g = random.randint(100, 255)
            b = random.randint(100, 255)
            random.seed(None)
            # 80% chance of being background color (transparency effect), 20% confetti
            if (seed_val % 5) != 0:
                return self.lerp_color((20, 20, 30), (50, 50, 70), h_ratio)
            return (r, g, b)

        # --- 125. Ancient Hieroglyph (Archeology) ---
        # Sandstone body with Glowing Blue runes (Sine wave patterns)
        if mode == 'Ancient Hieroglyph':
            sandstone = (194, 178, 128)
            glow_blue = (0, 255, 255)
            # Create a "writing" pattern
            writing = math.sin(calc_i * 0.8) + math.cos(h_ratio * 15)
            if writing > 1.2:
                return glow_blue
            return self.lerp_color((60, 50, 30), sandstone, h_ratio)

        # --- 126. Vapor-Grid (Aesthetic) ---
        # Vertical grid lines (Black) over a Sunset Gradient
        if mode == 'Vapor-Grid':
            # Draw black grid lines every 5th bar
            if calc_i % 5 == 0: return (0, 0, 0)
            # Cyan to Pink gradient
            return self.lerp_color((0, 255, 255), (255, 105, 180), h_ratio)

        # --- 127. Nuclear Fallout (Apocalyptic) ---
        # Sickly Green, Ash Grey, and Warning Orange
        if mode == 'Nuclear Fallout':
            if h_ratio < 0.4: return (30, 40, 30)  # Dark Ash
            if h_ratio < 0.8: return (173, 255, 47)  # Radioactive Green
            return (255, 69, 0)  # Meltdown Orange

        # --- 128. Kaleidoscope Fracture (Geometric) ---
        # Complex symmetrical colors based on mirrored indices
        if mode == 'Kaleidoscope Fracture':
            # Mirror logic
            mirror_i = abs((total / 2) - calc_i)
            hue = (mirror_i * 5 + (h_ratio * 100) + (t * 20)) % 360
            c = pygame.Color(0)
            c.hsla = (hue, 80, 50, 100)
            return (c.r, c.g, c.b)

        # --- 129. Dragonfruit (Nature) ---
        # Pink skin, White flesh, Black seeds
        if mode == 'Dragonfruit':
            if h_ratio < 0.15: return (255, 0, 100)  # Pink Skin
            # White flesh with random seeds
            random.seed(calc_i + int(h_ratio * 10))
            is_seed = random.random() > 0.85
            random.seed(None)
            if is_seed: return (10, 10, 10)
            return (240, 240, 240)

        # --- 130. Tuxedo Night (Formal) ---
        # Black Suit, White Shirt, Red Bowtie/Rose
        if mode == 'Tuxedo Night':
            if h_ratio < 0.6: return (15, 15, 20)  # Suit
            if h_ratio < 0.9: return (255, 255, 255)  # Shirt
            return (200, 0, 0)  # Rose/Tie

        # --- 131. Bismuth Geode (Mineral) ---
        # Geometric steps of rainbow oxidation colors
        if mode == 'Bismuth Geode':
            # Quantize height to create "steps"
            step = int(h_ratio * 8)
            # Map steps to specific Bismuth colors
            cols = [
                (192, 192, 192), (255, 255, 0), (0, 255, 0), (0, 0, 255),
                (75, 0, 130), (255, 0, 255), (255, 165, 0), (255, 215, 0)
            ]
            return cols[step % 8]

        # --- 132. Heat Vision (Predator) ---
        # Deep Blue (Cold) -> Green -> Red -> White (Hot)
        if mode == 'Heat Vision':
            if h_ratio < 0.33:
                return self.lerp_color((0, 0, 100), (0, 255, 0), h_ratio * 3)
            elif h_ratio < 0.66:
                return self.lerp_color((0, 255, 0), (255, 0, 0), (h_ratio - 0.33) * 3)
            else:
                return self.lerp_color((255, 0, 0), (255, 255, 255), (h_ratio - 0.66) * 3)

        # --- 133. Miami Hotline (80s Action) ---
        # Horizontal Split: Teal water below, Magenta sky above
        if mode == 'Miami Hotline':
            if h_ratio < 0.5:
                return self.lerp_color((0, 20, 60), (0, 255, 200), h_ratio * 2)
            else:
                return self.lerp_color((200, 0, 100), (255, 100, 200), (h_ratio - 0.5) * 2)

        # --- 134. Singularity Event (Cosmic) ---
        # Black center bar with accretion disk edges
        if mode == 'Singularity Event':
            # Calculate distance from center of visualizer
            center_dist = abs(calc_i - (total / 2)) / (total / 2)
            if center_dist < 0.2: return (0, 0, 0)  # Event Horizon
            # Redshift/Blueshift effect
            if calc_i < total / 2:
                return self.lerp_color((50, 0, 0), (255, 100, 50), h_ratio)  # Redshift
            else:
                return self.lerp_color((0, 0, 50), (100, 200, 255), h_ratio)  # Blueshift

        # --- 135. Fiber Optic (Tech) ---
        # Dark cable with bright white/colored tip
        if mode == 'Fiber Optic':
            if h_ratio > 0.95:
                # Color changes based on index
                hue = (calc_i * 10) % 360
                c = pygame.Color(0);
                c.hsla = (hue, 100, 50, 100)
                return (c.r, c.g, c.b)
            return (20, 20, 25)

        # --- 136. Cathedral Glass (Stained Glass) ---
        # Large blocks of vibrant colors with black leading lines
        if mode == 'Cathedral Glass':
            # Create "Panes" using integer division
            pane_id = int((calc_i / total) * 10) + int(h_ratio * 5)
            # Leading lines (borders of panes)
            if (calc_i % int(total / 10)) == 0: return (10, 10, 10)

            random.seed(pane_id)
            # Deep rich colors
            cols = [(200, 0, 0), (0, 0, 200), (200, 200, 0), (0, 150, 0), (100, 0, 150)]
            c = random.choice(cols)
            random.seed(None)
            # Add light gradient
            return self.lerp_color((c[0] // 2, c[1] // 2, c[2] // 2), c, (h_ratio % 0.2) * 5)

        # --- 137. Peppermint Swirl (Candy) ---
        # Diagonal Red and White stripes
        if mode == 'Peppermint Swirl':
            # Diagonal math: index + scaled height
            stripe = (calc_i + int(h_ratio * 20)) % 4
            if stripe < 2: return (255, 255, 255)
            return (220, 20, 60)

        # --- 138. Digital Distortion (Glitch) ---
        # Greyscale with random colored "bad blocks"
        if mode == 'Digital Distortion':
            # Chance to glitch based on volume
            random.seed(calc_i + t)
            is_glitch = random.random() > (0.95 - (val / 500))
            random.seed(None)

            if is_glitch:
                return random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])

            g = int(h_ratio * 200)
            return (g, g, g)

        # --- 139. Forest Fire (Nature/Disaster) ---
        # Green trees at bottom, turning into raging Fire at top
        if mode == 'Forest Fire':
            if h_ratio < 0.4:
                return self.lerp_color((10, 30, 10), (34, 139, 34), h_ratio * 2.5)
            else:
                return self.lerp_color((34, 139, 34), (255, 69, 0), (h_ratio - 0.4) * 1.6)

        # --- 140. Arctic Aurora (Atmosphere) ---
        # Black sky with waves of Green and Purple
        if mode == 'Arctic Aurora':
            # Wave interference
            wave = math.sin(calc_i * 0.2 + t) + math.sin(h_ratio * 5)
            if wave > 0:
                return self.lerp_color((0, 20, 40), (0, 255, 150), abs(wave))
            else:
                return self.lerp_color((0, 20, 40), (150, 0, 255), abs(wave))

        # --- 141. Stealth Mode (Military) ---
        # Matte Black with faint Green Radar Sweep
        if mode == 'Stealth Mode':
            # Radar Sweep logic
            sweep_pos = (t * 2) % total
            dist = abs(calc_i - sweep_pos)
            if dist > total / 2: dist = total - dist  # Wrap around

            # Base matte black
            col = (20, 20, 20)

            # Radar line
            if dist < 5:
                intensity = (5 - dist) / 5
                col = self.lerp_color(col, (0, 255, 0), intensity)

            # Grid lines
            if h_ratio > 0.2 and h_ratio < 0.22: return (0, 100, 0)
            if h_ratio > 0.5 and h_ratio < 0.52: return (0, 100, 0)

            return col

        # --- 142. Velvet Lounge (Luxury) ---
        # Deep Red curtain texture with Gold dust
        if mode == 'Velvet Lounge':
            # Cloth fold texture using sine
            fold = (math.sin(calc_i * 0.3) + 1) / 2
            base_red = self.lerp_color((60, 0, 10), (140, 0, 20), fold)

            # Gold dust at top
            if h_ratio > 0.8:
                random.seed(calc_i + int(t))
                if random.random() > 0.7: return (255, 215, 0)
                random.seed(None)

            return base_red

        # --- 143. X-Ray Vision (Medical) ---
        # Negative Space: Black Background, Bone White Skeleton, Dark Blue internal
        if mode == 'X-Ray Vision':
            # Inverted feel: Bright in middle, dark edges
            if h_ratio < 0.2: return (0, 0, 0)
            if h_ratio < 0.8: return self.lerp_color((0, 0, 50), (100, 100, 120), (h_ratio - 0.2) * 1.6)
            return (240, 240, 255)  # Bone

        # --- 144. Koi Stream (Japanese Art) ---
        # Flowing Blue water with Orange/White Koi patterns moving
        if mode == 'Koi Stream':
            # Water background
            water = self.lerp_color((0, 10, 30), (0, 100, 180), h_ratio)
            # Fish pattern moving
            fish_pat = math.sin((calc_i * 0.5) - (t * 2)) + math.cos(h_ratio * 5)
            if fish_pat > 1.5: return (255, 140, 0)  # Orange
            if fish_pat > 1.0: return (255, 255, 255)  # White
            return water

        # --- 145. Emerald Cavern (Fantasy) ---
        # Dark Grey Stone with Glowing Green Crystal Clusters
        if mode == 'Emerald Cavern':
            # Stone
            base = (40, 40, 45)
            # Crystal clusters based on noise
            cluster = math.sin(calc_i * 1.5) * math.sin(h_ratio * 10)
            if cluster > 0.8:
                return self.lerp_color((0, 100, 50), (100, 255, 150), h_ratio)
            return base

        # --- 146. Caution Tape (Industrial) ---
        # Diagonal Yellow and Black stripes
        if mode == 'Caution Tape':
            # Sharper angle than peppermint
            stripe = (calc_i + int(h_ratio * 10)) % 6
            if stripe < 3: return (255, 215, 0)  # Safety Yellow
            return (10, 10, 10)  # Black

        # --- 147. Starry Night (Impressionism) ---
        # Swirling Blues and Yellows (Van Gogh style)
        if mode == 'Starry Night':
            # Turbulence
            flow = math.sin(calc_i * 0.1 + t) + math.cos(h_ratio * 0.1 + calc_i * 0.1)
            base_blue = self.lerp_color((0, 0, 100), (100, 150, 255), h_ratio)

            if flow > 1.5: return (255, 255, 0)  # Star/Moon
            if flow < -1.0: return (0, 0, 50)  # Dark swirl
            return base_blue

        # --- 148. 8-Bit Hero (Retro Game) ---
        # Limited color palette, blocky steps
        if mode == '8-Bit Hero':
            # Quantize height into 4 distinct colors
            level = int(h_ratio * 4)
            if level == 0: return (0, 0, 150)  # Blue Pants
            if level == 1: return (255, 0, 0)  # Red Shirt
            if level == 2: return (255, 200, 150)  # Skin tone
            return (100, 50, 0)  # Hair

        # --- 149. Blood Diamond (Gemstone) ---
        # Deep Red with refractive rainbows
        if mode == 'Blood Diamond':
            base_red = self.lerp_color((50, 0, 0), (200, 0, 0), h_ratio)
            # Refraction sparkle
            sparkle = math.sin(calc_i * 50 + t * 5)
            if sparkle > 0.95:
                # Rainbow tint
                hue = (calc_i * 20) % 360
                c = pygame.Color(0);
                c.hsla = (hue, 50, 80, 100)
                return (c.r, c.g, c.b)
            return base_red

        # --- 150. Rainbow Road (Kart) ---
        # Moving rainbow tiles
        if mode == 'Rainbow Road':
            # Checkerboard pattern moving downwards
            check_x = calc_i // 4
            check_y = int(h_ratio * 10 - t * 5)

            hue = ((check_x + check_y) * 30) % 360
            c = pygame.Color(0)
            c.hsla = (hue, 100, 50, 100)
            return (c.r, c.g, c.b)

        # --- 151. Neural Network (Sci-Fi) ---
        # Blue synaptic connections that flash white/cyan on spikes
        if mode == 'Neural Network':
            # Simulate synapse firing
            fire = math.sin(calc_i * 0.8 + t * 4)
            if h_ratio > 0.8 and fire > 0.5: return (255, 255, 255) # Firing
            base_blue = (0, 20, 80)
            return self.lerp_color(base_blue, (0, 150, 255), h_ratio * 1.5)

        # --- 152. Holographic Data (Tech) ---
        # Translucent Cyan with flickering "data lines"
        if mode == 'Holographic Data':
            # Scanline effect
            scan = (int(h_ratio * 50) + int(t * 10)) % 4
            if scan == 0: return (100, 255, 255) # Bright line
            return self.lerp_color((0, 20, 40), (0, 100, 100), h_ratio)

        # --- 153. Cryo-Chamber (Atmosphere) ---
        # Deep Freeze Blue, White Mist, Glass Green edges
        if mode == 'Cryo-Chamber':
            if h_ratio < 0.2: return (0, 50, 50) # Liquid Nitrogen
            if h_ratio < 0.8: return self.lerp_color((0, 50, 50), (100, 200, 255), (h_ratio - 0.2) * 1.6)
            return (200, 240, 255) # Mist

        # --- 154. Dyson Sphere (Space) ---
        # Solar surface (Yellow/Orange) contained by Hexagon Grid (Black/Grey)
        if mode == 'Dyson Sphere':
            # Grid pattern
            grid = (calc_i % 3 == 0) or (int(h_ratio * 10) % 3 == 0)
            if grid: return (30, 30, 30) # Structure
            return self.lerp_color((255, 69, 0), (255, 255, 0), h_ratio) # Star

        # --- 155. Warp Drive (Motion) ---
        # Streaks of Star White on Deep Blue, curving outward
        if mode == 'Warp Drive':
            # Curvature
            curve = math.sin(calc_i * 0.1 + t * 5)
            if curve > 0.9: return (255, 255, 255) # Star Streak
            return self.lerp_color((0, 0, 20), (0, 0, 100), h_ratio)

        # --- 156. Nanobot Swarm (Grey Goo) ---
        # Silver/Grey metallic clouds with Red collective intelligence
        if mode == 'Nanobot Swarm':
            noise = math.sin(calc_i * 45 + t)
            grey = int(50 + h_ratio * 150)
            base = (grey, grey, grey)
            if noise > 0.95 and h_ratio > 0.5: return (255, 0, 0) # Eye
            return base

        # --- 157. Cybernetic Implant (Body Horror) ---
        # Flesh tones merging into Chrome and Neon
        if mode == 'Cybernetic Implant':
            if h_ratio < 0.4: return (150, 100, 80) # Skin
            if h_ratio < 0.5: return (50, 0, 0) # Scar
            if h_ratio < 0.9: return (192, 192, 192) # Chrome
            return (0, 255, 0) # LED

        # --- 158. Hard Light Bridge (Portal) ---
        # Semi-transparent Blue/White forcefield
        if mode == 'Hard Light Bridge':
            if h_ratio > 0.9: return (200, 200, 255) # Surface
            # Interference pattern
            inter = math.sin(h_ratio * 50 - t * 5)
            if inter > 0.5: return (100, 150, 255)
            return (50, 100, 200)

        # --- 159. Plasma Cannon (Weapon) ---
        # Purple Core -> Pink -> White Energy
        if mode == 'Plasma Cannon':
            return self.lerp_color((50, 0, 100), (255, 255, 255), h_ratio ** 0.5)

        # --- 160. Force Field (Defense) ---
        # Hexagonal Orange shielding
        if mode == 'Force Field':
            # Hex logic approximated
            hex_pat = (math.sin(calc_i) + math.cos(h_ratio * 10))
            if hex_pat > 1.2: return (255, 200, 0) # Edge
            return self.lerp_color((50, 20, 0), (200, 100, 0), h_ratio)

        # --- 161. Bioluminescent Algae (Nature) ---
        # Dark Water -> Glowing Blue dots on agitation (volume)
        if mode == 'Bioluminescent Algae':
            base_water = (0, 10, 20)
            # Agitation based on height
            if random.random() > (1.0 - h_ratio):
                return (0, 255, 255) # Glow
            return base_water

        # --- 162. Volcanic Lightning (Disaster) ---
        # Ash Cloud (Dark Grey) with bursts of Purple Lightning and Red Magma
        if mode == 'Volcanic Lightning':
            if h_ratio < 0.2: return (255, 50, 0) # Lava
            # Random Lightning
            random.seed(int(t*10) + calc_i)
            is_bolt = random.random() > 0.97
            random.seed(None)
            if is_bolt: return (180, 100, 255)
            return (40, 40, 45) # Ash

        # --- 163. Monsoon Season (Weather) ---
        # Heavy Grey Rain -> Green lush vegetation
        if mode == 'Monsoon Season':
            # Rain texture
            is_rain = (int(calc_i * 3 + t * 20) % 5) == 0
            if is_rain: return (150, 150, 180)
            return self.lerp_color((0, 40, 0), (0, 150, 50), h_ratio)

        # --- 164. Tundra Permafrost (Cold) ---
        # Frozen Earth -> Ice -> Snow
        if mode == 'Tundra Permafrost':
            if h_ratio < 0.2: return (60, 50, 40) # Earth
            if h_ratio < 0.8: return (100, 180, 200) # Ice
            return (255, 255, 255) # Snow

        # --- 165. Desert Bloom (Rare Event) ---
        # Sand -> Sudden vivid flowers at top
        if mode == 'Desert Bloom':
            if h_ratio < 0.8: return (210, 180, 140) # Sand
            # Random flower colors
            seed_val = int(calc_i)
            random.seed(seed_val)
            col = random.choice([(255, 0, 0), (255, 0, 255), (255, 255, 0)])
            random.seed(None)
            return col

        # --- 166. Deep Cave Crystals (Geology) ---
        # Dark Rock background, vibrant Magenta/Cyan crystals
        if mode == 'Deep Cave Crystals':
            if h_ratio < 0.5: return (20, 20, 25) # Rock
            # Crystal refraction
            hue = (calc_i * 25) % 360
            c = pygame.Color(0); c.hsla = (hue, 80, 50, 100)
            return (c.r, c.g, c.b)

        # --- 167. Geyser Eruption (Water) ---
        # Steam White -> Boiling Water Blue
        if mode == 'Geyser Eruption':
            # Bubbles
            bubble = math.sin(calc_i * 10 + t * 10)
            if bubble > 0.8: return (255, 255, 255)
            return self.lerp_color((0, 100, 255), (200, 240, 255), h_ratio)

        # --- 168. Tornado Alley (Wind) ---
        # Swirling Grey/Green wind patterns
        if mode == 'Tornado Alley':
            swirl = math.sin(h_ratio * 10 + t * 5 + calc_i * 0.5)
            base = (60, 70, 60) # Greenish grey sky
            light = (120, 130, 120)
            return self.lerp_color(base, light, (swirl + 1) / 2)

        # --- 169. Morning Dew (Macro) ---
        # Leaf Green with water droplets (White highlight)
        if mode == 'Morning Dew':
            base_green = self.lerp_color((20, 60, 20), (50, 150, 50), h_ratio)
            # Droplet sphere math approx
            drop = math.sin(calc_i * 2) * math.sin(h_ratio * 8)
            if drop > 0.9: return (255, 255, 255) # Reflection
            if drop > 0.7: return (0, 100, 100) # Water body
            return base_green

        # --- 170. Autumn Canopy (Season) ---
        # Green -> Yellow -> Orange -> Red -> Brown
        if mode == 'Autumn Canopy':
            if h_ratio < 0.2: return (0, 100, 0)
            if h_ratio < 0.4: return (255, 255, 0)
            if h_ratio < 0.6: return (255, 140, 0)
            if h_ratio < 0.8: return (160, 0, 0)
            return (100, 60, 20)

        # --- 171. Bauhaus Construct (Design) ---
        # Primary Colors (Red, Blue, Yellow) + Black/White geometry
        if mode == 'Bauhaus Construct':
            # Blocky assignment based on index
            grp = (calc_i // 5) % 4
            if grp == 0: return (20, 20, 20) # Black
            if grp == 1: return (200, 0, 0) # Red
            if grp == 2: return (0, 0, 200) # Blue
            return (220, 200, 0) # Yellow

        # --- 172. De Stijl Grid (Mondrian) ---
        # White background with black lines and primary color blocks
        if mode == 'De Stijl Grid':
            # Use random seed based on index to assign properties
            random.seed(calc_i)
            r = random.random()
            random.seed(None)
            if r > 0.9: return (255, 0, 0)
            if r > 0.8: return (0, 0, 255)
            if r > 0.7: return (255, 255, 0)
            if r < 0.1: return (10, 10, 10) # Black lines
            return (245, 245, 245) # White

        # --- 173. Pointillism (Art) ---
        # Dots of opposing colors blending by eye (simulated by noise)
        if mode == 'Pointillism':
            # Green/Red mix
            noise = (math.sin(calc_i * 99) + 1) / 2
            return self.lerp_color((0, 150, 50), (200, 50, 0), noise)

        # --- 174. Surrealist Dream (Dali) ---
        # Melting clocks: Gold and Sky Blue distortion
        if mode == 'Surrealist Dream':
            # Melt drip effect
            drip = math.sin(calc_i * 0.2 + t)
            if drip > 0: return self.lerp_color((218, 165, 32), (255, 255, 255), h_ratio)
            return self.lerp_color((135, 206, 235), (0, 0, 100), h_ratio)

        # --- 175. Art Nouveau Gold (Luxury) ---
        # Flowing organic Gold lines on Dark Green
        if mode == 'Art Nouveau Gold':
            # Vine pattern
            vine = math.sin(h_ratio * 10 + calc_i * 0.5)
            if vine > 0.7: return (218, 165, 32)
            return (10, 40, 20)

        # --- 176. Brutalist Concrete (Architecture) ---
        # Shades of unpainted grey concrete, harsh lighting
        if mode == 'Brutalist Concrete':
            # Blocky shading
            shade = int((calc_i % 3) * 20)
            grey = 100 + shade
            # Harsh light at top
            if h_ratio > 0.9: return (255, 255, 240)
            return (grey, grey, grey)

        # --- 177. Pop Art Halftone (Warhol) ---
        # Cyan/Magenta dots
        if mode == 'Pop Art Halftone':
            dot = (calc_i + int(h_ratio * 20)) % 2
            if dot == 0: return (0, 255, 255)
            return (255, 0, 255)

        # --- 178. Impressionist Water (Monet) ---
        # Soft dabs of Blue, Green, and Lilac
        if mode == 'Impressionist Water':
            # Soft noise
            n = math.sin(calc_i * 0.8 + h_ratio * 5)
            if n < -0.3: return (100, 149, 237) # Cornflower Blue
            if n < 0.3: return (143, 188, 143) # Sea Green
            return (221, 160, 221) # Plum

        # --- 179. Cubist Fracture (Picasso) ---
        # Sharp angular shards of Earth tones
        if mode == 'Cubist Fracture':
            shard = (int(calc_i / 3) + int(h_ratio * 5)) % 4
            if shard == 0: return (160, 82, 45) # Sienna
            if shard == 1: return (210, 180, 140) # Tan
            if shard == 2: return (112, 128, 144) # Slate
            return (40, 40, 40) # Outline

        # --- 180. Vaporwave Statue (Aesthetic) ---
        # Marble White with Pink/Cyan glitch
        if mode == 'Vaporwave Statue':
            glitch = random.random()
            if glitch > 0.95: return (255, 0, 255)
            if glitch > 0.90: return (0, 255, 255)
            # Marble shading
            shade = 220 + int(math.sin(calc_i)*30)
            return (shade, shade, shade)

        # --- 181. Liquid Mercury (Material) ---
        # Highly reflective Silver flowing
        if mode == 'Liquid Mercury':
            # Specular highlight calculation
            spec = math.sin(h_ratio * 3 - t * 2 + calc_i * 0.1)
            val_g = 150
            if spec > 0.9: val_g = 255
            elif spec > 0.5: val_g = 200
            else: val_g = 100
            return (val_g, val_g, val_g)

        # --- 182. Damascus Steel (Metal) ---
        # Wavy Grey/Dark Grey woodgrain pattern
        if mode == 'Damascus Steel':
            grain = math.sin(calc_i * 0.5 + math.sin(h_ratio * 10))
            col = self.lerp_color((50, 50, 60), (180, 180, 190), (grain + 1) / 2)
            return col

        # --- 183. Carbon Fiber (Tech) ---
        # Black/Dark Grey woven pattern
        if mode == 'Carbon Fiber':
            weave = (int(calc_i) + int(h_ratio * 20)) % 2
            if weave == 0: return (20, 20, 20)
            return (60, 60, 65)

        # --- 184. Brushed Aluminum (Industrial) ---
        # Horizontal streaks of Light Grey
        if mode == 'Brushed Aluminum':
            streak = random.random() * 0.2
            grey = int(180 + streak * 50)
            return (grey, grey, grey + 10)

        # --- 185. Oxidized Copper (Aging) ---
        # Copper -> Verdigris (Teal)
        if mode == 'Oxidized Copper':
            # Patina spots
            noise = math.sin(calc_i * 0.9 + h_ratio * 2)
            if noise > 0: return (64, 224, 208) # Verdigris
            return (184, 115, 51) # Copper

        # --- 186. Stained Glass Window (Religion) ---
        # Backlit vibrant colors with black leading
        if mode == 'Stained Glass Window':
            # Leading lines
            if calc_i % 6 == 0 or int(h_ratio * 10) % 5 == 0:
                return (0, 0, 0)
            # Random pane colors (consistent by pos)
            random.seed(calc_i * 100 + int(h_ratio * 5))
            c = random.choice([(200, 0, 0), (0, 0, 200), (255, 200, 0), (0, 150, 50)])
            random.seed(None)
            return c

        # --- 187. Mosaic Tile (Ancient) ---
        # Small squares of varying Blue/White
        if mode == 'Mosaic Tile':
            # Tile logic
            r_seed = int(calc_i) + int(h_ratio * 10) * 100
            random.seed(r_seed)
            var = random.randint(-20, 20)
            base = 150 + var
            random.seed(None)
            return (base - 50, base, base + 50)

        # --- 188. Royal Tapestry (Medieval) ---
        # Woven Red/Gold pattern
        if mode == 'Royal Tapestry':
            pattern = (int(calc_i / 2) + int(h_ratio * 10)) % 2
            if pattern == 0: return (100, 0, 20) # Maroon
            return (218, 165, 32) # Gold Thread

        # --- 189. Denim & Leather (Texture) ---
        # Dark Blue Jeans texture vs Black Leather
        if mode == 'Denim & Leather':
            if h_ratio < 0.5:
                # Denim stitching
                if calc_i % 8 == 0: return (255, 165, 0)
                return (25, 25, 112)
            else:
                return (20, 20, 20) # Leather

        # --- 190. Rusty Chain (Decay) ---
        # Iron links with Rust
        if mode == 'Rusty Chain':
            link = int(h_ratio * 10) % 2
            if link == 0: return (10, 10, 10) # Gap
            # Rust gradient
            return self.lerp_color((100, 100, 110), (160, 60, 20), h_ratio)

        # --- 191. Doppler Effect (Physics) ---
        # Redshift (left) to Blueshift (right)
        if mode == 'Doppler Effect':
            # Horizontal gradient based on index (calc_i) relative to total
            pos = calc_i / max(1, total)
            return self.lerp_color((255, 0, 0), (0, 0, 255), pos)

        # --- 192. Sonic Boom (Shockwave) ---
        # White cone in middle, Mach diamonds behind
        if mode == 'Sonic Boom':
            center_dist = abs(calc_i - (total / 2)) / (total / 2)
            if center_dist < 0.1: return (255, 255, 255) # Jet
            # Diamonds
            diamond = math.sin(center_dist * 20 - t * 10)
            if diamond > 0.5: return (255, 200, 150)
            return (100, 100, 255)

        # --- 193. Interference Pattern (Wave) ---
        # Constructive/Destructive waves (Black/White bands)
        if mode == 'Interference Pattern':
            wave1 = math.sin(calc_i * 0.3 + t)
            wave2 = math.sin(calc_i * 0.4 - t)
            construct = (wave1 + wave2) / 2
            val_c = int((construct + 1) * 127)
            return (val_c, val_c, val_c)

        # --- 194. Chaos Theory (Math) ---
        # Strange Attractor colors (Butterfly effect)
        if mode == 'Chaos Theory':
            # Sensitive dependence on initial conditions (index)
            r = int((math.sin(calc_i) + 1) * 127)
            g = int((math.sin(calc_i * 1.1) + 1) * 127)
            b = int((math.sin(calc_i * 1.2) + 1) * 127)
            # brighten based on volume
            boost = int(h_ratio * 100)
            return (min(255, r+boost), min(255, g+boost), min(255, b+boost))

        # --- 195. Fractal Boundary (Mandelbrot) ---
        # Psychedelic bands at edges
        if mode == 'Fractal Boundary':
            # Iterative map simulation
            z = h_ratio * 10
            if int(z) % 2 == 0: return (0, 0, 0)
            hue = (calc_i * 10 + t * 50) % 360
            c = pygame.Color(0); c.hsla = (hue, 100, 50, 100)
            return (c.r, c.g, c.b)

        # --- 196. String Theory (Multiverse) ---
        # Vibrating "strings" of 11 dimensions (colors)
        if mode == 'String Theory':
            dim = calc_i % 11
            # Assign specific color per dimension index
            cols = [
                (255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255),
                (255,0,255), (255,255,255), (128,0,0), (0,128,0), (0,0,128), (128,128,0)
            ]
            return self.lerp_color(cols[dim], (255, 255, 255), h_ratio)

        # --- 197. Dark Energy (Cosmic) ---
        # Expansion force: Purple pushing against Black
        if mode == 'Dark Energy':
            force = h_ratio * h_ratio # Exponential growth
            return self.lerp_color((10, 0, 20), (100, 0, 200), force)

        # --- 198. Antimatter Containment (Sci-Fi) ---
        # Magnetic Trap (Grey) containing Positrons (Gold)
        if mode == 'Antimatter Containment':
            if h_ratio < 0.1 or h_ratio > 0.9: return (50, 50, 60) # Magnets
            # Annihilation flickering
            if random.random() > 0.9: return (255, 255, 255)
            return (255, 215, 0)

        # --- 199. Schrodinger's Cat (Quantum) ---
        # Alive (Green) or Dead (Red) - undetermined until observed (drawn)
        if mode == 'Schrodinger\'s Cat':
            # Fluctuate based on time, different for every bar
            state = math.sin(calc_i * 1337 + t)
            if state > 0: return (0, 255, 0)
            return (255, 0, 0)

        # --- 200. Time Dilation (Relativity) ---
        # Slow moving Red (high gravity) vs Fast Blue (low gravity)
        if mode == 'Time Dilation':
            # Bottom moves slow, Top moves fast
            shift = math.sin(t * (0.5 + h_ratio * 5))
            return self.lerp_color((100, 0, 0), (0, 100, 255), (shift + 1) / 2)

        # --- 201. Quantum Realm (Subatomic) ---
        # Deep violet background with nervous, jittery cyan particles
        if mode == 'Quantum Realm':
            # Create subatomic "jitter" using high frequency sine
            jitter = math.sin(calc_i * 50 + t * 20)
            base = (20, 0, 40)
            if jitter > 0.8: return (0, 255, 255)  # Electron
            return self.lerp_color(base, (100, 0, 200), h_ratio)

        # --- 202. Viking Fire (Norse) ---
        # Cold steel grey bottom, roaring orange/yellow fire top
        if mode == 'Viking Fire':
            if h_ratio < 0.4:
                # Steel texture
                metal = 80 + int(math.sin(calc_i) * 20)
                return (metal, metal, metal + 10)
            else:
                # Fire texture
                return self.lerp_color((255, 69, 0), (255, 255, 0), (h_ratio - 0.4) * 1.6)

        # --- 203. Cyber Wasp (Aggressive) ---
        # High contrast Yellow and Black diagonal stripes
        if mode == 'Cyber Wasp':
            # Sharp diagonal math
            stripe = (calc_i + int(h_ratio * 15) - int(t * 5)) % 6
            if stripe < 3: return (255, 215, 0)
            return (10, 10, 10)

        # --- 204. Hyper-Loop (Speed) ---
        # Blurring streaks of white on blue moving horizontally
        if mode == 'Hyper-Loop':
            # Simulation of motion blur
            streak = math.sin(h_ratio * 5 + t * 20)
            if streak > 0.9: return (255, 255, 255)
            return self.lerp_color((0, 0, 100), (0, 100, 255), h_ratio)

        # --- 205. Alien Flora (Exoplanet) ---
        # Dark Purple stems with neon Pink/Blue bioluminescent tips
        if mode == 'Alien Flora':
            if h_ratio < 0.6: return (30, 0, 60)  # Stem
            # Pulsing flower
            pulse = (math.sin(t * 3) + 1) / 2
            col1 = (0, 255, 255)
            col2 = (255, 0, 255)
            return self.lerp_color(col1, col2, pulse * h_ratio)

        # --- 206. Tesla Coil (Electricity) ---
        # Dark purple with arcing white lightning patterns
        if mode == 'Tesla Coil':
            # Lightning arc math
            arc = math.sin(calc_i * 0.8 + t * 15) * math.sin(h_ratio * 20)
            if arc > 0.95: return (200, 200, 255)  # Arc
            return self.lerp_color((10, 0, 30), (80, 0, 150), h_ratio)

        # --- 207. Coronal Mass (Solar) ---
        # Roaring Red/Orange surface with bright Yellow ejection loops
        if mode == 'Coronal Mass':
            # Turbulent surface
            turb = math.sin(calc_i * 0.3 + t) + math.cos(h_ratio * 10)
            if turb > 1.2: return (255, 255, 200)  # Ejection
            return self.lerp_color((150, 20, 0), (255, 100, 0), h_ratio)

        # --- 208. Police Chase (Action) ---
        # Strobing Red and Blue lights
        if mode == 'Police Chase':
            # Strobe effect based on time
            strobe = int(t * 5) % 2
            if strobe == 0:
                return self.lerp_color((0, 0, 0), (255, 0, 0), h_ratio)
            else:
                return self.lerp_color((0, 0, 0), (0, 0, 255), h_ratio)

        # --- 209. Glitch Mob (Digital) ---
        # Grey background with random RGB color artifacting
        if mode == 'Glitch Mob':
            random.seed(int(t * 10) + calc_i)
            is_glitch = random.random() > 0.92
            random.seed(None)
            if is_glitch: return random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
            grey = int(h_ratio * 150)
            return (grey, grey, grey + 10)

        # --- 210. Void Glass (Obsidian) ---
        # Glossy Black/Purple with sharp white reflections
        if mode == 'Void Glass':
            # Specular highlight calculation
            spec = math.sin(h_ratio * 5 - calc_i * 0.2)
            if spec > 0.95: return (255, 255, 255)
            return self.lerp_color((0, 0, 0), (40, 0, 60), h_ratio)

        # --- 211. Raw Copper (Material) ---
        # Metallic shiny orange/brown stripes
        if mode == 'Raw Copper':
            # Metallic sheen
            sheen = math.sin(calc_i + h_ratio * 10)
            base = (184, 115, 51)
            highlight = (255, 200, 150)
            return self.lerp_color(base, highlight, (sheen + 1) / 2)

        # --- 212. Neon Skyline (City) ---
        # Black buildings (silhouettes) with random lighted windows
        if mode == 'Neon Skyline':
            # Windows pattern
            window = (int(calc_i) % 4 != 0) and (int(h_ratio * 20) % 3 != 0)
            if window and h_ratio < 0.8:
                random.seed(calc_i + int(h_ratio * 10))
                is_lit = random.random() > 0.7
                random.seed(None)
                if is_lit: return (255, 255, 200)
            return (10, 10, 15)

        # --- 213. Marshmallow (Soft) ---
        # White puffy bottom fading into soft Pink
        if mode == 'Marshmallow':
            return self.lerp_color((255, 250, 250), (255, 182, 193), h_ratio)

        # --- 214. Radioactive Isotope (Sci-Fi) ---
        # Glowing Blue core, Green unstable edge
        if mode == 'Radioactive Isotope':
            if h_ratio < 0.7:
                return self.lerp_color((0, 0, 50), (0, 100, 255), h_ratio * 1.4)
            return self.lerp_color((0, 100, 255), (50, 255, 50), (h_ratio - 0.7) * 3.3)

        # --- 215. Steampunk Gear (Mechanical) ---
        # Interlocking Brass and Iron colors
        if mode == 'Steampunk Gear':
            # Tooth pattern
            tooth = int(calc_i * 0.5) % 2
            if tooth == 0: return (165, 105, 30)  # Brass
            return (80, 80, 80)  # Iron

        # --- 216. Samurai Lacquer (Armor) ---
        # Deep Red and Black segments with Gold trim
        if mode == 'Samurai Lacquer':
            seg = int(h_ratio * 8)
            pos_in_seg = (h_ratio * 8) - seg
            if pos_in_seg > 0.9: return (215, 180, 50)  # Gold Trim
            if seg % 2 == 0: return (140, 0, 0)  # Red Lacquer
            return (10, 10, 10)  # Black

        # --- 217. Biolum Jellyfish (Deep Sea) ---
        # Translucent Pink/Purple body with bright Blue nerves
        if mode == 'Biolum Jellyfish':
            nerve = math.sin(calc_i * 2 + t * 2)
            if nerve > 0.9: return (0, 255, 255)
            return self.lerp_color((50, 0, 50), (150, 50, 150), h_ratio)

        # --- 218. Tartan Plaid (Fabric) ---
        # Red background with Green/Black criss-cross
        if mode == 'Tartan Plaid':
            # Grid logic
            v_line = calc_i % 6 == 0
            h_line = int(h_ratio * 20) % 6 == 0
            if v_line or h_line: return (0, 0, 0)
            if (calc_i // 6) % 2 == (int(h_ratio * 20) // 6) % 2:
                return (0, 100, 0)  # Green square
            return (200, 0, 0)  # Red base

        # --- 219. Honeycomb Gold (Structure) ---
        # Yellow Hexagons with Orange borders
        if mode == 'Honeycomb Gold':
            hex_pat = math.sin(calc_i * 1.5) + math.cos(h_ratio * 10)
            if hex_pat > 1.0: return (255, 140, 0)  # Border
            return (255, 215, 0)  # Honey

        # --- 220. Pastel Goth (Aesthetic) ---
        # Matte Black dripped with Pastel Pink and Mint
        if mode == 'Pastel Goth':
            # Drip logic
            drip = math.sin(calc_i * 0.3 + t) + h_ratio
            if drip > 1.5:
                if calc_i % 2 == 0: return (255, 182, 193)  # Pink
                return (152, 251, 152)  # Mint
            return (20, 20, 20)

        # --- 221. Urban Neon (Reflections) ---
        # Wet Asphalt (dark grey) reflecting multicolored lights
        if mode == 'Urban Neon':
            asphalt = (30, 30, 35)
            # Reflection pools
            pool = math.sin(calc_i * 0.1 + h_ratio * 5)
            if pool > 0.8:
                # Color based on index
                hue = (calc_i * 20) % 360
                c = pygame.Color(0);
                c.hsla = (hue, 80, 50, 100)
                return (c.r, c.g, c.b)
            return asphalt

        # --- 222. Frozen Lake (Winter) ---
        # Deep Blue water covered by cracked White Ice
        if mode == 'Frozen Lake':
            # Cracks
            crack = random.random()  # Noise-like
            random.seed(int(calc_i * 50 + h_ratio * 50))
            is_crack = random.random() > 0.9
            random.seed(None)
            if is_crack: return (255, 255, 255)
            return self.lerp_color((0, 0, 50), (100, 200, 255), h_ratio)

        # --- 223. Blood Cells (Microscopic) ---
        # Red background with brighter Red donut shapes
        if mode == 'Blood Cells':
            # Cell shape approx
            cell = math.sin(calc_i) * math.sin(h_ratio * 10 - t)
            if cell > 0.5: return (255, 100, 100)  # Cell rim
            if cell > 0.3: return (100, 0, 0)  # Cell center
            return (180, 0, 0)  # Plasma

        # --- 224. Graffiti Wall (Street Art) ---
        # Concrete grey with random splashes of bright spray paint
        if mode == 'Graffiti Wall':
            random.seed(int(calc_i / 5) + int(h_ratio * 5))
            color_idx = random.randint(0, 4)
            random.seed(None)

            base = (60, 60, 60)
            colors = [(255, 0, 100), (0, 255, 255), (255, 255, 0), (50, 255, 50), base]
            return colors[color_idx]

        # --- 225. Aurora Veil (Atmosphere) ---
        # Shifting translucent curtains of Green and Purple
        if mode == 'Aurora Veil':
            # Wave curtain math
            curtain = math.sin(calc_i * 0.1 + t) + math.sin(h_ratio * 5 + t * 0.5)
            if curtain > 0:
                return self.lerp_color((0, 20, 0), (0, 255, 100), abs(curtain))
            else:
                return self.lerp_color((10, 0, 20), (150, 0, 255), abs(curtain))

        # --- 226. Roulette Wheel (Casino) ---
        # Alternating Red, Black, and Green (Zero)
        if mode == 'Roulette Wheel':
            # Slot based on index
            slot = (calc_i + int(t)) % 37
            if slot == 0: return (0, 255, 0) # Zero
            if slot % 2 == 0: return (200, 0, 0) # Red
            return (20, 20, 20) # Black

        # --- 227. Blueprint Tech (Architectural) ---
        # Deep Blue background (implied), White lines
        if mode == 'Blueprint Tech':
            # White grid lines on blue
            is_grid = (calc_i % 10 == 0) or (int(h_ratio * 10) % 5 == 0)
            if is_grid: return (255, 255, 255)
            # Fill
            return self.lerp_color((0, 50, 150), (0, 100, 255), h_ratio)

        # --- 228. Sonar Radar (Submarine) ---
        # Green sweep on Black
        if mode == 'Sonar Radar':
            # Radar sweep calculation
            sweep = (t * 2) % total
            dist = abs(calc_i - sweep)
            if dist > total/2: dist = total - dist
            # Fade trail
            if dist < 15:
                intensity = int(255 * (1 - (dist/15)))
                return (0, intensity, 0)
            # Blip objects based on height
            if h_ratio > 0.8: return (0, 255, 0)
            return (0, 20, 0)

        # --- 229. Glitch TV (Static) ---
        # Greyscale noise with random color bars
        if mode == 'Glitch TV':
            random.seed(int(calc_i * t))
            is_noise = random.random() > 0.8
            random.seed(None)
            if is_noise:
                return (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            grey = random.randint(50, 200)
            return (grey, grey, grey)

        # --- 230. Traffic Light (Urban) ---
        # Vertical stacking: Green -> Yellow -> Red
        if mode == 'Traffic Light':
            if h_ratio < 0.33: return (0, 255, 0) # Green
            if h_ratio < 0.66: return (255, 200, 0) # Yellow
            return (255, 0, 0) # Red

        # --- 231. Peppermint Candy (Sweet) ---
        # Red and White spiral
        if mode == 'Peppermint Candy':
            spiral = (calc_i + int(h_ratio * 10) + int(t*2)) % 2
            if spiral == 0: return (255, 255, 255)
            return (220, 20, 60)

        # --- 232. Construction Zone (Industrial) ---
        # Orange and Black diagonal stripes
        if mode == 'Construction Zone':
            stripe = (calc_i + int(h_ratio * 5)) % 4
            if stripe < 2: return (255, 140, 0) # Safety Orange
            return (20, 20, 20)

        # --- 233. Night Vision Goggles (Tactical) ---
        # Monochromatic Green with film grain
        if mode == 'Night Vision Goggles':
            # Grain
            random.seed(int(t*100 + calc_i))
            grain = random.randint(-30, 30)
            random.seed(None)
            val_g = int(h_ratio * 200) + 50 + grain
            return (0, max(0, min(255, val_g)), 0)

        # --- 234. CMYK Process (Print) ---
        # Cyan, Magenta, Yellow bands
        if mode == 'CMYK Process':
            if h_ratio < 0.33: return (0, 255, 255) # Cyan
            if h_ratio < 0.66: return (255, 0, 255) # Magenta
            return (255, 255, 0) # Yellow

        # --- 235. Vapor Grid (Retrowave) ---
        # Purple gradient with pink grid lines
        if mode == 'Vapor Grid':
            # Grid
            if calc_i % 6 == 0: return (255, 100, 200) # Pink line
            return self.lerp_color((40, 0, 60), (0, 255, 255), h_ratio)

        # --- 236. Radioactive Decay (Hazard) ---
        # Sickly Green with glowing particles
        if mode == 'Radioactive Decay':
            # Particles
            part = math.sin(calc_i * 10 + t * 5)
            if part > 0.9: return (200, 255, 200)
            return self.lerp_color((20, 30, 0), (100, 255, 0), h_ratio)

        # --- 237. Gold Bullion (Wealth) ---
        # Solid metallic gold shading
        if mode == 'Gold Bullion':
            # Specular sheen
            sheen = (math.sin(calc_i * 0.5 - t) + 1) / 2
            base = (218, 165, 32)
            high = (255, 255, 200)
            return self.lerp_color(base, high, h_ratio * sheen)

        # --- 238. Cyber Circuit (Hardware) ---
        # Dark Green board, Gold traces
        if mode == 'Cyber Circuit':
            # Traces
            trace = (calc_i % 5 == 0) or (int(h_ratio * 15) % 4 == 0)
            if trace: return (180, 150, 50) # Gold
            return (0, 40, 0) # PCB Green

        # --- 239. Red Alert (Emergency) ---
        # Pulsing Red and White
        if mode == 'Red Alert':
            pulse = math.sin(t * 10)
            if pulse > 0: return (255, 0, 0)
            return (255, 255, 255)

        # --- 240. Mariana Trench (Deep Sea) ---
        # Black to Dark Blue gradient
        if mode == 'Mariana Trench':
            return self.lerp_color((0, 0, 0), (0, 0, 100), h_ratio)

        # --- 241. Jungle Camo (Military) ---
        # Patchy Green, Brown, Black
        if mode == 'Jungle Camo':
            # Noise-based patches
            patch = math.sin(calc_i * 0.5) + math.cos(h_ratio * 5)
            if patch > 1: return (30, 30, 30) # Black
            if patch < 0: return (100, 70, 40) # Brown
            return (34, 139, 34) # Green

        # --- 242. Ruby Geode (Mineral) ---
        # Grey Rock exterior, Ruby Red crystal interior
        if mode == 'Ruby Geode':
            if h_ratio < 0.2: return (60, 60, 65) # Rock
            # Crystal facet
            facet = (calc_i % 2) * 50
            r = min(255, 150 + int(h_ratio * 100) + facet)
            return (r, 0, 40)

        # --- 243. Firefly Night (Nature) ---
        # Dark Blue night with yellow sparks
        if mode == 'Firefly Night':
            random.seed(int(calc_i + t))
            spark = random.random() > 0.95
            random.seed(None)
            if spark: return (255, 255, 100)
            return self.lerp_color((5, 5, 20), (20, 20, 60), h_ratio)

        # --- 244. Pixel Art (Retro) ---
        # Primary colors in blocks
        if mode == 'Pixel Art':
            # Quantize
            q = int(h_ratio * 4)
            if q == 0: return (0, 0, 200)
            if q == 1: return (0, 200, 0)
            if q == 2: return (200, 0, 0)
            return (200, 200, 0)

        # --- 245. Barcode (Data) ---
        # Black and White vertical lines of varying thickness (simulated)
        if mode == 'Barcode':
            random.seed(calc_i)
            is_black = random.choice([True, False])
            random.seed(None)
            if is_black: return (0, 0, 0)
            return (255, 255, 255)

        # --- 246. Brass Knuckles (Metal) ---
        # Brass and Steel gradient
        if mode == 'Brass Knuckles':
            if h_ratio < 0.5:
                # Brass
                return self.lerp_color((100, 80, 20), (180, 140, 40), h_ratio * 2)
            else:
                # Steel
                return self.lerp_color((100, 100, 100), (220, 220, 230), (h_ratio - 0.5) * 2)

        # --- 247. Ice Shard (Cold) ---
        # Sharp White/Cyan
        if mode == 'Ice Shard':
            if h_ratio > 0.8: return (255, 255, 255)
            return self.lerp_color((200, 255, 255), (0, 200, 255), 1 - h_ratio)

        # --- 248. Neon Sign (Advertising) ---
        # Black background, hollow bright neon tubes
        if mode == 'Neon Sign':
            # Only edges are colored (simulated)
            return self.lerp_color((255, 0, 100), (0, 255, 255), h_ratio)

        # --- 249. Petrol Station (Gritty) ---
        # Concrete Grey with Rainbow Oil stains
        if mode == 'Petrol Station':
            # Concrete
            base = (80, 80, 80)
            # Oil stain logic
            stain = math.sin(calc_i * 0.2 + h_ratio * 3)
            if stain > 0.5:
                hue = (calc_i * 20) % 360
                c = pygame.Color(0); c.hsla = (hue, 50, 50, 100)
                return (c.r, c.g, c.b)
            return base

        # --- 250. Sepia Memories (Photo) ---
        # Monochromatic Brown/Cream scale
        if mode == 'Sepia Memories':
            return self.lerp_color((60, 30, 0), (240, 220, 180), h_ratio)

        # --- 251. Cybernetic Heart (Pulsing Tech) ---
        # Red core with black crust, pulsing brightness based on time
        if mode == 'Cybernetic Heart':
            pulse = (math.sin(t * 4) + 1) / 2
            # Digital noise pattern
            is_vein = (int(calc_i * 0.5) ^ int(h_ratio * 20)) % 5 == 0
            if is_vein: return (255, 50, 50) # Bright Artery
            # Dark pulsating background
            val_r = int(50 + (pulse * 100))
            return (val_r, 0, 0)

        # --- 252. Aurora Borealis II (Natural Phenomenon) ---
        # Complex wave interference creating curtains of Green/Purple
        if mode == 'Aurora Borealis II':
            # Create waving "curtains"
            curtain = math.sin(calc_i * 0.1 + t) + math.sin(calc_i * 0.05 - t * 0.5) + math.sin(h_ratio * 5)
            if curtain > 0.5:
                return self.lerp_color((0, 255, 100), (255, 255, 255), (curtain - 0.5))
            return self.lerp_color((10, 0, 30), (100, 0, 200), (curtain + 2) / 2.5)

        # --- 253. Gothic Stained Glass (Art) ---
        # Blocks of deep vivid colors separated by black lead lines
        if mode == 'Gothic Stained Glass':
            # Lead lines
            if calc_i % 8 == 0 or int(h_ratio * 12) % 6 == 0:
                return (10, 10, 10)
            # Random fixed colors based on position seed
            random.seed(int(calc_i / 8) + int(h_ratio * 2) * 100)
            c = random.choice([(200, 0, 0), (0, 0, 200), (200, 200, 0), (128, 0, 128), (0, 100, 0)])
            random.seed(None)
            return c

        # --- 254. Synthwave Grid (Retrowave) ---
        # Vertical purple grid lines over a sunset gradient
        if mode == 'Synthwave Grid':
            # Grid lines every 10 bars
            if calc_i % 10 == 0: return (0, 255, 255) # Cyan Grid
            # Sunset Gradient
            if h_ratio < 0.5:
                return self.lerp_color((45, 0, 90), (180, 0, 80), h_ratio * 2)
            return self.lerp_color((180, 0, 80), (255, 200, 0), (h_ratio - 0.5) * 2)

        # --- 255. Biohazard Warning (Industrial) ---
        # Yellow and Black diagonal stripes (Hazard tape)
        if mode == 'Biohazard Warning':
            # Diagonal math
            stripe = (calc_i + int(h_ratio * 15)) % 6
            if stripe < 3: return (255, 255, 0) # Safety Yellow
            return (20, 20, 20) # Black

        # --- 256. Liquid Gold (Material) ---
        # Metallic sheen that moves with time
        if mode == 'Liquid Gold':
            # Specular highlight calculation using sine
            sheen = math.sin(calc_i * 0.2 + h_ratio * 5 - t * 2)
            base = (218, 165, 32)
            highlight = (255, 255, 220)
            if sheen > 0.8: return highlight
            return self.lerp_color((100, 80, 10), base, (sheen + 1) / 2)

        # --- 257. Cherry Blossom (Nature) ---
        # Pink petals falling (simulated noise)
        if mode == 'Cherry Blossom':
            # Branch brown at bottom
            if h_ratio < 0.15: return (80, 50, 30)
            # Falling petals logic
            noise = math.sin(calc_i * 90 + h_ratio * 40 + t)
            if noise > 0.8: return (255, 240, 245) # White/Pink highlight
            return self.lerp_color((255, 183, 197), (255, 105, 180), h_ratio)

        # --- 258. Abyssal Biolum (Deep Sea) ---
        # Dark Blue water with neon blue dots
        if mode == 'Abyssal Biolum':
            base = self.lerp_color((0, 0, 10), (0, 20, 60), h_ratio)
            # Bioluminescent spots
            spot = math.sin(calc_i * 50) * math.sin(h_ratio * 30 + t)
            if spot > 0.95: return (0, 255, 255)
            return base

        # --- 259. 8-Bit Arcade (Retro) ---
        # Quantized primary colors
        if mode == '8-Bit Arcade':
            level = int(h_ratio * 4)
            if level == 0: return (0, 0, 180) # Dark Blue
            if level == 1: return (0, 180, 0) # Mario Green
            if level == 2: return (255, 0, 0) # Red
            return (255, 255, 0) # Coin Yellow

        # --- 260. Magma Chamber (Geology) ---
        # Noise texture shifting from black rock to bright lava
        if mode == 'Magma Chamber':
            noise = math.sin(calc_i * 0.5 + t) + math.cos(h_ratio * 10)
            if noise > 1.0: return (40, 40, 40) # Floating Rock
            return self.lerp_color((200, 0, 0), (255, 200, 0), h_ratio)

        # --- 261. Prism Refraction (Physics) ---
        # White base splitting into RGB at the top
        if mode == 'Prism Refraction':
            if h_ratio < 0.6: return (240, 240, 255) # White Light
            # Split
            split = calc_i % 3
            if split == 0: return (255, 0, 0)
            if split == 1: return (0, 255, 0)
            return (0, 0, 255)

        # --- 262. Midnight Rain (Atmosphere) ---
        # Dark blue background with falling white streaks
        if mode == 'Midnight Rain':
            # Rain streaks
            drop = (h_ratio * 20 + t * 5 + calc_i) % 15
            if drop < 1: return (200, 200, 255) # Streak
            return self.lerp_color((5, 5, 20), (20, 20, 80), h_ratio)

        # --- 263. Steampunk Brass (Mechanical) ---
        # Gradient of copper/brass with "gear tooth" pattern
        if mode == 'Steampunk Brass':
            # Gear teeth pattern
            is_tooth = (calc_i % 3) == 0
            col_brass = (181, 166, 66)
            col_copper = (184, 115, 51)
            base = col_brass if is_tooth else col_copper
            # Oxidation at top
            if h_ratio > 0.9: return (64, 224, 208)
            return base

        # --- 264. Holo-Glitch (Sci-Fi) ---
        # Translucent cyan with random horizontal offsets (glitch)
        if mode == 'Holo-Glitch':
            random.seed(int(t * 10) + int(h_ratio * 5))
            glitch = random.random() > 0.9
            random.seed(None)
            if glitch: return (255, 255, 255)
            # Hologram banding
            band = math.sin(h_ratio * 50 - t * 5)
            if band > 0: return (0, 200, 255)
            return (0, 50, 100)

        # --- 265. Predator Thermal (Vision) ---
        # Blue -> Green -> Red -> White spectrum
        if mode == 'Predator Thermal':
            if h_ratio < 0.33:
                return self.lerp_color((0, 0, 100), (0, 255, 0), h_ratio * 3)
            elif h_ratio < 0.66:
                return self.lerp_color((0, 255, 0), (255, 0, 0), (h_ratio - 0.33) * 3)
            else:
                return self.lerp_color((255, 0, 0), (255, 255, 255), (h_ratio - 0.66) * 3)

        # --- 266. Cotton Candy Dream (Pastel) ---
        # Swirling soft Pink and Blue
        if mode == 'Cotton Candy Dream':
            swirl = math.sin(calc_i * 0.2 + t)
            c1 = (255, 182, 193) # Pastel Pink
            c2 = (173, 216, 230) # Pastel Blue
            return self.lerp_color(c1, c2, (swirl + 1) / 2)

        # --- 267. Radio Wave Interference (Physics) ---
        # Moiré pattern effect (Black/White rings)
        if mode == 'Radio Wave Interference':
            w1 = math.sin(calc_i * 0.5 + t)
            w2 = math.sin(h_ratio * 10)
            inter = (w1 + w2)
            val_bw = int(((math.sin(inter * 5) + 1) / 2) * 255)
            return (val_bw, val_bw, val_bw)

        # --- 268. Toxic Sludge (Hazard) ---
        # Neon Green and Purple bubbling texture
        if mode == 'Toxic Sludge':
            bubble = math.sin(calc_i * 0.8 + t) + math.cos(h_ratio * 8)
            if bubble > 1.0: return (57, 255, 20) # Neon Green
            return (75, 0, 130) # Deep Purple

        # --- 269. Cosmic Nebula (Space) ---
        # Complex noise blending Pink, Blue, and Black stars
        if mode == 'Cosmic Nebula':
            # Star
            random.seed(calc_i + int(h_ratio * 100))
            is_star = random.random() > 0.98
            random.seed(None)
            if is_star: return (255, 255, 255)
            # Cloud
            cloud = math.sin(calc_i * 0.1) + math.sin(h_ratio * 5 + t)
            return self.lerp_color((20, 0, 40), (200, 0, 150), (cloud + 2) / 4)

        # --- 270. Art Deco Luxury (Design) ---
        # Gold and Black geometric patterns
        if mode == 'Art Deco Luxury':
            # Chevron pattern
            pat = (calc_i + int(h_ratio * 10)) % 4
            if pat < 2: return (218, 165, 32) # Gold
            return (10, 10, 10) # Black

        # --- 271. Vampire Velvet (Gothic) ---
        # Deep Red with shadow texture
        if mode == 'Vampire Velvet':
            # Cloth fold texture
            fold = (math.sin(calc_i * 0.4) + 1) / 2
            col = self.lerp_color((50, 0, 0), (180, 0, 20), fold)
            if h_ratio > 0.8: return (255, 0, 0) # Blood tip
            return col

        # --- 272. Moving Candy Cane (Seasonal) ---
        # Red and White diagonal stripes that scroll up
        if mode == 'Moving Candy Cane':
            # Scrolling math
            stripe = (calc_i + int(h_ratio * 20) - int(t * 5)) % 6
            if stripe < 3: return (255, 255, 255)
            return (220, 20, 60)

        # --- 273. The Matrix (Sci-Fi) ---
        # Black background with falling green code trails
        if mode == 'The Matrix':
            trail = (h_ratio * 15 - t * 4) % 10
            if trail > 8: return (200, 255, 200) # Leader
            if trail > 3: return (0, 200, 0) # Body
            return (0, 20, 0) # Fade

        # --- 274. Oil Slick Shimmer (Texture) ---
        # Black liquid with moving rainbow interference
        if mode == 'Oil Slick Shimmer':
            if h_ratio < 0.2: return (10, 10, 10) # Oil base
            # Moving rainbow
            hue = (calc_i * 5 + h_ratio * 50 + t * 10) % 360
            c = pygame.Color(0)
            c.hsla = (hue, 60, 40, 100)
            return (c.r, c.g, c.b)

        # --- 275. Architectural Blueprint (Design) ---
        # Royal Blue background (implied), White lines
        if mode == 'Architectural Blueprint':
            # Grid lines
            is_grid = (calc_i % 12 == 0) or (int(h_ratio * 20) % 5 == 0)
            if is_grid: return (255, 255, 255) # Line
            return (0, 50, 150) # Blueprint Blue

        # --- 276. Pharaoh's Tomb (Historical) ---
        # Lapis Lazuli Blue with Gold Flakes and Sandstone base
        if mode == 'Pharaoh\'s Tomb':
            # Lapis Blue Base
            base = (25, 25, 112)
            # Gold Flecks (Randomized by position)
            random.seed(calc_i * 100 + int(h_ratio * 20))
            is_gold = random.random() > 0.9
            random.seed(None)

            if is_gold: return (255, 215, 0)
            if h_ratio < 0.15: return (194, 178, 128)  # Sandstone base
            return self.lerp_color(base, (0, 50, 160), h_ratio)

        # --- 277. Fatal Error (Glitch/Tech) ---
        # BSOD Blue background, White text artifacts, Red Critical Failure
        if mode == 'Fatal Error':
            # Critical Volume Failure
            if val > 80 and (int(t * 10) % 2 == 0): return (255, 0, 0)

            # "Text" artifacts
            is_text = (calc_i % 7 == 0) and (int(h_ratio * 30) % 2 == 0)
            if is_text: return (255, 255, 255)

            return (0, 0, 170)  # Windows BSOD Blue

        # --- 278. Karesansui (Zen Garden) ---
        # Raked Sand (Beige banding) with Dark Grey Rocks
        if mode == 'Karesansui':
            # Raked Sand Texture (Sine wave bands)
            rake = math.sin(h_ratio * 40 + calc_i * 0.2)
            sand_col = (235, 225, 200)
            shadow_col = (210, 200, 180)

            # "Rocks" (Random clusters)
            rock_noise = math.sin(calc_i * 0.5) * math.sin(h_ratio * 5)
            if rock_noise > 0.8: return (60, 60, 65)

            return self.lerp_color(shadow_col, sand_col, (rake + 1) / 2)

        # --- 279. Oxidized Statue (Material) ---
        # Bronze bottom, transitioning to Verdigris (Teal) via noise
        if mode == 'Oxidized Statue':
            bronze = (205, 127, 50)
            verdigris = (64, 224, 208)
            # Corrosion pattern
            corrosion = (math.sin(calc_i * 0.8) + 1) / 2
            # Higher up = more corrosion
            threshold = 1.0 - h_ratio
            if corrosion > threshold: return verdigris
            return bronze

        # --- 280. South Beach (Aesthetic) ---
        # Pastel Pink and Teal Art Deco Split
        if mode == 'South Beach':
            # Diagonal split
            split = (calc_i + int(h_ratio * 20)) % 20
            if split < 10: return (255, 182, 193)  # Pastel Pink
            return (0, 255, 255)  # Cyan

        # --- 281. Sugar Rush (Candy) ---
        # Swirling pattern of Red, White, and Mint Green
        if mode == 'Sugar Rush':
            # Complex swirl math
            swirl = int(calc_i * 0.5 + h_ratio * 10 + t * 2) % 3
            if swirl == 0: return (255, 0, 50)  # Red
            if swirl == 1: return (255, 255, 255)  # White
            return (100, 255, 180)  # Mint

        # --- 282. Mainframe (Tech) ---
        # Black background, glowing Green data lines, Orange processing heat
        if mode == 'Mainframe':
            # Data Lines
            if calc_i % 4 == 0: return (0, 20, 0)  # Dark gap
            if h_ratio > 0.8: return (255, 165, 0)  # Overheat

            # Blinking LED effect
            blink = math.sin(calc_i * 10 + t * 5)
            if blink > 0.8: return (50, 255, 50)  # Bright Green
            return (0, 100, 0)  # Dim Green

        # --- 283. Eldritch Void (Horror) ---
        # Non-euclidean Purple/Black/Sickly Green
        if mode == 'Eldritch Void':
            # Writhing texture
            writhing = math.sin(calc_i * 0.9 + t) + math.cos(h_ratio * 10 - t)
            if writhing > 1.2: return (20, 0, 40)  # Void
            if writhing < -1.0: return (50, 255, 50)  # Sickly Green
            return self.lerp_color((75, 0, 130), (0, 0, 0), h_ratio)

        # --- 284. Mother of Pearl (Iridescent) ---
        # Shifting Pinks, Greys, and Greens based on viewing angle (index)
        if mode == 'Mother of Pearl':
            angle = calc_i * 0.1 + t
            # FIX: Clamp values to 255 to prevent crash (Original math allowed up to 280)
            r = min(255, int((math.sin(angle) + 1) * 40 + 200))
            g = min(255, int((math.sin(angle + 2) + 1) * 20 + 210))
            b = min(255, int((math.sin(angle + 4) + 1) * 40 + 200))
            return (r, g, b)

        # --- 285. Solar Storm (Space) ---
        # Burning Yellow/Orange loops on Black
        if mode == 'Solar Storm':
            # Magnetic loops
            loop = abs(math.sin(calc_i * 0.1 - t * 2) * math.sin(h_ratio * 3.14))
            if loop > 0.8: return (255, 255, 200)  # White hot
            if loop > 0.2: return self.lerp_color((100, 0, 0), (255, 140, 0), loop)
            return (20, 0, 0)  # Dark space

        # --- 286. Memphis Design (80s Art) ---
        # Random Geometric shapes, Squiggles, Clashing Pastels
        if mode == 'Memphis Design':
            # Blocky noise based on grid
            grid_x = int(calc_i / 5)
            grid_y = int(h_ratio * 5)
            seed_val = grid_x + grid_y * 100
            random.seed(seed_val)
            col_choice = random.choice([
                (255, 255, 0), (0, 255, 255), (255, 0, 255), (0, 0, 0), (255, 255, 255)
            ])
            random.seed(None)
            return col_choice

        # --- 287. Bioluminescent Bay (Nature) ---
        # Dark water that glows neon blue ONLY when "agitated" (high volume)
        if mode == 'Bioluminescent Bay':
            base_water = (5, 5, 20)
            # Motion calculation (using volume)
            if h_ratio > 0.4:
                # Sparkles
                random.seed(int(t * 20) + calc_i)
                sparkle = random.random()
                random.seed(None)
                if sparkle > (1.0 - h_ratio): return (0, 255, 255)
            return base_water

        # --- 288. Chromatic Aberration (Optics) ---
        # Red Left, Green Middle, Blue Right (Separated channels)
        if mode == 'Chromatic Aberration':
            # Offset the logic based on channel
            # This simulates looking through a broken lens
            return (
                int(255 * min(1.0, h_ratio * 1.2)),  # Red channel boosted
                int(255 * min(1.0, h_ratio)),  # Green normal
                int(255 * min(1.0, h_ratio * 0.8))  # Blue lagged
            )

        # --- 289. Server Room (Tech) ---
        # Dark Racks with blinking status lights
        if mode == 'Server Room':
            if calc_i % 3 == 0: return (10, 10, 10)  # Rack divider
            # Lights
            if int(h_ratio * 20) % 2 == 0:
                # Random status
                random.seed(int(t * 2) + calc_i + int(h_ratio * 10))
                stat = random.random()
                random.seed(None)
                if stat > 0.9: return (255, 0, 0)  # Error
                if stat > 0.4: return (0, 255, 0)  # OK
                return (0, 50, 0)  # Off
            return (20, 20, 25)  # Metal

        # --- 290. Malachite (Mineral) ---
        # Banded Light and Dark Green distorted by noise
        if mode == 'Malachite':
            # Warped bands
            warp = math.sin(calc_i * 0.1) * 5
            band = math.sin((h_ratio * 20) + warp)
            return self.lerp_color((0, 100, 50), (100, 230, 150), (band + 1) / 2)

        # --- 291. Liquid Nitrogen (Element) ---
        # Flowing White Mist over Cold Blue
        if mode == 'Liquid Nitrogen':
            mist = math.sin(calc_i * 0.2 + t) + math.sin(h_ratio * 10 - t * 2)
            if mist > 0.5: return (255, 255, 255)  # Fog
            return self.lerp_color((0, 20, 50), (100, 200, 255), h_ratio)

        # --- 292. Retro Wallpaper (70s Design) ---
        # Curved bands of Brown, Orange, and Yellow
        if mode == 'Retro Wallpaper':
            # Curve equation
            curve = math.sin(calc_i * 0.1) * 0.5
            pos = h_ratio + curve
            if pos < 0.33: return (139, 69, 19)  # Brown
            if pos < 0.66: return (255, 140, 0)  # Orange
            return (255, 215, 0)  # Yellow

        # --- 293. Diamond Heist (Luxury) ---
        # Deep Blue Velvet with sharp White/Cyan sparkles
        if mode == 'Diamond Heist':
            # Sparkle logic
            spark = math.pow(math.sin(calc_i * 30 + t * 5), 50)  # Sharp spikes
            if spark > 0.5: return (200, 255, 255)
            return self.lerp_color((0, 0, 20), (0, 0, 80), h_ratio)

        # --- 294. Sushi Platter (Food) ---
        # Salmon Pink, Nori Black, Rice White layers
        if mode == 'Sushi Platter':
            if h_ratio < 0.2: return (245, 245, 245)  # Rice
            if h_ratio < 0.3: return (10, 20, 10)  # Nori
            if h_ratio < 0.7:
                # Salmon fat stripes
                stripe = int(calc_i + h_ratio * 20) % 3
                if stripe == 0: return (255, 200, 180)
                return (250, 128, 114)  # Salmon
            return (0, 0, 0)  # Chopsticks (bg)

        # --- 295. Volcanic Ash (Disaster) ---
        # Falling Grey particles, Red glow from beneath
        if mode == 'Volcanic Ash':
            # Glow from bottom
            glow = self.lerp_color((255, 50, 0), (50, 50, 50), h_ratio * 2)
            # Ash flakes
            noise = (calc_i * 123432 + int(t * 10)) % 17
            if noise == 0: return (150, 150, 150)
            return glow

        # --- 296. Shepard Tone (Illusion) ---
        # Barber pole effect that seems to rise forever
        if mode == 'Shepard Tone':
            # Infinite scrolling pattern
            scroll = (h_ratio * 10 - t) % 1.0
            val_s = int(scroll * 255)
            return (val_s, val_s, val_s)

        # --- 297. Syntax Highlighting (Code) ---
        # Dark Grey BG, colorful keywords based on bar index
        if mode == 'Syntax Highlighting':
            # Simulate code indentation
            indent = (calc_i * 7) % 20
            if h_ratio * 60 < indent: return (30, 30, 30)  # BG

            # Token colors
            token = calc_i % 5
            if token == 0: return (249, 38, 114)  # Pink
            if token == 1: return (166, 226, 46)  # Green
            if token == 2: return (102, 217, 239)  # Blue
            if token == 3: return (253, 151, 31)  # Orange
            return (248, 248, 242)  # White

        # --- 298. Gothic Noir (Cinema) ---
        # High contrast Black and White with Film Grain
        if mode == 'Gothic Noir':
            base = (0, 0, 0) if h_ratio < 0.5 else (200, 200, 200)
            # Grain
            grain = random.randint(-30, 30)
            r = max(0, min(255, base[0] + grain))
            return (r, r, r)

        # --- 299. Radioactive Decay II (Hazard) ---
        # Sickly Yellow/Green interference pattern
        if mode == 'Radioactive Decay II':
            interf = math.sin(calc_i * 0.5) * math.sin(h_ratio * 20)
            if interf > 0: return (200, 255, 0)
            return (50, 50, 0)

        # --- 300. God Mode (Ultimate) ---
        # Rapidly shifting Rainbow + White flashes on beat
        if mode == 'God Mode':
            # Beat flash
            if val > 80: return (255, 255, 255)

            hue = (calc_i * 5 + t * 50) % 360
            c = pygame.Color(0)
            c.hsla = (hue, 100, 50, 100)
            return (c.r, c.g, c.b)

        # Fallback
        return (255, 255, 255)

    def trigger_carousel_switch(self):
        """Prepares the fade transition and loads the next image"""
        folder = self.bg_params.get('carousel_path', "")
        if not folder or not os.path.exists(folder): return

        # Get valid images
        valid_exts = ('.png', '.jpg', '.jpeg', '.bmp')
        images = [f for f in os.listdir(folder) if f.lower().endswith(valid_exts)]

        if not images: return

        # 1. Snapshot current image as "Previous" for the fade out
        if self.bg_original_image:
            self.bg_prev_image = self.bg_original_image
            self.bg_transition_start = time.time()
            self.bg_is_transitioning = True

        # 2. Pick new image
        next_img_name = random.choice(images)
        full_path = os.path.join(folder, next_img_name)

        try:
            self.bg_original_image = pygame.image.load(full_path).convert_alpha()
        except Exception as e:
            print(f"Carousel Load Error: {e}")

    def load_bg_carousel_folder(self):
        """UI Prompt for folder selection"""
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select Image Folder")
        if folder:
            self.bg_params['carousel_path'] = folder
            # Load first image immediately
            self.trigger_carousel_switch()
            # Cancel transition for the very first load so it appears instantly
            self.bg_is_transitioning = False
            self.bg_prev_image = None
        else:
            # If cancelled, revert to None
            self.bg_params['img_enabled'] = 0

    def load_bg_image(self):
        """Loads raw background image or carousel folder"""
        mode = self.bg_params.get('img_enabled', 0)

        # Mode 4 is Carousel
        if mode == 4:
            path = self.bg_params.get('carousel_path', "")
            if not path or not os.path.exists(path):
                self.load_bg_carousel_folder()
            return

        # Standard Single Image
        path = self.bg_params.get('img_path', "")

        if not path or not os.path.exists(path):
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
            if not path:
                self.bg_params['img_enabled'] = 0
                return

        try:
            # Store the ORIGINAL raw image
            self.bg_original_image = pygame.image.load(path).convert_alpha()
            self.bg_params['img_path'] = path
        except Exception as e:
            print(f"Error loading image: {e}")
            self.bg_params['img_enabled'] = 0
            self.bg_original_image = None

    def load_bg_video(self):
        """Loads background video using Threading"""
        path = self.bg_params.get('video_path', "")

        if not path or not os.path.exists(path):
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi *.mkv *.mov")])
            if not path:
                self.bg_params['img_enabled'] = 0
                return

        try:
            if self.video_cap:
                try:
                    self.video_cap.release()
                except:
                    pass

            # Use the new Threaded Class
            self.video_cap = ThreadedVideo(path)
            self.bg_video_fps = self.video_cap.fps

            self.bg_params['video_path'] = path
            self.bg_video_surface_cache = None
        except Exception as e:
            print(f"Error loading video: {e}")
            self.bg_params['img_enabled'] = 0
            self.video_cap = None

    def draw_background(self):
        w, h = self.screen.get_size()

        # Identify active modes (strings)
        mode1 = BG_MODES[self.current_bg_mode]
        mode2 = BG_MODES[self.current_bg_mode_2]

        active_modes_list = []
        if mode1 != 'None': active_modes_list.append(mode1)
        if mode2 != 'None': active_modes_list.append(mode2)

        # --- 1. Draw Base Color (Based ONLY on Layer 1) ---
        if mode1 == 'Solid Dark':
            self.screen.fill((15, 15, 20))
        elif mode1 == 'Deep Space' or mode1 == 'Warp Speed':
            self.screen.fill((5, 5, 10))
        elif mode1 == 'Matrix Rain':
            self.screen.fill((0, 10, 0))
        elif mode1 == 'Fire':
            self.screen.fill((20, 5, 0))
        elif mode1 == 'Fog':
            self.screen.fill((20, 25, 30))
        else:
            self.screen.fill((10, 10, 15))

        # --- 2. CUSTOM BACKGROUND LOGIC ---
        img_mode = self.bg_params.get('img_enabled', 0)

        # Prepare to draw Image (as fallback or primary)
        should_draw_image = False
        should_draw_video = False

        # Calculate Time
        if self.is_dragging_seek:
            total_seconds = (self.current_duration / 2) / RATE
            curr_t = total_seconds * self.drag_progress
        else:
            curr_t = (self.current_offset / 2) / RATE

        # Get Settings
        offset_val = self.bg_params.get('video_offset', 0.0)  # User input offset

        # --- VIDEO LOGIC (Modes 2 & 3) ---
        if img_mode in [2, 3]:
            if self.video_cap is None: self.load_bg_video()

            if self.video_cap and self.video_cap.running:
                # Calculated Video Time
                video_time_ptr = curr_t - offset_val

                # Bounds Check
                if 0 <= video_time_ptr <= self.video_cap.duration:
                    should_draw_video = True

                    if not self.paused:
                        # 1. SYNC: Tell the thread where we are.
                        # This allows the thread to skip frames internally if it lags.
                        self.video_cap.sync(video_time_ptr)

                        # 2. RETRIEVE: Get best frame
                        frame_info = self.video_cap.get_frame(video_time_ptr)

                        if frame_info is not None and frame_info[0] is not None:
                            data, shape = frame_info
                            h_frame, w_frame = shape

                            self.bg_video_surface_cache = pygame.image.frombuffer(
                                data, (w_frame, h_frame), "RGB"
                            )
                else:
                    should_draw_video = False

        # --- DRAW VIDEO ---
        if should_draw_video and self.bg_video_surface_cache:
            vid_surf = self.bg_video_surface_cache

            # Apply Video Opacity
            vid_op = self.bg_params.get('video_opacity', 1.0)
            if vid_op < 0.99:
                vid_surf.set_alpha(int(vid_op * 255))
            else:
                vid_surf.set_alpha(255)

            # Apply X/Y Positioning
            off_x = self.bg_params.get('video_pos_x', 0.0) * 600
            off_y = self.bg_params.get('video_pos_y', 0.0) * 600
            center_pos = (w // 2 + int(off_x), h // 2 + int(off_y))

            vr = vid_surf.get_rect(center=center_pos)

            # Simple fit check
            if vr.width != w and vr.height != h:
                vid_surf = pygame.transform.scale(vid_surf, (w, h))
                vr = vid_surf.get_rect(center=center_pos)

            self.screen.blit(vid_surf, vr)
        else:
            # Fallback trigger: If Mode 2 (Video Only) but video is out of bounds/invalid, show image?
            # Or if Mode 3 (Dual) and video is valid, do we blend?
            # Per request: "Video disappears and is reappeared with selected image"
            if img_mode == 2 and not should_draw_video:
                should_draw_image = True  # Fallback for Video Only mode
            elif img_mode == 3:
                # Mode 3 Logic: Show Image if Video not playing, OR blend if desired.
                # Currently simplified to: Show Video if valid, else Show Image.
                if not should_draw_video:
                    should_draw_image = True

        # --- DRAW IMAGE (Mode 1, Mode 4, or Fallback for 2/3) ---
        if img_mode == 1 or img_mode == 4: should_draw_image = True

        if should_draw_image:
            # Check for missing assets based on mode
            if img_mode == 4 and not self.bg_params.get('carousel_path'):
                self.load_bg_image()  # This will trigger folder select
            elif img_mode != 4 and self.bg_original_image is None and self.bg_params.get('img_path'):
                self.load_bg_image()

            # --- TRANSITION LOGIC ---
            # Helper to process and draw a specific image surface
            def process_and_draw(img_surf, alpha_override=None):
                user_opacity = self.bg_params.get('img_opacity', 0.5)
                # Combine user opacity with fade transition alpha
                final_opacity = user_opacity if alpha_override is None else (user_opacity * alpha_override)

                pulse = self.bg_params.get('img_pulse_scale', 0.05)
                bright = self.bg_params.get('img_bright', 0.0) * 100
                anim = BG_IMAGE_ANIMS[self.bg_params.get('img_anim', 0)]

                iw, ih = img_surf.get_size()
                # --- FIX START: CYCLIC BOUNDARY AWARENESS ---
                # The movement amplitude used later (currently hardcoded to 30)
                cycle_amp = 30.0

                # Determine required coverage dimensions
                req_w = w
                req_h = h

                # If Cyclic, the image must be taller/wider by 2x the amplitude
                # to prevent black bars appearing during movement.
                if anim == 'Cyclic':
                    req_h += (cycle_amp * 2)
                    # If you ever add horizontal movement, uncomment the line below:
                    # req_w += (cycle_amp * 2)

                # Calculate scale to cover the largest requirement while keeping aspect ratio
                scale = max(req_w / iw, req_h / ih)
                # --- FIX END ---

                if anim == 'Pulse': scale += (self.current_energy * pulse)

                nw, nh = int(iw * scale), int(ih * scale)
                # Optimization: Only scale if needed
                draw_img = pygame.transform.scale(img_surf, (nw, nh))

                if bright > 0:
                    overlay = pygame.Surface(draw_img.get_size(), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, int(min(255, bright * 2.5))))
                    draw_img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

                draw_img.set_alpha(int(final_opacity * 255))
                r = draw_img.get_rect(center=(w // 2, h // 2))
                # --- UPDATE MOVEMENT TO USE VARIABLE ---
                if anim == 'Cyclic':
                    r.centery += math.sin(time.time() * 0.5) * cycle_amp
                self.screen.blit(draw_img, r)

            # 1. Check Fade State
            if self.bg_is_transitioning:
                now = time.time()
                dur = max(0.01, self.bg_params.get('carousel_fade', 2.0))
                elapsed = now - self.bg_transition_start
                progress = elapsed / dur

                if progress >= 1.0:
                    # Transition Done
                    self.bg_is_transitioning = False
                    self.bg_prev_image = None
                    if self.bg_original_image:
                        process_and_draw(self.bg_original_image, alpha_override=1.0)
                else:
                    # Draw Previous (Fading Out)
                    # CHANGE: We fade this out using (1.0 - progress) so it disappears smoothly
                    if self.bg_prev_image:
                        process_and_draw(self.bg_prev_image, alpha_override=(1.0 - progress))

                    # Draw New (Fading In)
                    if self.bg_original_image:
                        process_and_draw(self.bg_original_image, alpha_override=progress)
            else:
                # Normal Static Draw
                if self.bg_original_image:
                    process_and_draw(self.bg_original_image)

        # --- 3. Draw Particles (Overlay) ---
        # Determine max particles based on mode
        max_p = int(self.bg_params.get('max_particles', 1500))

        # OPTIMIZATION: Radial mode uses heavy geometry.
        # Reduce particles to prevent Main Thread saturation.
        if VISUAL_MODES[self.current_visual_mode] == 'Radial':
            max_p = min(max_p, 300)

        if 'Fog' in active_modes_list: max_p = 25  # Fog needs fewer, larger particles

        # Trim particles if slider is lowered
        if len(self.particles) > max_p:
            self.particles = self.particles[:max_p]

        if len(self.particles) < max_p:
            # FIX: Explicitly block particles for None AND Solid Dark
            # Mode 1 (Solid Dark) should not spawn particles
            if mode1 not in ['None', 'Solid Dark']:
                self.particles.append(Particle(w, h, mode1))
            if mode2 not in ['None', 'Solid Dark']:
                self.particles.append(Particle(w, h, mode2))

        if active_modes_list:
            # Filter out particles not in current modes
            active = [p for p in self.particles if p.mode in active_modes_list]
            # Optimization: Don't reassign list every frame if length matches
            if len(active) != len(self.particles): self.particles = active

            for p in self.particles:
                p.update(self.current_energy, self.bg_params, w, h)
                p.draw(self.screen, self.bg_params)
        else:
            self.particles = []

    def draw_visuals(self, fft_data):
        num = len(fft_data)
        if num == 0: return
        w, h = self.screen.get_size()
        vis_h = h - self.ui_panel_height
        cx, cy = w // 2, vis_h // 2
        mode = VISUAL_MODES[self.current_visual_mode]
        bw = w / num

        # --- INJECT PHYSICS STATE ---
        if not hasattr(self, 'wave_impulse'):
            self.wave_impulse = 0.0

        # Initialize peak heights
        if len(self.peak_heights) != num:
            self.peak_heights = np.zeros(num)

        # Extract Params
        current_params = self.vis_params_sets[mode]
        p_thick_raw = current_params['thick']
        p_len = current_params['length']
        p_size = current_params['size']
        p_jit = current_params['jitter'] * 20
        p_rate = current_params['rate']
        p_thresh = current_params.get('threshold', 0.5)
        # Get thickness once per frame (not per bar)
        p_hollow_thk = current_params.get('hollow_thick', 1.0)
        show_line = current_params.get('show_line', True)

        # --- NEW: NOISE RECEPTION (GATE) LOGIC ---
        # Reduces jitter by cutting off frequencies below the user-defined slider
        p_noise_gate = current_params.get('noise_gate', 0.15)
        if p_noise_gate > 0:
            # Calculate cut-off (Scaling factor 30 is arbitrary based on typical FFT magnitude)
            gate_val = p_noise_gate * 30.0
            # Subtract gate value, but keep it non-negative
            fft_data = np.maximum(0, fft_data - gate_val)

        # --- 1. APPLY SORTING ---
        sort_mode_name = SORT_MODES[self.current_sort_mode]
        sorted_data = np.zeros(num)

        # Pre-calculate Bass Kick (used for scaling later)
        bass_kick = np.mean(fft_data[:4]) if len(fft_data) > 4 else 0

        if sort_mode_name == 'Bass & Melody':
            mid = num // 2
            bass_limit = 12
            if num > bass_limit:
                bass_core = fft_data[:bass_limit]
                melody_core = fft_data[bass_limit:]
                b_len = len(bass_core)
                b_mid = b_len // 2
                sorted_data[mid - b_mid: mid - b_mid + b_len: 2] = bass_core[::-1][::2]
                sorted_data[mid - b_mid + 1: mid - b_mid + b_len: 2] = bass_core[::2]
                start_b = mid - b_mid
                left_end = start_b
                if left_end > 0:
                    l_data = melody_core[1::2]
                    lim = min(len(l_data), left_end)
                    sorted_data[left_end - lim: left_end] = l_data[:lim][::-1]
                r_start = start_b + b_len
                if r_start < num:
                    r_data = melody_core[0::2]
                    lim = min(len(r_data), num - r_start)
                    sorted_data[r_start: r_start + lim] = r_data[:lim]
                fft_data = sorted_data
            else:
                sorted_data[mid:] = fft_data[0::2]
                sorted_data[:mid] = fft_data[1::2][::-1]
                fft_data = sorted_data

        elif sort_mode_name == 'Order: Pyramid (Center)':
            # Sort by HEIGHT (Magnitude) -> Loudest in Center
            # 1. Sort the raw data (Small -> Large)
            s = np.sort(fft_data)

            # 2. Distribute to create a pyramid
            # Evens go Left (Ascending), Odds go Right (Descending)
            left_side = s[::2]  # [0, 2, 4...] (Ascending)
            right_side = s[1::2][::-1]  # [..., 5, 3, 1] (Descending)

            # 3. Combine
            lim_l = len(left_side)
            sorted_data[:lim_l] = left_side
            sorted_data[lim_l:] = right_side
            fft_data = sorted_data

        elif sort_mode_name == 'Order: Valley (Edges)':
            # Sort by HEIGHT (Magnitude) -> Loudest at Edges
            # 1. Sort the raw data (Large -> Small)
            s = np.sort(fft_data)[::-1]

            # 2. Distribute to create a valley
            # Evens go Left (Descending), Odds go Right (Ascending)
            left_side = s[::2]  # [Largest, 3rd Largest...]
            right_side = s[1::2][::-1]  # [..., 4th Largest, 2nd Largest]

            # 3. Combine
            lim_l = len(left_side)
            sorted_data[:lim_l] = left_side
            sorted_data[lim_l:] = right_side
            fft_data = sorted_data

        elif sort_mode_name == 'Experimental Bass & Melody':
            # --- DUAL INWARD FLOW (EDGES -> CENTER) ---

            # 1. Define Half-Screen Size
            half_num = (num // 2) + (num % 2)

            # 2. Initialize Half-Buffer for Physics
            if not hasattr(self, 'wave_history_half') or len(self.wave_history_half) != half_num:
                self.wave_history_half = np.zeros(half_num)

            # 3. Calculate Impulse (Bass Energy)
            bass_raw = np.mean(fft_data[:5]) if len(fft_data) > 0 else 0

            # Soft Threshold / Gate
            gate_val = p_thresh * 50.0
            impulse = max(0, bass_raw - gate_val)

            # 4. Propagate Wave (Physics Step)
            self.wave_history_half[1:] = self.wave_history_half[:-1] * 0.90

            # --- FIX 1: Increase Impulse Multiplier ---
            # Old: (impulse * 0.8) -> Resulted in lower center peaks
            # New: (impulse * 1.2) -> Matches the height of other bass-heavy modes
            self.wave_history_half[0] = (self.wave_history_half[0] * 0.3) + (impulse * 1.2)

            # 5. Construct the Full Screen Waves (Mirroring)
            physics_wave = np.zeros(num)
            physics_wave[:half_num] = self.wave_history_half
            physics_wave[num - half_num:] = self.wave_history_half[::-1]

            # 6. Sort Raw FFT Data
            sorted_data = np.zeros(num)
            left_src = fft_data[0::2]
            right_src = fft_data[1::2]
            l_lim = min(len(left_src), half_num)
            sorted_data[:l_lim] = left_src[:l_lim]
            r_lim = min(len(right_src), num - half_num)
            sorted_data[num - r_lim:] = right_src[:r_lim][::-1]

            # --- FIX 2: Remove Dampening on Raw Data ---
            # Old: sorted_data * 0.5 -> Cut melody height in half
            # New: sorted_data       -> Full height
            fft_data = np.maximum(physics_wave, sorted_data)

            # Apply horizontal smoothing
            if num > 2:
                fft_data[1:-1] = (fft_data[:-2] + fft_data[1:-1] + fft_data[2:]) / 3.0

        elif sort_mode_name == 'Experimental Outward':
            # --- DUAL OUTWARD FLOW (CENTER -> EDGES) ---

            # 1. Define Half-Screen Size
            half_num = (num // 2) + (num % 2)

            # 2. Initialize Half-Buffer for Physics
            if not hasattr(self, 'wave_history_half') or len(self.wave_history_half) != half_num:
                self.wave_history_half = np.zeros(half_num)

            # 3. Calculate Impulse (Bass Energy)
            bass_raw = np.mean(fft_data[:5]) if len(fft_data) > 0 else 0
            gate_val = p_thresh * 50.0
            impulse = max(0, bass_raw - gate_val)

            # 4. Propagate Wave (Physics Step)
            self.wave_history_half[1:] = self.wave_history_half[:-1] * 0.90
            self.wave_history_half[0] = (self.wave_history_half[0] * 0.3) + (impulse * 1.2)

            # 5. Construct the Full Screen Waves
            # FLIPPED: Index 0 (High Energy) goes to the Center
            physics_wave = np.zeros(num)

            # Left Side: Reversed so index 0 touches the center
            physics_wave[:half_num] = self.wave_history_half[::-1]

            # Right Side: Normal so index 0 touches the center
            physics_wave[num - half_num:] = self.wave_history_half

            # 6. Sort Raw FFT Data
            # FLIPPED: Low frequencies (index 0) go to the Center
            sorted_data = np.zeros(num)
            left_src = fft_data[0::2]
            right_src = fft_data[1::2]

            l_lim = min(len(left_src), half_num)
            # Reverse left side so low freqs are at the right (center of screen)
            sorted_data[:l_lim] = left_src[:l_lim][::-1]

            r_lim = min(len(right_src), num - half_num)
            # Keep right side normal so low freqs are at the left (center of screen)
            sorted_data[num - r_lim:] = right_src[:r_lim]

            # 7. Combine
            fft_data = np.maximum(physics_wave, sorted_data)

            # Apply horizontal smoothing
            if num > 2:
                fft_data[1:-1] = (fft_data[:-2] + fft_data[1:-1] + fft_data[2:]) / 3.0

        elif sort_mode_name == 'Experimental Bass & Melody (Left-Right)':
            # --- FLOW (LEFT -> RIGHT) ---
            # Bass (Index 0) on Left, Treble on Right.

            # 1. Initialize Full Buffer for Physics
            if not hasattr(self, 'wave_history_full') or len(self.wave_history_full) != num:
                self.wave_history_full = np.zeros(num)

            # 2. Calculate Impulse (Bass Energy)
            bass_raw = np.mean(fft_data[:5]) if len(fft_data) > 0 else 0
            gate_val = p_thresh * 50.0
            impulse = max(0, bass_raw - gate_val)

            # 3. Propagate Wave (Rightward)
            # Shift everything to the right
            self.wave_history_full[1:] = self.wave_history_full[:-1] * 0.90
            # Inject new impulse at Left (Index 0)
            self.wave_history_full[0] = (self.wave_history_full[0] * 0.3) + (impulse * 1.2)

            # 4. Combine Physics with Raw Data
            # fft_data is already Low->High (Left->Right), so we use it directly
            fft_data = np.maximum(self.wave_history_full, fft_data)

            # 5. Apply horizontal smoothing
            if num > 2:
                fft_data[1:-1] = (fft_data[:-2] + fft_data[1:-1] + fft_data[2:]) / 3.0

        elif sort_mode_name == 'Experimental Bass & Melody (Right-Left)':
            # --- FLOW (RIGHT -> LEFT) ---
            # Bass (Index -1) on Right, Treble on Left.

            # 1. Initialize Full Buffer for Physics
            if not hasattr(self, 'wave_history_full') or len(self.wave_history_full) != num:
                self.wave_history_full = np.zeros(num)

            # 2. Calculate Impulse (Bass Energy)
            bass_raw = np.mean(fft_data[:5]) if len(fft_data) > 0 else 0
            gate_val = p_thresh * 50.0
            impulse = max(0, bass_raw - gate_val)

            # 3. Propagate Wave (Leftward)
            # Shift everything to the left
            self.wave_history_full[:-1] = self.wave_history_full[1:] * 0.90
            # Inject new impulse at Right (Last Index)
            self.wave_history_full[-1] = (self.wave_history_full[-1] * 0.3) + (impulse * 1.2)

            # 4. Combine Physics with Raw Data
            # Reverse fft_data so Low Freqs are at the Right
            fft_data = np.maximum(self.wave_history_full, fft_data[::-1])

            # 5. Apply horizontal smoothing
            if num > 2:
                fft_data[1:-1] = (fft_data[:-2] + fft_data[1:-1] + fft_data[2:]) / 3.0

        p_thick = max(1, int(p_thick_raw * 2))
        if mode == 'Radial':
            p_thick = max(1, int(p_thick_raw * 4))
        elif mode == 'Waveform':
            p_thick = max(1, int(p_thick_raw * 1.5))

        jit_x = random.uniform(-p_jit, p_jit) if p_jit > 0 else 0
        jit_y = random.uniform(-p_jit, p_jit) if p_jit > 0 else 0

        # --- WAVEFORM MODE ---
        if mode == 'Waveform':
            points = []
            main_col = self.get_bar_color(50, num // 2, num)
            for i, db in enumerate(fft_data):
                h_val = db * 8 * p_len
                points.append((i * bw + jit_x, vis_h - h_val + jit_y))
            if len(points) > 1:
                pygame.draw.lines(self.screen, main_col, False, points, p_thick)
            return

        # --- SETUP HEIGHT SCALING ---
        vis_h_scale = (vis_h / 80) * 2.5 * p_len

        # --- PULSE LOGIC ---
        if sort_mode_name == 'Experimental Bass & Melody':
            # Since Impulse handles the height, we only apply a small thickness pulse
            if bass_kick > 20:
                p_thick = int(p_thick * (1.0 + (bass_kick / 150.0)))
        else:
            # Standard pulse for other modes
            if bass_kick > 30:
                vis_h_scale *= (1.0 + ((bass_kick - 30) / 100.0))

        for i, db in enumerate(fft_data):
            bar_h = db * vis_h_scale

            if bar_h < 1:
                bar_h = 1
            elif bar_h > vis_h - 10:
                bar_h = vis_h - 10

            # Check Idle Mode Logic
            idle_idx = current_params.get('idle_mode', 0)

            # If bar is at minimum height (flat)
            if bar_h <= 1.0:
                if idle_idx == 1:  # Disappear
                    continue  # Skip drawing this bar completely
                elif idle_idx == 2:  # Match Dock Color
                    # Get the same color used for the dock divider
                    col = self.get_bar_color(50, 0, 10)
                else:
                    # Original behavior: calculate standard color
                    col = self.get_bar_color(bar_h, i, num)
            else:
                # Standard behavior for active bars
                col = self.get_bar_color(bar_h, i, num)

            if bar_h >= self.peak_heights[i]:
                self.peak_heights[i] = bar_h
            else:
                self.peak_heights[i] -= 2.0
            ph = self.peak_heights[i]

            b_jit_x = random.uniform(-p_jit, p_jit) if p_jit > 0 else 0
            b_jit_y = random.uniform(-p_jit, p_jit) if p_jit > 0 else 0

            # --- LINEAR VARIANTS WITH TEXTURE SUPPORT ---
            if 'Linear' in mode:
                x_pos = int(i * bw + b_jit_x)
                width_ratio = 0.95 if p_thick_raw > 1.2 else min(0.9, p_thick_raw * 0.8)
                draw_w = max(1, int(bw * width_ratio))

                # Rectangle Definitions
                rect_y = vis_h - bar_h + b_jit_y
                full_rect = (x_pos, rect_y, draw_w, bar_h)

                # Get Texture Mode
                style = BAR_STYLES[self.current_bar_style]

                # --- CALCULATE HOLLOW THICKNESS (APPLIES TO ALL SHAPES) ---
                # 1. Get Slider Value
                p_hollow_thk = current_params.get('hollow_thick', 1.0)

                # 2. Calculate Pixel Width based on Style
                line_width = 0  # Default 0 = Fill

                if style == 'Hollow (1px)':
                    # Use slider as raw pixels (1 to 8)
                    line_width = int(p_hollow_thk)

                elif style == 'Hollow (Thick)':
                    # Use slider as multiplier relative to bar width
                    base = max(2, int(draw_w * 0.2))
                    line_width = int(base * p_hollow_thk)

                # 3. Safety: Ensure we don't error out if width is 0 or negative
                if line_width < 1: line_width = 1

                # Helper to draw the bar based on shape
                if mode == 'Linear':
                    # --- ARTISTIC TEXTURE RENDERING ---
                    if style == 'Solid':
                        pygame.draw.rect(self.screen, col, full_rect)

                    elif style == 'Border (White)':
                        pygame.draw.rect(self.screen, col, full_rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), full_rect, width=1)

                    elif style == 'Border (Theme)':
                        # Darken the inside
                        dark_col = (col[0] // 4, col[1] // 4, col[2] // 4)
                        pygame.draw.rect(self.screen, dark_col, full_rect)
                        pygame.draw.rect(self.screen, col, full_rect, width=2)

                    elif style == 'Hollow (1px)':
                        # Use slider as exact pixels (1 to 8)
                        thk = int(p_hollow_thk)
                        # Only clamp if it would completely crash Pygame (width > radius)
                        # We allow it to fill the bar if thickness is high
                        if thk >= draw_w // 2:
                            pygame.draw.rect(self.screen, col, full_rect)  # Fill if too thick
                        else:
                            pygame.draw.rect(self.screen, col, full_rect, width=thk)

                    elif style == 'Hollow (Thick)':
                        # Use slider as multiplier
                        # Base thickness is 20% of width
                        base = max(2, int(draw_w * 0.2))
                        thk = int(base * p_hollow_thk)

                        if thk >= draw_w // 2:
                            pygame.draw.rect(self.screen, col, full_rect)  # Fill if too thick
                        else:
                            pygame.draw.rect(self.screen, col, full_rect, width=thk)

                    elif style == 'Horizontal Line (Center)':
                        # Just a line in the vertical center of the bar's potential height
                        # Or a line floating at the top? Let's do floating line
                        pygame.draw.rect(self.screen, col, (x_pos, rect_y, draw_w, 4))
                        # And a line in the middle of the volume
                        mid_y = rect_y + (bar_h / 2)
                        pygame.draw.line(self.screen, col, (x_pos, mid_y), (x_pos + draw_w, mid_y), 2)

                    elif style == 'Horizontal Line (Double)':
                        pygame.draw.rect(self.screen, col, full_rect, width=1)
                        # Two horizontal lines cutting through
                        y1 = rect_y + (bar_h * 0.33)
                        y2 = rect_y + (bar_h * 0.66)
                        # Use 'col' instead of white
                        pygame.draw.line(self.screen, col, (x_pos, y1), (x_pos + draw_w, y1), 1)
                        pygame.draw.line(self.screen, col, (x_pos, y2), (x_pos + draw_w, y2), 1)

                    elif style == 'Segmented (Blocks)':
                        # Break into blocks
                        block_h = max(4, int(draw_w))
                        curr_y = rect_y
                        while curr_y < rect_y + bar_h:
                            pygame.draw.rect(self.screen, col, (x_pos, curr_y, draw_w, block_h - 1))
                            curr_y += block_h

                    elif style == 'Crossed':
                        pygame.draw.rect(self.screen, col, full_rect, width=1)
                        pygame.draw.line(self.screen, col, (x_pos, rect_y), (x_pos + draw_w, rect_y + bar_h), 1)
                        pygame.draw.line(self.screen, col, (x_pos + draw_w, rect_y), (x_pos, rect_y + bar_h), 1)

                    elif style == 'Gradient Fill':
                        # Simulated gradient by drawing lines with decreasing brightness
                        steps = 10
                        step_h = bar_h / steps
                        for s in range(steps):
                            fade = 1.0 - (s / steps)
                            c = (int(col[0] * fade), int(col[1] * fade), int(col[2] * fade))
                            pygame.draw.rect(self.screen, c, (x_pos, rect_y + (s * step_h), draw_w, step_h + 1))

                    elif style == 'Inverted Fill':
                        # Calculate the "Base" color (Volume = 0)
                        base_col = self.get_bar_color(0, i, num)

                        # Calculate difference between the active bar color and the base color
                        diff = sum([abs(col[k] - base_col[k]) for k in range(3)])

                        # If colors are distinct (Dual Color/Gradient themes), use base color.
                        # If they are the same (Single Color themes), default to Black.
                        fill_col = base_col if diff > 40 else (10, 10, 10)

                        pygame.draw.rect(self.screen, fill_col, full_rect)
                        pygame.draw.line(self.screen, col, (x_pos, rect_y), (x_pos + draw_w, rect_y), 3)
                        pygame.draw.rect(self.screen, col, full_rect, width=1)
                elif mode == 'Linear (Pointy)':
                    pts = [(x_pos, vis_h + b_jit_y), (x_pos + draw_w, vis_h + b_jit_y),
                           (x_pos + draw_w // 2, vis_h - bar_h + b_jit_y)]

                    if 'Hollow' in style:
                        # Use calculated line_width
                        # Note: Polygon width behaves differently than rect, usually safer
                        pygame.draw.polygon(self.screen, col, pts, width=line_width)
                    else:
                        pygame.draw.polygon(self.screen, col, pts)
                elif mode == 'Linear (Round)':
                    rad = min(draw_w // 2, int(bar_h // 2))
                    if rad < 1: rad = 1

                    if 'Hollow' in style:
                        # Safety: For rounded rects, width cannot be >= radius in some pygame versions
                        # or it looks ugly. We clamp it.
                        safe_width = min(line_width, rad)

                        # If the line is so thick it fills the radius, just fill it
                        if safe_width >= rad:
                            pygame.draw.rect(self.screen, col, full_rect, border_radius=rad)
                        else:
                            pygame.draw.rect(self.screen, col, full_rect, border_radius=rad, width=safe_width)
                    else:
                        pygame.draw.rect(self.screen, col, full_rect, border_radius=rad)
                elif mode == 'Linear (Blocks)':
                    block_h = max(4, int(draw_w * 0.8))
                    gap = 2
                    current_y = vis_h - block_h
                    while current_y > vis_h - bar_h:
                        pygame.draw.rect(self.screen, col, (x_pos, current_y + b_jit_y, draw_w, block_h))
                        current_y -= (block_h + gap)
                elif mode == 'Linear (Needle)':
                    center_x = x_pos + draw_w // 2
                    pygame.draw.line(self.screen, col, (center_x, vis_h), (center_x, vis_h - bar_h), 2)
                    pygame.draw.circle(self.screen, col, (center_x, int(vis_h - bar_h)), int(draw_w // 2))

                if show_line:
                    pygame.draw.rect(self.screen, (255, 255, 255), (x_pos, vis_h - ph - 2 + b_jit_y, draw_w, 2))

            elif mode == 'Reflex':
                draw_w = max(1, int(bw * p_thick_raw - 1))
                x_pos = int(i * bw + b_jit_x)

                # --- STYLE CALCULATIONS ---
                style = BAR_STYLES[self.current_bar_style]

                # Calculate Line Width (Shared logic with Linear)
                line_width = 1
                if style == 'Hollow (1px)':
                    line_width = int(p_hollow_thk)
                elif style == 'Hollow (Thick)':
                    base = max(2, int(draw_w * 0.2))
                    line_width = int(base * p_hollow_thk)
                if line_width < 1: line_width = 1

                # --- REFLEX RECTANGLES ---
                # 1. Main Bar (Centered on Vertical Axis)
                rect_main = pygame.Rect(x_pos, cy - bar_h / 2 + b_jit_y, draw_w, bar_h)
                # 2. Reflection (Below Main Bar)
                rect_refl = pygame.Rect(x_pos, cy + bar_h / 2 + b_jit_y, draw_w, bar_h)

                dim_col = (col[0] // 4, col[1] // 4, col[2] // 4)

                # Iterate to draw both Main and Reflection with textures
                for full_rect, draw_col in [(rect_main, col), (rect_refl, dim_col)]:
                    rect_y = full_rect.y

                    # --- TEXTURE RENDERING (Adapted from Linear) ---
                    if style == 'Solid':
                        pygame.draw.rect(self.screen, draw_col, full_rect)

                    elif style == 'Border (White)':
                        pygame.draw.rect(self.screen, draw_col, full_rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), full_rect, width=1)

                    elif style == 'Border (Theme)':
                        dark_c = (draw_col[0] // 4, draw_col[1] // 4, draw_col[2] // 4)
                        pygame.draw.rect(self.screen, dark_c, full_rect)
                        pygame.draw.rect(self.screen, draw_col, full_rect, width=2)

                    elif style == 'Hollow (1px)' or style == 'Hollow (Thick)':
                        # Fill if too thick for the width
                        if line_width >= draw_w // 2:
                            pygame.draw.rect(self.screen, draw_col, full_rect)
                        else:
                            pygame.draw.rect(self.screen, draw_col, full_rect, width=line_width)

                    elif style == 'Horizontal Line (Center)':
                        # Top floating line
                        pygame.draw.rect(self.screen, draw_col, (x_pos, rect_y, draw_w, 4))
                        # Middle line
                        mid_y = rect_y + (bar_h / 2)
                        pygame.draw.line(self.screen, draw_col, (x_pos, mid_y), (x_pos + draw_w, mid_y), 2)

                    elif style == 'Horizontal Line (Double)':
                        pygame.draw.rect(self.screen, draw_col, full_rect, width=1)
                        y1 = rect_y + (bar_h * 0.33)
                        y2 = rect_y + (bar_h * 0.66)
                        pygame.draw.line(self.screen, draw_col, (x_pos, y1), (x_pos + draw_w, y1), 1)
                        pygame.draw.line(self.screen, draw_col, (x_pos, y2), (x_pos + draw_w, y2), 1)

                    elif style == 'Segmented (Blocks)':
                        block_h = max(4, int(draw_w))
                        curr_y = rect_y
                        # Ensure we don't draw past the rectangle height
                        while curr_y < rect_y + bar_h:
                            draw_h = min(block_h - 1, (rect_y + bar_h) - curr_y)
                            if draw_h > 0:
                                pygame.draw.rect(self.screen, draw_col, (x_pos, curr_y, draw_w, draw_h))
                            curr_y += block_h

                    elif style == 'Crossed':
                        pygame.draw.rect(self.screen, draw_col, full_rect, width=1)
                        pygame.draw.line(self.screen, draw_col, (x_pos, rect_y), (x_pos + draw_w, rect_y + bar_h), 1)
                        pygame.draw.line(self.screen, draw_col, (x_pos + draw_w, rect_y), (x_pos, rect_y + bar_h), 1)

                    elif style == 'Gradient Fill':
                        steps = 10
                        step_h = bar_h / steps
                        for s in range(steps):
                            fade = 1.0 - (s / steps)
                            c = (int(draw_col[0] * fade), int(draw_col[1] * fade), int(draw_col[2] * fade))
                            # Clamp height to fit
                            this_y = rect_y + (s * step_h)
                            if this_y < rect_y + bar_h:
                                pygame.draw.rect(self.screen, c, (x_pos, this_y, draw_w, step_h + 1))

                    elif style == 'Inverted Fill':
                        # Calculate Base color (Volume = 0)
                        base_col = self.get_bar_color(0, i, num)
                        # If drawing reflection, dim the base color too
                        if draw_col == dim_col:
                            base_col = (base_col[0] // 4, base_col[1] // 4, base_col[2] // 4)

                        diff = sum([abs(draw_col[k] - base_col[k]) for k in range(3)])
                        fill_col = base_col if diff > 40 else (10, 10, 10)

                        pygame.draw.rect(self.screen, fill_col, full_rect)
                        pygame.draw.line(self.screen, draw_col, (x_pos, rect_y), (x_pos + draw_w, rect_y), 3)
                        pygame.draw.rect(self.screen, draw_col, full_rect, width=1)

            elif mode == 'Radial':
                # --- "QUANTUM FLUX REACTOR" (LUT + MATRIX MATH OPTIMIZED) ---

                # 1. Dynamics
                bass_pulse = bass_kick * 1.0 * p_size
                base_radius = (45 * p_size) + (bass_pulse * 0.4)

                t = pygame.time.get_ticks()
                # Only calculate rotation scalars once per frame
                rot_base = t * 0.0005 * p_rate
                rot_geo = t * 0.001

                # Rotation Matrix Scalars (The only trig needed this frame)
                rc = math.cos(rot_base)
                rs = math.sin(rot_base)

                # 2. Lookup Table Management (Run once on startup or resize)
                if self.rad_lut_num != num:
                    self.rad_lut_num = num
                    # Pre-calculate Unit Vectors at rotation 0
                    idx = np.arange(num)
                    base_angles = idx * ((2 * math.pi) / num)
                    self.rad_lut_cos = np.cos(base_angles)
                    self.rad_lut_sin = np.sin(base_angles)
                    self.rad_lut_indices = idx

                    # Pre-allocate point buffer (N, 2) to avoid memory churn
                    # We make it 3x size to hold shell, mid, and total points if needed,
                    # but separate arrays are cleaner for readability.
                    pass

                # 3. MATRIX ROTATION (Superfast)
                # Apply rotation matrix to the static LUT
                # New_Cos = Old_Cos * cos(r) - Old_Sin * sin(r)
                # New_Sin = Old_Cos * sin(r) + Old_Sin * cos(r)
                # This replaces np.cos(array) entirely with multiplication
                cos_a = self.rad_lut_cos * rc - self.rad_lut_sin * rs
                sin_a = self.rad_lut_cos * rs + self.rad_lut_sin * rc

                # 4. Radii Math
                vis_scale_local = vis_h_scale * 0.5
                r_mid = base_radius + (fft_data * vis_scale_local * 0.5)
                r_total = base_radius + (fft_data * vis_scale_local)
                r_shell = r_total + 15 + (fft_data * 1.5) + (bass_pulse * 0.2)

                # 5. Coordinate Calculation (Float ops)
                # Center + Direction * Radius
                x_mid = cx + cos_a * r_mid
                y_mid = cy + sin_a * r_mid
                x_tot = cx + cos_a * r_total
                y_tot = cy + sin_a * r_total
                x_shl = cx + cos_a * r_shell
                y_shl = cy + sin_a * r_shell

                # 6. Colors
                # (Optimized color extraction kept from previous step)
                theme_c = self.get_bar_color(100, 0, num)
                try:
                    c_obj = pygame.Color(theme_c)
                    h, s, l, a = c_obj.hsla
                    sec_c = pygame.Color(0);
                    sec_c.hsla = ((h + 40) % 360, s, max(60, l), 100)
                    sec_c = (sec_c.r, sec_c.g, sec_c.b)
                    ter_c = pygame.Color(0);
                    ter_c.hsla = ((h - 20) % 360, s, max(20, l * 0.4), 100)
                    ter_c = (ter_c.r, ter_c.g, ter_c.b)
                except:
                    sec_c = ter_c = theme_c

                # 7. RENDER STACK

                # A. Spokes (Masking Optimization)
                spoke_step = max(1, num // 24)

                # Slicing is virtually free in NumPy
                # We slice the pre-calculated arrays directly
                spoke_vols = fft_data[::spoke_step]

                # Boolean mask: Where volume > 2.0
                mask = spoke_vols > 2.0

                if np.any(mask):
                    # Apply mask to the SLICED arrays (not the full arrays)
                    # This dramatically reduces data handling
                    s_indices = self.rad_lut_indices[::spoke_step][mask]

                    # We need to fetch the actual coordinates for these specific indices
                    # Using integer indexing on numpy arrays is fast
                    s_xm = x_mid[s_indices].astype(np.int32)
                    s_ym = y_mid[s_indices].astype(np.int32)
                    s_xt = x_tot[s_indices].astype(np.int32)
                    s_yt = y_tot[s_indices].astype(np.int32)
                    s_xs = x_shl[s_indices].astype(np.int32)
                    s_ys = y_shl[s_indices].astype(np.int32)

                    # Mask Inner Points calculation
                    r_mask_spoke = base_radius - 5
                    s_cos = cos_a[s_indices]
                    s_sin = sin_a[s_indices]
                    s_x_in = (cx + s_cos * r_mask_spoke).astype(np.int32)
                    s_y_in = (cy + s_sin * r_mask_spoke).astype(np.int32)

                    # Tight drawing loop over only active spokes
                    for k in range(len(s_indices)):
                        pygame.draw.line(self.screen, ter_c, (s_x_in[k], s_y_in[k]), (s_xm[k], s_ym[k]), 1)
                        pygame.draw.line(self.screen, sec_c, (s_xm[k], s_ym[k]), (s_xt[k], s_yt[k]), 1)
                        pygame.draw.line(self.screen, sec_c, (s_xt[k], s_yt[k]), (s_xs[k], s_ys[k]), 1)

                # B. Batch Conversion for Polylines
                # Direct memory mapping is faster than column_stack
                # We create empty int32 containers and fill them
                # This prevents creating temporary float64 tuples

                def make_points(arr_x, arr_y):
                    # This is the fastest way to zip 2 numpy arrays for Pygame
                    # Create (N, 2) array
                    pts = np.empty((len(arr_x), 2), dtype=np.int32)
                    pts[:, 0] = arr_x
                    pts[:, 1] = arr_y
                    return pts

                points_mid = make_points(x_mid, y_mid)
                points_tot = make_points(x_tot, y_tot)
                points_shl = make_points(x_shl, y_shl)

                # C. Draw Main Layers
                if len(points_tot) > 2:
                    pygame.draw.polygon(self.screen, ter_c, points_tot.tolist())
                if len(points_mid) > 1:
                    pygame.draw.lines(self.screen, sec_c, True, points_mid.tolist(), 2)
                if len(points_tot) > 1:
                    pygame.draw.lines(self.screen, theme_c, True, points_tot.tolist(), 3)
                if len(points_shl) > 1:
                    pygame.draw.lines(self.screen, sec_c, True, points_shl.tolist(), 1)

                # 8. REACTOR CORE (Low Cost Geometry)

                # A. Tunnel
                mask_r = int(base_radius - 5)
                if mask_r > 10:
                    pygame.draw.circle(self.screen, (30, 30, 35), (cx, cy), mask_r)
                    pygame.draw.circle(self.screen, (15, 15, 20), (cx, cy), int(mask_r * 0.75))
                    pygame.draw.circle(self.screen, (5, 5, 8), (cx, cy), int(mask_r * 0.5))
                    pygame.draw.circle(self.screen, theme_c, (cx, cy), mask_r, 2)

                    # B. Hex-Locks (Cached rotation logic)
                    lock_r = int(mask_r * 0.92)
                    # Constant offsets for diamond shape to avoid per-frame Trig
                    # Diamond 'forward' length = 5, 'width' = 5

                    for k in range(6):
                        la = rot_base + (k * 1.0472)  # 1.0472 is pi/3
                        cla, sla = math.cos(la), math.sin(la)

                        px, py = cx + cla * lock_r, cy + sla * lock_r

                        # Orthogonal vectors for diamond width
                        # fwd = (cla*5, sla*5), side = (-sla*5, cla*5)
                        fx, fy = cla * 5, sla * 5
                        dx, dy = -sla * 5, cla * 5

                        d_pts = [
                            (px + fx, py + fy),
                            (px + dx, py + dy),
                            (px - fx, py - fy),
                            (px - dx, py - dy)
                        ]

                        # Shadow (Hardcoded offset +3)
                        s_pts = [(x + 3, y + 3) for x, y in d_pts]

                        pygame.draw.polygon(self.screen, (0, 0, 0), s_pts)
                        pygame.draw.polygon(self.screen, theme_c, d_pts)
                        pygame.draw.polygon(self.screen, ter_c, d_pts, 2)

                    # C. Wave (Vectorized)
                    osc_r = int(mask_r * 0.82)
                    res = 100
                    k_arr = np.arange(res + 1)
                    theta = (k_arr / res) * 2 * math.pi

                    wave_val = np.sin((theta * 12) + (t * 0.005)) * (3 + bass_pulse * 0.1)
                    # Fast cosine power approximation for avoidance
                    align = np.cos(6 * theta)
                    # Using multiplication instead of power for speed (align^2 * align * 12)
                    # masking negatives to 0
                    align = np.maximum(0, align)
                    avoid = align * align * align * 12

                    fin_r = osc_r + wave_val - avoid

                    real_ang = theta + rot_base
                    w_x = cx + np.cos(real_ang) * fin_r
                    w_y = cy + np.sin(real_ang) * fin_r

                    wave_pts = make_points(w_x, w_y)
                    pygame.draw.lines(self.screen, theme_c, False, wave_pts.tolist(), 2)

                # D. Rose Curve (Optimized)
                rose_r_max = (mask_r * 0.45) + (bass_pulse * 0.2)
                # We can reuse the theta array from Wave!
                # Just need cos(4*theta)
                r_rose = rose_r_max * np.cos(4 * theta)
                th_rot = theta + rot_geo
                rx = cx + np.cos(th_rot) * r_rose
                ry = cy + np.sin(th_rot) * r_rose

                rose_pts = make_points(rx, ry)
                if len(rose_pts) > 2:
                    pygame.draw.lines(self.screen, sec_c, True, rose_pts.tolist(), 1)

                # E. Singularity
                eye_r = int(6 + (bass_pulse * 0.1))
                pygame.draw.circle(self.screen, sec_c, (cx, cy), int(eye_r * 1.5), 1)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), eye_r)

        # --- ORB MODE ---
        if mode == 'Orb':
            bass = np.mean(fft_data[:5]) if len(fft_data) > 5 else 0
            mids = np.mean(fft_data[10:30]) if len(fft_data) > 30 else 0
            col = self.get_bar_color(bass * 5, 0, num)
            t = pygame.time.get_ticks() * 0.0004
            rad_core = (15 * p_size) + (bass * 20 * p_len)
            rad_shell = max((55 * p_size) + (mids * 8 * p_len), rad_core + 15)
            dim_col = (col[0] // 3, col[1] // 3, col[2] // 3)

            pygame.draw.circle(self.screen, dim_col, (cx, cy), int(rad_shell - 5), 1)
            pygame.draw.circle(self.screen, col, (cx, cy), int(rad_shell), 1)
            pygame.draw.circle(self.screen, col, (cx, cy), int(rad_core), 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), int(rad_core * 0.5))

            orbit_defs = [[1.3, 0.30, 1.0, 2], [1.6, 0.15, -0.5, 1], [1.9, 0.45, 0.8, 1]]
            for i, (dist_mult, tilt, speed, thick) in enumerate(orbit_defs):
                r_x = rad_shell * dist_mult
                r_y = r_x * tilt
                angle_offset = (t * speed) + (i * 2.5)
                rect = pygame.Rect(cx - r_x, cy - r_y, r_x * 2, r_y * 2)
                pygame.draw.arc(self.screen, dim_col, rect, 0, math.pi * 2, thick)
                hl_start = (angle_offset % (math.pi * 2))
                hl_end = hl_start + 0.5
                pygame.draw.arc(self.screen, (255, 255, 255), rect, hl_start, hl_end, thick + 2)
                sat_x = cx + math.cos(angle_offset) * r_x
                sat_y = cy - math.sin(angle_offset) * r_y
                if sat_y > cy - 5:
                    pygame.draw.circle(self.screen, (255, 255, 255), (sat_x, sat_y), 4)

    def draw_ui_pattern(self, surface):
        mode = UI_PATTERN_MODES[self.current_ui_pattern_mode]
        if mode == 'None': return

        w, h = surface.get_size()
        # Lighter color than the background (18, 18, 22)
        pat_col = (30, 30, 38)

        if mode == 'Grid':
            step = 20
            for x in range(0, w, step):
                pygame.draw.line(surface, pat_col, (x, 0), (x, h), 1)
            for y in range(0, h, step):
                pygame.draw.line(surface, pat_col, (0, y), (w, y), 1)

        elif mode == 'Dots':
            step = 20
            for x in range(10, w, step):
                for y in range(10, h, step):
                    pygame.draw.circle(surface, pat_col, (x, y), 2)

        elif mode == 'Hexagon':
            step_x, step_y = 30, 26
            for row, y in enumerate(range(0, h + step_y, step_y)):
                offset = (step_x // 2) if row % 2 else 0
                for x in range(offset, w, step_x):
                    pygame.draw.circle(surface, pat_col, (x, y), 4, 1)

        elif mode == 'Stripes':
            step = 30
            for i in range(-h, w, step):
                pygame.draw.line(surface, pat_col, (i, 0), (i + h, h), 2)

        elif mode == 'Circuit':
            random.seed(42)
            for _ in range(40):
                x1 = random.randint(0, w)
                y1 = random.randint(0, h)
                x2 = x1 + random.choice([-50, 50, 0])
                y2 = y1 + random.choice([-50, 50, 0])
                pygame.draw.line(surface, pat_col, (x1, y1), (x2, y2), 2)
                pygame.draw.circle(surface, pat_col, (x1, y1), 3)
            random.seed(None)

        # --- NEW PATTERNS ---

        elif mode == 'Checkers':
            step = 40
            for y in range(0, h, step):
                for x in range(0, w, step):
                    if (x // step + y // step) % 2 == 0:
                        pygame.draw.rect(surface, pat_col, (x, y, step, step))

        elif mode == 'Crosshatch':
            step = 20
            for i in range(-h, w, step):
                pygame.draw.line(surface, pat_col, (i, 0), (i + h, h), 1)
                pygame.draw.line(surface, pat_col, (i, h), (i + h, 0), 1)

        elif mode == 'Waves':
            step_x = 40
            for y in range(20, h, 30):
                points = []
                for x in range(0, w + step_x, step_x):
                    offset_y = math.sin(x * 0.05) * 10
                    points.append((x, y + offset_y))
                if len(points) > 1:
                    pygame.draw.lines(surface, pat_col, False, points, 2)

        elif mode == 'ZigZag':
            step = 30
            height = 15
            for y in range(20, h, 40):
                points = []
                for i, x in enumerate(range(0, w + step, step)):
                    y_offset = -height if i % 2 == 0 else height
                    points.append((x, y + y_offset))
                pygame.draw.lines(surface, pat_col, False, points, 2)

        elif mode == 'Binary':
            # Draws random 1s and 0s representation (rects and lines)
            random.seed(123)
            for y in range(10, h, 20):
                for x in range(10, w, 15):
                    if random.random() > 0.5:
                        pygame.draw.rect(surface, pat_col, (x, y, 6, 10), 1)  # "0" box
                    else:
                        pygame.draw.line(surface, pat_col, (x + 3, y), (x + 3, y + 10), 1)  # "1" line
            random.seed(None)

        elif mode == 'Bubbles':
            random.seed(99)
            for _ in range(60):
                bx = random.randint(0, w)
                by = random.randint(0, h)
                br = random.randint(5, 15)
                pygame.draw.circle(surface, pat_col, (bx, by), br, 1)
            random.seed(None)

        elif mode == 'Bricks':
            bw, bh = 40, 20
            for row, y in enumerate(range(0, h, bh + 2)):
                offset = -20 if row % 2 == 0 else 0
                for x in range(offset, w, bw + 2):
                    pygame.draw.rect(surface, pat_col, (x, y, bw, bh), 1)

        elif mode == 'Stars':
            step = 50
            for y in range(20, h, step):
                offset = 25 if (y // step) % 2 == 0 else 0
                for x in range(20 + offset, w, step):
                    pygame.draw.line(surface, pat_col, (x - 5, y), (x + 5, y), 1)
                    pygame.draw.line(surface, pat_col, (x, y - 5), (x, y + 5), 1)

        elif mode == 'Noise':
            # Static noise texture
            random.seed(55)
            for _ in range(400):
                nx = random.randint(0, w)
                ny = random.randint(0, h)
                surface.set_at((nx, ny), (50, 50, 60))
            random.seed(None)

        elif mode == 'Triangles':
            step = 40
            for y in range(0, h, step):
                for x in range(0, w, step):
                    # Draw upward pointing triangle
                    p1 = (x + step // 2, y)
                    p2 = (x, y + step)
                    p3 = (x + step, y + step)
                    pygame.draw.polygon(surface, pat_col, [p1, p2, p3], 1)

    def draw_ui(self):
        # --- CLEAR INTERACTION RECTS ---
        self.ui_buttons = {}
        self.ui_toggles = {}
        self.ui_dropdowns = {}
        self.param_slider_rects = {}

        w, h = self.screen.get_size()
        panel_h = self.ui_panel_height

        # --- OPTIMIZED DOCK DRAWING (Surface Caching) ---
        # Only redraw the heavy background pattern if dimensions/pattern changed
        if (self.ui_surface_cache is None or
                self.ui_surface_cache.get_width() != w or
                self.ui_surface_cache.get_height() != panel_h or
                self.settings_changed):  # Redraw if settings (like pattern) change

            self.ui_surface_cache = pygame.Surface((w, panel_h))
            self.ui_surface_cache.fill((18, 18, 22))
            # Draw Pattern onto the cache
            self.draw_ui_pattern(self.ui_surface_cache)

            theme = self.get_bar_color(50, 0, 10)  # Get current theme color
            self.ui_surface_cache.set_alpha(250)
            pygame.draw.line(self.ui_surface_cache, theme, (0, 0), (w, 0), 3)

        # Blit the cached surface (Fast!)
        self.screen.blit(self.ui_surface_cache, (0, h - panel_h))
        self.resize_handle_rect = pygame.Rect(0, h - panel_h, w, 8)
        # If the dock is minimized (pulled down), stop rendering the UI elements inside it
        if panel_h < 40:
            return

        theme = self.get_bar_color(50, 0, 10)  # Needed for dynamic elements below

        # Layout Constants
        row_1_y = h - panel_h + (panel_h * 0.2)  # Title
        row_3_y = h - panel_h + (panel_h * 0.55)  # Controls
        row_4_y = h - panel_h + (panel_h * 0.75)  # Seek Bar
        row_5_y = h - 15  # Status

        # --- TITLE ---
        if self.playlist:
            name = os.path.basename(self.playlist[self.current_song_index])
            if name.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                name = os.path.splitext(name)[0]
            if len(name) > 40: name = name[:37] + "..."

            # Draw Title
            ts = self.render_text(name, self.title_font, (255, 255, 255))
            title_rect = ts.get_rect(center=(w // 2, row_1_y))
            self.screen.blit(ts, title_rect)

            # --- Dropdown Arrow ---
            arrow_txt = "▼"
            arrow_surf = self.ui_font.render(arrow_txt, True, (150, 150, 150))
            arrow_rect = arrow_surf.get_rect(midleft=(title_rect.right + 10, row_1_y))
            self.screen.blit(arrow_surf, arrow_rect)

            # Make the click area cover the title and arrow
            full_rect = title_rect.union(arrow_rect).inflate(20, 10)
            self.ui_dropdowns['playlist'] = full_rect

            # Playlist Counter
            if self.show_playlist_counter:
                count_str = f"{self.current_song_index + 1} / {len(self.playlist)}"
                cs = self.render_text(count_str, self.ui_font, (120, 120, 120))
                self.screen.blit(cs, cs.get_rect(center=(w // 2, row_1_y + 25)))

        # --- DYNAMIC CONTROLS LAYOUT ---
        gap = self.font_size * 1.5
        # INCREASED loop_w from 24 to 36 to fit the arrow symbol comfortably
        shuf_w, loop_w, prev_w, play_w, next_w = 24, 36, 30, 40, 30

        vol_lbl = self.ui_font.render("VOL", True, (150, 150, 150))
        vol_bar_w = 80
        sm_lbl = self.ui_font.render("Smooth", True, (150, 150, 150))
        sm_bar_w = 80

        # Added loop_w twice (for two buttons) plus gaps
        total_width = (shuf_w + gap + loop_w + gap + loop_w + gap +
                       prev_w + gap + play_w + gap + next_w + gap +
                       vol_lbl.get_width() + 5 + vol_bar_w + gap +
                       sm_lbl.get_width() + 5 + sm_bar_w)

        current_x = (w - total_width) // 2

        # Shuffle
        self.btn_shuffle_rect = pygame.Rect(current_x, row_3_y - 12, shuf_w, 24)
        shuf_col = theme if self.shuffle_mode else (100, 100, 100)
        # Use centering logic for Shuffle too
        shuf_txt = self.ui_font.render("RND", True, shuf_col)
        self.screen.blit(shuf_txt, shuf_txt.get_rect(center=self.btn_shuffle_rect.center))
        current_x += shuf_w + gap

        # --- LOOP ONCE (Button "↻1") ---
        self.btn_loop_once_rect = pygame.Rect(current_x, row_3_y - 12, loop_w, 24)
        l1_col = theme if self.loop_once else (100, 100, 100)

        # Unicode u"\u27F3" is a Clockwise Circle Arrow.
        # If that doesn't render on your system, use "RPT 1"
        l1_surf = self.ui_font.render(u"Rep 1", True, l1_col)

        # This line ensures the text is perfectly centered in the button
        self.screen.blit(l1_surf, l1_surf.get_rect(center=self.btn_loop_once_rect.center))

        current_x += loop_w + gap

        # --- LOOP FOREVER (Button "↻∞") ---
        self.btn_loop_forever_rect = pygame.Rect(current_x, row_3_y - 12, loop_w, 24)
        linf_col = theme if self.loop_forever else (100, 100, 100)

        # Unicode Arrow + Infinity Symbol
        linf_surf = self.ui_font.render(u"Rep \u221E", True, linf_col)

        # Center the text
        self.screen.blit(linf_surf, linf_surf.get_rect(center=self.btn_loop_forever_rect.center))

        current_x += loop_w + gap

        # Prev
        self.btn_prev_rect = pygame.Rect(current_x, row_3_y - 15, prev_w, 30)
        cx, cy = self.btn_prev_rect.center
        col_btn = (220, 220, 220)
        pygame.draw.polygon(self.screen, col_btn, [(cx - 5, cy), (cx + 5, cy - 8), (cx + 5, cy + 8)])
        pygame.draw.rect(self.screen, col_btn, (cx - 8, cy - 8, 2, 16))
        current_x += prev_w + gap

        # Play
        self.btn_play_rect = pygame.Rect(current_x, row_3_y - 20, play_w, 40)
        cx, cy = self.btn_play_rect.center
        pygame.draw.circle(self.screen, col_btn, (cx, cy), 20, 2)
        if self.paused or not self.playing:
            pygame.draw.polygon(self.screen, col_btn, [(cx - 4, cy - 8), (cx - 4, cy + 8), (cx + 8, cy)])
        else:
            pygame.draw.rect(self.screen, col_btn, (cx - 6, cy - 8, 4, 16))
            pygame.draw.rect(self.screen, col_btn, (cx + 2, cy - 8, 4, 16))
        current_x += play_w + gap

        # Next
        self.btn_next_rect = pygame.Rect(current_x, row_3_y - 15, next_w, 30)
        cx, cy = self.btn_next_rect.center
        pygame.draw.polygon(self.screen, col_btn, [(cx + 5, cy), (cx - 5, cy - 8), (cx - 5, cy + 8)])
        pygame.draw.rect(self.screen, col_btn, (cx + 6, cy - 8, 2, 16))
        current_x += next_w + gap

        # Volume
        self.screen.blit(vol_lbl, (current_x, row_3_y - vol_lbl.get_height() // 2))
        current_x += vol_lbl.get_width() + 5
        self.vol_bar_rect = pygame.Rect(current_x, row_3_y - 3, vol_bar_w, 6)
        hitbox_vol = self.vol_bar_rect.inflate(0, 14)
        pygame.draw.rect(self.screen, (50, 50, 60), self.vol_bar_rect, border_radius=3)
        pygame.draw.rect(self.screen, theme, (current_x, row_3_y - 3, vol_bar_w * self.volume, 6), border_radius=3)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(current_x + vol_bar_w * self.volume), row_3_y), 6)
        self.vol_bar_rect = hitbox_vol
        current_x += vol_bar_w + gap

        # Smoothing
        self.screen.blit(sm_lbl, (current_x, row_3_y - sm_lbl.get_height() // 2))
        current_x += sm_lbl.get_width() + 5
        self.smooth_bar_rect = pygame.Rect(current_x, row_3_y - 3, sm_bar_w, 6)
        hitbox_sm = self.smooth_bar_rect.inflate(0, 14)
        pygame.draw.rect(self.screen, (50, 50, 60), self.smooth_bar_rect, border_radius=3)
        pygame.draw.rect(self.screen, (100, 100, 200), (current_x, row_3_y - 3, sm_bar_w * self.smoothing_factor, 6),
                         border_radius=3)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(current_x + sm_bar_w * self.smoothing_factor), row_3_y),
                           6)
        self.smooth_bar_rect = hitbox_sm

        # --- SEEK BAR ---
        bw = w * 0.8
        bx = (w - bw) // 2
        self.seek_bar_rect = pygame.Rect(bx - 10, row_4_y - 10, bw + 20, 20)
        prog = self.drag_progress if self.is_dragging_seek else (self.current_offset / max(1, self.current_duration))
        prog = min(1.0, max(0.0, prog))

        pygame.draw.rect(self.screen, (60, 60, 70), (bx, row_4_y, bw, 4), border_radius=2)
        pygame.draw.rect(self.screen, theme, (bx, row_4_y, bw * prog, 4), border_radius=2)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(bx + bw * prog), int(row_4_y + 2)), 6)

        cur_s = int((self.current_duration * prog / 2) / RATE)
        tot_s = int((self.current_duration / 2) / RATE)
        t1 = self.ui_font.render(f"{cur_s // 60}:{cur_s % 60:02d}", True, (200, 200, 200))
        t2 = self.ui_font.render(f"{tot_s // 60}:{tot_s % 60:02d}", True, (200, 200, 200))
        self.screen.blit(t1, (bx - t1.get_width() - 10, row_4_y - t1.get_height() // 2))
        self.screen.blit(t2, (bx + bw + 10, row_4_y - t2.get_height() // 2))

        # BPM
        if self.show_bpm:
            bpm_txt = f"BPM: {self.bpm}" if self.bpm > 0 else "BPM: --"
            self.screen.blit(self.ui_font.render(bpm_txt, True, (100, 255, 100)), (w - 80, h - panel_h - 25))

        # Status Message
        if time.time() < self.status_timer:
            ss = self.title_font.render(self.status_msg, True, (255, 255, 255))
            sr = ss.get_rect(bottomright=(w - 20, row_5_y))
            br = sr.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0), br, border_radius=5)
            pygame.draw.rect(self.screen, theme, br, 2, border_radius=5)
            self.screen.blit(ss, sr)

        # --- SETTINGS TOGGLE BUTTON ---
        btn_settings = pygame.Rect(w - 110, h - panel_h + 10, 100, 30)
        col = theme if self.show_settings else (60, 60, 70)
        pygame.draw.rect(self.screen, col, btn_settings, border_radius=4)
        lbl_txt = "CLOSE" if self.show_settings else "SETTINGS"
        lbl = self.ui_font.render(lbl_txt, True, (255, 255, 255))
        self.screen.blit(lbl, lbl.get_rect(center=btn_settings.center))

        # ADDED THIS TO ENSURE IT PERSISTS
        self.ui_buttons['toggle_settings'] = btn_settings

        # --- DRAW OVERLAY ---
        if self.show_settings:
            self.draw_settings_overlay(w, h, panel_h, theme)

    # Helper for Menu to keep draw_ui clean
    def draw_settings_overlay(self, w, h, panel_h, theme):
        # 1. Create Overlay Surface
        overlay_h = h - panel_h
        overlay = pygame.Surface((w, overlay_h))
        overlay.fill((10, 10, 12))
        overlay.set_alpha(235)  # High opacity for readability
        self.screen.blit(overlay, (0, 0))

        # Draw borderline
        pygame.draw.line(self.screen, theme, (0, overlay_h - 1), (w, overlay_h - 1), 2)

        # 2. Layout Configuration - COMPACT SPACING
        col_w = w // 3
        start_y = 8  # Very close to top
        padding = 15  # Tight padding
        header_gap = 22  # Gap between header and content
        slider_step = 20  # Height per slider row
        control_step = 32  # Height per button row

        # --- COLUMN 1: SLIDERS ---
        x = padding
        y = start_y

        # Determine label and color
        if self.settings_target == 'FG':
            toggle_text = "EDIT: VISUALIZER"
            toggle_col = (100, 200, 255)
        elif self.settings_target == 'CLR':
            toggle_text = "EDIT: COLOR THEME"
            toggle_col = (255, 100, 255)
        else:  # BG
            toggle_text = "EDIT: BACKGROUND"
            toggle_col = (255, 150, 100)

        self.screen.blit(self.bold_font.render("PARAMETERS TARGET", True, theme), (x, y))
        y += header_gap

        target_btn_rect = pygame.Rect(x, y, col_w - 40, 24)
        pygame.draw.rect(self.screen, (40, 40, 50), target_btn_rect, border_radius=4)
        pygame.draw.rect(self.screen, toggle_col, target_btn_rect, 1, border_radius=4)

        lbl = self.ui_font.render(toggle_text, True, toggle_col)
        self.screen.blit(lbl, lbl.get_rect(center=target_btn_rect.center))

        self.ui_buttons['toggle_param_target'] = target_btn_rect
        y += 28  # Gap after toggle button

        # --- SLIDER DEFINITIONS ---
        slider_defs = []

        if self.settings_target == 'FG':
            # Foreground (Visualizer Geometry)
            slider_defs = [
                ("Bar Count", "bar_count", 10.0, 300.0),
                ("Geo Rate", "rate", 0.0, 9.0),
                ("Thick", "thick", 0.0, 3.0),
                ("Length", "length", 0.0, 3.0),
                ("Size", "size", 0.0, 3.0),
                ("Jitter", "jitter", 0.0, 3.0),
                ("Collapse", "decay", 0.0, 3.0),
                ("Threshold", "threshold", 0.0, 3.0),
                ("Noise Gate", "noise_gate", 0.0, 3.0),
                ("Hollow Width", "hollow_thick", 0.0, 5.0)
            ]
            cur_mode_name = VISUAL_MODES[self.current_visual_mode]
            current_params = self.vis_params_sets[cur_mode_name]

        elif self.settings_target == 'CLR':
            # Color Theme Parameters
            slider_defs = [
                ("Cycle Speed", "rate", 0.1, 3.0),
                ("Variance", "color", 0.1, 3.0),
                ("Split Thresh", "threshold", 0.0, 1.0)
            ]
            cur_color_name = COLOR_MODES[self.current_color_mode]
            current_params = self.color_params_sets[cur_color_name]

        else:
            # --- DYNAMIC BACKGROUND SLIDERS (FIXED) ---
            active_bg_modes = set()
            m1 = BG_MODES[self.current_bg_mode]
            m2 = BG_MODES[self.current_bg_mode_2]

            if m1 not in ['None', 'Solid Dark']: active_bg_modes.add(m1)
            if m2 not in ['None', 'Solid Dark']: active_bg_modes.add(m2)

            # 1. Always show Image/Video Ops
            slider_defs = [
                ("Img Opacity", "img_opacity", 0.0, 1.0),
                ("Vid Opacity", "video_opacity", 0.0, 1.0),
                ("Img Pulse", "img_pulse_scale", 0.0, 1.0),
                ("Video Pos X", "video_pos_x", -1.0, 1.0),
                ("Video Pos Y", "video_pos_y", -1.0, 1.0),
                ("Glow Opacity", "glow_intensity", 0.0, 1.0),
                ("Glow Height", "glow_height", 0.1, 1.0),
                ("Glow Pulse", "glow_pulse", 0.0, 3.0),
                ("Glow Red", "glow_r", 0.0, 1.0),
                ("Glow Green", "glow_g", 0.0, 1.0),
                ("Glow Blue", "glow_b", 0.0, 1.0)
            ]

            # 2. If any particle effect is active, show standard physics AND COLORS
            if active_bg_modes:
                slider_defs.append(("Particle Count", "max_particles", 0.0, 1500.0)) # New Slider
                slider_defs.append(("Speed", "rate", 0.0, 3.0))
                slider_defs.append(("Size", "size", 0.0, 3.0))
                slider_defs.append(("Red", "red", 0.0, 1.0))
                slider_defs.append(("Green", "green", 0.0, 1.0))
                slider_defs.append(("Blue", "blue", 0.0, 1.0))

            # 3. Context Specific (Extras)
            if 'Fog' in active_bg_modes:
                # Fog uses "size" for density logic in update(), but we can keep it simple
                pass
            if 'Warp Speed' in active_bg_modes:
                slider_defs += [
                    ("Warp X", "center_x", 0.0, 1.0),
                    ("Warp Y", "center_y", 0.0, 1.0),
                ]
            if 'Rain Effect' in active_bg_modes or 'Matrix Rain' in active_bg_modes:
                slider_defs += [
                    ("Drop Len", "length", 0.5, 3.0),
                    ("Drop Thk", "thick", 0.5, 3.0),
                ]
            if any(m in ['Fire', 'Sparks', 'Magic Particles'] for m in active_bg_modes):
                slider_defs += [
                    ("Chaos", "jitter", 0.0, 1.0),
                ]

            # Filter duplicates
            unique_defs = []
            seen_keys = set()
            for lbl, key, min_v, max_v in slider_defs:
                if key not in seen_keys:
                    unique_defs.append((lbl, key, min_v, max_v))
                    seen_keys.add(key)
            slider_defs = unique_defs
            current_params = self.bg_params

        # --- DRAW SLIDERS ---
        for label, key, min_v, max_v in slider_defs:
            self.screen.blit(self.ui_font.render(label, True, (200, 200, 200)), (x, y))

            # Colored sliders for RGB
            s_theme = theme
            if key == 'red':
                s_theme = (255, 80, 80)
            elif key == 'green':
                s_theme = (80, 255, 80)
            elif key == 'blue':
                s_theme = (80, 80, 255)

            bar_w = col_w - 90  # Slightly wider bar area
            bar_rect = pygame.Rect(x + 75, y + 3, bar_w, 8)

            val = current_params.get(key, min_v)

            pct = (val - min_v) / (max_v - min_v) if max_v > min_v else 0
            pct = max(0.0, min(1.0, pct))

            pygame.draw.rect(self.screen, (50, 50, 60), bar_rect, border_radius=4)
            pygame.draw.rect(self.screen, s_theme, (x + 75, y + 3, bar_w * pct, 8), border_radius=4)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(x + 75 + bar_w * pct), y + 7), 5)

            self.param_slider_rects[key] = (bar_rect.inflate(0, 10), min_v, max_v)
            y += slider_step

        # --- PRECISE VIDEO TRIGGER INPUT ---
        if self.settings_target == 'BG':
            y += 2
            # Label
            self.screen.blit(self.ui_font.render("Video Offset (s):", True, (200, 200, 200)), (x, y))

            # Input Box Background
            input_rect = pygame.Rect(x + 110, y - 2, 60, 20)
            is_active = (self.active_input == 'video_offset')  # Check for new ID
            box_col = (20, 20, 30) if not is_active else (50, 50, 70)
            border_col = (100, 100, 100) if not is_active else theme

            pygame.draw.rect(self.screen, box_col, input_rect, border_radius=4)
            pygame.draw.rect(self.screen, border_col, input_rect, 1, border_radius=4)

            # Text Display
            if is_active:
                disp_txt = self.input_text
            else:
                val = self.bg_params.get('video_offset', 0.0)
                disp_txt = f"{val:.1f}"

            txt_surf = self.ui_font.render(disp_txt, True, (255, 255, 255))
            self.screen.blit(txt_surf, (input_rect.x + 5, input_rect.y + 2))

            # Register Button with new ID
            self.ui_buttons['input_video_offset'] = input_rect
            y += 25

        # --- CAROUSEL FADE INPUT ---
        if self.settings_target == 'BG' and self.bg_params.get('img_enabled') == 4:
            # Label
            self.screen.blit(self.ui_font.render("Fade Duration (s):", True, (200, 200, 200)), (x, y))

            # Input Box
            input_rect = pygame.Rect(x + 130, y - 2, 60, 20)
            is_active = (self.active_input == 'carousel_fade')
            box_col = (20, 20, 30) if not is_active else (50, 50, 70)
            border_col = (100, 100, 100) if not is_active else theme

            pygame.draw.rect(self.screen, box_col, input_rect, border_radius=4)
            pygame.draw.rect(self.screen, border_col, input_rect, 1, border_radius=4)

            # Text Display
            if is_active:
                disp_txt = self.input_text
            else:
                val = self.bg_params.get('carousel_fade', 2.0)
                disp_txt = f"{val:.1f}"

            txt_surf = self.ui_font.render(disp_txt, True, (255, 255, 255))
            self.screen.blit(txt_surf, (input_rect.x + 5, input_rect.y + 2))

            # Register Button
            self.ui_buttons['input_carousel_fade'] = input_rect
            y += 25

        if self.settings_target == 'FG':
            cur_mode_name = VISUAL_MODES[self.current_visual_mode]
            current_params = self.vis_params_sets[cur_mode_name]

            y += 5
            # 1. Peak Line Toggle
            t_rect = pygame.Rect(x, y, 16, 16)
            is_on = current_params.get('show_line', True)
            col = theme if is_on else (60, 60, 60)
            pygame.draw.rect(self.screen, col, t_rect, border_radius=3)
            if is_on:
                pygame.draw.line(self.screen, (255, 255, 255), (x + 3, y + 8), (x + 7, y + 13), 2)
                pygame.draw.line(self.screen, (255, 255, 255), (x + 7, y + 13), (x + 13, y + 3), 2)
            self.screen.blit(self.ui_font.render("Show Peak Line", True, (200, 200, 200)), (x + 25, y + 1))
            self.ui_buttons['toggle_peak_line'] = t_rect

            # 2. Collapse Mode Dropdown
            y += 24
            self.screen.blit(self.ui_font.render("Collapse Method:", True, (200, 200, 200)), (x, y))

            c_mode_idx = current_params.get('collapse_mode', 0)
            dd_rect = pygame.Rect(x, y + 16, col_w - 60, 22)
            pygame.draw.rect(self.screen, (40, 40, 50), dd_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 100), dd_rect, 1, border_radius=4)

            curr_txt = COLLAPSE_MODES[c_mode_idx]
            self.screen.blit(self.ui_font.render(curr_txt, True, (255, 255, 255)), (x + 8, y + 20))
            arrow = "▲" if self.active_dropdown == 'collapse_mode' else "▼"
            self.screen.blit(self.ui_font.render(arrow, True, (150, 150, 150)), (dd_rect.right - 15, y + 20))
            self.ui_dropdowns['collapse_mode'] = dd_rect

            y += 42
            self.screen.blit(self.ui_font.render("Idle Behavior (Silence):", True, (200, 200, 200)), (x, y))

            idle_mode_idx = current_params.get('idle_mode', 0)

            dd_rect_idle = pygame.Rect(x, y + 16, col_w - 60, 22)
            pygame.draw.rect(self.screen, (40, 40, 50), dd_rect_idle, border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 100), dd_rect_idle, 1, border_radius=4)

            curr_idle_txt = IDLE_MODES[idle_mode_idx]
            self.screen.blit(self.ui_font.render(curr_idle_txt, True, (255, 255, 255)), (x + 8, y + 20))
            arrow = "▲" if self.active_dropdown == 'idle_mode' else "▼"
            self.screen.blit(self.ui_font.render(arrow, True, (150, 150, 150)), (dd_rect_idle.right - 15, y + 20))
            self.ui_dropdowns['idle_mode'] = dd_rect_idle

        elif self.settings_target == 'BG':
            # --- Fullscreen Toggle ---
            y += 5
            t_rect = pygame.Rect(x, y, 16, 16)
            # Check state
            is_on = self.is_fullscreen
            col = theme if is_on else (60, 60, 60)
            pygame.draw.rect(self.screen, col, t_rect, border_radius=3)
            if is_on:
                # Draw Checkmark
                pygame.draw.line(self.screen, (255, 255, 255), (x + 3, y + 8), (x + 7, y + 13), 2)
                pygame.draw.line(self.screen, (255, 255, 255), (x + 7, y + 13), (x + 13, y + 3), 2)
            self.screen.blit(self.ui_font.render("Fullscreen Mode", True, (200, 200, 200)), (x + 25, y + 1))
            self.ui_buttons['toggle_fullscreen'] = t_rect
            y += 24

            # --- 1. Warp Toggle ---
            y += 5
            t_rect = pygame.Rect(x, y, 16, 16)
            is_on = self.bg_params.get('hide_center', False)
            col = theme if is_on else (60, 60, 60)
            pygame.draw.rect(self.screen, col, t_rect, border_radius=3)
            if is_on:
                pygame.draw.line(self.screen, (255, 255, 255), (x + 3, y + 8), (x + 7, y + 13), 2)
                pygame.draw.line(self.screen, (255, 255, 255), (x + 7, y + 13), (x + 13, y + 3), 2)
            self.screen.blit(self.ui_font.render("Hide Warp Artifact", True, (200, 200, 200)), (x + 25, y + 1))
            self.ui_buttons['toggle_warp_center'] = t_rect

            # --- GLOW TOGGLE ---
            y += 24
            t_rect = pygame.Rect(x, y, 16, 16)
            is_on = self.bg_params.get('glow_enabled', False)
            col = theme if is_on else (60, 60, 60)
            pygame.draw.rect(self.screen, col, t_rect, border_radius=3)
            if is_on:
                pygame.draw.line(self.screen, (255, 255, 255), (x + 3, y + 8), (x + 7, y + 13), 2)
                pygame.draw.line(self.screen, (255, 255, 255), (x + 7, y + 13), (x + 13, y + 3), 2)
            self.screen.blit(self.ui_font.render("Enable Bottom Glow", True, (200, 200, 200)), (x + 25, y + 1))
            self.ui_buttons['toggle_glow'] = t_rect

            # --- 2. Background Image Mode Dropdown ---
            y += 24
            self.screen.blit(self.ui_font.render("Background Image:", True, (200, 200, 200)), (x, y))

            img_mode_idx = self.bg_params.get('img_enabled', 0)
            if img_mode_idx < 0 or img_mode_idx >= len(BG_IMAGE_OPTIONS):
                img_mode_idx = 0

            dd_rect = pygame.Rect(x, y + 16, col_w - 60, 22)
            pygame.draw.rect(self.screen, (40, 40, 50), dd_rect, border_radius=4)

            curr_txt = BG_IMAGE_OPTIONS[img_mode_idx]
            self.screen.blit(self.ui_font.render(curr_txt, True, (255, 255, 255)), (x + 8, y + 20))
            arrow = "▲" if self.active_dropdown == 'img_enabled' else "▼"
            self.screen.blit(self.ui_font.render(arrow, True, (150, 150, 150)), (dd_rect.right - 15, y + 20))
            self.ui_dropdowns['img_enabled'] = dd_rect

            # --- 3. Image Animation Dropdown ---
            y += 42
            self.screen.blit(self.ui_font.render("Image Animation:", True, (200, 200, 200)), (x, y))

            anim_idx = self.bg_params.get('img_anim', 0)
            dd_rect_anim = pygame.Rect(x, y + 16, col_w - 60, 22)
            pygame.draw.rect(self.screen, (40, 40, 50), dd_rect_anim, border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 100), dd_rect_anim, 1, border_radius=4)

            curr_anim = BG_IMAGE_ANIMS[anim_idx]
            self.screen.blit(self.ui_font.render(curr_anim, True, (255, 255, 255)), (x + 8, y + 20))
            arrow = "▲" if self.active_dropdown == 'img_anim' else "▼"
            self.screen.blit(self.ui_font.render(arrow, True, (150, 150, 150)), (dd_rect_anim.right - 15, y + 20))
            self.ui_dropdowns['img_anim'] = dd_rect_anim

        # --- COLUMN 2: MODES ---
        x = col_w + padding
        y = start_y

        self.screen.blit(self.bold_font.render("DISPLAY MODES", True, theme), (x, y))
        y += header_gap

        def draw_dd(label, current_val, key_id, y_pos):
            self.screen.blit(self.ui_font.render(label, True, (200, 200, 200)), (x, y_pos))
            dd_rect = pygame.Rect(x, y_pos + 16, col_w - 60, 22)
            pygame.draw.rect(self.screen, (40, 40, 50), dd_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 100), dd_rect, 1, border_radius=4)

            txt_str = str(current_val).replace('.ttf', '').capitalize()
            if len(txt_str) > 20: txt_str = txt_str[:18] + "..."

            self.screen.blit(self.ui_font.render(txt_str, True, (255, 255, 255)), (x + 8, y_pos + 20))
            arrow = "▲" if self.active_dropdown == key_id else "▼"
            self.screen.blit(self.ui_font.render(arrow, True, (150, 150, 150)), (dd_rect.right - 15, y_pos + 20))

            self.ui_dropdowns[key_id] = dd_rect
            return y_pos + 44  # Tight vertical spacing

        y = draw_dd("Visual Style", VISUAL_MODES[self.current_visual_mode], 'visual', y)
        y = draw_dd("Color Theme", COLOR_MODES[self.current_color_mode], 'color', y)
        y = draw_dd("Bar Texture", BAR_STYLES[self.current_bar_style], 'bar_style', y)
        y = draw_dd("Background Layer 1", BG_MODES[self.current_bg_mode], 'bg', y)
        y = draw_dd("Background Layer 2", BG_MODES[self.current_bg_mode_2], 'bg2', y)
        y = draw_dd("UI Pattern", UI_PATTERN_MODES[self.current_ui_pattern_mode], 'ui_pattern', y)
        y = draw_dd("Data Layout", SORT_MODES[self.current_sort_mode], 'sort', y)
        y = draw_dd("Font", self.font_name, 'font', y)

        y += 5
        self.screen.blit(self.ui_font.render(f"Font Size: {self.font_size}", True, (200, 200, 200)), (x, y))
        btn_down = pygame.Rect(x + 100, y - 2, 30, 24)
        btn_up = pygame.Rect(x + 140, y - 2, 30, 24)

        pygame.draw.rect(self.screen, (60, 60, 70), btn_down, border_radius=3)
        self.screen.blit(self.ui_font.render("-", True, (255, 255, 255)), (btn_down.centerx - 3, btn_down.y + 2))
        pygame.draw.rect(self.screen, (60, 60, 70), btn_up, border_radius=3)
        self.screen.blit(self.ui_font.render("+", True, (255, 255, 255)), (btn_up.centerx - 4, btn_up.y + 2))

        self.ui_buttons['font_down'] = btn_down
        self.ui_buttons['font_up'] = btn_up

        # --- COLUMN 3: CONTROLS ---
        x = col_w * 2 + padding
        y = start_y

        self.screen.blit(self.bold_font.render("LIBRARY & CONTROLS", True, theme), (x, y))
        y += header_gap

        # Toggles
        toggle_rect = pygame.Rect(x, y, 16, 16)
        color = theme if self.show_bpm else (60, 60, 60)
        pygame.draw.rect(self.screen, color, toggle_rect, border_radius=3)
        if self.show_bpm:
            pygame.draw.line(self.screen, (255, 255, 255), (x + 3, y + 8), (x + 7, y + 13), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (x + 7, y + 13), (x + 13, y + 3), 2)

        self.screen.blit(self.ui_font.render("Show BPM Counter", True, (220, 220, 220)), (x + 25, y + 1))
        self.ui_toggles['bpm'] = toggle_rect
        y += 28

        toggle_rect = pygame.Rect(x, y, 16, 16)
        color = theme if self.show_playlist_counter else (60, 60, 60)
        pygame.draw.rect(self.screen, color, toggle_rect, border_radius=3)
        if self.show_playlist_counter:
            pygame.draw.line(self.screen, (255, 255, 255), (x + 3, y + 8), (x + 7, y + 13), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (x + 7, y + 13), (x + 13, y + 3), 2)

        self.screen.blit(self.ui_font.render("Show Track Counter", True, (220, 220, 220)), (x + 25, y + 1))
        self.ui_toggles['playlist_counter'] = toggle_rect
        y += 28

        btn_width = col_w - 60

        # --- COLOR CYCLE DROPDOWN ---
        self.screen.blit(self.ui_font.render("Color Cycle:", True, (200, 200, 200)), (x, y))
        y += 16

        dd_rect_cycle = pygame.Rect(x, y, btn_width, 22)
        pygame.draw.rect(self.screen, (40, 40, 50), dd_rect_cycle, border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 100), dd_rect_cycle, 1, border_radius=4)

        cycle_txt = COLOR_CYCLE_MODES[self.current_color_cycle_mode]
        self.screen.blit(self.ui_font.render(cycle_txt, True, (255, 255, 255)), (x + 8, y + 4))
        arrow = "▲" if self.active_dropdown == 'color_cycle' else "▼"
        self.screen.blit(self.ui_font.render(arrow, True, (150, 150, 150)), (dd_rect_cycle.right - 15, y + 4))

        self.ui_dropdowns['color_cycle'] = dd_rect_cycle
        y += 32 # Add spacing before the next element

        def draw_btn(text, action_key, y_pos, col=(60, 60, 70)):
            r = pygame.Rect(x, y_pos, btn_width, 26)  # Reduced Height
            pygame.draw.rect(self.screen, col, r, border_radius=4)
            lbl = self.ui_font.render(text, True, (255, 255, 255))
            self.screen.blit(lbl, lbl.get_rect(center=r.center))
            self.ui_buttons[action_key] = r
            return y_pos + control_step

        # --- SORT PLAYLIST DROPDOWN ---
        self.screen.blit(self.ui_font.render("Sort Playlist:", True, (200, 200, 200)), (x, y))
        y += 16

        dd_rect = pygame.Rect(x, y, btn_width, 22)
        pygame.draw.rect(self.screen, (40, 40, 50), dd_rect, border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 100), dd_rect, 1, border_radius=4)

        self.screen.blit(self.ui_font.render("Select Sort Order...", True, (255, 255, 255)), (x + 8, y + 4))
        arrow = "▲" if self.active_dropdown == 'sort_algo' else "▼"
        self.screen.blit(self.ui_font.render(arrow, True, (150, 150, 150)), (dd_rect.right - 15, y + 4))

        self.ui_dropdowns['sort_algo'] = dd_rect
        y += control_step

        y = draw_btn("Add Audio Files...", 'add_file', y)
        y = draw_btn("Add Folder...", 'add_folder', y)
        y += 5
        y = draw_btn("Save Playlist", 'save_list', y, (40, 80, 40))
        y = draw_btn("Load Playlist", 'load_list', y, (40, 60, 80))
        y = draw_btn("Clear Playlist", 'clear_list', y, (80, 40, 40))

        # --- DRAW ACTIVE DROPDOWN LIST ---
        if self.active_dropdown:
            options = []
            if self.active_dropdown == 'visual':
                options = VISUAL_MODES
            elif self.active_dropdown == 'color':
                options = COLOR_MODES
            elif self.active_dropdown == 'bar_style':
                options = BAR_STYLES
            elif self.active_dropdown == 'bg':
                options = BG_MODES
            elif self.active_dropdown == 'bg2':
                options = BG_MODES
            elif self.active_dropdown == 'ui_pattern':
                options = UI_PATTERN_MODES
            elif self.active_dropdown == 'sort':
                options = SORT_MODES
            elif self.active_dropdown == 'font':
                options = self.available_fonts
            elif self.active_dropdown == 'collapse_mode':
                options = COLLAPSE_MODES
            elif self.active_dropdown == 'idle_mode':
                options = IDLE_MODES
            elif self.active_dropdown == 'img_enabled':
                options = BG_IMAGE_OPTIONS
            elif self.active_dropdown == 'img_anim':
                options = BG_IMAGE_ANIMS
            elif self.active_dropdown == 'playlist':
                options = [os.path.basename(p) for p in self.playlist]
            elif self.active_dropdown == 'sort_algo':
                options = SORT_ALGO
            elif self.active_dropdown == 'color_cycle':
                options = COLOR_CYCLE_MODES

            parent_rect = self.ui_dropdowns[self.active_dropdown]
            item_h = 24
            total_items = len(options)
            visible_items = min(total_items, self.dropdown_max_visible)
            menu_h = visible_items * item_h

            screen_h = self.screen.get_height()

            # --- EXPAND PLAYLIST WIDTH & CENTER IT ---
            actual_width = parent_rect.width
            menu_x = parent_rect.x

            if self.active_dropdown == 'playlist':
                actual_width = max(600, int(w * 0.5))  # Much wider to fit song names
                menu_x = parent_rect.centerx - (actual_width // 2)

            if parent_rect.bottom + menu_h > screen_h:
                menu_y = parent_rect.top - menu_h
            else:
                menu_y = parent_rect.bottom

            menu_rect = pygame.Rect(menu_x, menu_y, actual_width, menu_h)

            # --- TRANSLUCENT MODERN BACKGROUND ---
            bg_surf = pygame.Surface((menu_rect.width, menu_rect.height), pygame.SRCALPHA)
            bg_surf.fill((15, 15, 20, 240))  # Dark with slight transparency
            self.screen.blit(bg_surf, menu_rect.topleft)
            pygame.draw.rect(self.screen, theme, menu_rect, 2, border_radius=6)

            show_scrollbar = total_items > self.dropdown_max_visible
            scroll_w = 12 if show_scrollbar else 0
            start_idx = self.dropdown_scroll_offset
            end_idx = min(start_idx + visible_items, total_items)
            display_opts = options[start_idx:end_idx]

            self.ui_dropdown_options_rects = []
            mx, my = pygame.mouse.get_pos()

            for i, opt in enumerate(display_opts):
                opt_rect = pygame.Rect(menu_x, menu_y + (i * item_h), actual_width - scroll_w, item_h)

                # --- THEME-COLORED HOVER EFFECT ---
                is_hover = opt_rect.collidepoint(mx, my)
                if is_hover:
                    hover_col = (theme[0], theme[1], theme[2], 40)  # Tinted transparent highlight
                    h_surf = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                    h_surf.fill(hover_col)
                    self.screen.blit(h_surf, opt_rect.topleft)
                    pygame.draw.rect(self.screen, theme, (opt_rect.x, opt_rect.y, 4, item_h))  # Left accent line

                txt_str = str(opt).replace('.ttf', '').title()

                # --- ACCURATE TEXT WIDTH CALCULATION ---
                max_text_w = actual_width - scroll_w - 20
                if self.ui_font.size(txt_str)[0] > max_text_w:
                    while len(txt_str) > 0 and self.ui_font.size(txt_str + "...")[0] > max_text_w:
                        txt_str = txt_str[:-1]
                    txt_str += "..."

                col_txt = (255, 255, 255) if is_hover else (180, 180, 180)
                self.screen.blit(self.ui_font.render(txt_str, True, col_txt), (menu_x + 15, opt_rect.y + 5))

                val_to_store = opt if self.active_dropdown == 'font' else (start_idx + i)
                self.ui_dropdown_options_rects.append((opt_rect, val_to_store))

            if show_scrollbar:
                track_rect = pygame.Rect(menu_x + actual_width - scroll_w, menu_y, scroll_w, menu_h)
                # Dimmed background for the track
                pygame.draw.rect(self.screen, (20, 20, 25), track_rect, border_bottom_right_radius=6,
                                 border_top_right_radius=6)

                view_ratio = visible_items / total_items
                thumb_h = max(20, int(menu_h * view_ratio))
                max_scroll_y = menu_h - thumb_h
                scroll_ratio = self.dropdown_scroll_offset / (total_items - visible_items)
                thumb_y = menu_y + (scroll_ratio * max_scroll_y)

                thumb_rect = pygame.Rect(menu_x + actual_width - scroll_w + 2, thumb_y, scroll_w - 4, thumb_h)

                # Theme-colored interactive scrollbar
                is_thumb_hover = self.is_dragging_scrollbar or thumb_rect.collidepoint(mx, my)
                col_thumb = theme if is_thumb_hover else (theme[0] // 2, theme[1] // 2, theme[2] // 2)
                pygame.draw.rect(self.screen, col_thumb, thumb_rect, border_radius=4)
                self.dropdown_track_rect = track_rect
                self.dropdown_thumb_rect = thumb_rect
            else:
                self.dropdown_track_rect = None
                self.dropdown_thumb_rect = None

    def draw_foreground_glow(self):
        """Draws glow ON TOP of everything.
           FIX: Uses RGB Multiplication on the 1px cache so Sliders/Pulse work with BLEND_ADD."""
        if not self.bg_params.get('glow_enabled', False):
            return

        w, h = self.screen.get_size()

        # 1. Get Params
        g_r = int(self.bg_params.get('glow_r', 1.0) * 255)
        g_g = int(self.bg_params.get('glow_g', 0.6) * 255)
        g_b = int(self.bg_params.get('glow_b', 0.2) * 255)
        g_h_pct = self.bg_params.get('glow_height', 0.4)
        g_h_px = int(h * g_h_pct)

        if g_h_px < 1: return

        # 2. Check Cache (1-pixel wide strip)
        current_glow_state = (g_r, g_g, g_b, g_h_px)

        if self.bg_glow_cache is None or self.bg_glow_last_params != current_glow_state:
            # Create 1px wide vertical gradient
            grad_surf = pygame.Surface((1, g_h_px))

            for y in range(g_h_px):
                progress = y / g_h_px
                curve = progress ** 2
                grad_surf.set_at((0, y), (int(g_r * curve), int(g_g * curve), int(g_b * curve)))

            self.bg_glow_cache = grad_surf
            self.bg_glow_last_params = current_glow_state

        # 3. Calculate Intensity (Opacity + Pulse)
        base_int = self.bg_params.get('glow_intensity', 0.5)
        pulse_slider = self.bg_params.get('glow_pulse', 1.0)

        # Pulse Logic
        total_intensity = base_int + (self.current_energy * 0.6 * pulse_slider)
        total_intensity = max(0.0, min(1.0, total_intensity))

        # 4. Draw
        if total_intensity > 0.005:
            # A. Copy the 1px strip (Very fast, tiny memory)
            work_strip = self.bg_glow_cache.copy()

            # B. Darken the RGB values based on intensity
            # BLEND_ADD works by adding RGB values. To make it fainter, we must darken the RGBs.
            mult_val = int(total_intensity * 255)
            work_strip.fill((mult_val, mult_val, mult_val), special_flags=pygame.BLEND_RGB_MULT)

            # C. Scale the darkened strip to screen width (Hardware optimized)
            draw_surf = pygame.transform.scale(work_strip, (w, g_h_px))

            # D. Blit with Additive Blend
            self.screen.blit(draw_surf, (0, h - g_h_px), special_flags=pygame.BLEND_ADD)

    def run(self):
        while self.running:
            # tick_busy_loop uses high CPU to ensure precise timing (prevents core sleeping)
            self.clock.tick_busy_loop(FPS)
            if self.song_finished_flag:
                self.song_finished_flag = False
                self.handle_song_end()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.stop_audio_flag = True
                    self.save_settings()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # --- SCROLL WHEEL ---
                    if self.show_settings and self.active_dropdown:
                        options_len = 0
                        if self.active_dropdown == 'visual':
                            options_len = len(VISUAL_MODES)
                        elif self.active_dropdown == 'color':
                            options_len = len(COLOR_MODES)
                        elif self.active_dropdown == 'bg':
                            options_len = len(BG_MODES)
                        elif self.active_dropdown == 'bg' or self.active_dropdown == 'bg2':
                            options_len = len(BG_MODES)
                        elif self.active_dropdown == 'ui_pattern':
                            options_len = len(UI_PATTERN_MODES)
                        elif self.active_dropdown == 'sort':
                            options_len = len(SORT_MODES)
                        elif self.active_dropdown == 'bar_style':
                            options_len = len(BAR_STYLES)
                        elif self.active_dropdown == 'font':
                            options_len = len(self.available_fonts)
                        elif self.active_dropdown == 'collapse_mode':
                            options_len = len(COLLAPSE_MODES)
                        elif self.active_dropdown == 'idle_mode':
                            options_len = len(IDLE_MODES)
                        elif self.active_dropdown == 'img_enabled':
                            options_len = len(BG_IMAGE_OPTIONS)
                        elif self.active_dropdown == 'img_anim':
                            options_len = len(BG_IMAGE_ANIMS)
                        elif self.active_dropdown == 'playlist':
                            options_len = len(self.playlist)
                        elif self.active_dropdown == 'sort_algo':
                            options_len = len(SORT_ALGO)
                        elif self.active_dropdown == 'color_cycle':
                            options_len = len(COLOR_CYCLE_MODES)

                        if event.button == 4:
                            self.dropdown_scroll_offset = max(0, self.dropdown_scroll_offset - 1)
                        elif event.button == 5:
                            self.dropdown_scroll_offset = min(max(0, options_len - self.dropdown_max_visible),
                                                              self.dropdown_scroll_offset + 1)

                    if event.button == 1:
                        mx, my = event.pos
                        # --- UNFOCUS IF CLICKING OUTSIDE ---
                        if self.active_input:
                            # Commit if we click away
                            if self.input_text:
                                try:
                                    val = float(self.input_text)

                                    if self.active_input == 'video_offset':
                                        if val < -1200: val = -1200
                                        self.bg_params['video_offset'] = val
                                        self.settings_changed = True

                                    elif self.active_input == 'carousel_fade':
                                        if val < 0: val = 0.0
                                        self.bg_params['carousel_fade'] = val
                                        self.settings_changed = True

                                except ValueError:
                                    pass
                            self.active_input = None
                            # Don't return, allow click to register on other UI elements
                        ui_handled = False

                        # --- 1. DROPDOWN OPTIONS & CLOSING LOGIC ---
                        if self.active_dropdown:
                            # A. Handle Scrollbar
                            if self.dropdown_track_rect and self.dropdown_track_rect.collidepoint(mx, my):
                                self.is_dragging_scrollbar = True
                                ui_handled = True

                            # B. Handle Option Clicks
                            if not ui_handled:
                                clicked_option = False
                                for r, val in self.ui_dropdown_options_rects:
                                    if r.collidepoint(mx, my):
                                        # Apply Value
                                        if self.active_dropdown == 'sort_algo':
                                            self.sort_playlist(val)
                                        elif self.active_dropdown == 'color_cycle':
                                            self.current_color_cycle_mode = val
                                        elif self.active_dropdown == 'playlist':
                                            self.start_song(val)  # 'val' acts as index here
                                        elif self.active_dropdown == 'visual':
                                            self.current_visual_mode = val
                                        elif self.active_dropdown == 'color':
                                            self.current_color_mode = val
                                        elif self.active_dropdown == 'bar_style':
                                            self.current_bar_style = val
                                        elif self.active_dropdown == 'bg':
                                            self.current_bg_mode = val
                                        elif self.active_dropdown == 'bg2':
                                            self.current_bg_mode_2 = val
                                        elif self.active_dropdown == 'ui_pattern':
                                            self.current_ui_pattern_mode = val
                                        elif self.active_dropdown == 'sort':
                                            self.current_sort_mode = val
                                        elif self.active_dropdown == 'font':
                                            self.font_name = val
                                            self.update_fonts()
                                        elif self.active_dropdown == 'collapse_mode':
                                            cur_mode = VISUAL_MODES[self.current_visual_mode]
                                            self.vis_params_sets[cur_mode]['collapse_mode'] = val
                                        elif self.active_dropdown == 'idle_mode':
                                            cur_mode = VISUAL_MODES[self.current_visual_mode]
                                            self.vis_params_sets[cur_mode]['idle_mode'] = val
                                        elif self.active_dropdown == 'img_enabled':
                                            prev_val = self.bg_params.get('img_enabled', 0)
                                            self.bg_params['img_enabled'] = val
                                            # If switched to Image (1)
                                            if val == 1 and prev_val != 1:
                                                self.bg_params['img_path'] = ""
                                                self.load_bg_image()
                                            # If switched to Video (2)
                                            elif val == 2 and prev_val != 2:
                                                self.bg_params['video_path'] = ""
                                                self.load_bg_video()
                                            elif val == 4 and prev_val != 4:
                                                self.bg_params['carousel_path'] = ""
                                                self.load_bg_carousel_folder()
                                        elif self.active_dropdown == 'img_anim':
                                            self.bg_params['img_anim'] = val

                                        self.active_dropdown = None
                                        clicked_option = True
                                        ui_handled = True
                                        self.settings_changed = True  # Flag for save
                                        break

                                if not clicked_option:
                                    # Check if we clicked the button that OPENED the dropdown
                                    opener_rect = self.ui_dropdowns.get(self.active_dropdown)
                                    if opener_rect and opener_rect.collidepoint(mx, my):
                                        # Don't close here; let Step C handle the toggle
                                        pass
                                    else:
                                        # Clicked into the void -> Close
                                        self.active_dropdown = None
                                        ui_handled = True

                        # C. Dropdown Openers
                        if not ui_handled:
                            for key, r in self.ui_dropdowns.items():
                                if r.collidepoint(mx, my):
                                    if self.active_dropdown != key:
                                        self.dropdown_scroll_offset = 0
                                        self.active_dropdown = key  # Open
                                    else:
                                        self.active_dropdown = None  # Toggle Close
                                    ui_handled = True

                            # D. Buttons (Settings Menu)
                            if not ui_handled:
                                for key, r in self.ui_buttons.items():
                                    if r.collidepoint(mx, my):
                                        # --- CHECK INPUT FOCUS ---
                                        if key == 'input_carousel_fade':
                                            self.active_input = 'carousel_fade'
                                            self.input_text = ""
                                            ui_handled = True
                                            continue
                                        elif key == 'input_video_offset':
                                            self.active_input = 'video_offset'
                                            self.input_text = ""  # Clear buffer
                                            ui_handled = True
                                            continue
                                        if key == 'add_file':
                                            self.get_files()
                                        elif key == 'add_folder':
                                            self.get_folder()
                                        elif key == 'save_list':
                                            self.save_playlist()
                                        elif key == 'load_list':
                                            self.load_playlist()
                                        elif key == 'clear_list':
                                            self.clear_playlist()
                                        elif key == 'font_up':
                                            self.font_size = min(48, self.font_size + 2)
                                            self.update_fonts()
                                            self.settings_changed = True
                                        elif key == 'font_down':
                                            self.font_size = max(8, self.font_size - 2)
                                            self.update_fonts()
                                            self.settings_changed = True
                                        elif key == 'toggle_settings':
                                            self.show_settings = not self.show_settings
                                        elif key == 'toggle_param_target':
                                            if self.settings_target == 'FG':
                                                self.settings_target = 'CLR'
                                            elif self.settings_target == 'CLR':
                                                self.settings_target = 'BG'
                                            else:
                                                self.settings_target = 'FG'
                                        elif key == 'toggle_peak_line':
                                            cur_mode = VISUAL_MODES[self.current_visual_mode]
                                            self.vis_params_sets[cur_mode]['show_line'] = not self.vis_params_sets[
                                                cur_mode].get('show_line', True)
                                            self.settings_changed = True
                                        elif key == 'toggle_warp_center':
                                            self.bg_params['hide_center'] = not self.bg_params.get('hide_center', False)
                                            self.settings_changed = True
                                        elif key == 'toggle_fullscreen':
                                            self.is_fullscreen = not self.is_fullscreen
                                            if self.is_fullscreen:
                                                # Switch to Exclusive Fullscreen (Game Mode)
                                                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                                            else:
                                                # Switch back to Windowed
                                                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                                            # IMPORTANT: Clear UI cache so it redraws at new size
                                            self.ui_surface_cache = None
                                        elif key == 'toggle_glow':
                                            self.bg_params['glow_enabled'] = not self.bg_params.get('glow_enabled', False)
                                            self.settings_changed = True
                                        ui_handled = True

                            # E. Toggles
                            if not ui_handled:
                                for key, r in self.ui_toggles.items():
                                    if r.collidepoint(mx, my):
                                        if key == 'bpm':
                                            self.show_bpm = not self.show_bpm
                                            self.settings_changed = True
                                        elif key == 'playlist_counter':
                                            self.show_playlist_counter = not self.show_playlist_counter
                                            self.settings_changed = True
                                        ui_handled = True

                            # F. Sliders (Settings Overlay)
                            if not ui_handled:
                                if self.settings_target == 'FG':
                                    target_dict = self.vis_params_sets[VISUAL_MODES[self.current_visual_mode]]
                                elif self.settings_target == 'CLR':
                                    target_dict = self.color_params_sets[COLOR_MODES[self.current_color_mode]]
                                else:
                                    target_dict = self.bg_params

                                for key, (rect, min_v, max_v) in self.param_slider_rects.items():
                                    if rect.collidepoint(mx, my):
                                        rel_x = mx - rect.x
                                        pct = max(0.0, min(1.0, rel_x / rect.width))
                                        target_dict[key] = min_v + (max_v - min_v) * pct
                                        self.settings_changed = True
                                        ui_handled = True

                        # --- 2. DOCK INTERACTIONS ---
                        if not ui_handled and 'toggle_settings' in self.ui_buttons:
                            if self.ui_buttons['toggle_settings'].collidepoint(mx, my):
                                self.show_settings = not self.show_settings
                                ui_handled = True

                        if not ui_handled:
                            if self.resize_handle_rect and self.resize_handle_rect.collidepoint(mx, my):
                                self.is_resizing_panel = True
                                ui_handled = True

                        # --- FIX: Add a new check here so ui_handled is actually used ---
                        if not ui_handled:
                            w_screen, h_screen = self.screen.get_size()
                            mouse_in_dock = my > (h_screen - self.ui_panel_height)

                            if mouse_in_dock or not self.show_settings:
                                if self.btn_play_rect and self.btn_play_rect.collidepoint(mx, my):
                                    self.paused = not self.paused
                                elif self.btn_next_rect and self.btn_next_rect.collidepoint(mx, my):
                                    self.next_song()
                                elif self.btn_prev_rect and self.btn_prev_rect.collidepoint(mx, my):
                                    self.prev_song()
                                elif self.btn_shuffle_rect and self.btn_shuffle_rect.collidepoint(mx, my):
                                    self.toggle_shuffle()
                                    self.settings_changed = True
                                elif self.btn_loop_once_rect and self.btn_loop_once_rect.collidepoint(mx, my):
                                    self.loop_once = not self.loop_once
                                    if self.loop_once:
                                        self.loop_forever = False  # Exclusive
                                        self.set_status("Loop Once: ON")
                                    else:
                                        self.set_status("Loop Once: OFF")
                                    self.settings_changed = True
                                elif self.btn_loop_forever_rect and self.btn_loop_forever_rect.collidepoint(mx, my):
                                    self.loop_forever = not self.loop_forever
                                    if self.loop_forever:
                                        self.loop_once = False  # Exclusive
                                        self.set_status("Loop Forever: ON")
                                    else:
                                        self.set_status("Loop Forever: OFF")
                                    self.settings_changed = True
                                elif self.seek_bar_rect and self.seek_bar_rect.collidepoint(mx, my):
                                    self.is_dragging_seek = True
                                    self.drag_progress = max(0.0, min(1.0, (
                                                mx - self.seek_bar_rect.x) / self.seek_bar_rect.width))
                                elif self.vol_bar_rect and self.vol_bar_rect.collidepoint(mx, my):
                                    self.is_dragging_vol = True
                                    self.volume = max(0.0,
                                                      min(1.0, (mx - self.vol_bar_rect.x) / self.vol_bar_rect.width))
                                    self.settings_changed = True
                                elif self.smooth_bar_rect and self.smooth_bar_rect.collidepoint(mx, my):
                                    self.is_dragging_smooth = True
                                    self.smoothing_factor = max(0.0, min(1.0, (
                                                mx - self.smooth_bar_rect.x) / self.smooth_bar_rect.width))
                                    self.settings_changed = True

                if event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    # Scrollbar Drag
                    if self.is_dragging_scrollbar and self.dropdown_track_rect:
                        options_len = 0
                        if self.active_dropdown == 'visual':
                            options_len = len(VISUAL_MODES)
                        elif self.active_dropdown == 'color':
                            options_len = len(COLOR_MODES)
                        elif self.active_dropdown == 'bar_style':
                            options_len = len(BAR_STYLES)
                        elif self.active_dropdown == 'bg':
                            options_len = len(BG_MODES)
                        elif self.active_dropdown == 'bar_style':
                            options_len = len(BAR_STYLES)
                        elif self.active_dropdown == 'bg' or self.active_dropdown == 'bg2':
                            options_len = len(BG_MODES)
                        elif self.active_dropdown == 'ui_pattern':
                            options_len = len(UI_PATTERN_MODES)
                        elif self.active_dropdown == 'sort':
                            options_len = len(SORT_MODES)
                        elif self.active_dropdown == 'font':
                            options_len = len(self.available_fonts)
                        elif self.active_dropdown == 'collapse_mode':
                            options_len = len(COLLAPSE_MODES)
                        elif self.active_dropdown == 'idle_mode':
                            options_len = len(IDLE_MODES)
                        elif self.active_dropdown == 'img_enabled':
                            options_len = len(BG_IMAGE_OPTIONS)
                        elif self.active_dropdown == 'img_anim':
                            options_len = len(BG_IMAGE_ANIMS)
                        elif self.active_dropdown == 'playlist':
                            options_len = len(self.playlist)
                        elif self.active_dropdown == 'color_cycle':
                            options_len = len(COLOR_CYCLE_MODES)

                        if options_len > self.dropdown_max_visible:
                            rel_y = my - self.dropdown_track_rect.y
                            track_h = self.dropdown_track_rect.height
                            pct = max(0.0, min(1.0, rel_y / track_h))
                            max_offset = options_len - self.dropdown_max_visible
                            self.dropdown_scroll_offset = int(pct * max_offset)

                    # Dock Sliders Drag
                    if self.is_dragging_seek:
                        self.drag_progress = max(0.0, min(1.0, (mx - self.seek_bar_rect.x) / self.seek_bar_rect.width))
                    if self.is_dragging_vol:
                        self.volume = max(0.0, min(1.0, (mx - self.vol_bar_rect.x) / self.vol_bar_rect.width))
                        self.settings_changed = True
                    if self.is_dragging_smooth:
                        self.smoothing_factor = max(0.0, min(1.0, (
                                    mx - self.smooth_bar_rect.x) / self.smooth_bar_rect.width))
                        self.settings_changed = True

                    # Overlay Sliders Drag
                    if self.show_settings and pygame.mouse.get_pressed()[0]:
                        if self.settings_target == 'FG':
                            target_dict = self.vis_params_sets[VISUAL_MODES[self.current_visual_mode]]
                        elif self.settings_target == 'CLR':
                            target_dict = self.color_params_sets[COLOR_MODES[self.current_color_mode]]
                        else:
                            target_dict = self.bg_params

                        for key, (rect, min_v, max_v) in self.param_slider_rects.items():
                            if rect.collidepoint(mx, my):
                                rel_x = mx - rect.x
                                pct = max(0.0, min(1.0, rel_x / rect.width))
                                target_dict[key] = min_v + (max_v - min_v) * pct
                                self.settings_changed = True

                    # Panel Resize
                    if self.is_resizing_panel:
                        new_h = self.screen.get_height() - my
                        self.ui_panel_height = max(self.min_panel_height, min(UI_PANEL_HEIGHT, new_h))
                        self.settings_changed = True

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_dragging_scrollbar = False
                        if self.is_dragging_seek:
                            self.is_dragging_seek = False
                            self.seek_request = int(self.current_duration * self.drag_progress)
                        self.is_dragging_vol = False
                        self.is_dragging_smooth = False
                        self.is_resizing_panel = False

                        # ONLY SAVE IF CHANGED
                        if self.settings_changed:
                            self.save_settings()
                            self.settings_changed = False

                if event.type == pygame.KEYDOWN:
                    # --- INPUT HANDLING ---
                    if self.active_input:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            # Commit Value
                            try:
                                if self.input_text:  # Only save if text exists
                                    val = float(self.input_text)

                                    if self.active_input == 'video_offset':
                                        if val < -1200: val = -1200
                                        self.bg_params['video_offset'] = val
                                        self.settings_changed = True

                                    elif self.active_input == 'carousel_fade':
                                        if val < 0: val = 0.0
                                        self.bg_params['carousel_fade'] = val
                                        self.settings_changed = True
                            except ValueError:
                                pass

                            self.active_input = None  # Unfocus
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.active_input = None
                        else:
                            # Allow numbers, dot, AND NEGATIVE SIGN
                            allowed = event.unicode.isnumeric() or event.unicode == '.' or event.unicode == '-'
                            if allowed:
                                # Prevent multiple dots
                                if event.unicode == '.' and '.' in self.input_text:
                                    pass
                                # Prevent minus sign unless it's the first character
                                elif event.unicode == '-' and len(self.input_text) > 0:
                                    pass
                                else:
                                    self.input_text += event.unicode
                    elif event.key == pygame.K_F11:
                        self.is_fullscreen = not self.is_fullscreen
                        if self.is_fullscreen:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                        self.ui_surface_cache = None
                    elif event.key == pygame.K_z or event.key == pygame.K_x:
                        self.color_flip = not self.color_flip
                        state = "Flipped" if self.color_flip else "Normal"
                        self.set_status(f"Colors: {state}")
                    elif event.key == pygame.K_TAB:
                        self.show_settings = not self.show_settings
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_n:
                        self.next_song()
                    elif event.key == pygame.K_p:
                        self.prev_song()

            # DRAW BACKGROUND
            self.draw_background()

            # 1. Determine Target Data
            if self.playing and not self.paused:
                target_fft = self.calculate_fft()
                self.displayed_fft = target_fft
                # Reset collapse state
                self.collapse_start_time = None
                self.fft_snapshot = target_fft.copy()
            else:
                # 2. Apply Custom Collapse Animation
                if self.collapse_start_time is None:
                    self.collapse_start_time = time.time()
                    self.fft_snapshot = self.displayed_fft.copy()

                # GET PARAMS FOR CURRENT MODE
                cur_mode = VISUAL_MODES[self.current_visual_mode]
                params = self.vis_params_sets[cur_mode]

                # Duration controlled by 'decay' slider (0.1s to 3.0s)
                duration = params.get('decay', 1.0)
                elapsed = time.time() - self.collapse_start_time

                if elapsed >= duration:
                    self.displayed_fft = np.zeros(60)
                else:
                    progress = elapsed / duration
                    c_mode = params.get('collapse_mode', 0)

                    # Calculate how much has collapsed (0.0 to 1.0)
                    drop_factor = self.get_ease_value(progress, c_mode)

                    # Apply to snapshot
                    self.displayed_fft = self.fft_snapshot * (1.0 - drop_factor)

            # DRAW VISUALS (Bars)
            self.draw_visuals(self.displayed_fft)

            # DRAW UI (Dock)
            self.draw_ui()

            # DRAW GLOW LAST (So it overlays the UI)
            self.draw_foreground_glow()

            pygame.display.flip()

        # --- CLEANUP LINES ---
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass

        # Check if self.p exists before terminating
        if self.p is not None:
            try:
                self.p.terminate()
            except:
                pass
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    MusicVisualizer().run()