class ModernTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Text Editor")
        self.root.geometry("1000x600")

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.create_widgets()
        self.create_menu()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(expand=1, fill='both')

        self.text_area = ctk.CTkTextbox(self.main_frame, wrap='word', undo=True)
        self.text_area.pack(expand=1, fill='both', side='right', padx=10, pady=10)

        self.status_bar = ctk.CTkLabel(self.root, text="Line: 1 | Column: 1", anchor='e')
        self.status_bar.pack(side='bottom', fill='x')

        self.text_area.bind('<KeyRelease>', self.update_status_bar)
        self.text_area.bind('<KeyRelease>', self.apply_syntax_highlighting)
        self.update_status_bar(None)

        self.file_explorer = ttk.Treeview(self.main_frame)
        self.file_explorer.pack(side='left', fill='y', padx=10, pady=10)
        self.file_explorer.bind('<<TreeviewSelect>>', self.on_file_select)

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.configure(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open File", command=self.open_file)
        self.file_menu.add_command(label="Open Folder", command=self.open_folder)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_editor)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=lambda: self.text_area.event_generate("<<Undo>>"))
        self.edit_menu.add_command(label="Redo", command=lambda: self.text_area.event_generate("<<Redo>>"))

    def new_file(self):
        self.text_area.delete(1.0, tk.END)

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                               filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.INSERT, content)
                self.update_status_bar(None)
                self.apply_syntax_highlighting(None)

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_file_explorer(folder_path)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                content = self.text_area.get(1.0, tk.END)
                file.write(content)

    def exit_editor(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()

    def update_status_bar(self, event):
        line, column = self.text_area.index(tk.INSERT).split('.')
        self.status_bar.configure(text=f"Line: {line} | Column: {column}")

    def apply_syntax_highlighting(self, event):
        self.text_area.tag_remove('keyword', '1.0', tk.END)
        self.text_area.tag_remove('comment', '1.0', tk.END)
        self.text_area.tag_remove('string', '1.0', tk.END)
        self.text_area.tag_remove('number', '1.0', tk.END)

        code = self.text_area.get(1.0, tk.END)
        self.highlight_pattern(r'\b(def|class|return|if|else|elif|while|for|import|from|as|try|except|finally|with|and|or|not|in|is|lambda|True|False)\b', 'keyword')
        self.highlight_pattern(r'#.*', 'comment')
        self.highlight_pattern(r'\".*?\"|\'[^\']*\'', 'string')
        self.highlight_pattern(r'\b\d+\b', 'number')

    def highlight_pattern(self, pattern, tag):
        start = '1.0'
        while True:
            pos = self.text_area.search(pattern, start, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end = f"{pos}+{len(self.text_area.get(pos, tk.INSERT))}c"
            self.text_area.tag_add(tag, pos, end)
            self.text_area.tag_config(tag, foreground=self.get_color_for_tag(tag))
            start = end

    def get_color_for_tag(self, tag):
        colors = {
            'keyword': 'blue',
            'comment': 'green',
            'string': 'red',
            'number': 'orange'
        }
        return colors.get(tag, 'black')

    def populate_file_explorer(self, folder_path):
        for item in self.file_explorer.get_children():
            self.file_explorer.delete(item)
        root_node = self.file_explorer.insert('', 'end', text=folder_path, open=True)
        self._populate_tree(root_node, folder_path)

    def _populate_tree(self, parent, path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            node = self.file_explorer.insert(parent, 'end', text=item, open=False)
            if is_dir:
                self._populate_tree(node, item_path)

    def on_file_select(self, event):
        selected_item = self.file_explorer.selection()[0]
        file_path = self.get_full_path(selected_item)
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.INSERT, content)
                self.update_status_bar(None)
                self.apply_syntax_highlighting(None)

    def get_full_path(self, item):
        path_parts = []
        while item:
            path_parts.insert(0, self.file_explorer.item(item, "text"))
            item = self.file_explorer.parent(item)
        return os.path.join(*path_parts)
