class Parser:
    def __init__(self, token_stream):
        self.source_ast = { 'main_scope': [] }
        self.symbol_table = [["name", "type", "value", "size", "dimension", "line_of_declaration", "line_of_usage", "address"]]
        self.been_declared = []
        self.token_stream = token_stream
        self.token_index = 0

    def parse(self, token_stream):

        while self.token_index < len(token_stream):
            token_type = token_stream[self.token_index][0]
            token_value = token_stream[self.token_index][1]
            
            # DONE
            if token_type == "DATATYPE" :
                self.declaration_parser(token_stream[self.token_index:], False)
            
            elif token_type == "KEYWORD" and token_value == "if":
                self.condition_statement_parser(token_stream[self.token_index:],False)

            # DONE
            elif token_type == "KEYWORD" and token_value == "while":
                self.while_loop_parser(token_stream[self.token_index:], False)

            # DONE
            elif token_type == "KEYWORD" and token_value == "for":
                self.for_loop_parser(token_stream[self.token_index:], False)
            
            elif token_type == "KEYWORD" and token_value == "fin":
                self.fin_loop_parser(token_stream[self.token_index:], False)

            # DONE
            elif token_type == "IDENTIFIER":
                self.assignment_parser(token_stream[self.token_index:], False)
            
            # DONE
            elif token_type == "PRINT_FUNCTION":
                self.print_function_parser(token_stream[self.token_index:], False)

            else:
                self.send_error_message(f"Unexpected token '{token_value}'", token_stream[self.token_index:])

        return [self.source_ast , self.symbol_table]



#  ----------------------------------------------------------------

# Ahmed
    def print_function_parser(self, token_stream, isInBody):
        ast = {'PrebuiltFunction': []}
        tokens_checked = 0

        for x in range(0, len(token_stream)):
            tokens_checked += 1
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            if x == 0:
                ast['PrebuiltFunction'].append( {'type': token_type} )

            elif x == 1:
                if token_value == "(":
                    continue
                else:
                    self.send_error_message("Missing '(' after function name", token_stream[x-1:x+1])

            elif x == 2 :
                if token_type in ['NUMBER', 'STRING', 'IDENTIFIER']:

                    if token_stream[x+1][1] == ")" :
                        if token_stream[x+2][1] == ";":
                            ast['PrebuiltFunction'].append( {'arguments': token_type} )
                            if token_type == 'NUMBER' or token_type == 'STRING':
                                ast['PrebuiltFunction'].append( {'value': token_value} )
                            else:
                                if token_value in self.been_declared:
                                    for line in self.symbol_table:
                                        if line[0] == token_value:
                                            line[6].append(token_stream[x][2])
                                            break
                                    ast['PrebuiltFunction'].append( {'value': token_value} )

                                else:
                                    self.send_error_message("Variable '%s' does not exist" % token_value, token_stream[0:tokens_checked + 1])
                            tokens_checked += 2
                            break
                        else:
                            self.send_error_message("Missing ';' after function call", token_stream[x-1:x+1])
                    else:
                        expression_tokens = []
                        op,cl = 0,0
                        flag = True
                        for token in token_stream[x:]:
                            if token[1] == "(":
                                op += 1
                            elif token[1] == ")":
                                cl += 1
                                if cl > op:
                                    flag = False
                                    break
                            expression_tokens.append(token)
                            tokens_checked += 1
                        if flag :
                            self.send_error_message("Missing ')' to close print()", token_stream[0:x+1])
                        else:
                            expression = self.equation_parser(expression_tokens)
                            ast['PrebuiltFunction'].append( {'value': expression[0]} )
                            if token_stream[tokens_checked][1] == ";":
                                tokens_checked += 1
                                break
                            else:
                                self.send_error_message("Missing ';' after print statement", token_stream[x-1:x+1])
        if not isInBody: 
            self.source_ast['main_scope'].append(ast)
            self.token_index += tokens_checked

        return [ast, tokens_checked]


    def equation_parser(self, equation):
        def parse_expression(tokens, min_precedence=0):
            nonlocal index
            if tokens[index][0] in ["NUMBER", "IDENTIFIER"]:
                if tokens[index][0] == "IDENTIFIER":
                    if tokens[index][1] in self.been_declared:
                        for line in self.symbol_table:
                            if line[0] == tokens[index][1]:
                                line[6].append(tokens[index][2])
                                break
                    else:
                        self.send_error_message(f"Variable '{tokens[index][1]}' is not declared.", tokens[index:])
                left_operand = {"type": tokens[index][0], "value": tokens[index][1]}
                index += 1
            elif tokens[index][0] == "DELIMITER" and tokens[index][1] == "(":
                index += 1
                left_operand = parse_expression(tokens)  # Recursively parse the sub-expression
                if index >= len(tokens) or tokens[index][0] != "DELIMITER" or tokens[index][1] != ")":
                    self.send_error_message(
                        "Missing ')' in equation",
                        tokens[:index + 1] if index < len(tokens) else tokens
                    )
                index += 1 
            else:
                self.send_error_message(
                    "Expected number, identifier, or '('",
                    tokens[:index + 1] if index < len(tokens) else tokens
                )

            while index < len(tokens) and tokens[index][0] == "MATHEMATICAL_OPERATOR" and precedence[tokens[index][1]] >= min_precedence:
                operator = tokens[index][1]
                current_precedence = precedence[operator]

                next_precedence = current_precedence + (1 if operator not in right_associative else 0)

                index += 1
                right_operand = parse_expression(tokens, next_precedence)

                left_operand = {
                    "type": "BinaryOperation",
                    "operator": operator,
                    "left": left_operand,
                    "right": right_operand
                }

            return left_operand

        precedence = {
            "**": 3,  # Highest
            "*": 2,
            "/": 2,
            "%": 2,
            "+": 1,
            "-": 1
        }

        right_associative = {"**"}

        index = 0
        ast = parse_expression(equation) 
        if index < len(equation):
            self.send_error_message("Unexpected tokens after equation", equation[index:])

        return ast, index


