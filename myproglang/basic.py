##################
#CONSTANTS
##################

DIGITS = "0123456789"

class Error:
    def __init__(self,pos_start,pos_end, error_name,details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'File{self.pos_start.fn}, line{self.pos_start.ln+1}'
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start,pos_end,details):
        super().__init__(pos_start,pos_end,'Illegal characters',details)


##############
#POSITION
##############

class Position:
    def __init__(self,idx,ln,col,fn,ftxt):
        self.idx=idx
        self.ln =ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt # we can tell user which file error came from and display the line

    def advance(self, current_char):
        self.idx += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self
    
    def copy(self):
        return Position(self.idx,self.ln,self.col,self.fn,self.ftxt ) #return a new position

################
#token
################

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_POW = "POWER"

class Token:
    def __init__(self,type_,value=None):
        self.type=type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}' # if token has value print type and value, otherwise just type
        return f'{self.type}'
        

#############
#LEXER -->first stage of compiling, takes the source code and turns it into a executable code.
#lexer will take source code as input and turns them into individual tokens, tokens are meaningful units of code such as keywordsi operators and identifiers.
'''
The lexer removes any whitespace and comments from the code and identifies the type and value of each token. 
The output of the lexer is typically a stream of tokens, which are passed on to the next stage of the compiler or interpreter for further processing.
In general, a lexer is a fundamental component of any compiler or interpreter that reads and processes source code written in a high-level programming language. 
The lexer helps to parse the input code and break it down into a form that can be more easily analyzed and translated into machine-readable instructions.
'''
#############

class Lexer:
    def __init__(self,fn,text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1,0,-1,fn,text ) #advance will immedieately increment
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char) #this advance is the advance of position class.
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance() #skip the tab or white space
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()    
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW))
                self.advance()                
            else:
                pos_start = self.pos.copy()
                char =self.current_char
                self.advance()
                return [],IllegalCharError(pos_start,self.pos,"'"+char+"'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count +=1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance() #go to next char
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
        
###########################
#RUN
###########################

def run(fn,text):
    lexer = Lexer(fn,text)
    tokens, error = lexer.make_tokens()
    return tokens, error