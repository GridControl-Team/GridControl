(function(root, _, $){
	"use strict";

	var GC = !root.GC ? (root.GC = {}) : root.GC;

	GC.Comm = function(screen) {
		console.log("Comm init!");
		this.screen = screen;
		this.channel = null;
		this.connect();
	};

	var proto = GC.Comm.prototype;

	proto.connect = function() {
		if (!_.isNull(this.channel)) {
			this.disconnect();
		}
		this.channel = new io.connect('//' + window.location.hostname + ':8001/tornado/stream');
		this.channel.on("message", _.bind(this.receive, this));

	};

	proto.disconnect = function() {
	};

	proto.receive = function(v) {
		utils.trace("received:", v);
		var msg = JSON.parse(v);
		switch (msg.type) {
			default:
				console.log(msg);
				break;
		}
	};

	proto.send = function(v) {
		this.channel.send(v);
	};


})(this, _, jQuery);
