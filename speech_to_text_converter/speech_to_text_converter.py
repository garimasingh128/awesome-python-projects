import speech_recognition as sr
recognizer= sr.Recognizer()

#Asks user to speak and records speech
with sr.Microphone() as source:
    print("Speak now")
    audio= recognizer.listen(source)

#Converts speech to text using Google's Web Speech API
    try:
        text= recognizer.recognize_google(audio)
        print(f"You said : {text}")
        
    except sr.UnknownValueError:
      print("Could not understand")

    except sr.RequestError:
       print("Network error")
