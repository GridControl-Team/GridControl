(function(root, $, _) {
	var getCookie = function (name) {
			var cookieValue = null;
			if (document.cookie && document.cookie !== '') {
					var cookies = document.cookie.split(';');
					var i;
					for (i = 0; i < cookies.length; i++) {
							var cookie = jQuery.trim(cookies[i]);
							// Does this cookie string begin with the name we want?
							if (cookie.substring(0, name.length + 1) == (name + '=')) {
									cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
									break;
							}
					}
			}
			return cookieValue;
	}
	var csrftoken = getCookie('csrftoken');

	var csrfSafeMethod = function (method) {
			// these HTTP methods do not require CSRF protection
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}
	var sameOrigin = function(url) {
			// test that a given url is a same-origin URL
			// url could be relative or scheme relative or absolute
			var host = document.location.host; // host + port
			var protocol = document.location.protocol;
			var sr_origin = '//' + host;
			var origin = protocol + sr_origin;
			// Allow absolute or scheme relative URLs to same origin
			return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
					(url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
					// or any other URL that isn't scheme relative or absolute i.e relative.
					!(/^(\/\/|http:|https:).*/.test(url));
	}
	$.ajaxSetup({
			beforeSend: function(xhr, settings) {
					if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
							// Send the token to same-origin, relative URLs only.
							// Send the token only if the method warrants CSRF protection
							// Using the CSRFToken value acquired earlier
							xhr.setRequestHeader("X-CSRFToken", csrftoken);
					}
			}
	});

	var GC = !root.GC ? (root.GC = {}) : root.GC;

	GC.Screen = function(e) {
		this.$el = $(e);
		this.user_map = {};
		this.userid = this.$el.attr("data-userid");
		$("#grid_panic .hide_panic").on("click", _.bind(this.hide_panic, this));
	};

	var screen = GC.Screen.prototype;

	screen.raise_exception = function(msg) {
		var $panic = $("#grid_panic");
		$("pre", $panic).text(msg);
		$panic.slideDown();
	};

	screen.hide_panic = function(evt) {
		var $panic = $("#grid_panic");
		$panic.fadeOut();
	};

	screen.update_usernames = function(usernames) {
		this.user_map = usernames;
	};

	screen.get_username = function(id) {
		return this.user_map[id];
	};

	screen.update_scores = function(scores) {
		var $score = $("#grid_scores ul");
		$score.empty();
		_.each(scores, function(v,k ){
			username = this.get_username(k);
			var $li = $("<li>");
			$li.text(username);
			var $span = $("<span>");
			$span.text(v);
			$li.append($span);
			$score.append($li);
		}, this);
	};

	screen.update_map = function(resource_map) {
		console.log("Updating map");
		this.$el.empty();
		_.each(resource_map, function(row) {
			_.each(row, function(v) {
				if (v === 1) {
					this.$el.append("<div class='grid grid-resource'>$</div>");
				} else {
					this.$el.append("<div class='grid grid-ground'>_</div>");
				}
			}, this);
		}, this);
	};

	screen.update_users = function(users) {
		console.log("Updating users");
		_.each(users, function(v, k) {
			var username = this.get_username(k);
			var $el = $("<div class='grid grid-user'>@</div>");
			$el.attr("data-userid", k);
			$el.attr("data-username", username);
			$el.css({"left": v[0] * 20, "top": v[1] * 20});
			var $span = $("<span></span>");
			$span.text(username);
			$el.append($span);
			this.$el.append($el);
		}, this);
	};


	GC.init = function() {
		var screen = $("#grid_screen")[0];
		if (!_.isUndefined(screen)) {
			var s = new GC.Screen(screen);
			var comm = new GC.Comm(s);
		}
	};

	$(function() {
			GC.init();
	});

})(this, jQuery, _);
