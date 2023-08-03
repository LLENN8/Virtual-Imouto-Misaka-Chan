from googletrans import Translator

def translate(text):
    try:
        translator = Translator(service_urls=['translate.googleapis.com'])
        translation = translator.translate(text, dest='ja')
        #print(translation.text)
        return translation.text
    except Exception as e:
        print("Error detect text: {0}".format(e))

