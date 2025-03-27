import os

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
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None
    
    def error(self):
        raise Exception('Invalid character')
    
    def move_forward(self):
        self.pos += 1  # Moves the parsing position forward
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def skip_whitespace(self):
        # Skips non-newline whitespace characters
        while self.current_char is not None and self.current_char.isspace() and self.current_char != '\n':
            self.move_forward()
    
    def integer(self):
        # Handle complex number parsing (integers and floats)
        result = ''
        is_float = False
        
        if self.current_char == '-':
            result += self.current_char
            self.move_forward()
        
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.move_forward()
        
        if self.current_char == '.':
            is_float = True
            result += self.current_char
            self.move_forward()
            
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.move_forward()
        
        return Token(TokenType.FLOAT if is_float else TokenType.INTEGER, 
                    float(result) if is_float else int(result))
    
    def identifier(self):
        # Parsing identifiers is tricky due to function and variable name rules
        result = ''
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.move_forward()

        if result == 'sin':
            return Token(TokenType.SIN, result)
        elif result == 'cos':
            return Token(TokenType.COS, result)

        return Token(TokenType.IDENTIFIER, result)
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                if self.current_char == '\n':
                    self.move_forward()
                    return Token(TokenType.EOL, '\n')
                self.skip_whitespace()
                continue

            if self.current_char.isdigit() or self.current_char == '-':
                return self.integer()
            if self.current_char.isalpha():
                return self.identifier()
            if self.current_char == '+':
                self.move_forward()
                return Token(TokenType.PLUS, '+')
            if self.current_char == '-':
                self.move_forward()
                return Token(TokenType.MINUS, '-')
            if self.current_char == '*':
                self.move_forward()
                return Token(TokenType.MULTIPLY, '*')
            if self.current_char == '/':
                self.move_forward()
                return Token(TokenType.DIVIDE, '/')
            if self.current_char == '=':
                self.move_forward()
                return Token(TokenType.ASSIGN, '=')
            if self.current_char == '(':
                self.move_forward()
                return Token(TokenType.LPAREN, '(')
            if self.current_char == ')':
                self.move_forward()
                return Token(TokenType.RPAREN, ')')
            self.error()
        return Token(TokenType.EOF, None)
    

def tokenize_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as file:
        all_tokens = []
        
        content = file.read()
        lexer = Lexer(content)
        
        while True:
            token = lexer.get_next_token()
            all_tokens.append(token)
            
            if token.type == TokenType.EOF:  # stop when EOF is reached
                break

        return all_tokens


if __name__ == '__main__':
    tokens = tokenize_file("test.txt")
    for token in tokens:
        print(token, end=" ")