# Gana
    def declaration_parser(self, token_stream, isInBody):

        ast = {'Declaration': [] }  
        tokens_checked = 0
        vld = False

        for x in range(0, len(token_stream)):
            tokens_checked += 1  
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            if x == 0: 
                ast['Declaration'].append({ "type": token_value })
                self.variable_line = token_stream[x][2]

            elif x == 1:
                if token_type == "IDENTIFIER":
                    if token_value in self.been_declared:
                        self.send_error_message("Variable '%s' already exists and cannot be defined again!" % token_value, self.token_stream[self.token_index:self.token_index + tokens_checked + 1])
                    else:
                        ast['Declaration'].append({ "name": token_value })
                        self.been_declared.append(token_value)

                else:
                    self.send_error_message("Invalid Variable Name '%s'" % token_value, self.token_stream[self.token_index:self.token_index + tokens_checked + 1] )

            elif x == 2:
                if token_type == "ASSIGNMENT_OPERATOR":
                    continue
                elif token_type == "END_LINE_OPERATOR":
                    ast['Declaration'].append({ "value": 'undefined' })
                    break
                else:
                    self.send_error_message("Variable Declaration Missing '='.", self.token_stream[self.token_index:self.token_index + tokens_checked + 2])

            elif x == 3 :
                if token_stream[x + 1][0] == "END_LINE_OPERATOR":
                    if (token_value.isnumeric() and token_stream[0][1] == "int") or (not(token_value.isnumeric()) and token_stream[0][1] == "str") or ( token_type == "ARRAY" and token_stream[0][1] == "arr"):
                        ast['Declaration'].append({ "value": token_value })
                        tokens_checked += 1
                        vld = False
                        break
                    else:
                        self.send_error_message("Variable value does not match defined type!", self.token_stream[self.token_index:self.token_index + tokens_checked + 1])

                else:
                    expression_tokens = []
                    op,cl = 0,0
                    flag = True
                    for token in token_stream[x:]:
                        if token[1] == ";":
                                flag = False
                                break
                        expression_tokens.append(token)
                        tokens_checked += 1
                    if flag :
                        self.send_error_message("Missing ';'", token_stream[0:x+1])
                    else:
                        expression = self.equation_parser(expression_tokens)
                        ast['Declaration'].append( {'value': expression[0]} )
                        vld = True
                        if token_stream[tokens_checked-1][1] == ";":
                            break
                        else:
                            self.send_error_message("Missing ';' after print statement", token_stream[x-1:x+1])

        type = ast['Declaration'][0]['type']
        name = ast['Declaration'][1]['name']
        value = ast['Declaration'][2]['value']
        if vld :value = "ex"
        

        if type == "int":
            size = 4
            dimension = 0
        elif type == "str":
            size = 2
            dimension = 0
        else:
            try:
                l = eval(value)
                num = len(l)
                if int(l[0]) == l[0] :
                    size = 4 * num
                else:
                    size = 2 * num
                dimension = 1
            except:
                self.send_error_message("Invalid object declaration!", self.token_stream[self.token_index:self.token_index + tokens_checked] )

        line_of_declaration = self.variable_line
        line_of_usage = [self.variable_line]

        if len(self.symbol_table) == 1:
            address = 0
        else:
            address = self.symbol_table[-1][-1] + self.symbol_table[-1][3]

        self.symbol_table.append( [name, type, value, size, dimension, line_of_declaration, line_of_usage, address] )

        if not isInBody:
            self.source_ast['main_scope'].append(ast)
            self.token_index += tokens_checked

        return [ast, tokens_checked]

    def assignment_parser(self, token_stream, isInBody):
        ast = {'Assignment': [] }  
        tokens_checked = 0

        for x in range(0, len(token_stream)):
            tokens_checked += 1
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            if x == 0:
                if token_type == "IDENTIFIER":
                    if token_value not in self.been_declared:
                        self.send_error_message("Variable '%s' does not exist" % token_value, self.token_stream[self.token_index:self.token_index + tokens_checked + 1])
                    else:
                        self.variable_line = token_stream[x][2]
                        ast['Assignment'].append({ "name": token_value })

                else:
                    self.send_error_message("Invalid Variable Name '%s'" % token_value, self.token_stream[self.token_index:self.token_index + tokens_checked + 1] )

            elif x == 1:
                if token_type == "ASSIGNMENT_OPERATOR":
                    continue
                else:
                    self.send_error_message("Variable Assignment Missing '='.", self.token_stream[self.token_index:self.token_index + tokens_checked + 2])

            elif x == 2 :
                if token_stream[x + 1][0] == "END_LINE_OPERATOR":
                    for line in self.symbol_table:
                        if line[0] == ast['Assignment'][0]["name"]:
                            crr_data = line[1]
                            line[6].append(token_stream[x - 1][2])
                            line[2] = token_value
                    
                    if (token_value.isnumeric() and crr_data == "int") or (not(token_value.isnumeric()) and crr_data == "str"):
                        ast['Assignment'].append({ "value": token_value })
                        tokens_checked += 1
                        vld = False
                        break
                    else:
                        self.send_error_message("Variable value does not match defined type!", self.token_stream[self.token_index:self.token_index + tokens_checked + 1])

                else:
                    expression_tokens = []
                    op,cl = 0,0
                    flag = True
                    for token in token_stream[x:]:
                        if token[1] == ";":
                                flag = False
                                break
                        expression_tokens.append(token)
                        tokens_checked += 1
                    if flag :
                        self.send_error_message("Missing ';'", token_stream[0:x+1])
                    else:
                        expression = self.equation_parser(expression_tokens)
                        ast['Assignment'].append( {'value': expression[0]} )
                        vld = True
                        if token_stream[tokens_checked-1][1] == ";":
                            break
                        else:
                            self.send_error_message("Missing ';'", token_stream[x-1:x+1])
        
        if vld:
            for line in self.symbol_table:
                if line[0] == ast['Assignment'][0]["name"]:
                    line[6].append(token_stream[x - 3][2])
                    line[2] = "ex"

        if not isInBody:
            self.source_ast['main_scope'].append(ast)
            self.token_index += tokens_checked

        return [ast, tokens_checked]





