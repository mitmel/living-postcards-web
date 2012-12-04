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
        // remove items without an animated_render
        //
        // NOTE: they currently don't get sent from the API
        // maybe they should have a place holder?
        return _.reject(response, function(postcard) {
            return !(_.has(postcard.resources, 'animated_render'));
        });
    }
});

/* VIEWS */

var PostcardSingleView = Backbone.View.extend({
    template: _.template($('#postcard-templ').html()),

    id: 'postcard-view',

    render: function(ev) {
        var html = this.template({'postcard': this.model.toJSON()});
        this.$el.html(html);

        return this;
    }
});

var PostcardGallery = Backbone.View.extend({
    template: _.template($('#postcard-gallery-templ').html()),

    id: 'gallery',

    orderby: '-updated',

    page: 1,

    pagesize: 12,

    pages_left: true,

    scroll_pos: 0,

    initialize: function() {
        var _this = this;
        _this.postcardListView ;

        // On a reload of the collection, rerender the list
        _this.model.on('reset', function() {
            if (_this.postcardListView) {
                _this.postcardListView.$el.remove(); 
            }
            _this.postcardListView = new PostcardListView({model:_this.model})
            lcont = _this.$el.find('#list-container')

            // ease in the html with a fade
            lcont.html(_this.postcardListView.render().el).fadeIn();
        });
    },

    _check_if_pages_left: function(xhr) {
        var _this = this;
        total = parseInt(_xhr.getResponseHeader('X-Object-Total'));
        if ((_this.page) * _this.pagesize >= total) {
            _this.pages_left = false;
        }
        else { 
            _this.pages_left = true;
        }
    },

    // this will fire the 'reset' handler of the collection
    reload: function(callback) {
        var _this = this;
        _this.page = 1;
        show_loading();
        _xhr = _this.model.fetch({
            data: { 
                orderby: _this.orderby,
                page: _this.page,
                pagesize: _this.pagesize,
            },
            success: function() {
                _this._check_if_pages_left(_xhr);
                hide_loading();
                if ( callback ) { callback(); }
            }
        });
    },

    // fires add event handler in postcardlistview
    load_more: function (callback) {
        var _this = this;
        if ( !_this.pages_left ) { return; }

        _this.page = _this.page + 1;

        // keep infinite scroll from firing multiple requests while this one
        // is loading
        disable_infinite_scroll();

        show_loading();
        _xhr = _this.model.fetch({
            data: { 
                orderby: _this.orderby,
                page: _this.page,
                pagesize: _this.pagesize,
            },
            complete: function() {
                //re-enable infinite scroll
                enable_infinite_scroll();
            },
            success: function() {
                _this._check_if_pages_left(_xhr);
                hide_loading();
                if ( callback ) { callback(); }
            },
            add: true,
        });
    },

    render: function(ev) {
        var _this = this;
        _this.$el.html(_this.template());

        return _this;
    },

});

var PostcardListView = Backbone.View.extend({

    className: 'postcard-list row',

    initialize: function() {
        var _this = this;
        _this.model.on('add', function(postcard) {
            item_view = new PostcardListItemView({model:postcard}).render().$el;

            // ease in the append with a fade
            item_view.hide().appendTo(_this.$el).fadeIn();
        });
    },

    // render the whole list. Done only on a reset of the gallery
    render: function(ev) {
        var _this = this;
        _this.model.each(function(postcard) { 
            var item = new PostcardListItemView({model:postcard}).render().$el;
            _this.$el.append(item);
        });

        return this;
    },

});

var PostcardListItemView = Backbone.View.extend({

    template: _.template($('#postcard-list-item-templ').html()),

    className: 'postcard span4',

    render: function(ev) {
        var _this = this;
        var html = _this.template({'postcard': _this.model.toJSON()});
        _this.$el.html(html);

        // bind the hover
        bind_postcard_hover(_this.$el);

        // fix the date
        //var date_obj = this.$el.find('.date span');
        //datetime = moment(date_obj.html());
        //date_obj.html(datetime.format("ddd, YYYY/M/D, h:mm a"));

        return this;
    }

});

