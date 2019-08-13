<template>
  <v-app style="height:100%;">
    <v-toolbar app dark color="#222831" dense>
      <v-toolbar-title class="headline">
        <a href="http://www.cemfi.de/" target="_blank" style="text-decoration: none;">
          <span style="color:#f96d00">cemfi.</span>
        </a>
        <span class="font-weight-thin">ScoreTube</span>
      </v-toolbar-title>
      <v-toolbar-items>
        <v-tabs
            v-model="activeTab"
            color="#222831"
            dark
            slider-color="#f96d00"
            style="margin-left: 20px"
            v-show="alignment==null"
        >
          <v-tab>
            <img
                :src="`${publicPath}icons/youtube.svg`"
                style="width:22px;height:22px;margin-right:5px;"
            >
            YouTube
          </v-tab>
          <v-tab>
            <img
                :src="`${publicPath}icons/audio.svg`"
                style="width:22px;height:22px;margin-right:5px;"
            >
            Audio
          </v-tab>
        </v-tabs>
      </v-toolbar-items>
      <v-spacer></v-spacer>
      v{{version}}
    </v-toolbar>

    <v-content>
      <div v-show="alignment==null">
        <input
            type="file"
            style="display:none"
            ref="meiFile"
            accept=".mei, .xml"
            @change="onMeiFilePicked"
        >
        <input
            type="file"
            style="display:none"
            ref="audioFile"
            accept=".mp3, .wav, *.wave"
            @change="onAudioFilePicked"
        >
        <div v-if="activeTab===0" class="centered" style="height:100%">
          <v-card class="pa-3 centered">
            <v-text-field
                color="accent"
                style="width:300px;"
                label="MEI file"
                readonly
                @click="pickMei"
                v-model="meiFile.name"
            ></v-text-field>
            <v-text-field
                color="accent"
                style="width:300px;"
                label="YouTube URL"
                v-model="youtubeUrl"
            ></v-text-field>
            <v-btn
                color="accent"
                @click="processYoutube"
                :loading="loading"
                :disabled="loading"
            >Start
            </v-btn>
          </v-card>
        </div>
        <div v-else-if="activeTab===1" class="centered" style="height:100%">
          <v-card class="pa-3 centered">
            <v-text-field
                color="accent"
                style="width:300px;"
                label="MEI file"
                readonly
                @click="pickMei"
                v-model="meiFile.name"
            ></v-text-field>
            <v-text-field
                color="accent"
                style="width:300px;"
                label="Audio file"
                readonly
                @click="pickAudio"
                v-model="audioFile.name"
            ></v-text-field>
            <v-btn color="accent" @click="processAudio" :loading="loading" :disabled="loading">Start</v-btn>
          </v-card>
        </div>
      </div>
      <div v-show="alignment!=null" style="padding-top:20px;">
        <div
            v-show="youtubePlayer!=null"
            style="text-align: center; background-color:#000000; width:100%;"
        >
          <div id="youtube" class=".text-center"></div>
        </div>
        <div id="meiSvg" ref="meiSvg" style="cursor:crosshair; overflow-x:scroll; overflow-y:auto"></div>
        <audio v-show="audioFile.name!==''" controls ref="audio" style="width:100%;;"></audio>
      </div>
    </v-content>

    <v-dialog v-model="showError" persistent max-width="350">
      <v-card>
        <v-card-text>Something went wrong:
          <div class="error--text">{{errorMsg}}</div>
          <v-divider class="my-3"></v-divider>
          (<a href="javascript:location.reload();">Refresh</a> page to start over.)
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script>
import axios from 'axios';
import $ from 'jquery';
import * as d3 from 'd3';
import getYouTubeID from 'get-youtube-id';

import { version } from '../package.json';
import utils from './utils';

axios.defaults.timeout = 180000; // 3 min timeout

