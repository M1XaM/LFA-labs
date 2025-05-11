import os
import re

class TokenType:
    ASSIGN = 'ASSIGN'
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    IDENTIFIER = 'IDENTIFIER'
    EOF = 'EOF'
    EOL = 'EOL'

    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    SIN = 'SIN'
    COS = 'COS'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f'Token({self.type}, {self.value})'


class Lexer:
    token_patterns = [
        (r'[ \t]+', None),  # skip whitespace but not newlines
        (r'\n', TokenType.EOL),
        (r'=', TokenType.ASSIGN),
        (r'\(', TokenType.LPAREN),
        (r'\)', TokenType.RPAREN),
        (r'\+', TokenType.PLUS),
        (r'-', TokenType.MINUS),
        (r'\*', TokenType.MULTIPLY),
        (r'/', TokenType.DIVIDE),
        (r'sin\b', TokenType.SIN),  # \b ensures it's a word boundary
        (r'cos\b', TokenType.COS),
        (r'-?\d+\.\d+', TokenType.FLOAT),  # floating point numbers
        (r'-?\d+', TokenType.INTEGER),  # integers
        (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),  # identifiers
    ]
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None
        self.line_number = 1
    
    def tokenize(self):
        tokens = []
        position = 0
        
        while position < len(self.text):
            match = None
            
            for pattern, token_type in self.token_patterns:
                regex = re.compile(pattern)
                match = regex.match(self.text, position)
                
                if match:
                    value = match.group(0)
                    if token_type:
                        if token_type == TokenType.INTEGER:
                            tokens.append(Token(token_type, int(value)))
                        elif token_type == TokenType.FLOAT:
                            tokens.append(Token(token_type, float(value)))
                        elif token_type == TokenType.EOL:
                            tokens.append(Token(token_type, value))
                            self.line_number += 1
                        else:
                            tokens.append(Token(token_type, value))
                    
                    position = match.end()
                    break
            
            if not match:
                raise Exception(f'Invalid token at position {position}, line {self.line_number}')
        
        tokens.append(Token(TokenType.EOF, None))
        return tokens


class ASTNode:
    pass

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f'({self.left} {self.op.value} {self.right})'

class UnaryOpNode(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    
    def __repr__(self):
        return f'{self.op.value}({self.expr})'

class NumberNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __repr__(self):
        return str(self.value)

class VariableNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.name = token.value
    
    def __repr__(self):
        return self.name

class AssignNode(ASTNode):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value
    
    def __repr__(self):
        return f'{self.variable} = {self.value}'

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
    
    def error(self, expected=None):
        token = self.current_token
        msg = f'Syntax error at token: {token}'
        if expected:
            msg += f', expected: {expected}'
        raise Exception(msg)
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        return self.current_token
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            result = self.current_token
            self.advance()
            return result
        else:
            self.error(token_type)
    
    def parse(self):
        statements = []
        
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.EOL:
                self.advance()  # Skip EOL tokens
                continue
                
            statements.append(self.statement())
                
            # Expect EOL or EOF after each statement
            if self.current_token.type not in (TokenType.EOL, TokenType.EOF):
                self.error('EOL or EOF')
        
        return statements
    
    def statement(self):
        if (self.current_token.type == TokenType.IDENTIFIER and 
            self.pos + 1 < len(self.tokens) and 
            self.tokens[self.pos + 1].type == TokenType.ASSIGN):
            return self.assignment()
        else:
            return self.expr()
    
    def assignment(self):
        var_token = self.eat(TokenType.IDENTIFIER)
        variable = VariableNode(var_token)
        self.eat(TokenType.ASSIGN)
        value = self.expr()
        return AssignNode(variable, value)
    
    def expr(self):
        node = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            if op.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            else:
                self.eat(TokenType.MINUS)
            
            node = BinaryOpNode(node, op, self.term())
        
        return node
    
    def term(self):
        node = self.factor()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token
            if op.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            else:
                self.eat(TokenType.DIVIDE)
            
            node = BinaryOpNode(node, op, self.factor())
        
        return node
    
    def factor(self):
        token = self.current_token
        
        if token.type in (TokenType.INTEGER, TokenType.FLOAT):
            self.advance()
            return NumberNode(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return VariableNode(token)
        elif token.type in (TokenType.SIN, TokenType.COS):
            return self.function_call()
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOpNode(Token(TokenType.MINUS, '-'), self.factor())
        else:
            self.error()
    
    def function_call(self):
        token = self.current_token
        if token.type == TokenType.SIN:
            self.eat(TokenType.SIN)
        else:
            self.eat(TokenType.COS)
        
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        
        return UnaryOpNode(token, expr)

def parse_file(file_path):
    abs_file_path = os.path.abspath(file_path)
    if not os.path.exists(abs_file_path):
        raise FileNotFoundError(f"File not found: {abs_file_path}")
    with open(abs_file_path, 'r') as file:
        content = file.read()
        lexer = Lexer(content)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return tokens, ast

def print_ast(node, indent=0):
    indent_str = '  ' * indent
    
    if isinstance(node, list):
        for item in node:
            print_ast(item, indent)
    elif isinstance(node, BinaryOpNode):
        print(f"{indent_str}BinaryOp:")
        print(f"{indent_str}  Operator: {node.op.value}")
        print(f"{indent_str}  Left:")
        print_ast(node.left, indent + 2)
        print(f"{indent_str}  Right:")
        print_ast(node.right, indent + 2)
    elif isinstance(node, UnaryOpNode):
        print(f"{indent_str}UnaryOp:")
        print(f"{indent_str}  Operator: {node.op.value}")
        print(f"{indent_str}  Expr:")
        print_ast(node.expr, indent + 2)
    elif isinstance(node, NumberNode):
        print(f"{indent_str}Number: {node.value}")
    elif isinstance(node, VariableNode):
        print(f"{indent_str}Variable: {node.name}")
    elif isinstance(node, AssignNode):
        print(f"{indent_str}Assignment:")
        print(f"{indent_str}  Variable:")
        print_ast(node.variable, indent + 2)
        print(f"{indent_str}  Value:")
        print_ast(node.value, indent + 2)
    else:
        print(f"{indent_str}Unknown node type: {type(node)}")


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(script_dir, "test.txt")
    
    try:
        tokens, ast = parse_file(test_file_path)
        
        print("Tokens:")
        for token in tokens:
            print(token, end=" ")
        print("\n")
        
        print("AST:")
        print_ast(ast)
    except Exception as e:
        print(f"Error: {e}")