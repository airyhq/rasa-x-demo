# Airy Rasa X Demo

## Run locally

To test the setup without using Rasa X you can run:

```shell script
rasa run --enable-api
```

in one terminal session and in another:

```shell script
rasa run actions
```

## Airy connector

The [Airy connector](./channels/airy.py) is a custom connector implemented by following the [rasa documentation](https://rasa.com/docs/rasa/user-guide/connectors/custom-connectors/). When running rasa in a container this directory needs to be mounted to `/app`.

Once running the rasa server will expose the webhook at `/webhooks/airy/webhook` 

## Testing the connector

For testing the connector you can use [ngrok](https://ngrok.com/). 

1) Replace the `system_token` and `api_host` in the `credentials.yml` file

2) Launch `ngrok http 5005` and keep it running

3) Point your [webhook subscription](https://airy.co/docs/core/api/webhook) to the url assigned to you by ngrok

4) `rasa run --enable-api`

5) Send a test message like "Hello there!" to one of your connected source channels

