$(function() {

/* MODELS */
var Postcard = Backbone.Model.extend({
    // overridden to have trailing slash
    url: function() {
        return POSTCARD_API_URL + this.id + '/';
    }
});

var PostcardCollection = Backbone.Collection.extend({
    model: Postcard,

    url: POSTCARD_API_URL,

    /*
    parse: function(response) {
        // check if there are any more items to get
    }
    */
});

/* VIEWS */

var PostcardView = Backbone.View.extend({

    template: _.template($('#postcard-templ').html()),

    id: 'postcard-view',

    render: function(eventName) {
        var html = this.template({'postcard': this.model.toJSON()});
        this.$el.html(html);
        return this;
    }

});

var PostcardListView = Backbone.View.extend({

    template: _.template($('#postcard-list-templ').html()),
   
    className: 'postcard-list',

    page: 1,

    // do something on add of the collection

    render: function(eventName) {
        var html = this.template({'postcards': this.model.toJSON()});
        this.$el.html(html);
        return this;
    },
});

/* APP */

var AppRouter = Backbone.Router.extend({

    routes: {
        '':'home',
        '!/map/':'map',
        '!/gallery/':'gallery',
        '!/postcard/:id/':'postcard',
    },

    home: function () {
        $('#content').html('HOME');
    },

    gallery: function () {
        if ( !this.postcardListView ) {
            var postcardListColl = new PostcardCollection();
            this.postcardListView = new PostcardListView({ model: postcardListColl });

            postcardListColl.fetch({
                data: {page: this.page},
                success: function() { 
                    $('#content').html(app.postcardListView.render().el);
                }
            });
        }
        else {
            $('#content').html(this.postcardListView.render().el);
        }
    },

    postcard: function (id) {
        var postcard = null;
        if ( this.postcardListView ) {
            postcard = this.postcardListView.model.get(id);
            this.postcardView = new PostcardView({ model: postcard });
            $('#content').html(this.postcardView.render().el);
        }
        else {
            postcard = new Postcard({'id': id});
            postcard.fetch({
                success: function(postcard) {
                    // TODO: this duplicates code
                    this.postcardView = new PostcardView({model: postcard });
                    $('#content').html(this.postcardView.render().el);
                }
            });
        }
    },

    map: function() {
        $('#content').html('A wild map appears!');
    }
});

app = new AppRouter();
Backbone.history.start();
});

var app = null;
