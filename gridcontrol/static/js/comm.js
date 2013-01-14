(function(root, _, $){
	"use strict";

	var GC = !root.GC ? (root.GC = {}) : root.GC;

	GC.Comm = function(screen) {
		console.log("Comm init!");
		this.screen = screen;
		this.userid = screen.userid;
		this.reconnect_timer = null;
		this.channel = null;
		this.connect();
	};

	var proto = GC.Comm.prototype;

	proto.connect = function() {
		if (!_.isNull(this.channel)) {
			return;
		}
		this.reconnect_timer = null;
		this.channel = new io.connect('//' + window.location.hostname + ':8001/tornado/stream?userid=' + this.userid, {
			'reconnect': false,
			'force new connection': true
		});
		this.channel.on("message", _.bind(this.receive, this));
		this.channel.on("connecting", _.bind(this.on_connecting, this));
		this.channel.on("connect", _.bind(this.on_connect, this));
		this.channel.on("disconnect", _.bind(this.on_disconnect, this));
		this.channel.on("error", _.bind(this.on_disconnect, this));
		this.channel.on("connect_failed", _.bind(this.on_disconnect, this));
		this.channel.on("reconnect_failed", _.bind(this.on_disconnect, this));
	};

	proto.on_disconnect = function() {
		console.log("Comm died!");
		this.channel = null;
		this.reconnect_timer = window.setTimeout(_.bind(this.connect, this), 3000);
		this.screen.on_disconnect();
	};

	proto.on_connect = function() {
		this.screen.on_connect();
	};

	proto.on_connecting = function() {
		this.screen.on_connecting();
	};

	proto.receive = function(v) {
		var msg = JSON.parse(v);
		switch (msg.type) {
			case "map":
				this.screen.update_map(msg.content);
				break;
			case "users":
				this.screen.update_users(msg.content);
				break;
			case "username":
				this.screen.update_usernames(msg.content);
				break;
			case "scores":
				this.screen.update_scores(msg.content);
				break;
			case "exception":
				this.screen.raise_exception(msg.content);
				break;
			case "history":
				this.screen.update_history(msg.content);
				break;
			default:
				console.log("Unknown message type:");
				console.log(msg);
				break;
		}
	};

	proto.send = function(v) {
		this.channel.send(v);
	};


})(this, _, jQuery);
