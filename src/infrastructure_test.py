import pytest
import unittest.mock

import infrastructure

class MyTestEvent1(infrastructure.Event):
    pass

class MyTestEvent2(infrastructure.Event):
    pass

class MySubEvent(MyTestEvent1):
    def __init__(self):
        super().__init__()

class MySubSubEvent(MySubEvent):
    def __init__(self):
        super().__init__()

class MyTestModule(infrastructure.Module):
    def __init__(self):
        super().__init__()
        self.count_calls = 0
        self.register_event('compiler')

    def handle_internal(self, event):
        self.count_calls += 1
        self.send(MyTestEvent2())
        return True

######################################
############## TESTS #################
######################################

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


def test_event_regex():
    re = infrastructure.build_event_regex("aa*bb")
    assert re.match('aabb')
    assert re.match('aa.bb')
    assert re.match('aa.asdbb')
    assert re.match('aa.asd.bb')
    assert not re.match('ab.aa.bb')
    re = infrastructure.build_event_regex("*bb")
    assert re.match('aabb')
    assert re.match('ab.aa.bb')
    assert not re.match("b")
    re = infrastructure.build_event_regex("*")
    assert re.match('asd')
    assert re.match('')
    assert not re.match(' ')
    re = infrastructure.build_event_regex("")
    assert not re.match('a')

def test_get_event_name():
    name1 = infrastructure.get_event_name(MyTestEvent1)
    assert name1 == 'MyTestEvent1'
    name2 = infrastructure.get_event_name('aa')
    assert name2 == 'aa'