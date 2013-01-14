(function(root, $, _) {
    "use strict";

    var mapping, source, parsed;

    function paddy(n, p) {
        var pad = new Array(1 + p).join('0');
        return (pad + n).slice(-pad.length);
    }

    var bind = function (el, query) {
        el.mouseover(function() {
            $(query).addClass('source_highlighted');
        });
        el.mouseout(function() {
            $(query).removeClass('source_highlighted');
        });
        el.click(function() {
            $('.source_line').removeClass('source_clicked');
            $(query).addClass('source_clicked');
        });
    };

    var make_line = function(n, m, line, all) {
        var css = 'line_' + m;
        var query = '.' + css;
        var line_num = paddy(n, (""+all.length).length);

        var el = $('<div class="source_line ' + css + '" />');
        el.append($('<span class="line_num" />').text(line_num));
        el.append(root.document.createTextNode(line));

        bind(el, query);

        return el;
    };

    var make_stack = function (frame) {
        var n = mapping[frame[1] - 1];
        var css = 'line_' + n;

        var el = $('<div class="source_line ' + css + '"/>');

        var src = source[n].split(' ');
        var last = src[src.length - 1];
        if (last[0] == '@') {
            frame.push(last);
        }

        el.text('[' + frame.join(', ') + ']');

        bind(el, '.' + css);

        return el;
    };

    var make_current = function (pos) {
        var css = 'line_' + mapping[pos - 1];
        var el = $('<div class="source_line current_line ' + css + '"/>');

        var frame = ['CURRENT', pos];
        el.text('[' + frame.join(', ') + ']');

        var query = '.' + css;
        $(query).addClass('current_line');
        bind(el, query);

        return el;
    };

    var make_mapping = function(reverse) {
        var i;
        mapping = []

        for (i = 0; i < source.length; i++) {
            mapping[reverse[i]] = i;
        }

        for (i = 0; i < parsed.length; i++) {
            if (mapping[i] == undefined) {
                mapping[i] = mapping[i-1];
            }
        }
    };

    root.load_debug = function (data) {
        var i;

        source = data.code.raw.split('\n');
        parsed = data.code.lines;

        make_mapping(data.code.mapping);

        for (i in source) {
            $('#raw_code').append(make_line(i, i, source[i], source));
        }

        for (i in parsed) {
            var code = parsed[i].join(" ");
            $('#parsed_code').append(make_line(i, mapping[i], code, parsed));
        }

        var exe = data.stack.exe;
        for (i in exe) {
            $('#stack').append(make_stack(exe[i]));
        }

        $('#stack').append(make_current(data.stack.pos));
    };
})(this, jQuery, _);
