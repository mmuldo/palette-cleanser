from palettecleanser import template
from palettecleanser import theme
from palettecleanser import palette
from palettecleanser import config
import yaml
import os
import jinja2 as j2

class TestTemplateFile:
    def test_generate_signature_hs(self):
        assert template.TemplateFile('test.hs').generate_signature() == f'-- {template.templated_signature}\n'

    def test_generate_signature_rasi(self):
        assert template.TemplateFile('test.rasi').generate_signature() == f'/* {template.templated_signature} */\n'

    def test_generate_signature_vimrc(self):
        assert template.TemplateFile('.vimrc').generate_signature() == f'" {template.templated_signature}\n'

    def test_generate_signature_yaml(self):
        assert template.TemplateFile('.yml').generate_signature() == f'# {template.templated_signature}\n'

    def test_generate_signature_default(self):
        assert template.TemplateFile('').generate_signature() == f'# {template.templated_signature}\n'

    def test_create(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        tmpl_dir_path = os.path.join(os.path.dirname(__file__), 'test_data', 'fake_config', 'templates')
        monkeypatch.setattr(config, 'templates_dir', tmpl_dir_path)

        template.TemplateFile('test_template_template0').create()
        with open(os.path.join(tmpl_dir_path, 'test_template_template0.j2'), 'r') as tmpl_file:
            assert tmpl_file.read() == '{{ default }}\ncurrent\n{{ overwrite }}\n'

    def test_create_missing(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        tmpl_dir_path = os.path.join(os.path.dirname(__file__), 'test_data', 'fake_config', 'templates')
        monkeypatch.setattr(config, 'templates_dir', tmpl_dir_path)

        template.TemplateFile('test_template_template1').create()
        assert os.path.exists(os.path.join(tmpl_dir_path, 'test_template_template1.j2'))

    def test_template(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        tmpl_dir_path = os.path.join(os.path.dirname(__file__), 'test_data', 'fake_config', 'templates')
        monkeypatch.setattr(config, 'templates_dir', tmpl_dir_path)
        env = j2.Environment(loader=j2.FileSystemLoader(config.templates_dir))
        monkeypatch.setattr(template, 'env', env)

        t = theme.Theme('theme name', [], '', {'test': 'hi'})
        template.TemplateFile('test_template_template2.yml').template(t)

        with open(os.path.join(os.environ['HOME'], 'test_template_template2.yml')) as f:
            assert yaml.load(f, Loader=yaml.Loader) == {'colors': ['hi']}

    def test_is_templated_false(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        assert not template.TemplateFile('test_template_template0').is_templated()

    def test_is_templated_true(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        assert template.TemplateFile('test_template_template2.yml').is_templated()

    def test_is_templated_missing(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        assert template.TemplateFile('test_template_template1').is_templated()

class TestTemplateDirectory:
    def test_create(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        tmpl_dir_path = os.path.join(os.path.dirname(__file__), 'test_data', 'fake_config', 'templates')
        monkeypatch.setattr(config, 'templates_dir', tmpl_dir_path)

        template.TemplateDirectory('test_template_dir', [
            template.TemplateFile('test_template_dir/test_template_template3.rasi'),
            template.TemplateFile('test_template_dir/test_template_template4.hs')
        ]).create()
        with open(os.path.join(tmpl_dir_path, 'test_template_dir/test_template_template3.rasi.j2'), 'r') as tmpl_file:
            assert tmpl_file.read() == '{{ test }}\n'
        with open(os.path.join(tmpl_dir_path, 'test_template_dir/test_template_template4.hs.j2'), 'r') as tmpl_file:
            assert tmpl_file.read() == '{{ test }}\n'

    def test_template(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data', 'fake_home')})
        tmpl_dir_path = os.path.join(os.path.dirname(__file__), 'test_data', 'fake_config', 'templates')
        monkeypatch.setattr(config, 'templates_dir', tmpl_dir_path)
        env = j2.Environment(loader=j2.FileSystemLoader(config.templates_dir))
        monkeypatch.setattr(template, 'env', env)

        t = theme.Theme('theme name', [], '', {'test': 'hi'})
        template.TemplateDirectory('test_template_dir2', [
            template.TemplateFile('test_template_dir2/test_template_template3.rasi'),
            template.TemplateFile('test_template_dir2/test_template_template4.hs')
        ]).template(t)

        with open(os.path.join(os.environ['HOME'], 'test_template_dir2/test_template_template3.rasi'), 'r') as tmpl_file:
            assert tmpl_file.read() == '/* @palette-cleanser */\nhi'
        with open(os.path.join(os.environ['HOME'], 'test_template_dir2/test_template_template4.hs'), 'r') as tmpl_file:
            assert tmpl_file.read() == '-- @palette-cleanser\nhi'


class TestTemplate:
    def test_from_path(self, monkeypatch):
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data/fake_home')})
        tmpl_dir_path = os.path.join(os.path.dirname(__file__), 'test_data', 'fake_config', 'templates')
        monkeypatch.setattr(config, 'templates_dir', tmpl_dir_path)

        assert template.from_path(
            config.templates_dir,
            'test_template_dir2',
            ['test_template_template3.rasi']
        ) == template.TemplateDirectory(
            'test_template_dir2',
            [template.TemplateFile('test_template_dir2/test_template_template4.hs')]
        )

    def test_template_managed(self, monkeypatch):
        monkeypatch.setattr(config, 'config_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config'))
        monkeypatch.setattr(config, 'templates_dir', os.path.join(os.path.dirname(__file__), 'test_data/fake_config/templates'))
        monkeypatch.setattr(os, 'environ', os.environ | {'HOME': os.path.join(os.path.dirname(__file__), 'test_data/fake_home')})
        env = j2.Environment(loader=j2.FileSystemLoader(config.templates_dir))
        monkeypatch.setattr(template, 'env', env)

        t = theme.Theme('theme name', [], '', {'test': 'hi'})
        template.template_managed(t)

        with open(os.path.join(os.environ['HOME'], 'test_template_dir3/test_template_template5.yml')) as f:
            assert yaml.load(f, Loader=yaml.Loader) == 'hi'

        assert not os.path.exists(os.path.join(os.environ['HOME'], 'test_template_dir3/test_template_template6.yml'))
