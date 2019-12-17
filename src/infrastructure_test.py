"""Tests for infrastructure module"""
import unittest.mock
import tempfile
import io

import pytest

import infrastructure

# pylint: disable=missing-docstring
# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods

class MyTestEvent1(infrastructure.Event):
    pass

class MyTestEvent2(infrastructure.Event):
    pass

class MySubEvent(MyTestEvent1):
    pass

class MySubSubEvent(MySubEvent):
    pass

class MyTestModule(infrastructure.Module):
    def __init__(self, name=None):
        if not name:
            name = "Test"
        super().__init__(name)

        self.count_calls = 0
        self.register_event('compiler')

    def handle_internal(self, event):
        self.count_calls += 1
        self.send(MyTestEvent2())
        return True

@pytest.fixture
def settings():
    return infrastructure.ModuleSettings()

class MyParser1(infrastructure.SettingsParser):
    def is_valid(self, value):
        if value in ['aa', 'bb', True, 'abc']:
            return True
        return False

    def get_options(self):
        return ['aa', 'bb', True]

class MyDefaultParser(MyParser1):
    @property
    def default(self):
        return 'abc'

######################################
############## TESTS #################
######################################

class TestTestScripts():
    INI1 = (
        f"[1]\n"
        f"module = MyTestModule\n"
    )

    INI2 = (
        f"[2]\n"
        f"module = WeirdLogger\n"
    )

    def test_non_exist_module_creation(self):
        ini = self.INI1 + self.INI2
        script = infrastructure.TestScript()
        with pytest.raises(ValueError):
            fake_file = io.StringIO(initial_value=ini)
            script.load_ini_settings(fake_file)

    def test_valid_module_creation(self):
        script = infrastructure.TestScript()
        script.add_class(MyTestModule)
        fake_file = io.StringIO(initial_value=self.INI1)
        script.load_ini_settings(fake_file)

    def test_invalid_module_creation(self):
        script = infrastructure.TestScript()
        script.add_class(MyTestModule)
        fake_file = io.StringIO(initial_value=self.INI2)
        with pytest.raises(ValueError):
            script.load_ini_settings(fake_file)

    @pytest.mark.skip
    def test_parse_settings_from_dict(self):
        pass 

    @pytest.mark.skip
    def test_run_notifications(self):
        """Check whether notifications are run with high priority"""
        pass


class TestEvent:
    def test_all_mro(self):
        event = MySubSubEvent()
        names = set(event.names)
        expected = ['MySubSubEvent', 'MySubEvent',
                    'MyTestEvent1', 'Event', 'object']
        assert set(expected) == names

    def test_name(self):
        event = infrastructure.Event()
        assert event.name == 'Event'


class TestModule:
    @pytest.mark.skip
    def test_module_event_wildcard(self):
        pass

    def test_add_event_from_module(self):
        main = infrastructure.TestScript()
        event1 = MyTestEvent1('compiler')
        module1 = MyTestModule()
        mock = unittest.mock.Mock()
        module1.register_event('MyTestEvent*', callback=mock)
        main.register(module1)
        main.add_event(event1)
        main.run()
        assert module1.count_calls == 1
        assert mock.call_count == 1

    def test_event_call_custom_name(self):
        main = infrastructure.TestScript()
        event1 = MyTestEvent1('compiler')
        event2 = MyTestEvent1()
        event3 = MyTestEvent2()
        module1 = MyTestModule()
        main.register(module1)
        main.add_event(event1)
        main.run()
        assert module1.count_calls == 1
        main.run()
        assert module1.count_calls == 1
        main.add_event(event1)
        main.run()
        assert module1.count_calls == 2
        main.add_event(event2)
        main.add_event(event1)
        main.add_event(event3)
        main.run()
        assert module1.count_calls == 3

    @pytest.mark.skip("Subclassing events not yet implemented")
    def test_subclass_event(self):
        assert False

    def test_register_event(self):
        module = MyTestModule()
        module.register_event(MyTestEvent1)
        assert not module.handle_event(MyTestEvent2())
        assert module.handle_event(MyTestEvent1())
        assert not module.handle_event(MyTestEvent2())


