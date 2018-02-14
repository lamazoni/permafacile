var app = app || {};
(function($) {
	'use strict';

	//ECMA-262 5th compatibility
	if (!Date.now) {
  		Date.now = function now() {
    		return new Date().getTime();
  		};
	}

	app.AppAgendaView = Backbone.View.extend({
		el: $('body'),
		initialize: function() {
			_.bindAll(this, 'render','renderWhenError');
			this.$containerSlot = this.$('.container');
			this.$paginator = this.$('.paginator');
			this.collection = new app.Slots();
			this.paginatorView= new app.Paginator({collection: this.collection});
			this.render();
			this.listenTo(this.collection,'request',this.renderLoading);
			this.collection.fetch({
				data : {
					special : 'all'
				}
			});
			this.collection.setPageSize(PAGE_SIZE);
			this.listenToOnce(this.collection,'sync',this.initAndrender);
			this.listenTo(this.collection,'sync',this.render);
			this.listenTo(this.collection,'error',this.renderWhenError);
			this.collection.on("pageable:state:change",this.render);
		},
		initAndrender: function() {
			console.log("AppView: initAndrender");
			let i = 0;
			let now = moment().dayOfYear();
			let todayPage = 1;
			let numsup = 0;
			_.each(this.collection.fullCollection,function(value,index){
				var aDate=moment(this.collection.fullCollection.at(index).get('date')).dayOfYear();
				if (aDate < now ) {
					if ( index != 0 && ((index % PAGE_SIZE) == 0)) {
						todayPage ++;
					}
					numsup ++;
					this.collection.fullCollection.at(index).opacity=true;
				}
			},this);
			if ( numsup > ( todayPage * PAGE_SIZE ) ) {
				todayPage ++;
			}
			this.collection = this.collection.getPage(todayPage);
			this.render();
		},
		render: function() {
			console.log("AppView: render");
			$(this.$containerSlot).empty();
			_(this.collection.models).each(function(aslot) {
                this.appendItem(aslot);
            }, this);
			$(this.$paginator).empty();
			$(this.$paginator).append(this.paginatorView.render().el);
		},
		appendItem : function(aslot) {
			// console.log("aslot:"+JSON.stringify(aslot));
			var aslotview = new app.SlotView({
                model: aslot
            });
            $(this.$containerSlot).append(aslotview.render().el);
		},
		renderWhenError: function() {
			$(".loading").remove();
			$(this.$containerSlot).append("<p>erreur survenue, rafraichir la page puis reessayer, contactez le support</p>");
		},
		renderLoading: function() {
			console.log("AppView: renderLoading");
			$(this.$containerSlot).append('<div class="loading"></div>');
		},
	});
})(jQuery);
