# Chat Completion API for StapleAI Recruitment

by Keshav Nath, night of 27/01/2025

## Basic rundown

1) Send a JSON Request to /openai-completion endpoing containing "prompt" and an optional "user_id"
2) You receive a json containing the OpenAI Text completion "completion"
3) Each succesful request is stored in an SQLite DB "chat_logs.db" with schema containing user_id, prompt, completion, timestamp
4) If you want to continue an old chat, then you can continue by putting in the same user_id as previously
5) Any errors are returned to the prompting user in a json containing "error": text
6) There is a manual rate limit (3 requests per minute)

## Considerations

1) Install requirements (for Flask, OpenAI, SQLite) from requirements.txt
2) Must have an OPENAI_API_KEY as environment varable
3) Rate limit can be changed
4) SQLite DB Destination can be changed, it is currently in the ./venv/sqlite folder itself so it's easy to validate using SQLite
5) If input body has no "prompt" field, or the "prompt" field is empty, an error is raised
6) If no "user_id" is provided, chats are logged under "anonymous" and cannot be recalled as chat hsitory

## Issues

1) Error checking is not too eloquent (just try-except and print)
2) Could not think of much input data validation outside of what is already implemented

## Image Examples

### Succesful Interaction - Postman

Basic Interaction
![](/img/success-1.png)

Continued Interaction 1
![](/img/success-2.png)

Continued Interaction 2
![](/img/success-3.png)

SQLite Logging
![](/img/success-4.png)

Rate Limit Hit
![](/img/ratelimit-1.png)

Missing Prompt
![](/img/fail-1.png)

Empty Prompt
![](/img/fail-2.png)