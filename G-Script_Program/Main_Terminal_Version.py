import lexer
import parser
import time
from pprint import pprint
# from graphviz import Digraph
# import matplotlib.pyplot as plt
# from collections import defaultdict

class main:
    def __init__(self):
        self.tokens_list = []
        self.parse_tree = {}
        self.symbol_table = []

    def compiler(self, file_path):
        content = ""
        file_path = file_path

        try:
            with open(file_path, "r") as file:
                content = file.read()
        except FileNotFoundError:
            print(f'[ERROR] Cannot find file "{file_path}". Please check the path and try again.')
            return

        # --------------------------------------
        #  LEXER
        # --------------------------------------

        print('|||||||||||||||||||||  LEXER LOG  ||||||||||||||||||||| \n')
        start_lexer_time = time.time()
        lex = lexer.Lexer()
        tokens = lex.tokenize(content)
        self.tokens_list = tokens
        # lex.process_file(content, 'tokens.txt')
        pprint(tokens)
        end_lexer_time = time.time()
        print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')

        # --------------------------------------
        #  PARSER
        # --------------------------------------

        print('|||||||||||||||||||||  PARSER LOG  |||||||||||||||||||| \n')
        start_parser_time = time.time()
        Parser = parser.Parser(tokens)
        parse_data = Parser.parse(tokens)
        self.parse_tree = parse_data[0]
        self.symbol_table = parse_data[1]
        pprint(parse_data)
        end_parser_time = time.time()
        print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||| \n')

        # --------------- TIME -------------------
        lexer_time = end_lexer_time - start_lexer_time
        parser_time = end_parser_time - start_parser_time

        print(f"Lexer Time: {lexer_time:.5f} seconds")
        print(f"Parser Time: {parser_time:.5f} seconds")
        print(f"Total Compiler Time: {(lexer_time + parser_time):5f} seconds")

    # ----------------------------- TOKENS VISUALIZATION -------------------------------

    # def visualize_tokens(self):
    #     if not self.tokens_list:
    #         print("[ERROR] No tokens found to visualize. Please run the compiler first.")
    #         return

    #     dot = Digraph(comment='Tokenization Tree')
    #     dot.attr(rankdir='LR')
    #     dot.attr('node', shape='ellipse', style='filled', fillcolor='lightblue', fontsize='12')

    #     grouped_tokens = defaultdict(list)
    #     for token in self.tokens_list:
    #         grouped_tokens[token[2]].append((token[0], token[1]))

    #     reversed_lines = sorted(grouped_tokens.keys(), reverse=True)

    #     for line in reversed_lines:
    #         tokens = grouped_tokens[line]
    #         for idx, (token_type, token_value) in enumerate(tokens):
    #             label = f"{token_type}\n{token_value}"
    #             dot.node(f'node_{line}_{idx}', label)

    #     for line in reversed_lines:
    #         tokens = grouped_tokens[line]
    #         for idx in range(len(tokens) - 1):
    #             dot.edge(f'node_{line}_{idx}', f'node_{line}_{idx + 1}')

    #     try:
    #         dot.render('token_visualization_horizontal', format='png', view=True)
    #         print("[INFO] Token visualization generated successfully.")
    #     except Exception as e:
    #         print(f"[ERROR] Failed to generate token visualization: {e}")

    # ----------------------------  SYMBOL TABLE  -----------------------------------
    # def display_table(self):
    #     data = self.symbol_table

    #     headers = data[0]
    #     rows = data[1:]

    #     fig, ax = plt.subplots(figsize=(10, 5))  # Adjusted size to make the window smaller

    #     ax.axis('tight')
    #     ax.axis('off')

    #     table = ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center', colColours=["#f5f5f5"]*len(headers))

    #     table.auto_set_font_size(False)
    #     table.set_fontsize(12)
    #     table.auto_set_column_width(col=list(range(len(headers))))
    #     plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    #     for (i, j), cell in table.get_celld().items():
    #         if i == 0:
    #             cell.set_fontsize(10)  # Smaller font size for the header
    #             cell.set_text_props(fontweight='bold', color='white')  # Bold and white text in header
    #             cell.set_facecolor('#4CAF50')  # Set header background color
    #         else:
    #             if i % 2 == 0:  
    #                 cell.set_facecolor('#f2f2f2')  
    #             cell.set_fontsize(12)

    #         cell.set_edgecolor('black')
    #         cell.set_height(0.1)

    #     plt.title('Symbol Table', fontsize=16, fontweight='bold')

    #     plt.show()

    # ----------------------------  AST TREE  -----------------------------------

    # def generate_parse_tree_graph(self):
    #     def add_nodes_edges(graph, parent, subtree):
    #         if isinstance(subtree, dict):
    #             for key, value in subtree.items():
    #                 child = f"{parent}_{key}"  # Unique node label
    #                 graph.node(child, key)  # Add node with key as label
    #                 graph.edge(parent, child)  # Add edge
    #                 add_nodes_edges(graph, child, value)
    #         elif isinstance(subtree, list):
    #             for item in subtree:
    #                 add_nodes_edges(graph, parent, item)  # Keep adding to the same parent
    #         else:
    #             # Leaf node
    #             child = f"{parent}_{str(subtree)}"
    #             graph.node(child, str(subtree))
    #             graph.edge(parent, child)

    #     dot = Digraph(format="png", engine="dot")
    #     root = "Program"
    #     dot.node(root, root)
    #     add_nodes_edges(dot, root, self.parse_tree)

    #     dot.render("parse_tree_graph", view=True)


program = main()
program.compiler("code_test.txt")

# Visualization
# program.visualize_tokens()
# program.display_table()
# program.generate_parse_tree_graph()