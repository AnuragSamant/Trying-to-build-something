#================================================Tokenizer============================================
#=======================================Vocab creation and saving===========================================
import json

def word_c(text, count):
    words=text.split()
    for i in words:
        byte_list=list(i.encode("utf-8"))
        if byte_list:
            byte_list[-1]=str(byte_list[-1])+"</w>"
            byte_list[:-1]=[str(b) for b in byte_list[:-1]]
            wt=tuple(byte_list)
            count[wt]=count.get(wt,0)+1

def frequency(word_dict,frequencies):
    for word_tuple,word_count in word_dict.items():
        for i in range(len(word_tuple)-1):
            pair=(word_tuple[i],word_tuple[i+1])
            frequencies[pair]=frequencies.get(pair, 0)+word_count

def pair(frequencies,newg):
    if not frequencies:
        return
    maxv=max(frequencies.values())
    if(maxv<1):
        return
    candidates=[key for key,value in frequencies.items() if value==maxv]
    candidates.sort() 
    newg.append(candidates[0])

def merge(word_dict,best_pair,vocab):
    first, second=best_pair
    # FIX: Agar kisi bhi token ke end mein </w> hai, toh use properly handle karein
    if("</w>" in first):
        # Standard BPE mein aamtaur par word ke bich mein </w> nahi aata, 
        # par agar first mein hai, toh use clean karein
        combined=first.replace("</w>", "")+","+second
    elif("</w>" in second):
        # Agar second token mein </w> hai (jaise 'g</w>'), toh use naye word ke end mein shift karein
        combined=first+","+second.replace("</w>", "")+"</w>"
    else:
        # Normal characters ke liye normal merge
        combined=first+","+second
    if(combined not in vocab):
        vocab.append(combined)
    new_word_dict={}
    for word_tuple, word_count in word_dict.items():
        new_word=[]
        i=0
        while(i < len(word_tuple)):
            if(i<len(word_tuple)-1 and word_tuple[i]==first and word_tuple[i+1]==second):
                new_word.append(combined)
                i+=2
            else:
                new_word.append(word_tuple[i])
                i+=1
        merged_word = tuple(new_word)
        new_word_dict[merged_word] = new_word_dict.get(merged_word, 0) + word_count
    return new_word_dict

def save_tokenizer(vocab, all_merge, filename="training.json"):
    serializable_merges=[list(pair) for pair in all_merge]
    data = {
        "vocab": vocab,
        "all_merge": serializable_merges
    }
    with open(filename,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

def load_tokenizer(filename="training.json"):
    with open(filename,"r",encoding="utf-8") as f:
        data = json.load(f)
    if(data):
        all_merge=[tuple(pair) for pair in data["all_merge"]]
        vocab=data["vocab"]
        print(f"Data loaded successfully from {filename}!")
        return vocab,all_merge
    else:
        print("Training data not exists.")

def tokenize(text,ittretion=1500):
    word_dict={}
    word_c(text,word_dict)
    base_chars=set()
    for word_tuple in word_dict.keys():
        for item in word_tuple:
            base_chars.add(item)
    vocab=sorted(list(base_chars))
    if("<unk>" not in vocab):
        vocab.insert(0,"<unk>")
    all_merge=[]
    for i in range(ittretion):
        frequencies={}
        frequency(word_dict,frequencies)
        if not frequencies:
            break
        newg=[]
        pair(frequencies,newg)
        if newg:
            all_merge.append(newg[0])
            word_dict=merge(word_dict,newg[0],vocab)
    save_tokenizer(vocab,all_merge,filename="training.json")
    print("Tokenizer vocabulary and merges are successfully updated saved to training.json!")
    return vocab,all_merge

def main_f_t(coi_check=0):
    with open("data.txt","r",encoding="utf-8") as f:
        text=f.read()
    if(coi_check==0):
        itt=input("Want to increase iteration Y/N ?:")
        if(itt.casefold()=="y" or itt.casefold()=="yes"):
            num=int(input("Enter new iteration:"))
            return tokenize(text,num)
        else:
            return tokenize(text)
    else:
        return tokenize(text)

#=======================================Encoding and embeding of data===========================================
def tokenid(deco,res):
    for j,i in enumerate(res):
        deco[i]=j

def encode_text(amer,res,deco):
    newd=input("Enter data to check:")
    words=newd.split()
    encid=[]
    for w in words:
        singled={}
        byte_list=list(w.encode("utf-8"))
        if byte_list:
            byte_list[-1]=str(byte_list[-1])+"</w>"
            byte_list[:-1]=[str(b) for b in byte_list[:-1]]
            wt=tuple(byte_list)
            singled[wt]=1
        for i in amer:
            singled=merge(singled,i,res)
        for j in singled.keys():
            for k in j:
                if k in deco:
                    encid.append(deco[k])
                else:
                    fallback_byte=str(ord(k[0])) if len(k)>0 else "0"
                    encid.append(deco.get(fallback_byte,0))
    return encid

def encoding(res,amer):
    deco={}
    tokenid(deco,res)
    encode=encode_text(amer,res,deco)
    print(encode)
    return encode,deco

#========================================Decoder of embeddings==========================================
def decoder(code,dictio):
    id_to_token={value: key for key, value in dictio.items()}
    dencr=[]
    byte_accumulator=[]
    for i in code:
        token=id_to_token.get(i, "")
        if(token=="<unk>"):
            if(byte_accumulator):
                dencr.append(bytes(byte_accumulator).decode("utf-8", errors="replace"))
                byte_accumulator=[]
            dencr.append("<unk>")
            continue
        is_end=token.endswith("</w>")
        clean_token=token.replace("</w>","")
        parts=clean_token.split(",")
        for p in parts:
            if(p.isdigit()):
                byte_accumulator.append(int(p))
        if(is_end):
            decoded_word=bytes(byte_accumulator).decode("utf-8", errors="replace")+" "
            dencr.append(decoded_word)
            byte_accumulator=[]
    if(byte_accumulator):
        dencr.append(bytes(byte_accumulator).decode("utf-8", errors="replace"))
    final_text="".join(dencr).strip()
    print(final_text)

try:
    tra=input("Want to train again Y/N?:")
    if(tra.casefold()=="y" or tra.casefold()=="yes"):
        choi=input("Want to add new data maually Y/N ?:")
        if(choi.casefold()=="y" or choi.casefold()=="yes"):
            try:
                with open("data.txt","+a",encoding="utf-8") as f:
                    new_da=input("Enter new data:")
                    wri=" "+new_da
                    f.write(wri)
            except Exception as e:
                print("Issue with file creation.")
                exit()
            resu=main_f_t()
            res=resu[0]
            amer=resu[1]
        else:
            resu=main_f_t(1)
            res=resu[0]
            amer=resu[1]   
    else:
        resu=load_tokenizer()
        if(resu):
            res=resu[0]
            amer=resu[1]
        else:
            exit()
    encode=encoding(res,amer)
    code=encode[0]
    dictio=encode[1]
    decoder(code,dictio)
except Exception as e:
    print(e)
    print("Something Went wrong.")
#==================================================================================
#==================================================================================