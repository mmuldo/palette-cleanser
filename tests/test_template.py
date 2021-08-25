from palettecleanser import template
from palettecleanser import theme
from palettecleanser import palette
from palettecleanser import config
import yaml
import os
import jinja2 as j2

class TestYAMLTemplateFile:
    def test_generate_signature(self):
        print(template.YAMLTemplateFile('randompath').generate_signature())

    def test_template(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        monkeypatch.setattr(config, 'templates_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/templates'))
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data/fake_home')})
        env = j2.Environment(loader=j2.FileSystemLoader(config.templates_dir))
        monkeypatch.setattr(template, 'env', env)


        cs = [palette.Color(30*i, 30*i, 30*i) for i in range(7)]
        p = palette.Palette(cs, 'test_template_palette0')
        p.save()
        t = theme.Theme('test_template_theme0', ['test_template_palette0'], '')
        tmpl = template.YAMLTemplateFile('example-yaml1.yml').template(t)

        with open(os.path.join(os.environ['HOME'], 'example-yaml1.yml')) as f:
            assert yaml.load(f, Loader=yaml.Loader) == {'colors': ['#3c3c3c']}

    def test_is_templated_false(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data/fake_home')})
        assert not template.YAMLTemplateFile('example-yaml0.yml').is_templated()

    def test_is_templated_true(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data/fake_home')})
        assert template.YAMLTemplateFile('example-yaml1.yml').is_templated()

class TestTemplate:
    def test_from_path(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data/fake_home')})
        assert template.from_path('some-config-dir', ['blah.txt']) == template.TemplateDirectory('some-config-dir', [template.YAMLTemplateFile('some-config-dir/example-yaml2.yml')])

    def test_template_managed(self, monkeypatch):
        monkeypatch.setattr(config, 'config_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config'))
        monkeypatch.setattr(config, 'palettes_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/palettes'))
        monkeypatch.setattr(config, 'templates_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/templates'))
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data/fake_home')})
        env = j2.Environment(loader=j2.FileSystemLoader(config.templates_dir))
        monkeypatch.setattr(template, 'env', env)

        t = theme.Theme('test_template_theme0', ['test_template_palette0'], '')
        template.template_managed(t)

        with open(os.path.join(os.environ['HOME'], 'sample-config.yml')) as f1, open(os.path.join(os.environ['HOME'], 'some-config-dir/example-yaml2.yml')) as f2:
            assert yaml.load(f1, Loader=yaml.Loader) == '#b4b4b4'
            assert yaml.load(f2, Loader=yaml.Loader) == '#969696'
