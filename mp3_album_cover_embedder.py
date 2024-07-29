"""
MP3 Album Cover Embedder

This program allows users to embed album covers into MP3 files' metadata.
It provides a user-friendly GUI to select MP3 files and cover images,
and it supports resizing the cover image to fit specific dimensions.

Authors:
- Kaden Hansen
- ChatGPT (OpenAI)

Sources:
- ChatGPT (OpenAI): Assisted in developing and debugging the program.
- Python Documentation: Reference for the libraries used.

License:
- GitHub MIT License

Usage:
- Run the program to open the GUI.
- Select the MP3 folder and cover image.
- Follow the on-screen prompts to embed the cover image.

"""
import os
import io
import re
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Menu, Label, Button, Toplevel, Text, Scrollbar, END, Checkbutton, IntVar
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.id3 import ID3, APIC, error as ID3Error, ID3NoHeaderError
from PIL import Image, ImageOps
import pyperclip
import json

class MP3AlbumCoverEmbedder:
    """
    A class to encapsulate the functionality for embedding album covers into MP3 files.

    Attributes:
    root: tk.Tk - The main Tkinter window.
    DEFAULT_MP3_FOLDER: str - Default folder path for MP3 files.
    mp3_folder: str - Path to the selected MP3 folder.
    settings: dict - Dictionary to store user settings.
    SETTINGS_FILE: str - Path to the settings JSON file.
    """

    def __init__(self, root: tk.Tk):
        """
        Initializes the MP3AlbumCoverEmbedder class.

        Parameters:
        root: tk.Tk - The main Tkinter window.
        """
        self.root = root
        self.root.title("MP3 Album Cover Embedder")
        self.DEFAULT_MP3_FOLDER = os.path.expanduser("~/Music")
        self.settings = {}
        self.SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
        self.load_settings()

        self.mp3_folder = self.settings.get("mp3_folder", self.DEFAULT_MP3_FOLDER)
        self.embed_folder = self.settings.get("embed_folder", os.path.join(os.path.dirname(__file__), "MP3AlbumCoverEmbedderEmbeds"))
        self.auto_save_embed = self.settings.get("auto_save_embed", True)
        self.show_corrupt_warning = self.settings.get("show_corrupt_warning", True)

        self.setup_ui()

    def load_settings(self) -> None:
        """
        Loads settings from the JSON file.

        No Return
        """
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'r') as file:
                self.settings = json.load(file)
        else:
            os.makedirs(os.path.dirname(self.SETTINGS_FILE), exist_ok=True)
            self.save_settings()  # Ensure settings.json is created if it doesn't exist

    def save_settings(self) -> None:
        """
        Saves settings to the JSON file.

        No Return
        """
        with open(self.SETTINGS_FILE, 'w') as file:
            json.dump(self.settings, file)

    def setup_ui(self) -> None:
        """
        Sets up the user interface components.

        No Return
        """
        menu = Menu(self.root)
        self.root.config(menu=menu)

        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Music Folder", command=self.change_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit_program)

        settings_menu = Menu(menu)
        menu.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change Save Embed Path", command=self.change_embed_folder)
        settings_menu.add_checkbutton(label="Don't Auto-Save Embeds", command=self.toggle_auto_save_embed)

        help_menu = Menu(menu)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Instructions", command=self.show_instructions)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "MP3 Album Cover Embedder v1.0\n\nMade by: Kaden Hansen & ChatGPT\n\nView GitHub Page for more info."))

        self.folder_label = Label(self.root, text=f"Selected Folder: {self.mp3_folder}")
        self.folder_label.pack(pady=10)

        start_button = Button(self.root, text="Start Processing", command=self.start_processing)
        start_button.pack(pady=10)

        quit_button = Button(self.root, text="Quit", command=self.quit_program)
        quit_button.pack(pady=10)

    def focus_window(self, window: tk.Toplevel) -> None:
        """
        Forces any window to the front so that the
        user knows what's in focus.
        """
        window.focus_set()  # Set focus to the new window
        window.grab_set()  # Ensure the new window stays on top
        
    def change_embed_folder(self) -> None:
        """
        Opens a dialog to select the embed save folder and updates settings.

        No Return
        """
        embed_folder = filedialog.askdirectory(title="Select Embed Save Folder", initialdir=self.embed_folder)
        if embed_folder:
            self.embed_folder = embed_folder
            self.settings['embed_folder'] = embed_folder
            self.save_settings()

    def toggle_auto_save_embed(self) -> None:
        """
        Toggles the auto-save embed setting and updates settings.

        No Return
        """
        self.auto_save_embed = not self.auto_save_embed
        self.settings['auto_save_embed'] = self.auto_save_embed
        self.save_settings()

    def get_albums(self, folder: str) -> dict:
        """
        Retrieves albums from the given MP3 folder.

        Parameters:
        folder: str - Path to the folder containing MP3 files.

        Return dict - A dictionary of albums with album names as keys and lists of MP3 files as values.
        """
        albums = {}
        mp3_files = [f for f in os.listdir(folder) if f.lower().endswith('.mp3')]

        if not mp3_files:
            return albums

        corrupted_files = []

        for i, mp3_file in enumerate(mp3_files):
            mp3_path = os.path.join(folder, mp3_file)
            try:
                audio = MP3(mp3_path, ID3=ID3)
                album = audio.get('TALB')
                if album:
                    album_name = album.text[0]
                    if album_name not in albums:
                        albums[album_name] = []
                    albums[album_name].append(mp3_file)
                else:
                    # Create a default album name based on the filename
                    default_album_name = os.path.splitext(mp3_file)[0]

                    # Replace underscores and multiple spaces
                    default_album_name = re.sub(r'[_]', ' ', default_album_name)
                    default_album_name = re.sub(r' +', ' ', default_album_name)

                    # Add space between word and number if not already present
                    default_album_name = re.sub(r'(?<=\D)(?=\d)', ' ', default_album_name)

                    # Ensure " - " stays as it is
                    default_album_name = re.sub(r' - ', ' - ', default_album_name)

                    # Title case while ensuring words with three or fewer characters and apostrophes are handled correctly
                    words = default_album_name.split()
                    if words[0] == "mom's":
                        pass
                    for j, word in enumerate(words):
                        if '-' in word:
                            subwords = word.split('-')
                            subwords = [subwords[0].capitalize()] + [sw if len(sw) <= 3 else sw.capitalize() for sw in subwords[1:]]
                            words[j] = '-'.join(subwords)
                        elif len(word) <= 3 or (len(word) == 4 and "'" in word):
                            words[j] = word.lower()
                        else:
                            words[j] = word.capitalize()
                    default_album_name = ' '.join(words)

                    if default_album_name not in albums:
                        albums[default_album_name] = []
                    albums[default_album_name].append(mp3_file)
            except (ID3Error, IOError, HeaderNotFoundError, ID3NoHeaderError) as e:
                corrupted_files.append(mp3_file)
                mp3_files.pop(i)

        if corrupted_files and self.show_corrupt_warning:
            self.show_corrupted_files_warning(corrupted_files)

        return albums

    def show_corrupted_files_warning(self, corrupted_files: list) -> None:
        """
        Displays a warning with the list of corrupted or unreadable files.

        Parameters:
        corrupted_files: list - List of corrupted or unreadable files.

        No Return
        """
        warning_window = Toplevel()
        warning_window.title("Corrupted Files")

        warning_text = (
            "The following files could not be read and will be skipped:\n\n"
            "These files may be broken or corrupt. Please try downloading them again or using different files."
        )
        Label(warning_window, text=warning_text, font=("Helvetica", 12, "bold")).pack(pady=10)

        text_frame = tk.Frame(warning_window)
        text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        text_box = Text(text_frame, wrap=tk.WORD, height=10)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(text_frame, command=text_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_box.config(yscrollcommand=scrollbar.set)

        for file in corrupted_files:
            text_box.insert(END, f"{file}\n")

        text_box.config(state=tk.DISABLED)

        # Don't show again checkbox
        dont_show_again_var = IntVar()
        Checkbutton(warning_window, text="Don't show again", variable=dont_show_again_var).pack(side=tk.LEFT, padx=10, pady=10)

        def on_ok() -> None:
            """
            Handles the OK button click event, updating the settings if the "Don't show again" checkbox is selected.

            No Return
            """
            if dont_show_again_var.get() == 1:
                self.show_corrupt_warning = False
                self.settings['show_corrupt_warning'] = False
                self.save_settings()
            warning_window.destroy()
            self.check_for_music_files()

        Button(warning_window, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=10, pady=10)

        # Center the warning_window on the screen
        warning_window.update_idletasks()
        width = warning_window.winfo_width()
        height = warning_window.winfo_height()
        x = (warning_window.winfo_screenwidth() // 2) - (width // 2)
        y = (warning_window.winfo_screenheight() // 2) - (height // 2)
        warning_window.geometry(f'{width}x{height}+{x}+{y}')

        self.focus_window(warning_window)

    def check_for_music_files(self) -> None:
        """
        Checks for the presence of MP3 files in the selected folder and prompts the user to select a new folder if none are found.

        No Return
        """
        albums = self.get_albums(self.mp3_folder)
        if not albums:
            mp3_files = [f for f in os.listdir(self.mp3_folder) if f.lower().endswith('.mp3')]
            if not mp3_files:
                messagebox.showwarning("No Music Files", "No music files found in the selected folder. Please select a folder with MP3 files.")
                self.mp3_folder = self.select_folder()
                if not self.mp3_folder:
                    return  # User cancelled folder selection
                self.check_for_music_files()
            else:
                messagebox.showwarning("No Albums Found", "No albums found in the selected folder. Default albums will be created based on filenames.")
                self.continue_processing({os.path.splitext(f)[0].replace('_', ' ').replace('-', ' ').title(): [f] for f in mp3_files})
        else:
            self.continue_processing(albums)

    def resize_cover_image(self, cover_image_path: str) -> Image:
        """
        Resizes the cover image to 240x240 pixels.

        Parameters:
        cover_image_path: str - Path to the cover image file.

        Return Image - The resized cover image.
        """
        cover_image = Image.open(cover_image_path).convert("RGB")
        cover_image = ImageOps.fit(cover_image, (240, 240), method=Image.LANCZOS, bleed=0.0, centering=(0.5, 0.5))
        return cover_image

    def show_details_window(self, updated_files: list, embed_example_path: str, album_name: str) -> None:
        """
        Displays a details window with the list of updated files.

        Parameters:
        updated_files: list - List of updated MP3 files.
        embed_example_path: str - Path to the embed example image.
        album_name: str - Name of the album.

        No Return
        """
        details_window = Toplevel()
        details_window.title("Details")

        title_text = f"Items That Have Changed In {album_name}".title()
        title_label = Label(details_window, text=title_text, font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        text_frame = tk.Frame(details_window)
        text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        text_box = Text(text_frame, wrap=tk.WORD, height=15)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(text_frame, command=text_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_box.config(yscrollcommand=scrollbar.set)

        # Insert updated files into the text box as an ordered list
        for i, file in enumerate(updated_files, 1):
            text_box.insert(END, f"{i}. {file}\n")

        if embed_example_path:
            text_box.insert(END, f"\nEmbed example image path:\n{embed_example_path}")
            text_box.insert(END, "\n\nTo open the file, you can press the buttons below to copy the path to the image or open the image directly.")
        else:
            text_box.insert(END, "\nNo embed example was saved for this process.")

        text_box.config(state=tk.DISABLED)

        def copy_embed_path() -> None:
            """
            Copies the embed example path to the clipboard.

            No Return
            """
            pyperclip.copy(embed_example_path)
            messagebox.showinfo("Copied", "Embed example path copied to clipboard.")

        def open_embed_example() -> None:
            """
            Opens the embed example image.

            No Return
            """
            os.startfile(embed_example_path)

        if embed_example_path:
            Button(details_window, text="Copy Embed Example Path", command=copy_embed_path).pack(pady=5)
            Button(details_window, text="Open Embed Example", command=open_embed_example).pack(pady=5)

        Button(details_window, text="Done", command=details_window.destroy).pack(pady=10)

        # Center the details_window on the screen
        details_window.update_idletasks()
        width = details_window.winfo_width()
        height = details_window.winfo_height()
        x = (details_window.winfo_screenwidth() // 2) - (width // 2)
        y = (details_window.winfo_screenheight() // 2) - (height // 2)
        details_window.geometry(f'{width}x{height}+{x}+{y}')

        self.focus_window(details_window)

    def embed_album_cover(self, folder: str, cover_image_path: str, album_name: str, mp3_files: list, option: int, resize: bool = False) -> None:
        """
        Embeds the cover image into the MP3 files' metadata.

        Parameters:
        folder: str - Path to the folder containing MP3 files.
        cover_image_path: str - Path to the cover image file.
        album_name: str - Name of the album.
        mp3_files: list - List of MP3 files in the album.
        option: int - Option for saving the image (1: same name as MP3 file, 2: album name).
        resize: bool - Whether to resize the cover image.

        No Return
        """
        folder = os.path.normpath(folder)  # Normalize the path

        if self.auto_save_embed:
            album_images_folder = os.path.join(self.embed_folder, f"{album_name.lower()}_image")
            os.makedirs(album_images_folder, exist_ok=True)
        else:
            album_images_folder = ""

        if resize:
            cover_image = self.resize_cover_image(cover_image_path)
        else:
            cover_image = Image.open(cover_image_path).convert("RGB")

        short_image_path = os.path.basename(cover_image_path).split(".")[0]

        jpeg_image_path = os.path.join(album_images_folder, f"{short_image_path}_embed_example.jpg") if album_images_folder else None
        if jpeg_image_path:
            cover_image.save(jpeg_image_path, format='JPEG')

        with io.BytesIO() as img_bytes:
            cover_image.save(img_bytes, format='JPEG')
            cover_data = img_bytes.getvalue()

        updated_files = []

        for mp3_file in mp3_files:
            mp3_path = os.path.join(folder, mp3_file)
            try:
                audio = MP3(mp3_path, ID3=ID3)

                if audio.tags is None:
                    audio.add_tags()

                if 'TALB' in audio:
                    audio.tags['TALB'].encoding = 0
                if 'TPE1' in audio:
                    audio.tags['TPE1'].encoding = 0
                if 'TIT2' in audio:
                    audio.tags['TIT2'].encoding = 0

                audio.tags.delall('APIC')

                audio.tags.add(
                    APIC(
                        encoding=0,
                        mime='image/jpeg',
                        type=0,
                        desc='',
                        data=cover_data
                    )
                )

                audio.save()
                updated_files.append(mp3_path)

            except (ID3Error, IOError, HeaderNotFoundError, ID3NoHeaderError) as e:
                messagebox.showerror("Error", f"Error updating {mp3_file}: {e}")

        self.show_processing_complete_window(updated_files, jpeg_image_path, album_name)

    def show_processing_complete_window(self, updated_files: list, jpeg_image_path: str, album_name: str) -> None:
        """
        Displays a window indicating the processing is complete and provides options to view details.

        Parameters:
        updated_files: list - List of updated MP3 files.
        jpeg_image_path: str - Path to the embed example image.
        album_name: str - Name of the album.

        No Return
        """
        complete_window = Toplevel(self.root)
        complete_window.title("Processing Complete")

        Label(complete_window, text=f"All songs and the embed example image from the album '{album_name}' have been saved correctly.").pack(pady=10)
        Button(complete_window, text="OK", command=complete_window.destroy).pack(side=tk.LEFT, padx=20, pady=10)
        Button(complete_window, text="Details...", command=lambda: [complete_window.destroy(), self.show_details_window(updated_files, jpeg_image_path, album_name)]).pack(side=tk.RIGHT, padx=20, pady=10)

        # Center the complete_window on the screen
        complete_window.update_idletasks()
        width = complete_window.winfo_width()
        height = complete_window.winfo_height()
        x = (complete_window.winfo_screenwidth() // 2) - (width // 2)
        y = (complete_window.winfo_screenheight() // 2) - (height // 2)
        complete_window.geometry(f'{width}x{height}+{x}+{y}')

        self.focus_window(complete_window)

    def select_folder(self) -> str:
        """
        Opens a dialog to select a folder.

        Return str - Path to the selected folder.
        """
        while True:
            folder_selected = filedialog.askdirectory(title="Select MP3 Folder", initialdir=self.DEFAULT_MP3_FOLDER)
            if not folder_selected:
                action = self.custom_warning_box("Selection Cancelled", "You cancelled the folder selection. What would you like to do?", True)
                if action == 'try':
                    continue
                elif action == 'back':
                    self.focus_window(self.root)
                    return None
                elif action == 'quit':
                    self.root.destroy()
                    return None
            else:
                return os.path.normpath(folder_selected)

    def select_image(self) -> str:
        """
        Opens a dialog to select an image file.

        Return str - Path to the selected image file.
        """
        while True:
            file_selected = filedialog.askopenfilename(title="Select Cover Image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")], initialdir=os.path.expanduser("~/Pictures"))
            if not file_selected:
                action = self.custom_warning_box("Selection Cancelled", "You cancelled the image selection. What would you like to do?", True)
                if action == 'try':
                    continue
                elif action == 'back':
                    self.focus_window(self.root)
                    return None
                elif action == 'quit':
                    self.root.destroy()
                    return None
            else:
                return file_selected

    def select_image_window(self) -> None:
        """
        Opens a window to select an image file and proceed with the embedding process.

        No Return
        """
        cover_image_path = self.select_image()
        if not cover_image_path:
            return  # User cancelled the selection or went back
        self.continue_processing(self.albums, cover_image_path)

    def start_processing(self) -> None:
        """
        Starts the process of embedding album covers into MP3 files.

        No Return
        """
        if not self.mp3_folder:
            messagebox.showerror("Error", "No music folder selected.")
            return

        self.check_for_music_files()

    def continue_processing(self, albums: dict, cover_image_path: str = None) -> None:
        """
        Continues the process of embedding album covers into MP3 files after checking for music files.

        Parameters:
        albums: dict - Dictionary of albums with album names as keys and lists of MP3 files as values.
        cover_image_path: str - Path to the selected cover image file (optional).

        No Return
        """
        self.albums = albums  # Save the albums state for navigation
        if cover_image_path is None:
            self.select_image_window()
            return

        album_keys = list(albums.keys())
        if len(album_keys) >= 15:
            album_window = Toplevel(self.root)
            album_window.title("Select Album")

            Label(album_window, text="Select an album by entering the number:").pack(pady=10)

            text_frame = tk.Frame(album_window)
            text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            text_box = Text(text_frame, wrap=tk.WORD, height=15)
            text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = Scrollbar(text_frame, command=text_box.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_box.config(yscrollcommand=scrollbar.set)

            album_str = "\n".join(f"{i+1}. {album}" for i, album in enumerate(album_keys))
            text_box.insert(END, album_str)
            text_box.config(state=tk.DISABLED)

            def on_back() -> None:
                """
                Handles the Back button click event.

                No Return
                """
                album_window.destroy()
                self.select_image_window()

            back_button = Button(album_window, text="Back", command=on_back)
            back_button.pack(side=tk.LEFT, padx=10, pady=10)

            def on_cancel() -> None:
                """
                Handles the Cancel button click event.

                No Return
                """
                album_window.destroy()
                self.select_image_window()

            cancel_button = Button(album_window, text="Cancel", command=on_cancel)
            cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

            valid_selection = False
            while not valid_selection:
                album_index = simpledialog.askinteger("Select Album", "Enter the album number:", parent=album_window)

                if album_index is not None and (1 <= album_index <= len(albums)):
                    valid_selection = True
                else:
                    messagebox.showwarning("Invalid Selection", "You entered an invalid selection. Please try again.")

            album_window.destroy()
        else:
            album_str = "\n".join(f"{i+1}. {album}" for i, album in enumerate(albums.keys()))

            valid_selection = False
            while not valid_selection:
                album_index = simpledialog.askinteger("Select Album", f"Select an album by entering the number:\n{album_str}")
                if isinstance(album_index, int) and album_index > len(albums):
                    messagebox.showwarning("Invalid Option", "You entered an invalid number. Please try again.")
                    continue
                elif album_index is not None and (1 <= album_index <= len(albums)):
                    valid_selection = True
                else:
                    response = self.custom_warning_box("Invalid Selection", "You cancelled the album selection. What would you like to do?")
                    if response == 'try':
                        continue
                    elif response == 'back':
                        self.select_image_window()
                        return
                    elif response == 'quit':
                        self.root.destroy()
                        return

        selected_album = album_keys[album_index - 1]
        mp3_files = albums[selected_album]

        valid_option = False
        while not valid_option:
            option = simpledialog.askinteger("Select Option", "Choose an option:\n1. Save image with the same name as the MP3 file\n2. Save image with the album name", initialvalue=2)
            
            if option in [1, 2]:
                valid_option = True
            else:
                action = self.custom_warning_box("Selection Cancelled", "You cancelled the image embed name option window. What would you like to do?")
                if action == 'try':
                    continue
                elif action == 'back':
                    self.continue_processing(albums, cover_image_path)
                elif action == 'quit':
                    self.root.destroy()
                    return None

        resize = messagebox.askyesno("Resize Image", "Resize cover image to 240x240 for MECHEN 2.4\" screen MP3/MP4 player?\n\n(Pressing no will save the original image to the file.)")

        self.embed_album_cover(self.mp3_folder, cover_image_path, selected_album, mp3_files, option, resize)

    def custom_warning_box(self, title: str, message: str, filedialog: bool = False) -> str:
        """
        Displays a custom warning box with options: Try Selection Again, Back, and Quit.

        Parameters:
        title: str - Title of the warning box.
        message: str - Message to be displayed in the warning box.
        filedialog: bool - Whether the warning is triggered by a file dialog (default: False).

        Return str - The option selected by the user: 'try', 'back', or 'quit'.
        """
        warning_window = Toplevel(self.root)
        warning_window.title(title)
        Label(warning_window, text=message).pack(pady=10)

        selected_option = tk.StringVar()

        def on_try_again() -> None:
            selected_option.set('try')
            warning_window.destroy()

        def on_back() -> None:
            selected_option.set('back')
            warning_window.destroy()

        def on_quit() -> None:
            if messagebox.askyesno("Confirm Quit", "Are you sure you want to quit? (This will quit the program entirely, saving no data.)"):
                selected_option.set('quit')
                warning_window.destroy()
        
        # Place the default back button before the Try selection again for better looks
        Button(warning_window, text="< Back", command=on_back).pack(side=tk.LEFT, padx=10, pady=10)

        # If the step completed was a dialog box, put this button in the window.
        if filedialog:
            Button(warning_window, text="Try Selection Again", command=on_try_again).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Another default button which will quit the program.
        Button(warning_window, text="Quit", command=on_quit).pack(side=tk.RIGHT, padx=10, pady=10)

        # Center the warning_window on the screen
        warning_window.update_idletasks()
        width = warning_window.winfo_width()
        height = warning_window.winfo_height()
        x = (warning_window.winfo_screenwidth() // 2) - (width // 2)
        y = (warning_window.winfo_screenheight() // 2) - (height // 2)
        warning_window.geometry(f'{width}x{height}+{x}+{y}')

        self.root.wait_window(warning_window)
        return selected_option.get()

    def change_folder(self) -> None:
        """
        Changes the selected music folder.

        No Return
        """
        self.mp3_folder = self.select_folder()
        if self.mp3_folder:
            self.settings['mp3_folder'] = self.mp3_folder
            self.save_settings()
            self.folder_label.config(text=f"Selected MP3 File Folder: {self.mp3_folder}")

    def show_instructions(self) -> None:
        """
        Displays a window with detailed instructions on how to use the program.

        No Return
        """
        instructions_window = Toplevel()
        instructions_window.title("Instructions")

        instructions = (
            "MP3 Album Cover Embedder v1.0\n\n"
            "This program allows you to correctly embed album covers into MP3 files' metadata. "
            "Follow these steps to use the program:\n\n"
            "1. Select the MP3 folder: Click 'File' > 'Change Music Folder' to select the folder "
            "containing your MP3 files. By default, it uses the path to your Music folder.\n\n"
            "2. Start Processing: Click 'Start Processing' to begin the process of embedding album covers. "
            "The program will analyze the selected folder and list all albums found.\n\n"
            "3. Select Album: When prompted, select the album you want to update by entering the corresponding number.\n\n"
            "4. Select Cover Image: Choose the cover image file you want to embed into the MP3 files.\n\n"
            "5. Choose Save Option: You will be prompted to choose how to save the image: "
            "1) Save with the same name as the MP3 file or 2) Save with the album name.\n\n"
            "6. Resize Image: Choose whether to resize the cover image to 240x240 pixels for compatibility with the MECHEN 2.4\" screen MP3/MP4 player.\n\n"
            "7. Completion: After processing, a completion window will appear with options to view detailed changes or finish.\n\n"
            "8. Details: If you choose to view details, you will see a list of all updated MP3 files and the path to the embed example image.\n\n"
            "Additional Features:\n"
            "- 'Copy Embed Example Path' button to copy the embed example image path to clipboard.\n"
            "- 'Open Embed Example' button to open the embed example image in the default application.\n"
            "- 'Quit' button to exit the program.\n\n"
            "Settings:\n"
            "- 'Change Save Embed Path': Allows you to change the folder where embed example images are saved.\n"
            "- 'Don't Auto-Save Embeds': If checked, you will be prompted to save an embed example image after processing.\n\n"
            "For more information, refer to the README on GitHub or contact me at mp3.m4r.gitproject@gmail.com."
        )

        Label(instructions_window, text="Instructions", font=("Helvetica", 16, "bold")).pack(pady=10)
        text_frame = tk.Frame(instructions_window)
        text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        text_box = Text(text_frame, wrap=tk.WORD, height=20)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(text_frame, command=text_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_box.config(yscrollcommand=scrollbar.set)

        text_box.insert(END, instructions)
        text_box.config(state=tk.DISABLED)

        Button(instructions_window, text="Close", command=instructions_window.destroy).pack(pady=10)

        # Center the instructions_window on the screen
        instructions_window.update_idletasks()
        width = instructions_window.winfo_width()
        height = instructions_window.winfo_height()
        x = (instructions_window.winfo_screenwidth() // 2) - (width // 2)
        y = (instructions_window.winfo_screenheight() // 2) - (height // 2)
        instructions_window.geometry(f'{width}x{height}+{x}+{y}')

        self.focus_window(instructions_window)

    def quit_program(self) -> None:
        """
        Quits the program.

        No Return
        """
        if messagebox.askyesno("Confirm Quit", "Are you sure you want to quit?"):
            self.root.quit()
        else:
            os.close(0)
            
if __name__ == "__main__":
    root = tk.Tk()
    app = MP3AlbumCoverEmbedder(root)
    root.mainloop()