# shimaa

    def for_loop_parser(self, token_stream, isInBody):
        tokens_checked = 0
        ast = {"ForStatement": {"initialization": [], "condition": [], "iteration": [], "body": []}}

        for x in range(len(token_stream)):
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            tokens_checked += 1

            if x == 0 :
                continue

            if x == 1:
                if token_value == "(":
                    continue
                else:
                    self.send_error_message("Missing '(' after 'for'", token_stream[0:tokens_checked])

            elif x == 2:
                if token_type == "IDENTIFIER" and token_value in self.been_declared:
                    for line in self.symbol_table:
                        if line[0] == token_value:
                            line[6].append(token_stream[x][2])
                            line[2] = token_stream[x+2][1]
                            break
                    ast['ForStatement']['initialization'].append({'name': token_value})
                elif token_type == "IDENTIFIER" and token_value not in self.been_declared:
                    self.symbol_table.append([token_value, "int", token_stream[x+2][1], 4, 0, token_stream[x][2], [token_stream[x][2]], 4 + self.symbol_table[-1][-1]])
                    self.been_declared.append(token_value)
                    ast['ForStatement']['initialization'].append({'name': token_value})
                    ast['ForStatement']['initialization'].append({'value': token_stream[x+2][1]})
                else:
                    self.send_error_message("Expected 'identifier' after 'for'", token_stream[0:tokens_checked])

            elif x == 3:
                if token_type == "ASSIGNMENT_OPERATOR":
                    continue
                else:
                    self.send_error_message("Missing '=' after variable declaration", token_stream[0:tokens_checked])

            elif x == 4:
                if token_type == "NUMBER":
                    ast['ForStatement']['initialization'].append({'value': token_value})
                else:
                    self.send_error_message("Expected a number after variable declaration", token_stream[0:tokens_checked])

            elif x == 5:
                if token_type == "DOUBLE_COLON":
                    continue
                else:
                    self.send_error_message("Missing '::' after initialization", token_stream[0:tokens_checked])

            elif x == 6:
                if token_type == "RELATIONAL_OPERATOR":
                    ast['ForStatement']['condition'].append({'relation': token_value})
                else:
                    self.send_error_message("Expected a relational operator after '::'", token_stream[0:tokens_checked])

            elif x == 7:
                if token_type in ["NUMBER", "IDENTIFIER"]:
                    if token_type == "IDENTIFIER" and token_value not in self.been_declared:
                        self.send_error_message(f"Variable '{token_value}' does not exist", token_stream[0:tokens_checked])
                    ast['ForStatement']['condition'].append({'value': token_value})
                    if token_type =="IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                else:
                    self.send_error_message("Expected a number or identifier in condition", token_stream[0:tokens_checked])

            elif x == 8:
                if token_type == "DOUBLE_COLON":
                    continue
                else:
                    self.send_error_message("Missing '::' after condition", token_stream[0:tokens_checked])

            elif x == 9:
                if token_type == "MATHEMATICAL_OPERATOR":
                    ast['ForStatement']['iteration'].append({'operator': token_value})
                else:
                    self.send_error_message("Expected a mathematical operator in iteration", token_stream[0:tokens_checked])

            elif x == 10:
                if token_type in ["NUMBER", "IDENTIFIER"]:
                    if token_type == "IDENTIFIER" and token_value not in self.been_declared:
                        self.send_error_message(f"Variable '{token_value}' does not exist", token_stream[0:tokens_checked])
                    ast['ForStatement']['iteration'].append({'value': token_value})
                    if token_type =="IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                else:
                    self.send_error_message("Expected a number or identifier in iteration", token_stream[0:tokens_checked])

            elif x == 11:
                if token_value == ")":
                    continue
                else:
                    self.send_error_message("Missing ')' after 'for' loop header", token_stream[0:tokens_checked])

            elif x == 12:
                if token_value == "{":
                    continue
                else:
                    self.send_error_message("Missing '{' to start 'for' loop body.", token_stream[0:x+1])
            elif x == 13:
                body_tokens = []
                op,cl = 0,0
                flag = True
                for token in token_stream[x:]:
                    if token[1] == "{":
                        op += 1
                    elif token[1] == "}":
                        cl += 1
                        if cl > op:
                            flag = False
                            break
                    body_tokens.append(token)
                    tokens_checked += 1
                if flag :
                    self.send_error_message("Missing '}' to close 'for' loop body.", token_stream[0:x+1])
                else:
                    ast['ForStatement']["body"] = self.parse_body(body_tokens)
            else:
                tokens_checked -= 1
                break

        if not isInBody :
            self.token_index += tokens_checked
            self.source_ast['main_scope'].append(ast)

        return [ast, tokens_checked]

    def fin_loop_parser(self, token_stream, isInBody):
        tokens_checked = 0
        ast = {"FinStatement": {"initialization": [], "data": [], "iteration": [], "body": []}}

        for x in range(len(token_stream)):
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            tokens_checked += 1

            if x == 0 :
                continue

            if x == 1:
                if token_value == "(":
                    continue
                else:
                    self.send_error_message("Missing '(' after 'fin'", token_stream[0:tokens_checked])

            elif x == 2:
                if token_type == "IDENTIFIER" and token_value in self.been_declared:
                    for line in self.symbol_table:
                        if line[0] == token_value:
                            line[6].append(token_stream[x][2])
                            line[2] = token_stream[x+2][1]
                            break
                    ast['FinStatement']['initialization'].append({'name': token_value})
                elif token_type == "IDENTIFIER" and token_value not in self.been_declared:
                    self.symbol_table.append([token_value, "int", token_stream[x+2][1], 4, 0, token_stream[x][2], [token_stream[x][2]], 4 + self.symbol_table[-1][-1]])
                    self.been_declared.append(token_value)
                    ast['FinStatement']['initialization'].append({'name': token_value})
                    ast['FinStatement']['initialization'].append({'value': "undefined"})
                else:
                    self.send_error_message("Expected 'identifier' after 'fin'", token_stream[0:tokens_checked])

            elif x == 3:
                if token_type == "DOUBLE_COLON":
                    continue
                else:
                    self.send_error_message("Missing '::' after initialization", token_stream[0:tokens_checked])

            elif x == 4:
                if token_type == "IDENTIFIER" :
                    if token_type == "IDENTIFIER" and token_value not in self.been_declared:
                        self.send_error_message(f"Variable '{token_value}' does not exist", token_stream[0:tokens_checked])
                    else:
                        for line in self.symbol_table:
                            if line[0] == token_value:
                                line[6].append(token_stream[x][2])
                                type = line[1]
                                break
                        if type in "arr":
                            ast['FinStatement']['data'].append({'value': token_value})
                        else:
                            self.send_error_message("Invalid data type Expect arr or set")
                else:
                    self.send_error_message("Expected a number or identifier in condition", token_stream[0:tokens_checked])
            elif x == 5:
                if token_type == "DOUBLE_COLON":
                    continue
                else:
                    self.send_error_message("Missing '::' after data", token_stream[0:tokens_checked])

            elif x == 6:
                if token_type == "MATHEMATICAL_OPERATOR":
                    ast['FinStatement']['iteration'].append({'operator': token_value})
                else:
                    self.send_error_message("Expected a mathematical operator in iteration", token_stream[0:tokens_checked])

            elif x == 7:
                if token_type in ["NUMBER", "IDENTIFIER"]:
                    if token_type == "IDENTIFIER" and token_value not in self.been_declared:
                        self.send_error_message(f"Variable '{token_value}' does not exist", token_stream[0:tokens_checked])
                    ast['FinStatement']['iteration'].append({'value': token_value})
                    if token_type =="IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                else:
                    self.send_error_message("Expected a number or identifier in iteration", token_stream[0:tokens_checked])

            elif x == 8:
                if token_value == ")":
                    continue
                else:
                    self.send_error_message("Missing ')' after 'fin' loop header", token_stream[0:tokens_checked])

            elif x == 9:
                if token_value == "{":
                    continue
                else:
                    self.send_error_message("Missing '{' to start 'fin' loop body.", token_stream[0:x+1])
            elif x == 10:
                body_tokens = []
                op,cl = 0,0
                flag = True
                for token in token_stream[x:]:
                    if token[1] == "{":
                        op += 1
                    elif token[1] == "}":
                        cl += 1
                        if cl > op:
                            flag = False
                            break
                    body_tokens.append(token)
                    tokens_checked += 1
                if flag :
                    self.send_error_message("Missing '}' to close 'for' loop body.", token_stream[0:x+1])
                else:
                    ast['FinStatement']["body"] = self.parse_body(body_tokens)
            else:
                tokens_checked -= 1
                break

        if not isInBody :
            self.token_index += tokens_checked
            self.source_ast['main_scope'].append(ast)

        return [ast, tokens_checked]




