from json import dump, load
class _default_setting:
	class Display:
		timeaxis_height = 50
		timeaxis_float = 8
		wave_height = 25
		wave_spacing = 6
		wave_stride = wave_height + wave_spacing
		wave_transit = 2
		initial_wave_width = 2000
		maximal_zoom = 6
		display_text_threshold = 10
		text_margin = 2
		horizontal_scroll_flip = True

_setting = None

def GetSetting(fname = str()):
	global _setting
	if _setting is None:
		_setting = _default_setting
		# TODO load configurations with fname and update _setting
	return _setting
