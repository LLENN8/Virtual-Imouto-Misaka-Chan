import tkinter as tk
from tkinter import scrolledtext, PhotoImage
import tkinter.font as tkfont
from tkinter import ttk
import random
import torch
from npl.model_loader import *
from utils.audio import *
from utils.translate import *
import threading

class ChatApp:
    def __init__(self, root):
        self.audio = Audio()
        self.root = root
        self.root.title("Misaka Chan")

        # Set UI colors
        self.sky_pink = "#FFB6C1"
        self.text_color = "black"

        # Set the background color of the root window
        self.root.configure(bg=self.sky_pink)

        # custom font for the UI elements
        custom_font = tkfont.Font(family="Helvetica", size=12)
        
        # set styles for Entry and Text widgets
        style = ttk.Style()
        style.configure("Custom.TEntry", background="white", foreground=self.text_color,
                        insertcolor=self.text_color, borderwidth=0, relief=tk.FLAT, font=custom_font)
        style.configure("Custom.TText", background="white", foreground=self.text_color,
                        insertcolor=self.text_color, borderwidth=0, relief=tk.FLAT, font=custom_font)

        try:
            # bot's image
            bot_pic = PhotoImage(file="misaka.png")
            bot_label = ttk.Label(root, image=bot_pic, background=self.sky_pink)
            bot_label.image = bot_pic
            bot_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        except tk.TclError:
            print("Error: Image not found. Please provide a valid image path.")

        # set chat history text box
        self.chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10,
                                                     background=self.sky_pink, foreground=self.text_color,
                                                     font=custom_font, relief=tk.FLAT, bd=0)
        self.chat_history.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        self.chat_history.config(state=tk.DISABLED)

        # set user input text box
        self.user_input = tk.Text(root, width=40, height=3, wrap=tk.WORD, font=custom_font, relief=tk.FLAT, bd=0)
        self.user_input.grid(row=2, column=0, padx=10, pady=5, columnspan=1)

        # set send button
        self.send_button = ttk.Button(root, text="Send", command=self.send_message, style="Custom.TButton")
        self.send_button.grid(row=2, column=1, padx=5, pady=5)
        self.user_input.config(height=3)

        # Create the record button
        self.recording_state = False 
        self.record_button = ttk.Button(root, text="Press and hold to record", style="Custom.TButton")
        self.record_button.grid(row=3, column=0, padx=5, pady=5, columnspan=2, sticky="nsew")
        self.record_button.bind("<Button-1>", lambda event: self.toggle_recording())
        self.record_button.bind("<ButtonRelease-1>", lambda event: self.record_button.after(500, self.toggle_recording))
        self.user_input.bind("<Return>", self.send_message)

        # set voice toggle checkbutton
        self.voice_enabled = tk.BooleanVar()
        self.voice_enabled.set(False)  # Voice enabled by default
        self.voice_toggle = ttk.Checkbutton(root, text="Enable VoiceVox", variable=self.voice_enabled)
        self.voice_toggle.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Load the AI model
        self.intents, self.all_words, self.tags, self.model = load_model()

    def get_bot_response(self, user_input):
        # Tokenize and convert the user's input to a bag of words
        sentence = tokenize(user_input)
        X = bag_of_words(sentence, self.all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(torch.device('cuda' if torch.cuda.is_available() else 'cpu')).unsqueeze(0)

        # Get the output from the AI model and predict the intent tag
        output = self.model(X)
        _, predicted = torch.max(output, dim=1)
        tag = self.tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        if prob.item() > 0.75:
            for intent in self.intents['intents']:
                if tag == intent["tag"]:
                    #get random respons based on tag
                    response = random.choice(intent['responses'])
                    return response
        else:
            #if there aren't any match tags and responses  
            return "I don't understand. OniiChan, Bakaaa!"
    
    def show_respon(self, user_message):
        # Update chat history with user's input
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"\n\nYou: \n{user_message}")
        self.chat_history.config(state=tk.DISABLED)
        # Get the bot's response and update chat
        ai_response = self.get_bot_response(user_message)
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"\n\nMisaka: \n{ai_response}")
        self.chat_history.config(state=tk.DISABLED)

        # Auto-scroll to the end of the chat
        self.chat_history.see(tk.END)

        # Speak response using TTS
        self.root.after(10, lambda: self.speak_bot_response(ai_response))

    def get_respon_from_audio_input(self):
        # record audio as input from user and transcribe it as user message
        self.audio.recording = True
        self.audio.record_audio()
        user_message = self.audio.transcribe_audio()
        self.show_respon(user_message)
    
    def send_message(self, event=None):
        # Get the user's input from the input box
        user_message = self.user_input.get("1.0", tk.END).strip()
        # Clear the user input box
        self.user_input.delete("1.0", tk.END)
        self.show_respon(user_message)

    def speak_bot_response(self, response):
        #if voicevox is enable, it will use voicevox to get voice for bot
        if self.voice_enabled.get():
            voice = Audio()
            voice.voicevox_tts(translate(response))
            voice.play_audio()

    #this function make button record work and changing text when pressed
    def toggle_recording(self):
        if not self.recording_state:
            self.recording_state = True
            self.record_button.config(text="Recording...")
            self.audio.thread = threading.Thread(target= self.get_respon_from_audio_input)
            self.audio.thread.daemon = True
            self.audio.thread.start()
        else:
            self.recording_state = False
            self.audio.recording = False
            self.record_button.config(text="Press and hold to record")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
