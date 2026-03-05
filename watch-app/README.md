# watch-app

Wear OS application for Samsung Galaxy Watch.

> Work in progress.

## Development

Use the Docker environment in [`../infra/`](../infra/) to build and run the app.

```bash
# From repo root — start the dev container
bash infra/run.sh
bash infra/into.sh

# Inside the container
cd ~/projects/watch-app
./gradlew assembleDebug
```
