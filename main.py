import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import psutil, subprocess, tempfile, glob, shutil, ctypes, random, os, math, re, time
from threading import Thread
from PIL import Image
from CTkMessagebox import CTkMessagebox


class App():
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry('1150x650+50+20')
        self.root.title("Silence Remover App")
        self.mainframe = ctk.CTkScrollableFrame(self.root)
        self.mainframe.pack(fill='both', expand=True)
        self.root.iconbitmap("iconfinal.ico")

        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=2)



        my_image = ctk.CTkImage(dark_image =Image.open('bg.png'), size=(1592, 80))

        lab = ctk.CTkLabel(self.mainframe,text="", image=my_image)
        lab.grid(row=0, column=0, sticky="we", columnspan=2)

        # CHOOSE FILE BUTTON
        self.ChooseFileButton = ctk.CTkButton(self.mainframe, text="Choose File", command=self.BrowseFiles)
        self.ChooseFileButton.grid(row=1, column=0,padx=(20,0), pady=10, sticky="w")
        #chosen file name display
        self.choosefile_textField = ctk.CTkLabel(self.mainframe, text="choosen File", anchor='w')
        self.choosefile_textField.grid(row=1, column=0, pady=10, padx=(170,20), sticky="W")

        #FFMPEG TEXT OUTPUT TEXTBOX
        self.ffmpegOutputText = ctk.CTkTextbox(self.mainframe, width=460, height=380, padx=10, pady=7, wrap='none') 
        self.ffmpegOutputText.grid(row=2, column=0,padx=(20,20), pady=10, sticky = 'we')


        #Display New filename
        self.setFileName_textField = ctk.CTkLabel(self.mainframe, text="Output File Name: ", anchor='w')
        self.setFileName_textField.grid(row=3, column=0, pady=10, padx=(20,0), sticky="W")

        #Edit New filename
        self.updateFileNameEntry_var = tk.StringVar()
        self.updateFileNameEntry_var.trace('w', self.cmdFileNameChange)

        self.setFileName = ctk.CTkEntry(self.mainframe, textvariable=self.updateFileNameEntry_var)
        self.setFileName.grid(row=3, column=0, pady=10, padx=(130,20), sticky="We")

        #--fps --sample-rate Check Boxes
        # self.fpsValue = False
        self.fpsValue = tk.BooleanVar()
        self.sampleValue = tk.BooleanVar()
        self.fpsCheck = ctk.CTkCheckBox(self.mainframe, text='--fps', variable=self.fpsValue, onvalue=True, offvalue=False, command=self.CheckBoxValueChanged)
        self.fpsCheck.grid(row=4, column=0, padx=(20,0), sticky="w")
        self.sampleRateCheck = ctk.CTkCheckBox(self.mainframe, text='--sample-rate', variable=self.sampleValue, onvalue=True, offvalue=False, command=self.CheckBoxValueChanged)
        self.sampleRateCheck.grid(row=4, column=0, padx=(120,0), sticky="w")
       
        #DISPLAY COMMAND
        self.cmd_Text= ctk.CTkLabel(self.mainframe, text="Command: ")
        self.cmd_Text.grid(row=5, column=0, padx=(20,0), pady=10, sticky="w")
        self.cmd_Entry = ctk.CTkEntry(self.mainframe)
        self.cmd_Entry.grid(row=5, column=0, padx=(100,20), sticky='We')

        #Run Button
        self.SubmitButton = ctk.CTkButton(self.mainframe, text="RUN", fg_color="green", hover_color='darkgreen', command=self.MainCutting)
        self.SubmitButton.grid(row=6, column=0, padx=(30,0),pady=10, sticky="w")

        #Rotate ↺ aniticlockwise button
        self.AntiClockRotateButton = ctk.CTkButton(self.mainframe, fg_color="#643A6B", hover_color='#5F264A', text="Rotate ↺", command=lambda: self.Rotate("2"))
        self.AntiClockRotateButton.grid(row=6, column=0, padx=(230,0),pady=10, columnspan=2, sticky="w")

        #Rotate ↻ clockwise button
        self.ClockRotateButton = ctk.CTkButton(self.mainframe, fg_color="#643A6B", hover_color='#5F264A', text="Rotate ↻", command=lambda: self.Rotate("1"))
        self.ClockRotateButton.grid(row=6, column=0, padx=(430,0), columnspan=2, pady=10, sticky="w")

        #CANCEL BUTTON
        self.CancelButton = ctk.CTkButton(self.mainframe, text="Cancel", command=self.stop_process)
        self.CancelButton.grid(row=1, column=1, pady=10, sticky="w")

        # VIDEO EDITING TERMINAL OUTPUT
        self.terminalOutputDisplay = ctk.CTkTextbox(self.mainframe, width=440, height=460, padx=10, pady=7, wrap='none')
        self.terminalOutputDisplay.grid(row=2, column=1, rowspan=3,padx=(0,20), pady=10, sticky="WE")

        #PROGRESS BAR
        self.prog_color = (["#9e58e8", "#60dbc7", '#75fc5d','#5dbdfc','#ea5dfc'])[random.randint(0,4)]
        self.ProgressBar = ctk.CTkProgressBar(self.mainframe, width=40, height=20, progress_color=self.prog_color)
        self.ProgressBar.grid(row=5, column=1, padx=(0,80), sticky='we')
        self.ProgressBar.set(0)
        self.ProgressBarPercentage = ctk.CTkLabel(self.mainframe, text='0%', font=("", 15, "bold"))
        self.ProgressBarPercentage.grid(row=5, column=1, sticky='e', padx=(0,20))

        to_disable = [self.ffmpegOutputText, self.sampleRateCheck, self.fpsCheck, self.setFileName, self.cmd_Text, self.cmd_Entry, self.setFileName_textField, self.SubmitButton,self.AntiClockRotateButton,self.ClockRotateButton, self.CancelButton, self.terminalOutputDisplay]

        for i in to_disable:
            i.configure(state="disabled")

        #start export success=false
        self.export = False



        self.cmdoptions = '--no-open'
        #SET IT ON TOP ON STARTUP
        if self.root.state() == "iconic":
            # restore the window and maximize it
            self.root.deiconify()
        #set window on top
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closeing)

        self.root.mainloop()
        return
    
    def on_closeing(self):
        try:
            self.stop_process()
        except:
            pass
        self.root.destroy()


    def CheckBoxValueChanged(self):
        self.cmd_Entry.configure(state='normal')
        self.cmd_Entry.delete(0, tk.END)

        fpsVarVal = (self.fpsValue.get())
        sampleVarVal = (self.sampleValue.get())

        if fpsVarVal and self.cmdoptions.find(" -fps 30") == -1:
            self.cmdoptions += ' -fps 30'
        elif not fpsVarVal:
            self.cmdoptions = self.cmdoptions.replace(' -fps 30', '')
        if sampleVarVal and self.cmdoptions.find(" --sample-rate 48000") == -1:
            self.cmdoptions += ' --sample-rate 48000'
        elif not sampleVarVal:
            self.cmdoptions = self.cmdoptions.replace(' --sample-rate 48000', '')

        self.command = f'auto-editor "{self.filename}" {self.cmdoptions} --debug -o "{self.filelocation+self.outputfilename}.{self.file_extension}"'
        self.cmd_Entry.insert(tk.END, self.command)

        self.cmd_Entry.configure(state='readonly')

    def cmdFileNameChange(self, *args):
        # Get the text from the Entry widget and update the Label text
        # self.label.configure(text=self.entry_var.get())
        self.cmd_Entry.configure(state='normal')
        self.cmd_Entry.delete(0, tk.END)
        self.outputfilename = (self.updateFileNameEntry_var.get())
        self.command = f'auto-editor "{self.filename}" {self.cmdoptions} --debug -o "{self.filelocation+self.outputfilename}.{self.file_extension}"'
        self.cmd_Entry.insert(tk.END, self.command)
        self.cmd_Entry.configure(state='readonly')

    def BrowseFiles(self):
        self.filename = filedialog.askopenfilename(title = "Select a File",filetypes = (("Media Files",("*.MP4*","*.MKV*")),("all files","*.*")))
        if(self.filename != ""):
            to_enable = [self.sampleRateCheck, self.fpsCheck, self.setFileName, self.cmd_Text, self.cmd_Entry, self.setFileName_textField, self.SubmitButton, self.AntiClockRotateButton,self.ClockRotateButton]
            for i in to_enable:
                i.configure(state='normal')
            # self.ffmpegOutputText.delete("1", "END")
            self.choosefile_textField.configure(text=self.filename)
            self.setFileName.delete(0, tk.END)
            self.filelocation = self.filename.replace((self.filename.split("/")[-1]), "")
            newlist = (self.filename.split("/")[-1]).split(".")
            print(newlist)
            self.file_extension = newlist[1]
            self.outputfilename = newlist[0]+" [Alter]"
            # print(self.outputfilename)
            self.setFileName.insert(0, self.outputfilename)
            # print(self.outputfilename)
            #Change column weight 
            self.mainframe.columnconfigure(1, weight=4)
                        
            self.ffmpegOutputText.configure(state='normal')
            # print(filename)
            cmd =['ffmpeg', '-hide_banner', '-i', self.filename]
            output = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, shell=True)
            self.ffmpegOutputText.delete("1.0", "end")
            self.ffmpegOutputText.insert(tk.END, output.stderr)
            self.cmd_Entry.delete(0,tk.END)
            self.cmd_Entry.insert(tk.END,  f'auto-editor "{self.filename}" {self.cmdoptions} --debug -o "{self.filelocation+self.setFileName.get()}"')
            self.cmd_Entry.configure(state='readonly')
            self.command = f'auto-editor "{self.filename}" {self.cmdoptions} --debug -o "{self.filelocation+self.setFileName.get()}"'

    def DelTemp(self):
        path = tempfile.gettempdir()
        # print(path+r"\tmp*")  
        for f in glob.glob(path+r"\tmp*"):
            self.terminalOutputDisplay.insert(tk.END, "Removing Temp File: "+f+"\n")
            # print(f)
            shutil.rmtree(f)
        for f in glob.glob(path+r"\ae-*"):
            self.terminalOutputDisplay.insert(tk.END, "Removing Temp File: "+f+"\n")
            # print(f)
            shutil.rmtree(f)

    def open(self, filename):
        if os.path.exists(filename):
            subprocess.Popen(r'explorer /select,"{}"'.format(os.path.abspath(filename)))
        else:
            print("File not found!")

    def pip_install(self):
        # output_lines = []
        while True:
            output = self.process.stdout.readline().decode('utf-8')
            output2= self.process.stderr.readline().decode('utf-8')
            if output == '' and self.process.poll() is not None:
                #OUTPUT
                self.terminalOutputDisplay.configure(state='normal')

                if self.process.returncode == 0:
                    #SUCCESS
                    #Progressbar Set
                    self.ProgressBar.stop()
                    self.ProgressBar.configure(mode='determinate')
                    self.ProgressBar.set(1)
                    self.ProgressBarPercentage.configure(text="100%")
                    #MESSAGE
                    CTkMessagebox(title="Success!", message="auto-editor successfully installed.", icon="check", option_1="OK", fade_in_duration=1)
                    self.SubmitButton.configure(state='normal')
                    self.ChooseFileButton.configure(state='normal')
                    self.CancelButton.configure(state='disabled')
                    self.AntiClockRotateButton.configure(state='normal')
                    self.ClockRotateButton.configure(state='normal')
                    
                else:
                    #Failed
                    self.ProgressBar.stop()
                    self.ProgressBar.configure(progress_color='red')
                    self.ProgressBar.configure(mode='determinate')
                    self.ProgressBar.set(1)
                    msg = CTkMessagebox(title="Install Failed", message="Could not download\n\ncheck right window to see problem", icon="warning", option_1="Cancel", option_2="Retry")
                    if msg.get() == "Retry":
                        #DISABLE AND ENABLE BUTTONS
                        self.CancelButton.configure(state='normal')
                        self.ChooseFileButton.configure(state='disabled')
                        self.SubmitButton.configure(state='disabled')
                        self.AntiClockRotateButton.configure(state='disabled')
                        self.ClockRotateButton.configure(state='disabled')
                        #RESET TERMINAL OUTPUT
                        self.terminalOutputDisplay.configure(state='normal')
                        self.terminalOutputDisplay.delete('1.0', 'end')
                        self.terminalOutputDisplay.insert(tk.END, "running>> pip install auto-editor\n")
                        # self.terminalOutputDisplay.configure(state='disabled')
                        #Progressbar reset
                        self.ProgressBar.configure(mode='indeterminate')
                        self.ProgressBar.configure(progress_color=self.prog_color)
                        self.ProgressBar.start()
                        #START PROCESS
                        try:
                            self.process_thread.join()
                            self.update_thread.join()
                        except:
                            pass
                        self.process = subprocess.Popen("pip install auto-editor -v", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        self.process_thread = Thread(target=self.run_process)
                        self.process_thread.start()
                    
                        self.update_thread = Thread(target=self.pip_install)
                        self.update_thread.start()
                    else:
                        #ENABLE BUTTONS
                        self.SubmitButton.configure(state='normal')
                        self.ChooseFileButton.configure(state='normal')
                        self.CancelButton.configure(state='disabled')
                        self.AntiClockRotateButton.configure(state='normal')
                        self.ClockRotateButton.configure(state='normal')
                    

                print("BREAKING BAD", str(self.process.returncode))
                break
            if output:
                self.terminalOutputDisplay.insert(tk.END, output.strip()+ "\n")
            if output2:
                self.terminalOutputDisplay.insert(tk.END,output2.strip() + "\n")

            self.terminalOutputDisplay.see(tk.END)
            time.sleep(0.1)

    def check_for_auto_editor(self):
        self.proc_output = subprocess.run("auto-editor", stderr=subprocess.PIPE, shell=True)
        
        if (self.proc_output.returncode != 0):
            self.start_install_process()
            return False
        else:
            return True
            
    def start_install_process(self):
        self.terminalOutputDisplay.configure(state='normal')
        self.terminalOutputDisplay.insert(tk.END, "return code: " + str(self.proc_output.returncode)+ "\n")        
        self.terminalOutputDisplay.insert(tk.END, "maybe auto-editor is not installed"+ "\n")
        msg = CTkMessagebox(title="Error", message="auto-editor not found\n\nClick Install to use\n>>pip install auto-editor", icon="cancel", option_1="Install", option_2="Cancel")
        self.terminalOutputDisplay.insert(tk.END, str(msg.get())+ "\n")
        if msg.get() == "Install":
            self.terminalOutputDisplay.insert(tk.END, "running>> pip install auto-editor\n")
            self.ProgressBar.configure(mode='indeterminate')
            self.ProgressBar.start()
            self.process = subprocess.Popen("pip install auto-editor -v", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.process_thread = Thread(target=self.run_process)
            self.process_thread.start()
            self.update_thread = Thread(target=self.pip_install)
            self.update_thread.start()
            
            
        else: 
            #ENABLE BUTTONS
            self.SubmitButton.configure(state='normal')
            self.ChooseFileButton.configure(state='normal')
            self.CancelButton.configure(state='disabled')
         
    def Rotate(self, param):
        self.end_it = False
        print(param)
        # return
        #reset progress bar
        self.ProgressBar.configure(mode='determinate')
        self.ProgressBar.set(0)
        self.ProgressBar.configure(progress_color=self.prog_color)
        self.ProgressBarPercentage.configure(text="0%")
        #Reset Cancel button function
        self.end_it = False

        #ENALBLE AND DIABLE BUTTONS
        self.CancelButton.configure(state='normal')
        self.ChooseFileButton.configure(state='disabled')
        self.SubmitButton.configure(state='disabled')
        self.AntiClockRotateButton.configure(state='disabled')
        self.ClockRotateButton.configure(state='disabled')
        
        #RESET TERMINAL TEXT
        self.terminalOutputDisplay.configure(state='normal')
        self.terminalOutputDisplay.delete('1.0', 'end')
        self.DelTemp()
        self.terminalOutputDisplay.configure(state='disabled')

        # Run FFmpeg to get the metadata of the video
        result = subprocess.run(['ffmpeg', '-i', self.filename], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

        # Convert the result to a string
        result_str = result.stderr.decode('utf-8')
        
        # Find the duration and frame rate in the output
        duration_str = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", result_str)
        fps_str = re.search(r"(\d+(?:\.\d+)?) fps", result_str).group(1)

        # Calculate duration in seconds
        hours, minutes, seconds = map(float, duration_str.groups())
        print(f"hours: {hours}, minutes: {minutes}, seconds: {seconds}")
        duration_secs = hours * 3600 + minutes * 60 + seconds

        # Print the duration and frame rate
        print(f"Duration: {duration_secs} seconds")
        print(f"Frame rate: {fps_str} fps")
        print(f"total frames: {(float(fps_str)*int(duration_secs))}")
        self.total_frames = math.floor(float(fps_str)*int(duration_secs))
        print(f"total math floor frames: {math.floor(float(fps_str)*int(duration_secs))}")

        #check if file exists
        self.rotatefilename= f"{self.filelocation+self.setFileName.get()}[rotated].{self.file_extension}"
        for i in range(40):
            if os.path.isfile(self.rotatefilename):
                print("Exists")
                self.rotatefilename = f"{self.filelocation+self.setFileName.get()}[rotated]({i}).{self.file_extension}"
            else:
                break
                
        self.rotatecmd = f'ffmpeg -i "{self.filename}" -y -progress pipe:1 -vf "transpose={param}" "{self.rotatefilename}"'
        
        
        # print(self.rotatecmd)
        self.terminalOutputDisplay.configure(state='normal')

        self.process = subprocess.Popen(self.rotatecmd, stdout=subprocess.PIPE, shell=True)
        self.process_thread = Thread(target=self.run_process)
        self.process_thread.start()
            
        self.update_thread = Thread(target=self.Rotateffmpeg)
        self.update_thread.start()
        pass

    def Rotateffmpeg(self):
        while True:
            output = self.process.stdout.readline().decode('utf-8')

            if (output == '' and self.process.poll() is not None) or (self.end_it):
                self.terminalOutputDisplay.configure(state='normal')
                self.terminalOutputDisplay.insert(tk.END, "Breaking Bad" + "\n")
                self.terminalOutputDisplay.configure(state='disabled')
                self.terminalOutputDisplay.see(tk.END)
                self.SubmitButton.configure(state='normal')
                self.ChooseFileButton.configure(state='normal')
                self.CancelButton.configure(state='disabled')
                self.AntiClockRotateButton.configure(state='normal')
                self.ClockRotateButton.configure(state='normal')
                # self.process_thread.termina
                try:
                    self.process_thread.join()
                    self.update_thread.join()
                except:
                    pass
                
                #PROGRESS ERROR/SUCESS
                self.ProgressBar.stop()
                self.ProgressBar.configure(mode='determinate')
                self.ProgressBar.set(1)  
                if self.process.returncode != 0:
                    #ERROR
                    self.ProgressBar.configure(progress_color="red") 
                    self.ProgressBarPercentage.configure(text="0%")            
                    CTkMessagebox(title="Error", message="Something went wrong!!!", icon="cancel")
                    if os.path.exists(self.rotatefilename):
                        os.remove(self.rotatefilename)

                else:
                    #SUCCESS
                    self.ProgressBarPercentage.configure(text="100%")
                    msg = CTkMessagebox(title="SUCCESS!", message="Video successfully saved.", icon="check", option_1="Open",  option_2="OK", fade_in_duration=1)
                    if msg.get()=="Open":
                        self.open(self.rotatefilename)
                print("Breaking bad")
                break
            
            strippedOut = output.strip()

            self.terminalOutputDisplay.configure(state='normal')
            self.terminalOutputDisplay.insert(tk.END, strippedOut + "\n")
            if "frame=" in strippedOut:
                try:
                    deb_frame = int(strippedOut.split("=")[-1])
                    self.ProgressBar.set(deb_frame/(self.total_frames))
                    self.ProgressBarPercentage.configure(text=str(int((deb_frame/(self.total_frames))*100))+"%")
                except:
                    pass
                print(strippedOut)
                
            
            self.terminalOutputDisplay.see(tk.END)
            self.terminalOutputDisplay.configure(state='disabled')
            time.sleep(0.05)
            #self.root.after(1000) update every 100ms

    def MainCutting(self): 
        #reset progress bar
        self.ProgressBar.configure(mode='determinate')
        self.ProgressBar.set(0)
        self.ProgressBar.configure(progress_color=self.prog_color)
        self.ProgressBarPercentage.configure(text="0%")

        #Reset export and cancel button functions
        self.export = False
        self.end_it = False

        #ENALBLE AND DIABLE BUTTONS
        self.CancelButton.configure(state='normal')
        self.ChooseFileButton.configure(state='disabled')
        self.SubmitButton.configure(state='disabled')
        self.AntiClockRotateButton.configure(state='disabled')
        self.ClockRotateButton.configure(state='disabled')
        
        #RESET TERMINAL TEXT
        self.terminalOutputDisplay.configure(state='normal')
        self.terminalOutputDisplay.delete('1.0', 'end')
        self.DelTemp()
        self.terminalOutputDisplay.configure(state='disabled')

        #CHECK IF AUTO_EDITOR INSTALLED:
        if (self.check_for_auto_editor()):
            self.process = subprocess.Popen(self.command, stderr=subprocess.PIPE, shell=True)
            self.process_thread = Thread(target=self.run_process)
            self.process_thread.start()
            
            self.update_thread = Thread(target=self.update_output)
            self.update_thread.start()
            print("Auto-editor exists")
        else:
            print("Auto editor doesnt exists")


    def stop_process(self):
        self.SubmitButton.configure(state='normal')
        self.ChooseFileButton.configure(state='normal')
        self.CancelButton.configure(state='disabled')
        self.AntiClockRotateButton.configure(state='normal')
        self.ClockRotateButton.configure(state='normal')

        # Killing process
        # self.process.terminate()
        self.end_it = True
        Cmdprocess = psutil.Process(self.process.pid)
        for proc in Cmdprocess.children(recursive=True):
            proc.kill()


    def run_process(self):     
        self.process.wait()

    def update_output(self):

        FrameCount = 0
        while True:
            output = self.process.stderr.readline().decode('utf-8')
            if (output == '' and self.process.poll() is not None) or self.end_it:
                self.terminalOutputDisplay.configure(state='normal')
                self.terminalOutputDisplay.insert(tk.END, "Breaking Bad" + "\n")
                self.terminalOutputDisplay.configure(state='disabled')
                self.terminalOutputDisplay.see(tk.END)
                self.SubmitButton.configure(state='normal')
                self.ChooseFileButton.configure(state='normal')
                self.CancelButton.configure(state='disabled')
                self.AntiClockRotateButton.configure(state='normal')
                self.ClockRotateButton.configure(state='normal')
                # self.process_thread.termina
                try:
                    self.process_thread.join()
                    self.update_thread.join()
                except:
                    pass
                #TEMP DELETION
                self.terminalOutputDisplay.configure(state='normal')
                self.DelTemp()
                self.terminalOutputDisplay.configure(state='disabled')

                #PROGRESS ERROR/SUCESS
                self.ProgressBar.stop()
                self.ProgressBar.configure(mode='determinate')
                self.ProgressBar.set(1)  
                if self.export != True:
                    #ERROR
                    self.ProgressBar.configure(progress_color="red") 
                    self.ProgressBarPercentage.configure(text="0%")            
                    CTkMessagebox(title="Error", message="Something went wrong!!!", icon="cancel")
                else:
                    #SUCCESS
                    self.ProgressBarPercentage.configure(text="100%")
                    #setting the filename to exported filename so it is taken into consideration in the rotate function
                    self.filename = self.filelocation+self.setFileName.get()+"."+self.file_extension
                    
                    msg = CTkMessagebox(title="SUCCESS!", message="Video successfully saved.", icon="check", option_1="Open",  option_2="OK", fade_in_duration=1)
                    if msg.get()=="Open":
                        self.open(self.filename)
                print("Breaking bad")
                break
            strippedOut = output.strip()
            if strippedOut:
                if "Debug: analyze: Audio Length:" in strippedOut:
                    self.terminalOutputDisplay.configure(state='normal')
                    FrameCount = int(strippedOut.split(" ")[-1])
                    self.terminalOutputDisplay.insert(tk.END,"Frame Count: "+ str(FrameCount) + "\n")
                    self.terminalOutputDisplay.configure(state='disabled')
                if "Debug: Keyframe" in strippedOut:
                    try: 
                        deb_frame = int(strippedOut.split()[-2])
                        self.ProgressBar.set(deb_frame/(FrameCount))
                        self.ProgressBarPercentage.configure(text=str(int((deb_frame/(FrameCount))*100))+"%")
                    except:
                        pass
                if "Debug: Total frames saved seeking" in strippedOut:
                    self.export= True
                    self.ProgressBar.configure(mode='indeterminate')
                    self.ProgressBar.start()
                self.terminalOutputDisplay.configure(state='normal')
                self.terminalOutputDisplay.insert(tk.END, strippedOut + "\n")
                self.terminalOutputDisplay.configure(state='disabled')
                self.terminalOutputDisplay.see(tk.END)
            # self.root.after(100)  update every 100ms
            time.sleep(0.1)

    
    

if __name__ == '__main__':
        kernel32 = ctypes.windll.kernel32
        console_window = kernel32.GetConsoleWindow()

        # # Minimize the console window
        if console_window != 0:
            user32 = ctypes.windll.user32
            user32.ShowWindow(console_window, 6) # SW_MINIMIZE

        App()        
        
