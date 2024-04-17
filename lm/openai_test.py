from openai import OpenAI

client = OpenAI(api_key="")

stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)

i = 0

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(str(i) + " " + chunk.choices[0].delta.content, end="")
        i += 1