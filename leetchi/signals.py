from blinker import Namespace


signals = Namespace()

request_finished = signals.signal('request_finished')

request_started = signals.signal('request_started')

pre_save = signals.signal('pre_save')

post_save = signals.signal('pre_save')