# Alaa
    def condition_statement_parser(self, token_stream, isNested):
        ast = {'IfStatement': {'Condition': [], 'Body': []}}
        tokens_checked = 0

        for x in range(len(token_stream)):
            tokens_checked += 1
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            if x == 0:
                    continue

            if x == 1:
                if token_value == "(":
                    continue
                else:
                    self.send_error_message("Missing '(' after 'if'", token_stream[0:tokens_checked + 1])
            elif x == 2:
                if token_type == "IDENTIFIER" or token_type == "NUMBER":
                    ast['IfStatement']['Condition'].append({'left': token_value})
                    if token_type =="IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                else:
                    self.send_error_message("Expected identifier or number in condition", token_stream[0:tokens_checked + 1])
            elif x == 3:
                if token_type == "RELATIONAL_OPERATOR":
                    ast['IfStatement']['Condition'].append({'operator': token_value})
                else:
                    self.send_error_message("Expected relational operator in condition", token_stream[0:tokens_checked + 1])
            elif x == 4:
                if token_type == "IDENTIFIER" or token_type == "NUMBER":
                    ast['IfStatement']['Condition'].append({'right': token_value})
                    if token_type =="IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                else:
                    self.send_error_message("Expected identifier or number in condition", token_stream[0:tokens_checked + 1])
            elif x == 5:
                if token_value == ")":
                    continue
                else:
                    self.send_error_message("Missing ')' after condition", token_stream[0:tokens_checked + 1])
            elif x == 6:
                if token_value == "{":
                    continue
                else:
                    self.send_error_message("Missing '{' to start 'if' body.", token_stream[0:x+1])
            elif x == 7:
                body_tokens = []
                ct = 0
                op,cl = 0,0
                flag = True 
                for token in token_stream[x:]:
                    if token[1] == "{":
                        op += 1
                    elif token[1] == "}":
                        cl += 1
                        if cl > op:
                            flag = False
                            break
                    body_tokens.append(token)
                    tokens_checked += 1
                    ct += 1
                if flag :
                    self.send_error_message("Missing '}' to close 'if' body.", token_stream[0:x+1])
                else:
                    ast['IfStatement']["Body"] = self.parse_body(body_tokens)

            # Parsing 'elif' statements
            elif token_value == "elif":
                elif_ast = self.elif_statement_parser(token_stream[x:])
                ast['IfStatement']['ElifStatement'] = elif_ast[0]["ElifStatement"]
                tokens_checked += elif_ast[1]
                

            # Parsing 'else' statement
            elif token_value == "else":
                if token_stream[x + 1][1] == "{":
                    x += 2
                    body_tokens = []
                    op,cl = 0,0
                    flag = True
                    for token in token_stream[x:]:
                        if token[1] == "{":
                            op += 1
                        elif token[1] == "}":
                            cl += 1
                            if cl > op:
                                flag = False
                                break
                        body_tokens.append(token)
                        tokens_checked += 1
                    if flag :
                        self.send_error_message("Missing '}' to close 'if' body.", token_stream[0:x+1])
                    else:
                        ast['IfStatement']['ElseBody'] = self.parse_body(body_tokens)
                        tokens_checked += 1
                        break
                else:
                    self.send_error_message("Missing '{' to start 'else' body.", token_stream[0:x+1])
            else:
                tokens_checked -= 1

        if not isNested:
            self.source_ast['main_scope'].append(ast)
            self.token_index += tokens_checked

        return [ast,tokens_checked]


    def elif_statement_parser(self, token_stream):
        ast = {'ElifStatement': {'Condition': [], 'Body': []}}
        tokens_checked = 0

        for x in range(len(token_stream)):
            tokens_checked += 1
            token_type = token_stream[x][0]
            token_value = token_stream[x][1]

            if x == 0:
                if token_value == "elif":
                    continue
                else:
                    self.send_error_message("Missing 'elif' keyword", token_stream[0:tokens_checked + 1])

            if x == 1:
                if token_value == "(":
                    continue
                else:
                    self.send_error_message("Missing '(' after 'elif'", token_stream[0:tokens_checked + 1])
            elif x == 2:
                if token_type == "IDENTIFIER" or token_type == "NUMBER":
                    ast['ElifStatement']['Condition'].append({'left': token_value})
                    if token_type =="IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                else:
                    self.send_error_message("Expected identifier or number in condition", token_stream[0:tokens_checked + 1])
            elif x == 3:
                if token_type == "RELATIONAL_OPERATOR":
                    ast['ElifStatement']['Condition'].append({'operator': token_value})
                else:
                    self.send_error_message("Expected relational operator in condition", token_stream[0:tokens_checked + 1])
            elif x == 4:
                if token_type == "IDENTIFIER" or token_type == "NUMBER":
                    ast['ElifStatement']['Condition'].append({'right': token_value})
                    if token_type =="IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                else:
                    self.send_error_message("Expected identifier or number in condition", token_stream[0:tokens_checked + 1])
            elif x == 5:
                if token_value == ")":
                    continue
                else:
                    self.send_error_message("Missing ')' after condition", token_stream[0:tokens_checked + 1])
            elif x == 6:
                if token_value == "{":
                    continue
                else:
                    self.send_error_message("Missing '{' to start 'if' body.", token_stream[0:x+1])
            elif x == 7:
                body_tokens = []
                op,cl = 0,0
                flag = True
                for token in token_stream[x:]:
                    if token[1] == "{":
                        op += 1
                    elif token[1] == "}":
                        cl += 1
                        if cl > op:
                            flag = False
                            break
                    body_tokens.append(token)
                    tokens_checked += 1
                if flag :
                    self.send_error_message("Missing '}' to close 'if' body.", token_stream[0:x+1])
                else:
                    ast['ElifStatement']["Body"] = self.parse_body(body_tokens)
                    break

        return [ast,tokens_checked]



