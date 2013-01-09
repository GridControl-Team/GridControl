(function(root, _, $){
	"use strict";

	var GC = !root.GC ? (root.GC = {}) : root.GC;

	GC.Comm = function(screen) {
		console.log("Comm init!");
		this.screen = screen;
		this.userid = screen.userid;
		this.channel = null;
		this.connect();
	};

	var proto = GC.Comm.prototype;

	proto.connect = function() {
		if (!_.isNull(this.channel)) {
			this.disconnect();
		}
		this.channel = new io.connect('//' + window.location.hostname + ':8001/tornado/stream?userid=' + this.userid);
		this.channel.on("message", _.bind(this.receive, this));

	};

	proto.disconnect = function() {
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
