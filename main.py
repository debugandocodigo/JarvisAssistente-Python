from dotenv import load_dotenv  # pip install python-dotenv
import openai  # pip install openai
import speech_recognition as sr  # pip install SpeechRecognition
import whisper  # pip install whisper-openai
import pyttsx3  # pip install pyttsx3
import os

load_dotenv()  # load .env file

openai.api_key = os.getenv('OPENAI_API_KEY')  # Obtendo a chave da API do OpenAI

microphone = sr.Microphone()  # Inicializando o microfone
recognizer = sr.Recognizer()  # Inicializando o reconhecedor de voz
engine = pyttsx3.init()  # Inicializando o motor de voz

# Configuração do Jarvis
config = {
    'chat': {
        'name': 'Jarvis',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.5,
        'max_tokens': 150,
        'messages': [
            {"role": "system", "content": "Você é um assistente gente boa. E meu nome é Debugando Código!"}
        ],
        'assistant_active': False,
        'commands': [
            {
                'name': 'activate_assistant',
                'words': [
                    'Jarvis', 'Jarvis ativar', 'Jarvis ative-se','Jarvis ative', 'Olá Jarvis',
                    'Oi Jarvis', 'Jarvis oi','Jarvis olá', 'Jarvis bom dia', 'Jarvis boa tarde',
                    'Jarvis boa noite',
                ],
                'action': 'activate_assistant'
            },
            {
                'name': 'exit_assistant',
                'words': [
                    'sair', 'tchau', 'até mais','até logo', 'até a próxima','até breve', 'sair do assistente',
                    'sair do Jarvis', 'desativar assistente','encerrar assistente', 'desativar Jarvis',
                ],
                'action': 'exit_assistant'
            }
        ]
    }
}

# Função para ativar o assistente
def activate_assistant():
    config['chat']['assistant_active'] = True
    speak("Olá, como posso ajudar?")

# Função para desativar o assistente
def exit_assistant():
    config['chat']['assistant_active'] = False
    speak("Até mais!")

# Função para ouvir e obter entrada de áudio
def listen():
    with microphone as source:
        print("Ouvindo...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=3, phrase_time_limit=20)
    try:
        print("Reconhecendo...")
        query = recognizer.recognize_google(audio, language='pt-BR')
        if query:
            print(f"Você disse: {query}\n")
        else:
            query = 'Não entendi. Repita por favor...'

    except Exception as e:
        print(e)
        query = ''
    return query

# Função para falar a resposta
def speak(response):
    voices = engine.getProperty('voices')  # Obtendo detalhes da voz
    engine.setProperty('rate', 180)  # Configurando velocidade da fala

    # for indice, vozes in enumerate(voices):  # listar vozes
    #     print(indice, vozes.name)

    engine.setProperty('voice', voices[59].id)  # Mudando para a voz masculina

    print("Jarvis: ", response, " usando a voz ", voices[59].name)

    engine.say(response)  # Reproduzindo a resposta
    engine.runAndWait()  # Esperando a resposta ser reproduzida

# Função para obter resposta do ChatGPT
def get_gpt3_response(message):
    messages = config.get('chat').get('messages')  # Obtendo mensagens
    messages.append({"role": "user", "content": message})  # Adicionando mensagem do usuário
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=config.get('chat').get('temperature'),
        max_tokens=config.get('chat').get('max_tokens'),
    )
    return [response.choices[0].message.content, response.usage]

# Loop principal
while True:
    user_input = listen()  # Obtendo entrada de áudio

    commands = config['chat'].get('commands')  # Obtendo comandos

    for command in commands:  # Verificando se o comando foi dito
        if user_input.lower() in [word.lower() for word in command.get('words')]:
            globals().get(command.get('action'))()
            break

    if config.get('chat').get('assistant_active') and user_input.lower() not in [word.lower() for word in commands[0].get('words')]:
        gpt3_response = get_gpt3_response(user_input)
        print("Resposta do ChatGPT:", gpt3_response)
        speak(gpt3_response[0])