# Nora
    def while_loop_parser(self, token_stream, isNested):
        ast = {'WhileLoop': {'Condition': [], 'Body': []}}
        tokens_checked = 0

        for x in range(0, len(token_stream)):
            tokens_checked += 1

            token_type = token_stream[x][0]
            token_value = token_stream[x][1]
            allowed_conditional_token_types = ['NUMBER', 'STRING', 'IDENTIFIER']

            if x == 0:
                continue
            if x == 1:
                if token_value == "(":
                    continue
                else:
                    self.send_error_message("Missing '(' after 'while' statement.", token_stream[0:x+1])

            elif x == 2:
                if token_type in allowed_conditional_token_types:
                    if token_type == "IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                            ast['WhileLoop']["Condition"].append({'value1': token_value})
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                    else:
                        ast['WhileLoop']["Condition"].append({'value1': token_value})
                else:
                    self.send_error_message("Invalid condition value '%s'. Expected number, string, or identifier." % token_value, token_stream[0:x+1])

            elif x == 3:
                if token_type == 'RELATIONAL_OPERATOR':
                    ast['WhileLoop']["Condition"].append({'comparison_type': token_value})
                else:
                    self.send_error_message("Invalid condition operator '%s'. Expected '==', '!=', '<', '>', '<=', '>='." % token_value, token_stream[0:x+1])

            elif x == 4:
                if token_type in allowed_conditional_token_types:
                    if token_type == "IDENTIFIER":
                        if token_value in self.been_declared:
                            for line in self.symbol_table:
                                if line[0] == token_value:
                                    line[6].append(token_stream[x][2])
                            ast['WhileLoop']["Condition"].append({'value2': token_value})
                        else:
                            self.send_error_message("Variable '%s' is not declared." % token_value, token_stream[0:x+1])
                    else:
                        ast['WhileLoop']["Condition"].append({'value2': token_value})
                else:
                    self.send_error_message("Invalid condition value '%s'. Expected number, string, or identifier." % token_value, token_stream[0:x+1])

            elif x == 5:
                if token_value == ")":
                    continue
                else:
                    self.send_error_message("Missing ')' after condition.", token_stream[0:x+1])

            elif x == 6:
                if token_value == "{":
                    continue
                else:
                    self.send_error_message("Missing '{' to start 'while' loop body.", token_stream[0:x+1])
            elif x == 7:
                body_tokens = []
                op,cl = 0,0
                flag = True
                for token in token_stream[x:]:
                    if token[1] == "{":
                        op += 1
                    elif token[1] == "}":
                        cl += 1
                        if cl > op:
                            flag = False
                            break
                    body_tokens.append(token)
                    tokens_checked += 1
                if flag :
                    self.send_error_message("Missing '}' to close 'while' loop body.", token_stream[0:x+1])
                else:
                    ast['WhileLoop']["Body"] = self.parse_body(body_tokens)
            else:
                tokens_checked -= 1
                break

        if not isNested:
            self.source_ast['main_scope'].append(ast)
            self.token_index += tokens_checked
        return [ast, tokens_checked]

