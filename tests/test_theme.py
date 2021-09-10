from palettecleanser import palette
from palettecleanser import theme
from palettecleanser import config
from PIL import Image
import os
import pytest

class TestTheme:
    def test_table(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        p0 = palette.Palette([palette.Color(0, 10, 15), palette.Color(40, 10, 5)], 'hi')
        p0.save()
        p1 = palette.Palette([palette.Color(105, 10, 165), palette.Color(40, 140, 5)], 'test')
        p1.save()

        t = theme.Theme('hello', ['hi', 'test'], 'test_data/muruusa-mountain.jpg')
        print()
        print(t)

    def test_from_image(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        with Image.open(os.path.join(os.path.dirname(__file__), 'test_data/muruusa-mountain.jpg')) as img:
            t = theme.from_image(img, 'muruusa3')
            print()
            print(t)

    def test_from_config(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        monkeypatch.setattr(config, 'themes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/themes'))
        p0 = palette.Palette([palette.Color(0, 10, 15), palette.Color(40, 10, 5)], 'hi')
        p0.save()
        p1 = palette.Palette([palette.Color(105, 10, 165), palette.Color(40, 140, 5)], 'test')
        p1.save()

        t = theme.Theme('hello', ['hi', 'test'], 'test_data/muruusa-mountain.jpg', {'blah': 1})
        t.save()
        t0 = theme.from_config('hello')
        assert t == t0
