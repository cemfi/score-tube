<template>
  <v-app style="height: 100%">
    <v-toolbar app dark color="#222831">
      <v-toolbar-title class="headline">
        <a href="http://www.cemfi.de/" target="_blank" style="text-decoration: none;">
          <span style="color:#f96d00">CEMFI.</span>
        </a>
        <span class="font-weight-thin">ScoreTube</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      v{{version}}
    </v-toolbar>

    <v-content>
      <v-container style="height:100%;" @drop.prevent="onFileDrop" @dragover.prevent>
        <v-card style="height:100%;">
          <v-tabs v-model="active" color="#222831" dark slider-color="#f96d00">
            <v-tab href="#youtube">YouTube</v-tab>
            <v-tab href="#youtube">Audio</v-tab>
            <v-tab-item>YouTube</v-tab-item>
            <v-tab-item>Audio</v-tab-item>
          </v-tabs>
        </v-card>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import axios from "axios";
import $ from "jquery";

import { version } from "../package.json";
import utils from "./utils";

axios.defaults.timeout = 180000; // 3 min timeout

export default {
  name: "App",
  components: {},
  data() {
    return {
      publicPath: process.env.BASE_URL,
      version,
      active: null,
    };
  }
};
</script>

<style>
.ellipsize-left {
  /* Standard CSS ellipsis */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;

  /* Beginning of string */
  direction: rtl;
  text-align: left;
}

.dropZone {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #222831;
  text-align: center;
}

.rotate {
  animation: rotation 2s infinite linear;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}
</style>
