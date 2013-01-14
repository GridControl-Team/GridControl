(function(root, $, _) {
	"use strict";

	var mapping, source, parsed;

	var bind = function ($el, query) {
		$el.mouseover(function() {
			$(query).addClass('source_highlighted');
		});
		$el.mouseout(function() {
			$(query).removeClass('source_highlighted');
		});
		$el.click(function() {
			$('.source_line').removeClass('source_clicked');
			$(query).addClass('source_clicked');
		});
	};

	var make_line = function(n, m, line, all) {
		var css = 'line_' + m;
		var query = '.' + css;
		var line_num = _.str.pad(n, (""+all.length).length, '0', 'left');

		var $el = $('<div class="source_line ' + css + '" />');
		$el.append($('<span class="line_num" />').text(line_num));
		$el.append(root.document.createTextNode(line));

		bind($el, query);

		return $el;
	};

	var make_stack = function (frame) {
		var n = mapping[frame[1] - 1];
		var css = 'line_' + n;

		var $el = $('<div class="source_line ' + css + '"/>');

		var src = source[n].split(' ');
		var last = src[src.length - 1];
		if (last[0] == '@') {
			frame.push(last);
		}

		$el.text('[' + frame.join(', ') + ']');

		bind($el, '.' + css);

		return $el;
	};

	var make_current = function (pos) {
		var css = 'line_' + mapping[pos - 1];
		var $el = $('<div class="source_line current_line ' + css + '"/>');

		var frame = ['CURRENT', pos];
		$el.text('[' + frame.join(', ') + ']');

		var query = '.' + css;
		$(query).addClass('current_line');
		bind($el, query);

		return $el;
	};

	var make_mapping = function(reverse) {
		mapping = []

		_.each(_.range(source.length), function(v) {
			mapping[reverse[v]] = v;
		});

		_.each(_.range(parsed.length), function(v) {
			if (_.isUndefined(mapping[v])) {
				mapping[v] = mapping[v-1];
			}
		});
	};

	root.load_debug = function (data) {
		source = data.code.raw.split('\n');
		parsed = data.code.lines;

		make_mapping(data.code.mapping);

		_.each(source, function(v, k) {
			$('#raw_code').append(make_line(k, k, v, source));
		});

		_.each(parsed, function(v, k) {
			var code = v.join(" ");
			$('#parsed_code').append(make_line(k, mapping[k], code, parsed));
		});

		_.each(data.stack.exe, function(v, k) {
			$('#stack').append(make_stack(v));
		});

		$('#stack').append(make_current(data.stack.pos));
	};
})(this, jQuery, _);
