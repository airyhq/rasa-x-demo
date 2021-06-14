# Supercharging Conversational AI with Human Agent Feedback Loops

We use Rasa X in combination with Airy Open Source Conversational Infrastructure to build a feedback loop between the model and human agents.

Sometimes users ask questions your model is not perfectly trained for yet, resulting in low confidence levels for the potential responses. We demonstrate how you can suggest potential responses to Human Support Agents via the Airy Inbox UI and have them select the correct response to be sent back to the user. We observe the chosen response and retrain the model with Rasa X to be able to fully automate the same request the next time.


## The Problem

Sometimes users write requests that your model can't reply to yet. These requests can be complex multi-intent requests, but also simple requests on topics your model isn't informed in yet.


## The standard solution

The standard choice is to handover the conversation at this point to a human agent. Often the conversation is picked up from the beginning again, and time and ressources are wasted on all sides. It has it's benefits too: No user is left behind, as the human agent should be able to answer all questions and messages, edge cases included.


## How it should be

Best would it be if your agents could close the gap of the model and train it in real time. This is where you can use Airy's Suggested Replies in combination with Rasa X: Train your models on the fly with Suggested Replies.


## Benefits

There are clear benefits of using a feedback loop over plain handover:

- Moderating chats is fast
- Agents provide labeled data
- Fast Conversation-Driven-Development improves the user experience

# How to run it

## Install Airy

Install Airy by following our [Installation Guide](https://airy.co/docs/core/getting-started/installation/introduction).

You can also follow our [AWS In-depth guide](https://blog.airy.co/tutorial-airy-installation-aws/).

## Run locally

In one terminal session:

```shell script
rasa run --enable-api
```

and in another:

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

3) Point your webhook subscription to the url assigned to you by ngrok

4) `rasa run --enable-api`

5) `rasa run actions`

6) Send a test message like "Hello there!" to one of your connected source channels

