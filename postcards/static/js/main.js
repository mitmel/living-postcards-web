var dispatcher = _.clone(Backbone.Events);

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

    parse: function(response) {
        // check if there are any more items to get
        
        // remove items without an animated_render
        // TODO: maybe they should have a place holder?
        //
        // NOTE: they currently don't get sent from the API
        return _.reject(response, function(postcard) {
            return !(_.has(postcard.resources, 'animated_render'));
        });
    }
});

/* VIEWS */
var PostcardSingleView = Backbone.View.extend({
    template: _.template($('#postcard-templ').html()),

    id: 'postcard-view',

    render: function(eventName) {
        var html = this.template({'postcard': this.model.toJSON()});
        this.$el.html(html);
        return this;
    }
});

var PostcardGallery = Backbone.View.extend({
    template: _.template($('#postcard-gallery-templ').html()),

    id: 'gallery',

    orderby: '-created',

    page: 1,

    pagesize: 99,

    initialize: function() {
        var _this = this;
        _this.postcardListView = new PostcardListView({model:_this.model});

        // On a reload of the collection, rerender the list
        _this.model.on('reset', function() {
            _this.postcardListView.$el.hide();
            _this.$el.append(_this.postcardListView.render().el);
            _this.postcardListView.$el.fadeIn();
        });
    },

    fetch: function() {
        var _this = this;
        _this.model.fetch({data: 
            { 
                'orderby': _this.orderby,
                //'page': _this.page,
                //'pagesize': _this.pagesize
            },
        });
    },

    render: function(eventName) {
        var _this = this;
        _this.$el.html(_this.template());

        // Recent activated by default

        // on clicking a gallery sort link
        _this.$el.find('.gallery-sort').click(function() {
            var orderby = $(this).attr('id');
            $('.gallery-sort').removeClass('active');
            $(this).addClass('active');
            _this.orderby = orderby;
            _this.fetch();
            return false;
        }); 

        return _this;
    },


});

var PostcardListView = Backbone.View.extend({

    template: _.template($('#postcard-list-templ').html()),
   
    className: 'postcard-list row',

    render: function(eventName) {
        var html = this.template({'postcards': this.model.toJSON()});
        this.$el.html(html);
        return this;
    },
});

var MapView = Backbone.View.extend({
    id: 'main-map',

    render: function(eventName) {
        var html = 'Map is in progress!'
        this.$el.html(html);
        return this;
    }
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
        // close last view
        dispatcher.trigger('closeView');

        $('#content').html('HOME');
    },

    gallery: function () {
        dispatcher.trigger('closeView');
        var gallery = null;

        if ( !app.postcardGallery ) {
            app.postcardCollection = new PostcardCollection();
            gallery = new PostcardGallery({'model': app.postcardCollection});
            gallery.fetch();
        }
        else {
            gallery = app.postcardGallery;
        }

        // rerender without refetching
        $('#content').html(gallery.render().el);
        gallery.$el.append(gallery.postcardListView.render().el);
        
        if ( !app.postcardGallery ) {
            $('#-created.gallery-sort').addClass('active');
            app.postcardGallery = gallery;
        }

        $(window).scroll(function () { 
            if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
                console.log('infinite scroll!');
                //Add something at the end of the page
            }
        });

        dispatcher.on('closeView', function() {
            $(window).unbind('scroll');
        });
    },

    postcard: function (id) {
        dispatcher.trigger('closeView');

        var postcard = null;
        if ( app.postcardListView ) {
            postcard = app.postcardListView.model.get(id);
            app.postcardSingleView = new PostcardSingleView({ model: postcard });
            $('#content').html(app.postcardSingleView.render().el);
            create_facebook_like();
        }
        else {
            postcard = new Postcard({'id': id});
            postcard.fetch({
                success: function(postcard) {
                    // TODO: this duplicates code
                    app.postcardSingleView = new PostcardSingleView({model: postcard });
                    $('#content').html(app.postcardSingleView.render().el);
                    create_facebook_like();
                }
            });
        }

        // on view close, cleanup
        dispatcher.on('closeView', function() {
            $('#facebook-like').html('');
            dispatcher.off('closeView');
        });
    },

    map: function() {
        dispatcher.trigger('closeView');

        this.mapView = new MapView();
        //var map = new Map();

        $('#content').html(this.mapView.render().el);

        /*
        map.init(this.mapView.el.id);

        $.get(GEOFEATURES_API_URL, function(data) {
            map.renderFeatures(data);
        });

        dispatcher.on('closeView', function() {
            //alert('map closed');
            dispatcher.off('closeView');
        });
        */
    }
});

app = new AppRouter();
Backbone.history.start();
});

var app = null;

function create_facebook_like() {
    $('#facebook-like').html('<fb:like send="true" width="450" show_faces="false" font="arial" data-layout="button_count"></fb:like>');
    // if FB doesn't exist that means that it hasn't been loaded yet
    // and when it does get loaded, it will auto parse the page.
    if ( typeof FB != 'undefined' && FB != null ) {
        FB.XFBML.parse();
    }
}

function update_facebook_likes(url) {
    // get id from url
    var match = /.*postcard\/([0-9]*)/.exec(url);
    var id = parseInt(match[1]);

    var url = FACEBOOK_LIKES_API_URL;

    $.post(url, {'id': match[1]});
}
