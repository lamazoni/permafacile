var app = app || {};
(function($) {
	'use strict';

	app.ChooseAttenderView = Backbone.View.extend({
		initialize : function (opts) {
			console.log("initialize");
			_.bindAll(this,'render','renderWhenError','chooseAttender','renderWithResult');
			this.model = new app.Attenders();
			this.listenTo(this.model, 'request', this.render);
			this.listenTo(this.model, 'sync', this.renderWithResult);
			this.listenTo(this.model, 'error', this.renderWhenError);
			this.model.fetch({
				data : {
					role : 'distributeur',
					slottype_name : 'legume',
				}
			});
			this.nameChoosen = "";
			this.parentView = opts.parentView;
			this.modalView = opts.modalView;
		},
		events: {
			'click li': 'selectAttender',
			'click #full-modal-apply-btn': 'chooseAttender',
		},
		potentialAttendersTemplate: _.template($('#potentialAttenders-view').html()),

		renderWithResult : function () {
			console.log("render ChooseAttenderView");
			this.$el.html(this.potentialAttendersTemplate({potentialAttenders: this.model.get('listofname'),loading:false,error:false}));
			this.$nameChoosen = this.$(".nameChoosen");
			console.log(".themodal:"+this.$('.themodal').attr('role'));
			return this;
		},
		render : function () {
			console.log("render renderWithLoadingIndicator");
			this.$el.html(this.potentialAttendersTemplate({potentialAttenders: [],loading:true,error:false}));
			return this;
		},
		renderWhenError : function () {
			console.log("render when error");
			this.$el.html(this.potentialAttendersTemplate({potentialAttenders: [],loading:true,error:true}));
			return this;
		},
		selectAttender : function (e) {
			console.log("selectAttender");
			this.$nameChoosen.empty();
			$(this.$nameChoosen).html($(e.target).text().trim());
			this.nameChoosen= $(e.target).text().trim();
		},
		chooseAttender : function (e) {
			console.log("chooseAttender");
			if ( this.nameChoosen.length > 0) {
				this.parentView.attend(this.nameChoosen,true);
			}
			this.modalView.hide();
		},
	});
	app.ChooseAttenderModalView = BackboneBootstrapModals.BaseModal.extend({
	    headerView: BackboneBootstrapModals.BaseHeaderView,
	    headerViewOptions: {
	             label: 'Choisir un participant',
	             labelId: 'myModalLabel',
	             showClose: true,
	     },
	     bodyView: app.ChooseAttenderView,
		 bodyViewOptions: function(){
			 return {parentView:this.parentView,modalView:this}
		 },
	     modalOptions: {
	        backdrop: true,
	        keyboard: true
	     }
	});

	app.SlotClockingView = Backbone.View.extend({
	    initialize: function() {
			console.log("Initialize SlotClockingView");
	        _.bindAll(this, 'renderCheckingList','renderWhenError','cancel','attend','toggleTheGuy','sendAttenders','addChooseAttenderView','displayChooseAttender');

			this.listenTo(this.model, 'change', this.renderCheckingList);
	        this.listenTo(this.model, 'error', this.renderWhenError);
			this.renderAndInit();
	    },
	    events: {
	        'click .cancel': 'cancel',
			'click .attend': 'attend',
			'click .complicated-switch': 'toggleTheGuy',
			'click .sendbutton': 'sendAttenders',
			'click .displayChooseAttender': 'displayChooseAttender',
	    },
	    slotTemplate: _.template($('#clocking-view').html()),
		checkingListTemplate: _.template($('#clocking-view-checkingList').html()),
		renderAndInit: function() {
			console.log("renderAndInit");
			this.setElement(this.slotTemplate());
			this.renderCheckingList();
		},
	    renderCheckingList: function() {
			var attenders=$.extend(true, [],this.model.get('attenders'));
			if ( ! this.tmpattenders ) {
				this.tmpattenders=_.map(attenders, (function () {
					let id = 0;
					return function (attender) {
						if (attender.hasOwnProperty("role") && attender.hasOwnProperty("name")) {
							attender.checked = true;
							attender.id=id++;
							return attender
						}
					}
				})());
			}
			this.tmpattenders=_.sortBy(this.tmpattenders,'role');
			console.log("renderCheckingList SlotClockingView");
			console.log("attenders BEFORE:"+JSON.stringify(this.model.get('attenders')));
			try {
				_.each(this.tmpattenders, function(element){
					if (! (element.hasOwnProperty("role") && element.hasOwnProperty("name")) && element.hasOwnProperty("checked")) {
						throw "not well formated attenders";
					}
				});
				this.$('.checkingList').empty();
				this.$('.checkingList').append(this.checkingListTemplate({
					date: moment(this.model.get('date')).format('dddd Do MMMM GGGG'),
					lock: this.model.get('lock'),
					people: this.tmpattenders,
					appearance: this.model.opacity ? "olive" : "green",
					showbutton: ! this.model.opacity,
				}));
			}
			catch (err) {
				console.log("cannot display:"+err);
			}
			console.log("attenders AFTER:"+JSON.stringify(this.model.get('attenders')));
	        return this;
	    },
		renderWhenError: function () {
			this.setElement("error, cannot reach");
			return this;
		},
		toggleTheGuy : function (e) {
			const clickedguy=$(e.target).attr('clickedguy');
			if ( clickedguy ) {
				console.log("ToggleTheGuy");
				$(e.target).toggleClass("active");
				console.log("the Guy:"+$(e.target).attr('clickedguy'));
				if ( $(e.target).hasClass("active") ) {
					this.cancel(clickedguy,$(e.target).attr('id'));
				} else {
					this.attend(clickedguy,false);
				}
			}
		},

		cancel : function (clickedguy,idattribute) {
			console.log("attenders model BEFORE:"+JSON.stringify(this.model.get('attenders')));
			console.log("clickedguy to cancel:"+clickedguy+"idattribute:"+idattribute);
			function foundElement (element) {
				if (element.hasOwnProperty("name")) {
					//TODO: get the distributeur role instead of presume distributeur
					return element.name == clickedguy && element.role == "distributeur";
				} else {
					return false;
				}
			}
			if (this.model.get('attenders').find(foundElement)) {
				this.model.get('attenders').splice(this.model.get('attenders').findIndex(foundElement),1);
			} else {
				console.log(clickedguy+" not found, cannot delete");
			}
			function foundElementByid (element) {
				if (element.hasOwnProperty("id")) {
					return element.id == idattribute;
				} else {
					return false;
				}
			}
			if (this.tmpattenders.find(foundElementByid)) {
				this.tmpattenders[this.tmpattenders.findIndex(foundElementByid)].checked = false;
			} else {
				console.log(clickedguy+" not found in tmpattenders, cannot delete");
			}
			console.log("attenders model AFTER:"+JSON.stringify(this.model.get('attenders')));
		},
		attend : function (clickedguy,isNew) {
			console.log("clickedguy to attend:"+clickedguy);
			console.log("attenders model BEFORE:"+JSON.stringify(this.model.get('attenders')));
			if ( isNew ) {
				//TODO: get the distributeur role instead of presume distributeur
				let idmax=0
				this.tmpattenders.forEach((attender) => {
					if (attender.id > idmax) {
						idmax = attender.id;
					}
				})
				idmax++;
				this.tmpattenders.push({name:clickedguy,role:'distributeur',checked:true,id:idmax});
				this.model.get('attenders').push({name:clickedguy,role:'distributeur'});
				this.renderCheckingList();
			} else {
				function foundElement (element) {
					if (element.hasOwnProperty("name")) {
						return element.name == clickedguy;
					} else {
						return false;
					}
				}
				this.tmpattenders[this.tmpattenders.findIndex(foundElement)].checked = true;
				this.model.get('attenders').push({name:clickedguy,role:'distributeur'});
			}
			console.log("attenders model AFTER:"+JSON.stringify(this.model.get('attenders')));
		},
		sendAttenders : function () {
			this.model.set({'lock':true});
			this.model.save();
		},
		addChooseAttenderView: function() {
			console.log("addChooseAttenderView");
			this.aChooseAttenderModalView = new app.ChooseAttenderModalView({parentView:this});
			this.aChooseAttenderModalView.render();
		},
		displayChooseAttender: function (e) {
			e.preventDefault();
			console.log("displayChooseAttender");
			this.addChooseAttenderView();
		}
	});

	app.AppClockingView = Backbone.View.extend({
		el: $('body'),
		initialize: function() {
			_.bindAll(this, 'initAndrender','render','renderWhenError','appendItem');
			this.$container = this.$('.container');
			this.$paginator = this.$('.paginator');
			this.collection = new app.Slots();
			this.paginatorView= new app.Paginator({collection: this.collection});
			this.listenTo(this.collection,'request',this.renderLoading);
			this.collection.fetch({
				data : {
					name : user_name,
					role : 'accueil-pointage',
					special : 'pointage'
				}
			});
			this.collection.setPageSize(1);
			this.listenToOnce(this.collection,'sync',this.initAndrender);
			this.listenTo(this.collection,'error',this.renderWhenError);
			this.collection.on("pageable:state:change",this.render);
			// this.listenTo(app.events, 'aChoosenAttenderRender', this.render);
		},
		initAndrender: function() {
			let now = moment().dayOfYear();
			let todayPage = 1;
			let discrepency = 1;
			_.each(this.collection.fullCollection,function(value,index){
				if ( this.collection.fullCollection.at(index).get('lock') && (discrepency > 0)) {
					todayPage ++;
				} else {
					discrepency -- ;
				}
				// All the received content should have a revolved date except the one of the day however here below take care of all
				if ( moment(this.collection.fullCollection.at(index).get('date')).dayOfYear() < now ) {
					this.collection.fullCollection.at(index).opacity=true;
				};
				},this);
			this.collection = this.collection.getPage(todayPage);
		},
		render: function() {
			console.log("AppView: render");
			$(this.$container).empty();
			_(this.collection.models).each(function(aslot) {
				console.log("adding aslot");
	               this.appendItem(aslot);
	           }, this);
			$(this.$paginator).empty();
			$(this.$paginator).append(this.paginatorView.render().el);
		},
		appendItem : function(aslot) {
			var aslotClockingView = new app.SlotClockingView({
                model: aslot
            });
            $(this.$container).append(aslotClockingView.render().el);
		},
		renderWhenError: function() {
			$(".loading").remove();
			$(this.el).append("A error occured, cannot render.");
		},
		// renderLoading: function() {
		// 	console.log("AppView: renderLoading");
		// 	$(this.$container).append('<div class="loading"></div>');
		// },
	});
})(jQuery);
