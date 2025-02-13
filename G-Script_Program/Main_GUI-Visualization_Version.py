import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from graphviz import Digraph
import matplotlib.pyplot as plt
import time
import lexer
import parser
from collections import defaultdict
from pprint import pprint


class CompilerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("G Compiler UI")
        self.root.geometry("900x650")
        self.root.configure(bg="#f4f4f4")

        self.file_path = ""
        self.tokens_list = []
        self.parse_tree = {}
        self.symbol_table = []
        self.lexer_time = 0
        self.parser_time = 0

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Header
        tk.Label(
            self.root, text="G-Script Compiler", font=("Helvetica", 18, "bold"), bg="#f4f4f4", pady=10
        ).pack()

        # File Selection
        file_frame = tk.Frame(self.root, bg="#f4f4f4")
        file_frame.pack(pady=10)

        tk.Label(file_frame, text="Source File:", bg="#f4f4f4", font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
        self.file_entry = tk.Entry(file_frame, width=50, state="readonly", font=("Helvetica", 12))
        self.file_entry.grid(row=0, column=1, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_file, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(
            row=0, column=2, padx=5
        )

        # Buttons
        button_frame = tk.Frame(self.root, bg="#f4f4f4")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Compile", command=self.compile_file, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(
            row=0, column=0, padx=10
        )
        tk.Button(button_frame, text="Visualize Tokens", command=self.visualize_tokens, bg="#2196F3", fg="white", font=("Helvetica", 12)).grid(
            row=0, column=1, padx=10
        )
        tk.Button(button_frame, text="Display Symbol Table", command=self.display_symbol_table, bg="#FF9800", fg="white", font=("Helvetica", 12)).grid(
            row=0, column=2, padx=10
        )
        tk.Button(button_frame, text="Generate Parse Tree", command=self.generate_parse_tree, bg="#9C27B0", fg="white", font=("Helvetica", 12)).grid(
            row=0, column=3, padx=10
        )
        tk.Button(button_frame, text="Save Report", command=self.save_report, bg="#E91E63", fg="white", font=("Helvetica", 12)).grid(
            row=0, column=4, padx=10
        )

        # Logs
        tk.Label(self.root, text="Compiler Logs:", bg="#f4f4f4", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.log_text = scrolledtext.ScrolledText(self.root, width=100, height=20, font=("Courier", 10))
        self.log_text.pack(padx=10, pady=10)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.file_path = file_path
            self.file_entry.config(state="normal")
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.file_entry.config(state="readonly")

    def compile_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a source file first.")
            return

        try:
            with open(self.file_path, "r") as file:
                content = file.read()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Cannot find file: {self.file_path}")
            return

        # Lexer
        self.log("Running Lexer...")
        start_lexer_time = time.time()
        lex = lexer.Lexer()
        self.tokens_list = lex.tokenize(content)
        pprint(self.tokens_list)
        self.log("Tokens generated successfully.")
        end_lexer_time = time.time()
        self.lexer_time = end_lexer_time - start_lexer_time

        # Parser
        self.log("Running Parser...")
        start_parser_time = time.time()
        Parser = parser.Parser(self.tokens_list)
        parse_data = Parser.parse(self.tokens_list)
        self.parse_tree, self.symbol_table = parse_data
        pprint(parse_data)
        end_parser_time = time.time()
        self.parser_time = end_parser_time - start_parser_time

        self.log(f"Lexer Time: {self.lexer_time:.5f} seconds")
        self.log(f"Parser Time: {self.parser_time:.5f} seconds")
        self.log(f"Total Compiler Time: {self.lexer_time + self.parser_time:.5f} seconds")

    def visualize_tokens(self):
        if not self.tokens_list:
            messagebox.showerror("Error", "No tokens found to visualize. Please compile the file first.")
            return

        dot = Digraph(comment="Tokenization Tree")
        dot.attr(rankdir="LR")
        dot.attr("node", shape="ellipse", style="filled", fillcolor="lightblue", fontsize="12")

        grouped_tokens = defaultdict(list)
        for token in self.tokens_list:
            grouped_tokens[token[2]].append((token[0], token[1]))

        for line, tokens in grouped_tokens.items():
            for idx, (token_type, token_value) in enumerate(tokens):
                label = f"{token_type}\n{token_value}"
                dot.node(f"node_{line}_{idx}", label)

            for idx in range(len(tokens) - 1):
                dot.edge(f"node_{line}_{idx}", f"node_{line}_{idx + 1}")

        try:
            dot.render("token_visualization", format="png", view=True)
            # messagebox.showinfo("Success", "Token visualization generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate token visualization: {e}")
    
    def display_symbol_table(self):
        if not self.symbol_table:
            messagebox.showerror("Error", "Symbol table is empty. Please compile the file first.")
            return

        headers = self.symbol_table[0]
        rows = self.symbol_table[1:]

        fig, ax = plt.subplots(figsize=(10, 5))  # Adjusted size to make the window smaller

        ax.axis('tight')
        ax.axis('off')

        table = ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center', colColours=["#f5f5f5"]*len(headers))
        table.auto_set_font_size(False)
        table.set_fontsize(12)

        table.auto_set_column_width(col=list(range(len(headers))))

        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_fontsize(10)  
                cell.set_text_props(fontweight='bold', color='white')  
                cell.set_facecolor('#4CAF50')  
            else:
                if i % 2 == 0:  
                    cell.set_facecolor('#f2f2f2')  
                cell.set_fontsize(12)

            cell.set_edgecolor('black')
            cell.set_height(0.1)

        plt.title('G Symbol Table', fontsize=16, fontweight='bold')

        plt.show()


    def generate_parse_tree(self):
        if not self.parse_tree:
            messagebox.showerror("Error", "Parse tree is empty. Please compile the file first.")
            return

        def add_nodes_edges(graph, parent, subtree):
            if isinstance(subtree, dict):
                for key, value in subtree.items():
                    child = f"{parent}_{key}"
                    graph.node(child, key)
                    graph.edge(parent, child)
                    add_nodes_edges(graph, child, value)
            elif isinstance(subtree, list):
                for item in subtree:
                    add_nodes_edges(graph, parent, item)
            else:
                child = f"{parent}_{str(subtree)}"
                graph.node(child, str(subtree))
                graph.edge(parent, child)

        dot = Digraph(format="png", engine="dot")
        root = "G Program"
        dot.node(root, root)
        add_nodes_edges(dot, root, self.parse_tree)

        try:
            dot.render("parse_tree_graph", view=True)
            # messagebox.showinfo("Success", "Parse tree generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate parse tree: {e}")

    def save_report(self):
        if not self.tokens_list or not self.parse_tree or not self.symbol_table:
            messagebox.showerror("Error", "No data to save. Please compile a file first.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Save Report As"
            )
            if not file_path:
                return

            with open(file_path, "w") as file:
                file.write("=== Compiler Report ===\n\n")
                file.write("Tokens:\n")
                for token in self.tokens_list:
                    file.write(f"{token}\n")
                file.write("\n")

                file.write("Symbol Table:\n")
                headers = self.symbol_table[0]
                rows = self.symbol_table[1:]
                file.write(f"{' | '.join(headers)}\n")
                file.write("-" * 50 + "\n")
                for row in rows:
                    file.write(f"{' | '.join(map(str, row))}\n")
                file.write("\n")

                file.write("Parse Tree:\n")
                file.write(f"{self.parse_tree}\n\n")

                file.write("Compilation Times:\n")
                file.write(f"Lexer Time: {self.lexer_time:.5f} seconds\n")
                file.write(f"Parser Time: {self.parser_time:.5f} seconds\n")
                file.write(f"Total Compiler Time: {self.lexer_time + self.parser_time:.5f} seconds\n")

            messagebox.showinfo("Success", f"Report saved successfully at {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerUI(root)
    root.mainloop()
