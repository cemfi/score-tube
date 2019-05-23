# ScoreTube

ScoreTube is a score following system based on MEI scores and audio files / YouTube videos.

## Requirements
Make sure to have [Docker](https://www.docker.com/) installed and running properly. That's it.

## How to Run
1. Get the docker image with the latest model

```bash
$ docker pull cemfi/score-tube
```

2. Run in container
```bash
$ docker run -p 8001:8001 -it cemfi/score-tube
```

3. Go to [http://localhost:8001](http://localhost:8001) and follow the onscreen instructions.