export default {
  name: 'App',
  components: {},
  data() {
    return {
      publicPath: process.env.BASE_URL,
      version,
      activeTab: 0,
      youtubeUrl: null,
      meiFile: { name: '' },
      audioFile: { name: '' },
      svgData: '',
      meiData: '',
      pixelToTime: {},
      timeToPixel: {},
      cursor: null,
      // eslint-disable-next-line
        verovio: new verovio.toolkit(),
      alignment: null,
      loading: false,
      youtubePlayer: null,
      audioPlayer: null,
      showError: false,
      errorMsg: null,
    };
  },
  mounted() {
    this.verovio.setOptions({
      scale: 30,
      breaks: 'none',
      font: 'Bravura',
    });
  },
  methods: {
    pickMei() {
      this.$refs.meiFile.click();
    },
    pickAudio() {
      this.$refs.audioFile.click();
    },
    onMeiFilePicked(e) {
      this.meiFile = e.target.files[0];
    },
    onAudioFilePicked(e) {
      this.audioFile = e.target.files[0];
    },
    processYoutube() {
      if (this.meiFile.name !== '' && this.youtubeUrl !== '') {
        this.loading = true;
        // eslint-disable-next-line
          const fd = new FormData();
        const url = this.youtubeUrl.indexOf('://') === -1
          ? `http://${this.youtubeUrl}`
          : this.youtubeUrl;
        fd.append('mei', this.meiFile);
        fd.append('youtube-url', url);
        axios
          .post('http://localhost:8001/align', fd, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
          .then((response) => {
            this.alignment = response.data;
            this.youtubePlayer = new YT.Player('youtube', {
              height: '390',
              width: '640',
              videoId: getYouTubeID(this.youtubeUrl),
            });

            $(document)
              .on('keypress', (e) => {
                if (e.which === 32) {
                  if (this.youtubePlayer.getPlayerState() !== 1) {
                    this.youtubePlayer.playVideo();
                  } else {
                    this.youtubePlayer.pauseVideo();
                  }
                }
              });

            const meiSvg = d3.select('#meiSvg');

            const reader = new FileReader();
            const that = this;
            reader.onload = () => {
              this.meiData = reader.result;
              this.svgData = this.verovio.renderData(this.meiData, {});
              this.$refs.meiSvg.innerHTML = this.svgData;
              d3.select('.page-margin')
                .append('line')
                .attr('id', 'cursor')
                .attr('x1', -10)
                .attr('x2', -10)
                .attr('y1', 0)
                .attr('y2', '100%')
                .attr('stroke-width', 75)
                .attr('stroke', '#f96d00');
              this.cursor = d3.select('#cursor');

              d3.select('.system')
                .append('rect')
                .attr('id', 'click-area')
                .attr('x', 0)
                .attr('y', 0)
                .attr('width', '100%')
                .attr('height', '100%')
                .attr('fill', '#000000')
                .attr('opacity', 0);

              d3.select('#click-area')
                .on('click', () => {
                  that.youtubePlayer.seekTo(
                    that.getTimeFromPixel(d3.mouse(d3.event.currentTarget)[0]),
                    true,
                  );
                });

              Object.keys(this.alignment)
                .forEach((key) => {
                  const { x } = meiSvg
                    .select(`#${key}`)
                    .node()
                    .getBBox();
                  this.pixelToTime[x.toString()] = this.alignment[key];
                  this.timeToPixel[this.alignment[key].toString()] = x;
                });

              setInterval(() => {
                this.updateCursor(this.youtubePlayer.getCurrentTime());
              }, 20);
            };
            reader.readAsText(this.meiFile);
          })
          .catch((error) => {
            console.log(JSON.stringify(error));
            this.errorMsg = error.response.data;
            this.showError = true;
          });
      }
    },
    processAudio() {
      if (this.meiFile.name !== '' && this.audioFile.name !== '') {
        this.loading = true;
        // eslint-disable-next-line
          const fd = new FormData();
        fd.append('mei', this.meiFile);
        fd.append('audio', this.audioFile);
        axios
          .post('http://localhost:8001/align', fd, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
          .then((response) => {
            this.alignment = response.data;
            this.audioPlayer = this.$refs.audio;
            this.audioPlayer.src = URL.createObjectURL(this.audioFile);

            $(document)
              .on('keypress', (e) => {
                if (e.which === 32) {
                  if (this.audioPlayer.paused) {
                    this.audioPlayer.play();
                  } else {
                    this.audioPlayer.pause();
                  }
                }
              });

            const meiSvg = d3.select('#meiSvg');

            const reader = new FileReader();
            const that = this;
            reader.onload = () => {
              this.meiData = reader.result;
              this.svgData = this.verovio.renderData(this.meiData, {});
              this.$refs.meiSvg.innerHTML = this.svgData;
              d3.select('.page-margin')
                .append('line')
                .attr('id', 'cursor')
                .attr('x1', -10)
                .attr('x2', -10)
                .attr('y1', 0)
                .attr('y2', '100%')
                .attr('stroke-width', 75)
                .attr('stroke', '#f96d00');
              this.cursor = d3.select('#cursor');

              d3.select('.system')
                .append('rect')
                .attr('id', 'click-area')
                .attr('x', 0)
                .attr('y', 0)
                .attr('width', '100%')
                .attr('height', '100%')
                .attr('fill', '#000000')
                .attr('opacity', 0);

              d3.select('#click-area')
                .on('click', () => {
                  that.audioPlayer.currentTime = that.getTimeFromPixel(
                    d3.mouse(d3.event.currentTarget)[0],
                  );
                });

              Object.keys(this.alignment)
                .forEach((key) => {
                  const { x } = meiSvg
                    .select(`#${key}`)
                    .node()
                    .getBBox();
                  this.pixelToTime[x.toString()] = this.alignment[key];
                  this.timeToPixel[this.alignment[key].toString()] = x;
                });

              setInterval(() => {
                this.updateCursor(this.audioPlayer.currentTime);
              }, 20);
            };
            reader.readAsText(this.meiFile);
          })
          .catch((error) => {
            this.errorMsg = error.response.data;
            this.showError = true;
          });
      }
    },
    updateCursor(time) {
      const pixel = this.getPixelFromTime(time);
      if (isNaN(pixel)) {
        this.cursor.attr('opacity', 0.0);
      } else {
        this.cursor.attr('opacity', 1.0);
        this.cursor.attr('x1', pixel);
        this.cursor.attr('x2', pixel);
      }
    },
    getTimeFromPixel(pixel) {
      const array = this.pixelToTime;
      const keyArray = $.map(array, (value, key) => key);
      const indices = utils.binaryIndexOf.call(keyArray, pixel);
      const keyLeft = keyArray[indices[0]];
      const keyRight = keyArray[indices[1]];
      const valueLeft = array[keyLeft];
      const valueRight = array[keyRight];

      let currentTime = 0;
      if (keyLeft !== null) {
        currentTime = utils.map(
          pixel,
          keyLeft,
          keyRight,
          valueLeft,
          valueRight,
        );
      }

      return currentTime;
    },
    getPixelFromTime(time) {
      const array = this.timeToPixel;
      const keyArray = $.map(array, (value, key) => key);
      const indices = utils.binaryIndexOf.call(keyArray, time);
      const keyLeft = keyArray[indices[0]];
      const keyRight = keyArray[indices[1]];
      const valueLeft = array[keyLeft];
      const valueRight = array[keyRight];

      return utils.map(time, keyLeft, keyRight, valueLeft, valueRight);
    },
  },
};
</script>

<style>
  .centered {
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
