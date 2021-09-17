# interface for LexieDevice and driver classes
# every possible action/attribute must be implemented here
# LexieDevice must import a driver based on product info
# for every possible action, LexieDevice must check during init, if it's implemented in the driver
# if yes, then call the action in the driver
# if no, throw a "NotSupportedException"
# Driver only needs to implement actions that are actually callable on device.

class ILexieDevice:
    """ Interface for LexieDevice and Driver devices """
    def action_turn(self, ison:bool): #pylint: disable=no-self-use # this is an interface...
        """ turn relay on . implement param: relay no. """
    def action_toggle(self): #pylint: disable=no-self-use # this is an interface...
        """ toggle relay. implement param: relay no. """
    def get_status(self):
        """  get relay status """
