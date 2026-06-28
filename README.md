# WeGo Transit Map

Don't use this lol, it's a stupid fork with a bunch of hacked either by my small webdev brain that barely understands JS or a stupid LLM with no context. All this does it have some goofy changes that I need for a project but that are completely stupid and useless outside of it.


![screenshot](screenshot.png)

Implementation of the General Transit Feed Specification (GTFS) Realtime feed for Nashville's WeGo Public Transit bus system. Displays all vehicle locations on a map.

Requires a [separate application](https://github.com/transitnownash/gtfs-rails-api) to be up and running for the static data components (route, shapes, trips, etc.) to work properly. Configure the endpoint as `GTFS_BASE_URL` in your environment.

## Development

Start the application with the default endpoint.

```bash
$ npm start
```

Run the test suite.

```bash
$ npm test
```

Build static app to `./build` folder.

```bash
$ npm run build
```
