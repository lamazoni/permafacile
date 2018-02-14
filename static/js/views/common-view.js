var app = app || {};
(function($) {
	'use strict';

	// aChoosenAttender, text (the li.text)

    app.events = _.extend({}, Backbone.Events);

	app.ChooseListRoleView = Backbone.View.extend({
		initialize : function (opts) {
			_.bindAll(this,'render','selectRole');
			this.parentView=opts.parentView;
			this.modalView=opts.modalView;
			this.model=opts.roles;
		},
		template : _.template($('#chooseListRole-view-template').html()),
		events: {
			'click .roleChoose':'selectRole'
		},
		selectRole: function (e) {
			console.log("Select role"+$(e.target).text());
			this.parentView.attendMe($(e.target).text().trim());
			this.modalView.hide();
		},
		render: function() {
			this.model.sort();
			this.$el.html(this.template({roles:this.model}));
			return this;
		}
	});


	app.ChooseListRoleModalView = BackboneBootstrapModals.BaseModal.extend({
	    headerView: BackboneBootstrapModals.BaseHeaderView,
	    headerViewOptions: {
	             label: 'Choisir un role',
	             labelId: 'myModalLabel2',
	             showClose: true,
	     },
	     bodyView: app.ChooseListRoleView,
		 bodyViewOptions: function(){
			 return {parentView:this.parentView,modalView:this,roles:this.roles}
		 },
	     modalOptions: {
	        backdrop: true,
	        keyboard: true
	     }
	});

	app.SlotView = Backbone.View.extend({
	    tagName: 'div',
	    initialize: function() {
			console.log("Initialize slotview");
			// this.model=app.Slot(this.model.toJSON);
	        _.bindAll(this, 'render','renderWhenError','cancelMe','attendMe','showMeRoleOrAttend');
	        this.listenTo(this.model, 'request', this.renderWithLoadingIndicator);
	        this.listenTo(this.model, 'sync', this.render);
	        this.listenTo(this.model, 'error', this.renderWhenError);
			// this.model.fetch();
	    },
	    events: {
	        'click .cancel': 'cancelMe',
			'click .attend': 'showMeRoleOrAttend',
	    },
	    slotTemplate: _.template($('#slot-template').html()),
		attendersByRole: function () {
			// console.log("user_profile:"+JSON.stringify(user_profile));
			let attendersByRole = {};
			this.model.get('attenders').forEach((attender) => {
				if (! attendersByRole.hasOwnProperty(attender["role"])) {
					attendersByRole[attender["role"]] = [];
				}
				attendersByRole[attender["role"]].push(attender["name"]);
			});
			//when nobody on this role put a empty tab
			this.model.get("slottype")["roles"].forEach((role) => {
				if (! attendersByRole.hasOwnProperty(role.name)){
					attendersByRole[role.name] = [];
				}
			});
			return attendersByRole
		},
		notFullRole : function () {
			let attendersByRole = this.attendersByRole();
			let notFullRole = [];
			this.model.get("slottype")["roles"].forEach((role) => {
				_.each(attendersByRole, (aRoleWithAttender,key) => {
					// console.log("role.name:"+role.name);
					if (key == role.name) {
						// console.log("lenght:"+aRoleWithAttender.length);
						if ( aRoleWithAttender.length < role.number) {
							notFullRole.push(role.name);
						}
					}
				});
			});
			return notFullRole;
		},
	    render: function() {
			let attendersByRole = this.attendersByRole();
			// console.log("attendersByRole:"+JSON.stringify(attendersByRole));
			let imPresent = false;
			this.model.get('attenders').forEach((attender) => {
				if (attender.name == user_name) {
					imPresent = true;
				}
			});
			//Workaround to have attendersByRole sorted by key
			let roles = [];
			this.model.get("slottype")["roles"].forEach((role) => {
				roles.push(role.name);
			});
			roles.sort();
			if ( this.model.get('lockCancelAttender') ) {
				imPresent = false;
			}
	        $(this.el).html(this.slotTemplate({
	            date: moment(this.model.get('date')).format('dd Do MMM'),
				lock: this.model.get('lock'),
				lockCancelAttender : this.model.opacity ? false : this.model.get('lockCancelAttender'),
				roles: roles,
				attendersByRole: attendersByRole,
				appearance: this.model.opacity ? "olive" : "green",
				showbuttons: ! this.model.opacity,
				imPresent: imPresent,
				icanAttend : this.notFullRole().length > 0 ? true : false,
	        }));
	        return this;
	    },
		renderWhenError: function () {
			$(this.el).html("erreur, rafraichir la page puis reessayer");
			return this;
		},
		renderWithLoadingIndicator: function () {
			$(this.el).html('<div class="loading"></div>');
			return this;
		},
		cancelMe : function () {
			var attenders=this.model.get('attenders');
			function foundElement (element) {
				if (element.hasOwnProperty("name")) {
					return element.name == user_name;
				} else {
					return false;
				}
			}
			if (attenders.find(foundElement)) {
				attenders.splice(attenders.findIndex(foundElement),1);
				this.model.save({'attenders':attenders});
			} else {
				console.log(user_name+" not found,cannot delete");
			}
			// console.log("attenders"+JSON.stringify(this.model.get('attenders')));
		},
		attendMe : function (myRole) {
			var attenders=this.model.get('attenders');
			attenders.push({name:user_name,role:myRole.toLowerCase()});
			this.model.set({'attenders':attenders});
			this.model.save();
			// this.model.save({'attenders':attenders});
			// console.log("attenders"+JSON.stringify(this.model.get('attenders')));
		},
		showMeRoleOrAttend : function () {
			// console.log("user profile:"+JSON.stringify(user_profile));
			let askForRole = [];
			if (user_profile.hasOwnProperty("rolesOnSlottypes")) {
				user_profile.rolesOnSlottypes.forEach((item) => {
					if (item.hasOwnProperty("role")) {
						askForRole.push(item.role);
					}
				});
			} else {
				console.log("error, cannot read profile");
			}
			let roles = _.intersection(askForRole,this.notFullRole());
			if ( roles.length > 1 ) {
				this.aChooseRoleView = new app.ChooseListRoleModalView({
					roles: roles,
					parentView: this,
				});
				this.aChooseRoleView.render();
			}
			if ( roles.length == 1 ) {
				this.attendMe(roles[0]);
			}
			if ( roles.length == 0 ) {
				console.log("error, no role found");
			}
		}
	});

	app.Paginator = Backbone.View.extend({
		el:$('.paginator'),
		paginationTemplate: _.template($('#pagination-view').html()),
    	events: {
	      'click a.first': 'loadFirstPage',
	      'click a.prev': 'loadPreviousPage',
	      'click a.page': 'loadPage',
	      'click a.next': 'loadNextPage',
	      'click a.last': 'loadLastPage'
	    },
		initialize: function () {
		  console.log("initialize paginator");
		},
	    loadFirstPage: function(e) {
	      this.collection=this.collection.getFirstPage();
		  this.render();
	    },
	    loadPreviousPage: function(e) {
	      this.collection=this.collection.getPreviousPage();
		  this.render();
	    },
	    // getPage: function(e) {
	    //   e.preventDefault();
	    //   this.collection.getPage($(e.target).text());
	    // },
	    loadNextPage: function(e) {
		//console.log("getNextPage");
	      this.collection=this.collection.getNextPage();
		  this.render();
	    },
	    loadLastPage: function(e) {
	      this.collection=this.collection.getLastPage();
		  this.render();
	    },
	    render: function() {
		  this.$el.html(this.paginationTemplate(this.collection.state));
		//console.log("STATE:"+JSON.stringify(this.collection.state));
	      return this;
	    }
	});
})(jQuery);