# First -> Nora
# ----------------------------------------------------------------

    def parse_body(self, token_stream):
        ast = [] 

        token_checked = 0
        while token_checked < len(token_stream):
            token_type = token_stream[token_checked][0]
            token_value = token_stream[token_checked][1]

            if token_type == "DATATYPE":
                dec_body = self.declaration_parser(token_stream[token_checked:], True)
                ast.append(dec_body[0])
                token_checked += dec_body[1]

            # Handle if statements
            elif token_type == "KEYWORD" and token_value == "if":
                if_body = self.condition_statement_parser(token_stream[token_checked:], True)
                ast.append(if_body[0])  
                token_checked += if_body[1]  

            # Handle while loops
            elif token_type == "KEYWORD" and token_value == "while":
                while_body = self.while_loop_parser(token_stream[token_checked:], True)
                ast.append(while_body[0]) 
                token_checked += while_body[1]  

            # Handle for loops
            elif token_type == "KEYWORD" and token_value == "for":
                for_body = self.for_loop_parser(token_stream[token_checked:], True)
                ast.append(for_body[0])  
                token_checked += for_body[1]

            elif token_type == "KEYWORD" and token_value == "fin":
                fin_body = self.fin_loop_parser(token_stream[token_checked:], True)
                ast.append(fin_body[0])  
                token_checked += fin_body[1]

            elif token_type == "KEYWORD" and token_value in ["break", "continue", "pass"] :
                ast.append({"LoopAdds": {"value" :token_value}})
                token_checked += 1

            # Handle variable assignments
            elif token_type == "IDENTIFIER":
                assignment_body = self.assignment_parser(token_stream[token_checked:], True)
                ast.append(assignment_body[0])  
                token_checked += assignment_body[1]  

            # Handle print statements
            elif token_type == "PRINT_FUNCTION":
                print_body = self.print_function_parser(token_stream[token_checked:], True)
                ast.append(print_body[0]) 
                token_checked += print_body[1] 

            # Handle unexpected tokens
            else:
                self.send_error_message(f"Unexpect token '{token_value}'", token_stream[token_checked:])
                token_checked += 1  

        return ast

    def send_error_message(self, msg, error_list):

        print("------------------------ ERROR FOUND ----------------------------")
        print(" " + msg)
        print('\033[91m', "".join(str(r) for v in error_list for r in (v[1] + " ") ) , '\033[0m')
        print("-----------------------------------------------------------------")
        quit()