class TestSettings:
    def test_one_option(self):
        settings = infrastructure.ModuleSettings()
        settings.add_options('key', [True])
        settings.add_options('key2', ['asd'])
        settings.add_options('key3', [None])
        settings['key'] = 'True'
        settings['key2'] = 'asd'
        assert settings['key'] == True
        assert settings['key2'] == 'asd'
        with pytest.raises(ValueError):
            settings['key3'] = None
        with pytest.raises(ValueError):
            settings['key3']
        settings['key3'] = 'None'
        assert settings['key3'] == None

    def test_multiple_options(self):
        settings = infrastructure.ModuleSettings()
        settings.add_options('key', [True, False, None])
        settings['key'] = 'False'
        assert settings['key'] == False
        settings.add_options('key 2', [True, 'abc'])
        settings['key 2'] = 'abc'
        assert settings['key 2'] == 'abc'
        settings['key'] = 'None'
        assert settings['key'] == None

    def test_parser(self):
        settings = infrastructure.ModuleSettings()
        settings.add_parser('key', MyParser1())
        settings['key'] = 'aa'
        assert settings['key'] == 'aa'
        with pytest.raises(ValueError):
            settings['key'] = 'ab'

    def test_default_parser(self):
        settings = infrastructure.ModuleSettings()
        settings.add_parser('key', MyDefaultParser())
        assert settings['key'] == 'abc'
        with pytest.raises(ValueError):
            settings['key'] = 'ab'
        settings['key'] = 'aa'
        assert settings['key'] == 'aa'

    def test_ini_format(self):
        settings = infrastructure.ModuleSettings()
        expect = { '# key1' : 'True # False',
                    'key2'  : 'False # True'}
        settings.add_options('key1', [False, True], default=True)
        settings.add_options('key2', ['False', 'True'])
        assert settings.get_ini_dict() == expect

    @pytest.mark.skip
    def test_ini_format_parser(self):
        pass

    def test_bool(self):
        settings = infrastructure.ModuleSettings()
        settings.add_options('key3', [None], default=None)
        assert settings
        settings.add_options('key1', [True])
        settings.add_options('key2', ['asd'])
        assert not settings
        settings['key1'] = 'True'
        assert not settings
        settings['key2'] = 'asd'
        assert settings

    @pytest.mark.skip
    def test_array_access(self):
        pass

    def test_default_option(self):
        settings = infrastructure.ModuleSettings()
        settings.add_options('key2', [True, 'f', None], default=None)
        assert settings['key2'] == None
        settings['key2'] = 'f'
        assert settings['key2'] == 'f'

class TestConsoleWriter:
    def test_notification(self):
        pass

def test_file_name_parser():
    fp1 = infrastructure.FileNameParser()
    fp2 = infrastructure.FileNameParser(accept_ne=True)
    with tempfile.NamedTemporaryFile("w") as f:
        with pytest.raises(ValueError):
            fp1.is_valid(f.name + "a")
        assert fp2.is_valid(f.name + "a")
        assert fp1.is_valid(f.name)
    assert list(fp1.get_options())

def test_event_regex():
    regex = infrastructure.build_wildcard_regex("aa*bb")
    assert regex.match('aabb')
    assert regex.match('aa.bb')
    assert regex.match('aa.asdbb')
    assert regex.match('aa.asd.bb')
    assert not regex.match('ab.aa.bb')
    regex = infrastructure.build_wildcard_regex("*bb")
    assert regex.match('aabb')
    assert regex.match('ab.aa.bb')
    assert not regex.match("b")
    regex = infrastructure.build_wildcard_regex("*")
    assert regex.match('asd')
    assert regex.match('')
    assert not regex.match(' ')
    regex = infrastructure.build_wildcard_regex("")
    assert not regex.match('a')

def test_get_event_name():
    name1 = infrastructure._get_event_name(MyTestEvent1)
    assert name1 == 'MyTestEvent1'
    name2 = infrastructure._get_event_name('aa')
    assert name2 == 'aa'

@pytest.mark.skip
def test_get_valid_event(self):
    pass

@pytest.mark.skip
def test_set_formatter(self):
    pass