var MapView = Backbone.View.extend({
        
    id: 'main-map',

    render: function(ev) {
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
        '!/:page/':'flat_page',
    },

    home: function () {
        this.flat_page('home');
    },

    flat_page: function(page) {
        dispatcher.trigger('closeView');

        // create and render the template
        html = _.template($('#' + page + '-page-templ').html())();
        $('#content').html(html); 

        // scroll to top
        $('body, html').animate({ scrollTop: 0 });
    },

    about: function() {
        dispatcher.trigger('closeView');
        // create and render the template
        html = _.template($('#about-page-templ').html())();
        $('#content').html(html); 
    },

    gallery: function () {
        dispatcher.trigger('closeView');
        var gallery = null;
        var new_gallery = false;

        // If there isn't a gallery view yet, create a new collection
        // and render the gallery
        if ( !app.postcardGallery ) {
            app.postcardCollection = new PostcardCollection();
            gallery = new PostcardGallery({'model': app.postcardCollection});
            app.postcardGallery = gallery;

            gallery.render();
            gallery.reload();

            new_gallery = true;
        }
        else {
            gallery = app.postcardGallery;
        }
        
        // put the content back in, ease in with a fade
        $('#content').hide().html(gallery.el).fadeIn();

        if ( new_gallery ) {
            $('#-updated.gallery-sort').addClass('active');
        }

        // enable infinite scrolling
        enable_infinite_scroll();       

        // bind the hover
        bind_postcard_hover(gallery.$el);

        // Recent activated by default
        // on clicking a gallery sort link
        gallery.$el.find('.gallery-sort').click(function() {

            // only reload if its not already active
            if (!$(this).hasClass('active')) {
                var orderby = $(this).attr('id');
                $('.gallery-sort').removeClass('active');
                $(this).addClass('active');
                gallery.orderby = orderby;

                // reload the gallery after setting the new orderby
                var list_div = gallery.$el.find('#list-container');
                list_div.fadeOut(function() {
                    gallery.reload();
                });

                return false;
            }
        }); 

        $('body, html').animate({ scrollTop: gallery.scroll_pos });

        dispatcher.on('closeView', function() {
            gallery.scroll_pos = $(window).scrollTop();

            // stop the animating gif because the mouse out event won't fire
            gallery.$el.find('.gif-preview').remove();
            disable_infinite_scroll();
            dispatcher.off('closeView');
        });
    },

    postcard: function (id) {
        dispatcher.trigger('closeView');

        var postcard = null;

        // If the postcardCollection exists, just get the postcard from there
        if ( app.postcardCollection ) {
            postcard = app.postcardCollection.get(id);
            app.postcardSingleView = new PostcardSingleView({ model: postcard });
            $('#content').html(app.postcardSingleView.render().el);
            create_facebook_like();
        }

        // Otherwise, have to fetch it
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

        // scroll to the last place the gallery was at
        $(window).scrollTop($('#content').offset().top);

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

/* HELPERS */

// bind the hover listener, el is a jquery object
function bind_postcard_hover(el) {
    el.find('.postcard-image').hover(
        function() {
            var gif_src = $(this).attr('data-gif-src');
            $(this).prepend('<img class="gif-preview" src=' + gif_src + '></img>');
        },
        function() {
            $(this).find('.gif-preview').remove();
        }
    );
}

function show_loading() {
    app.postcardGallery.$el.append(_.template($('#loader-templ').html()));
}

function hide_loading() {
    $('#loading').remove();
}

function enable_infinite_scroll() {
    $(window).scroll(function () { 
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            app.postcardGallery.load_more();
        }
    });
}

function disable_infinite_scroll() {
    $(window).unbind('scroll');
}

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
