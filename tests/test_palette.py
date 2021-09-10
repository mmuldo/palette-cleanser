from palettecleanser import palette
from palettecleanser import config
from PIL import Image
import os
import pytest

class TestColor:
    def test_distance(self):
        color0 = palette.Color(255, 0, 19)
        color1 = palette.Color(50, 45, 70)
        assert round(color0.distance(color1), ndigits=3) == 215.988

    def test_closest(self):
        color = palette.Color(3, 254, 253)

        # cyan has index 6 in base_colors
        assert color.closest(palette.ansi_normal_palette.colors) == 6

    def test_tone_darken(self):
        color = palette.Color(40, 50, 60)
        assert color.tone(50, False) == palette.Color(20, 25, 30)

    def test_tone_lighten(self):
        color = palette.Color(205, 215, 225)
        assert color.tone(50, True) == palette.Color(230, 235, 240)

    def test_tone_darken_100(self):
        color = palette.Color(40, 50, 60)
        assert color.tone(100, False) == palette.Color(0, 0, 0)

    def test_tone_lighten_100(self):
        color = palette.Color(40, 50, 60)
        assert color.tone(100, True) == palette.Color(255, 255, 255)

    def test_spectrum(self):
        color0 = palette.Color(100, 50, 0)
        color1 = palette.Color(0, 50, 100)
        assert color0.spectrum(color1, 6) == [
            palette.Color(100, 50, 0),
            palette.Color(80, 50, 20),
            palette.Color(60, 50, 40),
            palette.Color(40, 50, 60),
            palette.Color(20, 50, 80),
            palette.Color(0, 50, 100)
        ]

    def test_str(self):
        color = palette.Color(255, 37, 104)
        assert str(color) == '#ff2568'

    def test_str(self):
        color = palette.Color(255, 37, 104)
        print(color)

    def test_from_hex(self):
        color = palette.from_hex('#dd4c4f')
        assert color == palette.Color(221, 76, 79)

    def test_from_hex_error(self):
        with pytest.raises(palette.MalformedHexError) as e:
            palette.from_hex('fjdoasfdoasj')


class TestPalette:
    def test_tone(self):
        p = palette.Palette([palette.Color(0, 10, 15), palette.Color(40, 10, 5)])
        assert p.tone(50, False) == palette.Palette([palette.Color(0, 5, 8), palette.Color(20, 5, 3)])

    def test_str(self):
        p = palette.Palette([palette.Color(0, 170, 91), palette.Color(40, 10, 255)], 'hi')
        print()
        print(p)

    def test_from_hexes(self):
        p = palette.from_hexes(['000A0F', '280A05'], 'hi')
        assert p == palette.Palette([palette.Color(0, 10, 15), palette.Color(40, 10, 5)], 'hi')

    def test_from_hexes_error(self):
        with pytest.raises(palette.MalformedHexError) as e:
            palette.from_hexes(['000a0f', 'fjdoasfdoasj'])

    def test_save_overwrite(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        p = palette.Palette([palette.Color(105, 10, 165), palette.Color(40, 140, 5)], 'test')
        p.save()

    def test_save_dont_overwrite(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'n')
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        p = palette.Palette([palette.Color(110, 10, 165), palette.Color(40, 140, 5)], 'test')
        p.save()

    def test_from_config_exists(self, monkeypatch):
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        p = palette.Palette([palette.Color(105, 10, 165), palette.Color(40, 140, 5)], 'test')
        p0 = palette.from_config('test')
        assert p == p0

    def test_from_config_doesnt_exist(self, monkeypatch):
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        with pytest.raises(palette.PaletteNotFoundError) as e:
            palette.from_config('garbage garbage garbage')

    def test_from_ordered_colors_match(self):
        with Image.open(os.path.join(os.path.dirname(__file__), 'test_data/muruusa-mountain.jpg')) as img:
            p = palette.from_image(img, algorithm=palette.from_ordered_colors_match)
            print()
            print(p)

    def test_from_ordered_colors_find(self):
        with Image.open(os.path.join(os.path.dirname(__file__), 'test_data/muruusa-mountain.jpg')) as img:
            p = palette.from_image(img, algorithm=palette.from_ordered_colors_find)
            print()
            print(p)
