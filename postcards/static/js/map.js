Map = function() {var self = this;

self.map = null;

self.projection = new OpenLayers.Projection('EPSG:900913');
self.displayProjection = new OpenLayers.Projection('EPSG:4326');

self.geojson_format = new OpenLayers.Format.GeoJSON({ 
    internalProjection: self.projection, 
    externalProjection: self.displayProjection
});

self.postcardLayer = null;

self.options = {
    controls: [
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.PanZoomBar(),
    ]
}

self.init = function(div) {

    self.map = new OpenLayers.Map(div, self.options)

    self.cloudmadeLayer = new OpenLayers.Layer.CloudMade('CloudMade', {
        key: '55be8cc24afc49f4a4f7e8056455582c',
        styleId: 2
    });

    self.postcardLayer = new OpenLayers.Layer.Vector('Casts', {
        //styleMap: cast_stylemap,
        //strategies: [strategy],
        isBaseLayer: false,
        rendererOptions: {yOrdering: true}
    });

    self.map.addLayers([self.cloudmadeLayer, self.postcardLayer]);

    // todo: use a transform method with self.projection
    var epsg4326 = new OpenLayers.Projection('EPSG:4326');
    var center = new OpenLayers.LonLat(-71.110296,42.373851).transform(epsg4326, self.map.getProjectionObject());

    self.map.setCenter(center);
    self.map.zoomTo(13);
}

self.renderFeatures = function(features) {
    var postcards = self.geojson_format.read(features);
    self.postcardLayer.addFeatures(postcards);
}


}
