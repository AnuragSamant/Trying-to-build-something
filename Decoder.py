import Tokenizer
import Encoder

def decoder(code,dictio):
    id_to_token={value: key for key, value in dictio.items()}
    dencr=[]
    for i in code:
        token=id_to_token.get(i,"")
        if(token.endswith("</w>")):
            clean_token = token.replace("</w>"," ")
            dencr.append(clean_token)
        else:
            dencr.append(token)
    final_text="".join(dencr)
    print(final_text)

try:
    choi=input("Want to add new data to train Y/N ?:")
    if(choi.casefold()=="y" or choi.casefold()=="yes"):
        try:
            with open("data.txt","+a",encoding="utf-8") as f:
                new_da=input("Enter new data:")
                wri=" "+new_da
                f.write(wri)
                f.close()
        except Exception as e:
            print("Issue with file creation.")
            exit()
        resu=Tokenizer.main()
    else:
        resu=Tokenizer.load_tokenizer()
        if(resu):
            res=resu[0]
            amer=resu[1]
        else:
            exit()
    encode=Encoder.encoding(res,amer)
    code=encode[0]
    dictio=encode[1]
    decoder(code,dictio)
except Exception as e:
    print("Something Went wrong.")