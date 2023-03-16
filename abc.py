from retry import retry



@retry(ValueError, delay=1, tries=10)
def make_trouble(abc):
    if abc==1:
        print("abc = 1")
        raise ValueError("abc = 1")
    else:
        print("okok")
    
make_trouble(1)