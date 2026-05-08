class MockResponseChoiceMessage:
    def __init__(self, content):
        self.message = type("M", (), {"content": content})


class MockChoices(list):
    def __init__(self, content):
        super().__init__([MockResponseChoiceMessage(content)])


class MockChatCompletions:
    def __init__(self, response_text="Mocked reply"):
        self._response_text = response_text

    def create(self, model, messages, temperature=0):
        # Return an object similar to the OpenAI SDK response used in the app
        class Resp:
            def __init__(self, text):
                self.choices = [type("C", (), {"message": type("M", (), {"content": text})})]

        # You can customize output based on messages if desired
        return Resp(self._response_text)


class MockOpenAIClient:
    def __init__(self, response_text="Mocked reply"):
        self.chat = type("Chat", (), {"completions": MockChatCompletions(response_text)})
