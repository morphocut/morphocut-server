<template>
  <l-map :zoom="zoom" :center="center">
    <l-tile-layer :url="url" :attribution="attribution"></l-tile-layer>
    <l-marker :lat-lng="marker"></l-marker>
  </l-map>
</template>
<script>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { LMap, LTileLayer, LMarker } from "vue2-leaflet";

export default {
  components: { LMap, LTileLayer, LMarker },
  data() {
    return {
      zoom: 13,
      center: L.latLng(47.41322, -1.219482),
      url: "http://{s}.tile.osm.org/{z}/{x}/{y}.png",
      attribution:
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      marker: L.latLng(47.41322, -1.219482)
    };
  }
};
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>
