"""Module containing core infrastructure for testscripts.  """

import abc

class TestScript:
    """Class representing current run of testscript"""
    def __init__(self):
        """asd"""

    def register(self, module):
        """asd"""

    def fuck_pylint(self):
        """Stupid shit"""

    def add_event(self, module_ref, event):
        pass

# class TestScriptProxy: # Maybe later



class Module(abc.ABC):
    """Class serving as module for TestScript class"""
    def __init__(self, name: str):
        assert name and str(name)
        self.object_name = str(name)
        self.owner = None

    def register(self, parent_object: TestScript):
        """Registers parent, so module can send events to them"""
        assert not self.owner
        self.owner = parent_object

    def send(self, event):
        """Do somethings"""
        if self.owner:
            self.owner.

    def callback(self, event):
        # Called on full circle
        return True

    def handle_event(self, event):
        # Decide whether to accept or pass
        return self.handle_internal(event)

    @abc.abstractmethod
    def handle_internal(self, event):
        # This should be overridden
        return True

class Event:
    # Handled true/false # TestScript must know
    # Return to ....
    # For whom
    # Payload
    # Private data
    # Response

    def __init__(self):
        self.responses = []

    def add_response(self, data):
        raise NotImplementedError("Not yet")
        # self.responses.append(data)
    



